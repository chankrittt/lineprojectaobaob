"""Test all service connections"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(__file__))

from app.core.config import settings
from app.services.storage_service import storage_service
from app.services.vector_service import vector_service
from sqlalchemy.ext.asyncio import create_async_engine
from redis import asyncio as aioredis


async def test_postgres():
    """Test PostgreSQL connection"""
    print("\n📊 Testing PostgreSQL...")
    try:
        engine = create_async_engine(settings.DATABASE_URL)
        async with engine.connect() as conn:
            result = await conn.execute("SELECT 1")
        print("✅ PostgreSQL: Connected successfully")
        await engine.dispose()
        return True
    except Exception as e:
        print(f"❌ PostgreSQL: Failed - {e}")
        return False


async def test_redis():
    """Test Redis connection"""
    print("\n💾 Testing Redis...")
    try:
        redis = aioredis.from_url(settings.REDIS_URL)
        await redis.ping()
        print("✅ Redis: Connected successfully")
        await redis.close()
        return True
    except Exception as e:
        print(f"❌ Redis: Failed - {e}")
        return False


async def test_qdrant():
    """Test Qdrant connection"""
    print("\n🔍 Testing Qdrant...")
    try:
        info = await vector_service.get_collection_info()
        print(f"✅ Qdrant: Connected successfully")
        print(f"   Collection: {info['name']}")
        print(f"   Vectors: {info['vector_count']}")
        print(f"   Status: {info['status']}")
        return True
    except Exception as e:
        print(f"❌ Qdrant: Failed - {e}")
        return False


async def test_minio():
    """Test MinIO connection"""
    print("\n📦 Testing MinIO...")
    try:
        # Try to list buckets
        buckets = storage_service.client.list_buckets()
        print(f"✅ MinIO: Connected successfully")
        print(f"   Endpoint: {settings.MINIO_ENDPOINT}")
        print(f"   Total buckets: {len(buckets)}")

        # Check if our bucket exists
        if storage_service.client.bucket_exists(settings.MINIO_BUCKET_NAME):
            print(f"   ✓ Bucket '{settings.MINIO_BUCKET_NAME}' exists")
        else:
            print(f"   ⚠ Bucket '{settings.MINIO_BUCKET_NAME}' not found, creating...")
            storage_service.client.make_bucket(settings.MINIO_BUCKET_NAME)
            print(f"   ✓ Bucket created successfully")

        return True
    except Exception as e:
        print(f"❌ MinIO: Failed - {e}")
        print(f"   Check if MinIO is running at {settings.MINIO_ENDPOINT}")
        print(f"   Verify ACCESS_KEY and SECRET_KEY are correct")
        return False


async def test_gemini():
    """Test Gemini API connection"""
    print("\n🤖 Testing Gemini API...")
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        response = model.generate_content("Say 'Hello'")
        print(f"✅ Gemini API: Connected successfully")
        print(f"   Model: {settings.GEMINI_MODEL}")
        print(f"   Response: {response.text[:50]}...")
        return True
    except Exception as e:
        print(f"❌ Gemini API: Failed - {e}")
        print(f"   Check if GEMINI_API_KEY is correct")
        return False


async def main():
    print("=" * 60)
    print("🔍 Drive2 - Service Connection Tests")
    print("=" * 60)

    results = {}

    # Test all services
    results['postgres'] = await test_postgres()
    results['redis'] = await test_redis()
    results['qdrant'] = await test_qdrant()
    results['minio'] = await test_minio()
    results['gemini'] = await test_gemini()

    # Summary
    print("\n" + "=" * 60)
    print("📋 Summary")
    print("=" * 60)

    all_passed = all(results.values())
    passed = sum(results.values())
    total = len(results)

    for service, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {service.upper()}: {'PASS' if status else 'FAIL'}")

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All services connected successfully!")
        print("✨ You're ready to start developing!")
    else:
        print(f"⚠️  {total - passed} service(s) failed to connect")
        print("Please check the error messages above")

    print("=" * 60)

    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
