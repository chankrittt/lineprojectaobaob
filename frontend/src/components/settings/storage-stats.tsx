"use client";

import { HardDrive, TrendingUp } from "lucide-react";
import { formatFileSize } from "@/lib/utils";
import type { Stats } from "@/lib/types";

interface StorageStatsProps {
  stats?: Stats;
}

const STORAGE_LIMIT = 15 * 1024 * 1024 * 1024; // 15GB in bytes

export function StorageStats({ stats }: StorageStatsProps) {
  if (!stats) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-4 bg-gray-200 rounded w-1/4"></div>
        <div className="h-8 bg-gray-200 rounded"></div>
        <div className="h-4 bg-gray-200 rounded w-1/3"></div>
      </div>
    );
  }

  const usedBytes = stats.total_size || 0;
  const usedPercentage = (usedBytes / STORAGE_LIMIT) * 100;
  const remainingBytes = Math.max(0, STORAGE_LIMIT - usedBytes);

  return (
    <div className="space-y-6">
      {/* Storage overview */}
      <div className="flex items-center gap-4">
        <div className="p-3 bg-primary/10 rounded-lg">
          <HardDrive className="w-8 h-8 text-primary" />
        </div>
        <div className="flex-1">
          <div className="flex items-baseline gap-2 mb-1">
            <span className="text-3xl font-bold">{formatFileSize(usedBytes)}</span>
            <span className="text-gray-500">/ {formatFileSize(STORAGE_LIMIT)}</span>
          </div>
          <p className="text-sm text-gray-600">
            เหลือพื้นที่ {formatFileSize(remainingBytes)}
          </p>
        </div>
      </div>

      {/* Progress bar */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">การใช้งาน</span>
          <span className="text-sm font-medium text-gray-700">
            {usedPercentage.toFixed(1)}%
          </span>
        </div>
        <div className="h-4 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-500 ${
              usedPercentage > 90
                ? "bg-red-500"
                : usedPercentage > 75
                  ? "bg-yellow-500"
                  : "bg-primary"
            }`}
            style={{ width: `${Math.min(usedPercentage, 100)}%` }}
          />
        </div>
        {usedPercentage > 90 && (
          <p className="mt-2 text-sm text-red-600">
            พื้นที่เก็บข้อมูลใกล้เต็ม กรุณาลบไฟล์ที่ไม่ต้องการ
          </p>
        )}
      </div>

      {/* Quick stats */}
      <div className="grid grid-cols-3 gap-4 pt-4 border-t">
        <div className="text-center">
          <div className="text-2xl font-bold text-primary">
            {stats.total_files || 0}
          </div>
          <div className="text-xs text-gray-600 mt-1">ไฟล์ทั้งหมด</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-primary">
            {stats.total_collections || 0}
          </div>
          <div className="text-xs text-gray-600 mt-1">คอลเล็กชัน</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-primary">
            {stats.files_this_month || 0}
          </div>
          <div className="text-xs text-gray-600 mt-1 flex items-center justify-center gap-1">
            <TrendingUp className="w-3 h-3" />
            เดือนนี้
          </div>
        </div>
      </div>
    </div>
  );
}
