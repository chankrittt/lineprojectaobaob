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

  const { data: file, isLoading, error } = useQuery({
    queryKey: ["file", id],
    queryFn: () => apiClient.getFile(id),
    retry: 1,
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="bg-white border-b">
          <div className="max-w-4xl mx-auto px-4 py-4">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 bg-gray-200 rounded animate-pulse" />
              <div className="flex-1 h-6 bg-gray-200 rounded animate-pulse" />
            </div>
          </div>
        </div>
        <div className="max-w-4xl mx-auto px-4 py-6 space-y-6">
          <div className="bg-white rounded-lg shadow-sm h-96 animate-pulse" />
          <div className="bg-white rounded-lg shadow-sm p-6 space-y-3">
            <div className="h-4 bg-gray-200 rounded w-1/4 animate-pulse" />
            <div className="h-4 bg-gray-200 rounded animate-pulse" />
            <div className="h-4 bg-gray-200 rounded w-3/4 animate-pulse" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !file) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center max-w-md">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold mb-2">ไม่พบไฟล์</h2>
          <p className="text-gray-600 mb-6">
            {error ? "เกิดข้อผิดพลาดในการโหลดไฟล์" : "ไม่พบไฟล์ที่คุณต้องการ"}
          </p>
          <div className="flex gap-3 justify-center">
            <Button onClick={() => router.back()} variant="outline">
              ย้อนกลับ
            </Button>
            <Button onClick={() => router.push("/files")}>
              ไปหน้าไฟล์
            </Button>
          </div>
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
