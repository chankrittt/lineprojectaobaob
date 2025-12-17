"use client";

import { Calendar, HardDrive, FileType, User, Clock } from "lucide-react";
import { formatFileSize, formatDate, formatRelativeTime } from "@/lib/utils";
import type { File } from "@/lib/types";

interface FileMetaProps {
  file: File;
}

export function FileMeta({ file }: FileMetaProps) {
  const metadataItems = [
    {
      icon: FileType,
      label: "ประเภทไฟล์",
      value: file.mime_type,
    },
    {
      icon: HardDrive,
      label: "ขนาดไฟล์",
      value: formatFileSize(file.file_size),
    },
    {
      icon: Calendar,
      label: "อัปโหลดเมื่อ",
      value: formatDate(file.uploaded_at),
      subtitle: formatRelativeTime(file.uploaded_at),
    },
    {
      icon: User,
      label: "ชื่อไฟล์ต้นฉบับ",
      value: file.original_filename,
    },
    {
      icon: Clock,
      label: "สถานะการประมวลผล",
      value:
        file.processing_status === "completed"
          ? "เสร็จสมบูรณ์"
          : file.processing_status === "processing"
            ? "กำลังประมวลผล"
            : "รอประมวลผล",
      color:
        file.processing_status === "completed"
          ? "text-green-600"
          : file.processing_status === "processing"
            ? "text-yellow-600"
            : "text-gray-600",
    },
  ];

  // Add video metadata if available
  if (file.video_metadata) {
    const metadata = file.video_metadata;
    if (metadata.duration) {
      const minutes = Math.floor(metadata.duration / 60);
      const seconds = Math.floor(metadata.duration % 60);
      metadataItems.push({
        icon: Clock,
        label: "ความยาว",
        value: `${minutes}:${seconds.toString().padStart(2, "0")}`,
      });
    }
    if (metadata.width && metadata.height) {
      metadataItems.push({
        icon: FileType,
        label: "ความละเอียด",
        value: `${metadata.width} × ${metadata.height}`,
      });
    }
  }

  return (
    <div className="space-y-4">
      {metadataItems.map((item, index) => (
        <div
          key={index}
          className="flex items-start gap-3 pb-3 border-b last:border-0 last:pb-0"
        >
          <div className="p-2 bg-gray-100 rounded-lg">
            <item.icon className="w-4 h-4 text-gray-600" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-xs text-gray-500 mb-1">{item.label}</div>
            <div className={`text-sm font-medium ${item.color || "text-gray-900"} break-all`}>
              {item.value}
            </div>
            {item.subtitle && (
              <div className="text-xs text-gray-500 mt-1">{item.subtitle}</div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
