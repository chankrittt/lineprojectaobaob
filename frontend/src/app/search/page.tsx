"use client";

import { useState } from "react";
import { useSearchParams } from "next/navigation";
import { SearchBar } from "@/components/search/search-bar";
import { SearchResults } from "@/components/search/search-results";
import { SearchFilters } from "@/components/search/search-filters";
import { RecentSearches } from "@/components/search/recent-searches";

export default function SearchPage() {
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get("q") || "";

  const [query, setQuery] = useState(initialQuery);
  const [filters, setFilters] = useState({
    types: [] as string[],
    tags: [] as string[],
    dateFrom: null as Date | null,
    dateTo: null as Date | null,
  });

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
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm p-4 sticky top-24">
              <SearchFilters filters={filters} onChange={setFilters} />
              <div className="mt-6 pt-6 border-t">
                <RecentSearches onSearchClick={setQuery} />
              </div>
            </div>
          </div>

          {/* Results */}
          <div className="lg:col-span-3">
            {query ? (
              <SearchResults query={query} filters={filters} />
            ) : (
              <div className="text-center py-12 text-gray-500">
                <p>ป้อนคำค้นหาเพื่อเริ่มต้น</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
