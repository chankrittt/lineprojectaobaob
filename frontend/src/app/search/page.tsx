"use client";

import { Suspense, useState } from "react";
import { useSearchParams } from "next/navigation";
import { SearchBar } from "@/components/search/search-bar";
import { SearchResults } from "@/components/search/search-results";
import { SearchFilters } from "@/components/search/search-filters";
import { RecentSearches } from "@/components/search/recent-searches";

function SearchPageContent() {
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get("q") || "";

  const [query, setQuery] = useState(initialQuery);
  const [searchMode, setSearchMode] = useState<"semantic" | "keyword">("semantic");
  const [filters, setFilters] = useState({
    fileType: undefined as string | undefined,
    dateFrom: undefined as string | undefined,
    dateTo: undefined as string | undefined,
    minSize: undefined as number | undefined,
    maxSize: undefined as number | undefined,
  });

  const toggleSearchMode = () => {
    setSearchMode((prev) => (prev === "semantic" ? "keyword" : "semantic"));
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold mb-4">ค้นหาไฟล์</h1>
          <SearchBar
            value={query}
            onChange={setQuery}
            placeholder="ค้นหาจากชื่อไฟล์ เนื้อหา หรือแท็ก..."
            autoFocus
          />
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Filters Sidebar */}
          <div className="lg:col-span-1 space-y-4">
            <SearchFilters filters={filters} onChange={setFilters} />
            <div className="bg-white rounded-lg border p-4">
              <RecentSearches onSearchClick={setQuery} />
            </div>
          </div>

          {/* Results */}
          <div className="lg:col-span-3">
            {query ? (
              <SearchResults
                query={query}
                filters={filters}
                searchMode={searchMode}
                onToggleSearchMode={toggleSearchMode}
              />
            ) : (
              <div className="bg-white rounded-lg border p-12">
                <RecentSearches onSearchClick={setQuery} />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600">กำลังโหลด...</p>
        </div>
      </div>
    }>
      <SearchPageContent />
    </Suspense>
  );
}
