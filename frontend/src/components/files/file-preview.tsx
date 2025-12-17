"use client";

import { FileIcon } from "lucide-react";
import type { File } from "@/lib/types";

interface FilePreviewProps {
  file: File;
}

export function FilePreview({ file }: FilePreviewProps) {
  const renderPreview = () => {
    // Image preview
    if (file.mime_type.startsWith("image/")) {
      return (
        <img
          src={`${process.env.NEXT_PUBLIC_API_URL}/files/${file.id}/download`}
          alt={file.final_filename}
          className="max-w-full h-auto mx-auto"
        />
      );
    }

    // PDF preview
    if (file.mime_type === "application/pdf") {
      return (
        <iframe
          src={`${process.env.NEXT_PUBLIC_API_URL}/files/${file.id}/download`}
          className="w-full h-[600px]"
          title={file.final_filename}
        />
      );
    }

    // Video preview
    if (file.mime_type.startsWith("video/")) {
      return (
        <video
          controls
          className="max-w-full h-auto mx-auto"
          src={`${process.env.NEXT_PUBLIC_API_URL}/files/${file.id}/download`}
        >
          Your browser does not support the video tag.
        </video>
      );
    }

    // Audio preview
    if (file.mime_type.startsWith("audio/")) {
      return (
        <div className="p-8">
          <audio
            controls
            className="w-full"
            src={`${process.env.NEXT_PUBLIC_API_URL}/files/${file.id}/download`}
          >
            Your browser does not support the audio tag.
          </audio>
        </div>
      );
    }

    // Text preview
    if (
      file.mime_type.startsWith("text/") ||
      file.mime_type === "application/json"
    ) {
      return (
        <div className="p-8">
          <p className="text-sm text-gray-600 mb-4">
            ไม่สามารถแสดงตัวอย่างได้ กรุณาดาวน์โหลดเพื่อดู
          </p>
        </div>
      );
    }

    // Default: No preview available
    return (
      <div className="p-12 text-center">
        <FileIcon className="w-24 h-24 mx-auto mb-4 text-gray-300" />
        <p className="text-gray-600 mb-2">ไม่สามารถแสดงตัวอย่างได้</p>
        <p className="text-sm text-gray-500">
          {file.mime_type}
        </p>
      </div>
    );
  };

  return (
    <div className="bg-gray-50 min-h-[400px] flex items-center justify-center">
      {file.processing_status === "completed" ? (
        renderPreview()
      ) : (
        <div className="text-center py-12">
          <div className="animate-spin w-12 h-12 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">
            {file.processing_status === "pending"
              ? "รอประมวลผล..."
              : "กำลังประมวลผล..."}
          </p>
        </div>
      )}
    </div>
  );
}
