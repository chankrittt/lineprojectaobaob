"""
Rate Limiter & Quota Manager for Gemini API

Handles:
- Rate limiting (15 requests per minute)
- Daily quota tracking (1500 requests per day)
- Redis-based distributed rate limiting
- Fallback to Ollama when quota exceeded
"""

import logging
import time
from typing import Optional
from datetime import datetime, timedelta
import redis
import json

logger = logging.getLogger(__name__)


class RateLimiter:
    """Redis-based rate limiter for Gemini API"""

    def __init__(self, redis_client: redis.Redis):
        """
        Initialize rate limiter

        Args:
            redis_client: Redis client instance
        """
        self.redis = redis_client

        # Gemini API limits (Free tier)
        self.rpm_limit = 15  # Requests per minute
        self.daily_limit = 1500  # Requests per day

        # Redis keys
        self.rpm_key = "gemini:rate:rpm"
        self.daily_key_prefix = "gemini:quota:daily"

    def _get_daily_key(self) -> str:
        """Get Redis key for today's quota"""
        today = datetime.utcnow().strftime("%Y-%m-%d")
        return f"{self.daily_key_prefix}:{today}"

    def check_rate_limit(self) -> tuple[bool, Optional[str]]:
        """
        Check if request can proceed without hitting rate limits

        Returns:
            Tuple of (allowed: bool, reason: str)
            - (True, None) if request is allowed
            - (False, reason) if request should be blocked
        """
        try:
            # Check RPM limit
            current_rpm = self.redis.get(self.rpm_key)
            if current_rpm and int(current_rpm) >= self.rpm_limit:
                logger.warning(f"RPM limit exceeded: {current_rpm}/{self.rpm_limit}")
                return False, "rate_limit_rpm"

            # Check daily quota
            daily_key = self._get_daily_key()
            current_daily = self.redis.get(daily_key)
            if current_daily and int(current_daily) >= self.daily_limit:
                logger.warning(f"Daily quota exceeded: {current_daily}/{self.daily_limit}")
                return False, "quota_exceeded"

            return True, None

        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            # Fail open - allow request if Redis is down
            return True, None

    def increment_usage(self) -> dict:
        """
        Increment usage counters for both RPM and daily quota

        Returns:
            Dict with current usage stats
        """
        try:
            # Increment RPM counter (expires after 60 seconds)
            rpm_count = self.redis.incr(self.rpm_key)
            if rpm_count == 1:
                # First request in this minute, set expiry
                self.redis.expire(self.rpm_key, 60)

            # Increment daily counter (expires at end of day)
            daily_key = self._get_daily_key()
            daily_count = self.redis.incr(daily_key)
            if daily_count == 1:
                # First request today, set expiry to end of day
                now = datetime.utcnow()
                end_of_day = now.replace(hour=23, minute=59, second=59)
                seconds_until_eod = int((end_of_day - now).total_seconds())
                self.redis.expire(daily_key, seconds_until_eod)

            logger.info(f"Gemini API usage - RPM: {rpm_count}/{self.rpm_limit}, Daily: {daily_count}/{self.daily_limit}")

            return {
                'rpm_count': rpm_count,
                'rpm_limit': self.rpm_limit,
                'daily_count': daily_count,
                'daily_limit': self.daily_limit,
                'rpm_remaining': max(0, self.rpm_limit - rpm_count),
                'daily_remaining': max(0, self.daily_limit - daily_count)
            }

        except Exception as e:
            logger.error(f"Error incrementing usage: {e}")
            return {}

    def get_current_usage(self) -> dict:
        """
        Get current usage statistics without incrementing

        Returns:
            Dict with current usage stats
        """
        try:
            rpm_count = self.redis.get(self.rpm_key)
            rpm_count = int(rpm_count) if rpm_count else 0

            daily_key = self._get_daily_key()
            daily_count = self.redis.get(daily_key)
            daily_count = int(daily_count) if daily_count else 0

            return {
                'rpm_count': rpm_count,
                'rpm_limit': self.rpm_limit,
                'daily_count': daily_count,
                'daily_limit': self.daily_limit,
                'rpm_remaining': max(0, self.rpm_limit - rpm_count),
                'daily_remaining': max(0, self.daily_limit - daily_count),
                'rpm_percentage': round((rpm_count / self.rpm_limit) * 100, 2),
                'daily_percentage': round((daily_count / self.daily_limit) * 100, 2)
            }

        except Exception as e:
            logger.error(f"Error getting usage: {e}")
            return {}

    def wait_if_needed(self, max_wait_seconds: int = 60) -> bool:
        """
        Wait if RPM limit is hit (but daily quota is OK)

        Args:
            max_wait_seconds: Maximum seconds to wait

        Returns:
            True if waited and can proceed, False if should fallback
        """
        try:
            allowed, reason = self.check_rate_limit()

            # If daily quota exceeded, don't wait
            if reason == "quota_exceeded":
                return False

            # If RPM limit hit, wait
            if reason == "rate_limit_rpm":
                ttl = self.redis.ttl(self.rpm_key)
                if 0 < ttl <= max_wait_seconds:
                    logger.info(f"RPM limit hit, waiting {ttl} seconds...")
                    time.sleep(ttl + 1)  # Wait for counter to reset
                    return True
                else:
                    logger.warning(f"RPM wait time ({ttl}s) exceeds max ({max_wait_seconds}s)")
                    return False

            return True

        except Exception as e:
            logger.error(f"Error in wait_if_needed: {e}")
            return True

    def reset_daily_quota(self) -> None:
        """Reset daily quota (admin function)"""
        try:
            daily_key = self._get_daily_key()
            self.redis.delete(daily_key)
            logger.info("Daily quota reset successfully")
        except Exception as e:
            logger.error(f"Error resetting daily quota: {e}")

    def should_use_fallback(self) -> bool:
        """
        Check if should use Ollama fallback instead of Gemini

        Returns:
            True if should use fallback (quota exceeded or limits hit)
        """
        allowed, reason = self.check_rate_limit()
        return not allowed


class QuotaTracker:
    """Track API usage history and statistics"""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.history_key = "gemini:usage:history"

    def log_request(self, success: bool, model: str = "gemini", error: Optional[str] = None):
        """
        Log API request to history

        Args:
            success: Whether request succeeded
            model: Model used (gemini or ollama)
            error: Error message if failed
        """
        try:
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'success': success,
                'model': model,
                'error': error
            }

            # Add to sorted set with timestamp as score
            score = int(datetime.utcnow().timestamp())
            self.redis.zadd(
                self.history_key,
                {json.dumps(log_entry): score}
            )

            # Keep only last 7 days of history
            seven_days_ago = int((datetime.utcnow() - timedelta(days=7)).timestamp())
            self.redis.zremrangebyscore(self.history_key, 0, seven_days_ago)

        except Exception as e:
            logger.error(f"Error logging request: {e}")

    def get_statistics(self, hours: int = 24) -> dict:
        """
        Get usage statistics for the last N hours

        Args:
            hours: Number of hours to look back

        Returns:
            Dict with statistics
        """
        try:
            since = int((datetime.utcnow() - timedelta(hours=hours)).timestamp())
            entries = self.redis.zrangebyscore(self.history_key, since, '+inf')

            total = len(entries)
            successful = 0
            failed = 0
            gemini_count = 0
            ollama_count = 0

            for entry in entries:
                try:
                    data = json.loads(entry)
                    if data.get('success'):
                        successful += 1
                    else:
                        failed += 1

                    if data.get('model') == 'gemini':
                        gemini_count += 1
                    elif data.get('model') == 'ollama':
                        ollama_count += 1
                except:
                    pass

            return {
                'period_hours': hours,
                'total_requests': total,
                'successful': successful,
                'failed': failed,
                'success_rate': round((successful / total * 100) if total > 0 else 0, 2),
                'gemini_requests': gemini_count,
                'ollama_requests': ollama_count,
                'fallback_rate': round((ollama_count / total * 100) if total > 0 else 0, 2)
            }

        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}


# Singleton instances (will be initialized in app startup)
rate_limiter: Optional[RateLimiter] = None
quota_tracker: Optional[QuotaTracker] = None


def initialize_rate_limiter(redis_client: redis.Redis):
    """Initialize global rate limiter and quota tracker"""
    global rate_limiter, quota_tracker
    rate_limiter = RateLimiter(redis_client)
    quota_tracker = QuotaTracker(redis_client)
    logger.info("Rate limiter and quota tracker initialized")


def get_rate_limiter() -> Optional[RateLimiter]:
    """Get global rate limiter instance"""
    return rate_limiter


def get_quota_tracker() -> Optional[QuotaTracker]:
    """Get global quota tracker instance"""
    return quota_tracker
