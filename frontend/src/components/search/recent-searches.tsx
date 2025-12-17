"use client";

import { useState, useEffect } from "react";
import { History, X, TrendingUp } from "lucide-react";
import { Button } from "@/components/ui/button";

interface RecentSearchesProps {
  onSearchClick: (query: string) => void;
}

const STORAGE_KEY = "drive2_recent_searches";
const MAX_RECENT_SEARCHES = 10;

export function RecentSearches({ onSearchClick }: RecentSearchesProps) {
  const [recentSearches, setRecentSearches] = useState<string[]>([]);
  const [popularSearches] = useState<string[]>([
    "รูปภาพ",
    "เอกสาร",
    "วิดีโอ",
    "pdf",
  ]);

  // Load recent searches from localStorage
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        setRecentSearches(JSON.parse(stored));
      }
    } catch (error) {
      console.error("Failed to load recent searches:", error);
    }
  }, []);

  const handleSearchClick = (query: string) => {
    // Add to recent searches
    const updated = [
      query,
      ...recentSearches.filter((q) => q !== query),
    ].slice(0, MAX_RECENT_SEARCHES);

    setRecentSearches(updated);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
    } catch (error) {
      console.error("Failed to save recent search:", error);
    }

    onSearchClick(query);
  };

  const handleRemoveSearch = (query: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const updated = recentSearches.filter((q) => q !== query);
    setRecentSearches(updated);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
    } catch (error) {
      console.error("Failed to remove recent search:", error);
    }
  };

  const handleClearAll = () => {
    setRecentSearches([]);
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (error) {
      console.error("Failed to clear recent searches:", error);
    }
  };

  if (recentSearches.length === 0) {
    return (
      <div className="space-y-4">
        {/* Popular searches */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <TrendingUp className="w-4 h-4 text-gray-600" />
            <h3 className="font-medium text-sm">ยอดนิยม</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {popularSearches.map((query) => (
              <button
                key={query}
                onClick={() => handleSearchClick(query)}
                className="px-3 py-1.5 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-gray-200 transition-colors"
              >
                {query}
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Recent searches */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <History className="w-4 h-4 text-gray-600" />
            <h3 className="font-medium text-sm">ค้นหาล่าสุด</h3>
          </div>
          <Button
            onClick={handleClearAll}
            variant="ghost"
            size="sm"
            className="text-xs text-gray-500 hover:text-gray-700"
          >
            ล้างทั้งหมด
          </Button>
        </div>
        <div className="space-y-1">
          {recentSearches.map((query) => (
            <div
              key={query}
              onClick={() => handleSearchClick(query)}
              className="flex items-center justify-between px-3 py-2 rounded-lg hover:bg-gray-50 cursor-pointer group transition-colors"
            >
              <div className="flex items-center gap-2 flex-1 min-w-0">
                <History className="w-4 h-4 text-gray-400 flex-shrink-0" />
                <span className="text-sm text-gray-700 truncate">{query}</span>
              </div>
              <button
                onClick={(e) => handleRemoveSearch(query, e)}
                className="opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-200 rounded transition-opacity"
              >
                <X className="w-3 h-3 text-gray-500" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Popular searches */}
      <div>
        <div className="flex items-center gap-2 mb-3">
          <TrendingUp className="w-4 h-4 text-gray-600" />
          <h3 className="font-medium text-sm">ยอดนิยม</h3>
        </div>
        <div className="flex flex-wrap gap-2">
          {popularSearches.map((query) => (
            <button
              key={query}
              onClick={() => handleSearchClick(query)}
              className="px-3 py-1.5 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-gray-200 transition-colors"
            >
              {query}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
