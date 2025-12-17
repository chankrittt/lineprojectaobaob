"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { FileIcon, Loader2, Download, MoreVertical } from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { formatFileSize, formatRelativeTime, getFileIcon, truncate } from "@/lib/utils";
import type { File } from "@/lib/types";
import { Button } from "@/components/ui/button";

interface FileListProps {
  searchQuery?: string;
}

export function FileList({ searchQuery }: FileListProps) {
  const router = useRouter();

  const { data: files, isLoading, error } = useQuery({
    queryKey: ["files", searchQuery],
    queryFn: () => apiClient.getFiles({ search: searchQuery }),
  });

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
        เกิดข้อผิดพลาดในการโหลดไฟล์
      </div>
    );
  }

  if (!files || files.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <FileIcon className="w-16 h-16 mx-auto mb-4 text-gray-400" />
        <p>ไม่พบไฟล์</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border divide-y">
      {files.map((file: File) => (
        <div
          key={file.id}
          className="flex items-center gap-4 p-4 hover:bg-gray-50 transition-colors"
        >
          {/* Icon/Thumbnail */}
          <div
            className="flex-shrink-0 w-12 h-12 bg-gray-100 rounded flex items-center justify-center cursor-pointer"
            onClick={() => router.push(`/files/${file.id}`)}
          >
            {file.thumbnail_path ? (
              <img
                src={`${process.env.NEXT_PUBLIC_API_URL}/files/${file.id}/thumbnail`}
                alt={file.final_filename}
                className="w-full h-full object-cover rounded"
              />
            ) : (
              <span className="text-2xl">{getFileIcon(file.mime_type)}</span>
            )}
          </div>

          {/* File info */}
          <div
            className="flex-1 min-w-0 cursor-pointer"
            onClick={() => router.push(`/files/${file.id}`)}
          >
            <h3 className="font-medium text-sm mb-1 truncate" title={file.final_filename}>
              {file.final_filename}
            </h3>
            <div className="flex items-center gap-4 text-xs text-gray-500">
              <span>{formatFileSize(file.file_size)}</span>
              <span>{formatRelativeTime(file.uploaded_at)}</span>
              {file.processing_status !== "completed" && (
                <span className="text-yellow-600">
                  {file.processing_status === "pending" ? "รอประมวลผล" : "กำลังประมวลผล"}
                </span>
              )}
            </div>

            {/* Tags */}
            {file.ai_tags && file.ai_tags.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1">
                {file.ai_tags.slice(0, 3).map((tag) => (
                  <span
                    key={tag}
                    className="px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded"
                  >
                    #{tag}
                  </span>
                ))}
                {file.ai_tags.length > 3 && (
                  <span className="text-xs text-gray-500">
                    +{file.ai_tags.length - 3} more
                  </span>
                )}
              </div>
            )}

            {/* Summary */}
            {file.summary && (
              <p className="mt-1 text-xs text-gray-600 line-clamp-1">
                {truncate(file.summary, 100)}
              </p>
            )}
          </div>

          {/* Actions */}
          <div className="flex-shrink-0 flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={(e) => {
                e.stopPropagation();
                // Download logic
              }}
            >
              <Download className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={(e) => {
                e.stopPropagation();
                // More options
              }}
            >
              <MoreVertical className="w-4 h-4" />
            </Button>
          </div>
        </div>
      ))}
    </div>
  );
}
