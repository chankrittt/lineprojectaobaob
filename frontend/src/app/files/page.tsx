"use client";

import { useState } from "react";
import { FileList } from "@/components/files/file-list";
import { FileGrid } from "@/components/files/file-grid";
import { SearchBar } from "@/components/search/search-bar";
import { ViewToggle } from "@/components/ui/view-toggle";
import { FilterBar } from "@/components/files/filter-bar";
import { LayoutGrid, List } from "lucide-react";

export default function FilesPage() {
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [searchQuery, setSearchQuery] = useState("");

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold mb-4">ไฟล์ของฉัน</h1>

          <SearchBar
            value={searchQuery}
            onChange={setSearchQuery}
            placeholder="ค้นหาไฟล์..."
          />

          <div className="flex items-center justify-between mt-4">
            <FilterBar />
            <ViewToggle
              view={viewMode}
              onViewChange={setViewMode}
              options={[
                { value: "grid", icon: LayoutGrid, label: "Grid" },
                { value: "list", icon: List, label: "List" },
              ]}
            />
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        {viewMode === "grid" ? (
          <FileGrid searchQuery={searchQuery} />
        ) : (
          <FileList searchQuery={searchQuery} />
        )}
      </div>
    </div>
  );
}
