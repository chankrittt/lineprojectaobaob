"use client";

import { useState } from "react";
import { Filter, X } from "lucide-react";
import { Button } from "@/components/ui/button";

interface SearchFiltersProps {
  filters: {
    fileType?: string;
    dateFrom?: string;
    dateTo?: string;
    minSize?: number;
    maxSize?: number;
  };
  onChange: (filters: any) => void;
}

const FILE_TYPES = [
  { value: "", label: "ทุกประเภท" },
  { value: "image/", label: "รูปภาพ" },
  { value: "video/", label: "วิดีโอ" },
  { value: "audio/", label: "เสียง" },
  { value: "application/pdf", label: "PDF" },
  { value: "text/", label: "เอกสาร" },
];

const FILE_SIZES = [
  { value: "", label: "ทุกขนาด" },
  { value: "0-1", label: "< 1 MB" },
  { value: "1-10", label: "1-10 MB" },
  { value: "10-100", label: "10-100 MB" },
  { value: "100-1000", label: "100 MB - 1 GB" },
  { value: "1000-", label: "> 1 GB" },
];

export function SearchFilters({ filters, onChange }: SearchFiltersProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleFileTypeChange = (fileType: string) => {
    onChange({ ...filters, fileType: fileType || undefined });
  };

  const handleSizeChange = (sizeRange: string) => {
    if (!sizeRange) {
      onChange({ ...filters, minSize: undefined, maxSize: undefined });
      return;
    }

    const [min, max] = sizeRange.split("-").map(Number);
    onChange({
      ...filters,
      minSize: min * 1024 * 1024 || undefined,
      maxSize: max ? max * 1024 * 1024 : undefined,
    });
  };

  const handleDateFromChange = (date: string) => {
    onChange({ ...filters, dateFrom: date || undefined });
  };

  const handleDateToChange = (date: string) => {
    onChange({ ...filters, dateTo: date || undefined });
  };

  const handleClearFilters = () => {
    onChange({
      fileType: undefined,
      dateFrom: undefined,
      dateTo: undefined,
      minSize: undefined,
      maxSize: undefined,
    });
  };

  const hasActiveFilters =
    filters.fileType ||
    filters.dateFrom ||
    filters.dateTo ||
    filters.minSize !== undefined ||
    filters.maxSize !== undefined;

  return (
    <div className="bg-white rounded-lg border">
      {/* Filter header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-600" />
          <h3 className="font-medium text-sm">ตัวกรอง</h3>
          {hasActiveFilters && (
            <span className="px-2 py-0.5 bg-primary text-white text-xs rounded-full">
              มีการกรอง
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {hasActiveFilters && (
            <Button
              onClick={handleClearFilters}
              variant="ghost"
              size="sm"
              className="text-xs"
            >
              ล้างทั้งหมด
            </Button>
          )}
          <Button
            onClick={() => setIsExpanded(!isExpanded)}
            variant="ghost"
            size="sm"
          >
            {isExpanded ? "ซ่อน" : "แสดง"}
          </Button>
        </div>
      </div>

      {/* Filter options */}
      {isExpanded && (
        <div className="p-4 space-y-4">
          {/* File type filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              ประเภทไฟล์
            </label>
            <div className="grid grid-cols-2 gap-2">
              {FILE_TYPES.map((type) => (
                <button
                  key={type.value}
                  onClick={() => handleFileTypeChange(type.value)}
                  className={`px-3 py-2 text-sm rounded-lg border transition-colors ${
                    (filters.fileType || "") === type.value
                      ? "bg-primary text-white border-primary"
                      : "bg-white text-gray-700 border-gray-300 hover:border-primary"
                  }`}
                >
                  {type.label}
                </button>
              ))}
            </div>
          </div>

          {/* File size filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              ขนาดไฟล์
            </label>
            <div className="grid grid-cols-2 gap-2">
              {FILE_SIZES.map((size) => {
                const isActive =
                  !filters.minSize && !filters.maxSize
                    ? size.value === ""
                    : size.value !== "" &&
                      (() => {
                        const [min, max] = size.value.split("-").map(Number);
                        const minBytes = min * 1024 * 1024;
                        const maxBytes = max ? max * 1024 * 1024 : undefined;
                        return (
                          filters.minSize === minBytes &&
                          filters.maxSize === maxBytes
                        );
                      })();

                return (
                  <button
                    key={size.value}
                    onClick={() => handleSizeChange(size.value)}
                    className={`px-3 py-2 text-sm rounded-lg border transition-colors ${
                      isActive
                        ? "bg-primary text-white border-primary"
                        : "bg-white text-gray-700 border-gray-300 hover:border-primary"
                    }`}
                  >
                    {size.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Date range filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              วันที่อัปโหลด
            </label>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-xs text-gray-500 mb-1">จาก</label>
                <input
                  type="date"
                  value={filters.dateFrom || ""}
                  onChange={(e) => handleDateFromChange(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">ถึง</label>
                <input
                  type="date"
                  value={filters.dateTo || ""}
                  onChange={(e) => handleDateToChange(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
