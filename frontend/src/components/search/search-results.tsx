"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { FileIcon, Loader2, Sparkles, Search as SearchIcon } from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { formatFileSize, formatRelativeTime, getFileIcon, truncate } from "@/lib/utils";
import type { SearchResult } from "@/lib/types";
import { Button } from "@/components/ui/button";

interface SearchResultsProps {
  query: string;
  filters: {
    fileType?: string;
    dateFrom?: string;
    dateTo?: string;
    minSize?: number;
    maxSize?: number;
  };
  searchMode: "semantic" | "keyword";
  onToggleSearchMode: () => void;
}

export function SearchResults({
  query,
  filters,
  searchMode,
  onToggleSearchMode,
}: SearchResultsProps) {
  const router = useRouter();

  const { data: results, isLoading, error } = useQuery({
    queryKey: ["search", query, filters, searchMode],
    queryFn: () =>
      apiClient.searchFiles(query, {
        ...filters,
        semantic: searchMode === "semantic",
      }),
    enabled: query.length > 0,
  });

  if (query.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <SearchIcon className="w-16 h-16 mx-auto mb-4 text-gray-400" />
        <p>พิมพ์คำค้นหาเพื่อเริ่มต้น</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12 text-red-600">
        เกิดข้อผิดพลาดในการค้นหา
      </div>
    );
  }

  if (!results || results.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <FileIcon className="w-16 h-16 mx-auto mb-4 text-gray-400" />
        <p className="mb-4">ไม่พบผลลัพธ์</p>
        {searchMode === "keyword" && (
          <Button onClick={onToggleSearchMode} variant="outline" size="sm">
            <Sparkles className="w-4 h-4 mr-2" />
            ลองค้นหาแบบ Semantic
          </Button>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Search mode toggle */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-600">
          พบ {results.length} ไฟล์
        </p>
        <Button
          onClick={onToggleSearchMode}
          variant="outline"
          size="sm"
          className="gap-2"
        >
          {searchMode === "semantic" ? (
            <>
              <Sparkles className="w-4 h-4" />
              ค้นหาแบบ Semantic
            </>
          ) : (
            <>
              <SearchIcon className="w-4 h-4" />
              ค้นหาแบบปกติ
            </>
          )}
        </Button>
      </div>

      {/* Results list */}
      <div className="bg-white rounded-lg border divide-y">
        {results.map((result: SearchResult) => (
          <div
            key={result.file.id}
            onClick={() => router.push(`/files/${result.file.id}`)}
            className="flex items-center gap-4 p-4 hover:bg-gray-50 transition-colors cursor-pointer"
          >
            {/* Icon/Thumbnail */}
            <div className="flex-shrink-0 w-12 h-12 bg-gray-100 rounded flex items-center justify-center">
              {result.file.thumbnail_path ? (
                <img
                  src={`${process.env.NEXT_PUBLIC_API_URL}/files/${result.file.id}/thumbnail`}
                  alt={result.file.final_filename}
                  className="w-full h-full object-cover rounded"
                />
              ) : (
                <span className="text-2xl">{getFileIcon(result.file.mime_type)}</span>
              )}
            </div>

            {/* File info */}
            <div className="flex-1 min-w-0">
              <h3 className="font-medium text-sm mb-1 truncate">
                {result.file.final_filename}
              </h3>
              <div className="flex items-center gap-4 text-xs text-gray-500 mb-2">
                <span>{formatFileSize(result.file.file_size)}</span>
                <span>{formatRelativeTime(result.file.uploaded_at)}</span>
                {searchMode === "semantic" && result.score !== undefined && (
                  <span className="text-primary">
                    ความเกี่ยวข้อง: {Math.round(result.score * 100)}%
                  </span>
                )}
              </div>

              {/* Tags */}
              {result.file.ai_tags && result.file.ai_tags.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-2">
                  {result.file.ai_tags.slice(0, 3).map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded"
                    >
                      #{tag}
                    </span>
                  ))}
                  {result.file.ai_tags.length > 3 && (
                    <span className="text-xs text-gray-500">
                      +{result.file.ai_tags.length - 3}
                    </span>
                  )}
                </div>
              )}

              {/* Summary with highlights */}
              {result.file.summary && (
                <p className="text-xs text-gray-600 line-clamp-2">
                  {result.highlights && result.highlights.length > 0
                    ? result.highlights[0]
                    : truncate(result.file.summary, 150)}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
