"use client";

import { use } from "react";
import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { ArrowLeft, Download, Share2, Trash2, Edit2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { FilePreview } from "@/components/files/file-preview";
import { FileMeta } from "@/components/files/file-meta";
import { TagManager } from "@/components/files/tag-manager";
import { apiClient } from "@/lib/api-client";

interface FileDetailPageProps {
  params: Promise<{ id: string }>;
}

export default function FileDetailPage({ params }: FileDetailPageProps) {
  const { id } = use(params);
  const router = useRouter();

  const { data: file, isLoading } = useQuery({
    queryKey: ["file", id],
    queryFn: () => apiClient.getFile(id),
  });

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse">กำลังโหลด...</div>
      </div>
    );
  }

  if (!file) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-2">ไม่พบไฟล์</h2>
          <Button onClick={() => router.push("/files")}>กลับไปหน้าไฟล์</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => router.back()}
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <h1 className="text-xl font-bold flex-1 truncate">
              {file.final_filename}
            </h1>
            <div className="flex gap-2">
              <Button variant="outline" size="icon">
                <Share2 className="w-4 h-4" />
              </Button>
              <Button variant="outline" size="icon">
                <Download className="w-4 h-4" />
              </Button>
              <Button variant="outline" size="icon">
                <Edit2 className="w-4 h-4" />
              </Button>
              <Button variant="outline" size="icon">
                <Trash2 className="w-4 h-4 text-red-600" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 py-6 space-y-6">
        {/* Preview */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <FilePreview file={file} />
        </div>

        {/* Summary */}
        {file.summary && (
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-lg font-semibold mb-3">สรุปเนื้อหา</h2>
            <p className="text-gray-700 leading-relaxed">{file.summary}</p>
          </div>
        )}

        {/* Tags */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-semibold mb-3">แท็ก</h2>
          <TagManager fileId={id} tags={file.ai_tags || []} />
        </div>

        {/* Metadata */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-semibold mb-3">ข้อมูลไฟล์</h2>
          <FileMeta file={file} />
        </div>
      </div>
    </div>
  );
}
