"use client";

import { useState, useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { X } from "lucide-react";
import { apiClient } from "@/lib/api-client";
import type { Collection } from "@/lib/types";
import { Button } from "@/components/ui/button";

interface CreateCollectionDialogProps {
  open: boolean;
  onClose: () => void;
  collection?: Collection | null;
}

export function CreateCollectionDialog({
  open,
  onClose,
  collection,
}: CreateCollectionDialogProps) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const queryClient = useQueryClient();

  const isEditMode = !!collection;

  // Reset form when dialog opens/closes
  useEffect(() => {
    if (open) {
      setName(collection?.name || "");
      setDescription(collection?.description || "");
    } else {
      setName("");
      setDescription("");
    }
  }, [open, collection]);

  const createMutation = useMutation({
    mutationFn: (data: { name: string; description?: string }) =>
      apiClient.createCollection(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["collections"] });
      onClose();
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: { name: string; description?: string }) =>
      apiClient.updateCollection(collection!.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["collections"] });
      onClose();
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    const data = {
      name: name.trim(),
      description: description.trim() || undefined,
    };

    if (isEditMode) {
      updateMutation.mutate(data);
    } else {
      createMutation.mutate(data);
    }
  };

  const isPending = createMutation.isPending || updateMutation.isPending;

  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-bold">
            {isEditMode ? "แก้ไขคอลเล็กชัน" : "สร้างคอลเล็กชันใหม่"}
          </h2>
          <button
            onClick={onClose}
            disabled={isPending}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Name input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              ชื่อคอลเล็กชัน <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="เช่น เอกสารงาน, รูปภาพครอบครัว"
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              autoFocus
              disabled={isPending}
              required
            />
          </div>

          {/* Description input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              คำอธิบาย (ไม่บังคับ)
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="อธิบายเกี่ยวกับคอลเล็กชันนี้..."
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary resize-none"
              rows={3}
              disabled={isPending}
            />
          </div>

          {/* Error message */}
          {(createMutation.error || updateMutation.error) && (
            <div className="text-sm text-red-600">
              เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้ง
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              onClick={onClose}
              variant="outline"
              className="flex-1"
              disabled={isPending}
            >
              ยกเลิก
            </Button>
            <Button
              type="submit"
              className="flex-1"
              disabled={isPending || !name.trim()}
            >
              {isPending
                ? "กำลังบันทึก..."
                : isEditMode
                  ? "บันทึก"
                  : "สร้าง"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
