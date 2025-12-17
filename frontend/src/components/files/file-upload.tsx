"use client";

import { useState, useRef } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Upload, X, CheckCircle, AlertCircle, Loader2 } from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { formatFileSize } from "@/lib/utils";
import { Button } from "@/components/ui/button";

interface UploadFile {
  file: File;
  status: "pending" | "uploading" | "success" | "error";
  progress: number;
  error?: string;
}

export function FileUpload() {
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();

  const uploadMutation = useMutation({
    mutationFn: (file: File) => apiClient.uploadFile(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["files"] });
    },
  });

  const handleFileSelect = (selectedFiles: FileList | null) => {
    if (!selectedFiles) return;

    const newFiles: UploadFile[] = Array.from(selectedFiles).map((file) => ({
      file,
      status: "pending",
      progress: 0,
    }));

    setFiles((prev) => [...prev, ...newFiles]);

    // Upload files
    newFiles.forEach((uploadFile, index) => {
      uploadFile.status = "uploading";
      setFiles((prev) => [...prev]);

      uploadMutation.mutate(uploadFile.file, {
        onSuccess: () => {
          setFiles((prev) =>
            prev.map((f) =>
              f.file === uploadFile.file
                ? { ...f, status: "success", progress: 100 }
                : f
            )
          );
        },
        onError: (error: any) => {
          setFiles((prev) =>
            prev.map((f) =>
              f.file === uploadFile.file
                ? { ...f, status: "error", error: error.message }
                : f
            )
          );
        },
      });
    });
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFileSelect(e.dataTransfer.files);
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-4">
      {/* Drop zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          transition-colors
          ${
            isDragging
              ? "border-primary bg-primary/5"
              : "border-gray-300 hover:border-primary"
          }
        `}
      >
        <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
        <p className="text-sm text-gray-600 mb-1">
          คลิกเพื่อเลือกไฟล์ หรือลากไฟล์มาวางที่นี่
        </p>
        <p className="text-xs text-gray-500">
          รองรับ PDF, รูปภาพ, วิดีโอ และเอกสารอื่นๆ
        </p>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          onChange={(e) => handleFileSelect(e.target.files)}
          className="hidden"
        />
      </div>

      {/* File list */}
      {files.length > 0 && (
        <div className="space-y-2">
          <h3 className="font-medium text-sm">ไฟล์ที่กำลังอัปโหลด</h3>
          <div className="space-y-2">
            {files.map((uploadFile, index) => (
              <div
                key={index}
                className="flex items-center gap-3 p-3 bg-white border rounded-lg"
              >
                {/* Status icon */}
                <div className="flex-shrink-0">
                  {uploadFile.status === "uploading" && (
                    <Loader2 className="w-5 h-5 animate-spin text-primary" />
                  )}
                  {uploadFile.status === "success" && (
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  )}
                  {uploadFile.status === "error" && (
                    <AlertCircle className="w-5 h-5 text-red-600" />
                  )}
                  {uploadFile.status === "pending" && (
                    <div className="w-5 h-5 rounded-full border-2 border-gray-300" />
                  )}
                </div>

                {/* File info */}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">
                    {uploadFile.file.name}
                  </p>
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <span>{formatFileSize(uploadFile.file.size)}</span>
                    {uploadFile.status === "error" && (
                      <span className="text-red-600">{uploadFile.error}</span>
                    )}
                    {uploadFile.status === "success" && (
                      <span className="text-green-600">อัปโหลดสำเร็จ</span>
                    )}
                    {uploadFile.status === "uploading" && (
                      <span>กำลังอัปโหลด...</span>
                    )}
                  </div>

                  {/* Progress bar */}
                  {uploadFile.status === "uploading" && (
                    <div className="mt-2 h-1 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary transition-all duration-300"
                        style={{ width: `${uploadFile.progress}%` }}
                      />
                    </div>
                  )}
                </div>

                {/* Remove button */}
                {uploadFile.status !== "uploading" && (
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => removeFile(index)}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
