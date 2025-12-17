"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { FileIcon, Loader2 } from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { formatFileSize, formatRelativeTime, getFileIcon, truncate } from "@/lib/utils";
import type { File } from "@/lib/types";

interface FileGridProps {
  searchQuery?: string;
}

export function FileGrid({ searchQuery }: FileGridProps) {
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
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {files.map((file: File) => (
        <div
          key={file.id}
          onClick={() => router.push(`/files/${file.id}`)}
          className="bg-white rounded-lg border hover:border-primary hover:shadow-md transition-all cursor-pointer overflow-hidden"
        >
          {/* Thumbnail */}
          <div className="aspect-square bg-gray-100 flex items-center justify-center relative">
            {file.thumbnail_path ? (
              <img
                src={`${process.env.NEXT_PUBLIC_API_URL}/files/${file.id}/thumbnail`}
                alt={file.final_filename}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="text-6xl">{getFileIcon(file.mime_type)}</div>
            )}

            {/* Status badge */}
            {file.processing_status !== "completed" && (
              <div className="absolute top-2 right-2 px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded">
                {file.processing_status === "pending" ? "รอประมวลผล" : "กำลังประมวลผล"}
              </div>
            )}
          </div>

          {/* Info */}
          <div className="p-3">
            <h3 className="font-medium text-sm mb-1 truncate" title={file.final_filename}>
              {truncate(file.final_filename, 30)}
            </h3>
            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>{formatFileSize(file.file_size)}</span>
              <span>{formatRelativeTime(file.uploaded_at)}</span>
            </div>

            {/* Tags */}
            {file.ai_tags && file.ai_tags.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1">
                {file.ai_tags.slice(0, 2).map((tag) => (
                  <span
                    key={tag}
                    className="px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded"
                  >
                    #{tag}
                  </span>
                ))}
                {file.ai_tags.length > 2 && (
                  <span className="px-2 py-0.5 bg-gray-50 text-gray-600 text-xs rounded">
                    +{file.ai_tags.length - 2}
                  </span>
                )}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
