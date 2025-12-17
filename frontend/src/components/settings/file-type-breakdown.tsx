"use client";

import { FileIcon, Image, Video, Music, FileText, File } from "lucide-react";
import { formatFileSize } from "@/lib/utils";
import type { Stats } from "@/lib/types";

interface FileTypeBreakdownProps {
  stats?: Stats;
}

const FILE_TYPE_ICONS: Record<string, any> = {
  image: { icon: Image, color: "text-blue-600", bg: "bg-blue-50" },
  video: { icon: Video, color: "text-purple-600", bg: "bg-purple-50" },
  audio: { icon: Music, color: "text-green-600", bg: "bg-green-50" },
  document: { icon: FileText, color: "text-orange-600", bg: "bg-orange-50" },
  other: { icon: File, color: "text-gray-600", bg: "bg-gray-50" },
};

const FILE_TYPE_LABELS: Record<string, string> = {
  image: "รูปภาพ",
  video: "วิดีโอ",
  audio: "เสียง",
  document: "เอกสาร",
  other: "อื่นๆ",
};

export function FileTypeBreakdown({ stats }: FileTypeBreakdownProps) {
  if (!stats) {
    return (
      <div className="space-y-3">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="animate-pulse flex items-center gap-3">
            <div className="w-10 h-10 bg-gray-200 rounded-lg" />
            <div className="flex-1">
              <div className="h-4 bg-gray-200 rounded w-1/4 mb-2" />
              <div className="h-2 bg-gray-200 rounded" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  const fileTypeData = stats.file_types_breakdown || {};
  const totalSize = stats.total_size || 1; // Avoid division by zero

  // Convert file types to array and sort by size
  const sortedTypes = Object.entries(fileTypeData)
    .map(([type, data]: [string, any]) => ({
      type,
      count: data.count || 0,
      size: data.size || 0,
    }))
    .sort((a, b) => b.size - a.size);

  if (sortedTypes.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <FileIcon className="w-12 h-12 mx-auto mb-2 text-gray-400" />
        <p className="text-sm">ยังไม่มีไฟล์</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {sortedTypes.map(({ type, count, size }) => {
        const percentage = (size / totalSize) * 100;
        const iconData = FILE_TYPE_ICONS[type] || FILE_TYPE_ICONS.other;
        const Icon = iconData.icon;
        const label = FILE_TYPE_LABELS[type] || type;

        return (
          <div key={type} className="space-y-2">
            {/* Type header */}
            <div className="flex items-center gap-3">
              <div className={`p-2 ${iconData.bg} rounded-lg`}>
                <Icon className={`w-5 h-5 ${iconData.color}`} />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-gray-700">
                    {label}
                  </span>
                  <span className="text-sm text-gray-600">
                    {count} ไฟล์ • {formatFileSize(size)}
                  </span>
                </div>
                {/* Progress bar */}
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full transition-all duration-500 ${iconData.color.replace("text-", "bg-")}`}
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
              <div className="text-sm font-medium text-gray-700 w-12 text-right">
                {percentage.toFixed(1)}%
              </div>
            </div>
          </div>
        );
      })}

      {/* Total summary */}
      <div className="pt-4 border-t flex items-center justify-between text-sm">
        <span className="font-medium text-gray-700">ทั้งหมด</span>
        <span className="text-gray-600">
          {stats.total_files || 0} ไฟล์ • {formatFileSize(totalSize)}
        </span>
      </div>
    </div>
  );
}
