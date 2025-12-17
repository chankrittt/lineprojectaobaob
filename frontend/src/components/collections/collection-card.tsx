"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Folder, MoreVertical, Edit2, Trash2, FileIcon } from "lucide-react";
import type { Collection } from "@/lib/types";
import { apiClient } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { formatRelativeTime } from "@/lib/utils";

interface CollectionCardProps {
  collection: Collection;
  onClick?: () => void;
  onEdit?: (collection: Collection) => void;
}

export function CollectionCard({ collection, onClick, onEdit }: CollectionCardProps) {
  const [showMenu, setShowMenu] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const queryClient = useQueryClient();

  const deleteMutation = useMutation({
    mutationFn: () => apiClient.deleteCollection(collection.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["collections"] });
      setShowDeleteConfirm(false);
    },
  });

  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    setShowMenu(false);
    onEdit?.(collection);
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    setShowDeleteConfirm(true);
    setShowMenu(false);
  };

  const confirmDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    deleteMutation.mutate();
  };

  const cancelDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    setShowDeleteConfirm(false);
  };

  return (
    <div
      onClick={onClick}
      className="bg-white rounded-lg border hover:border-primary hover:shadow-md transition-all cursor-pointer overflow-hidden relative"
    >
      {/* Delete confirmation overlay */}
      {showDeleteConfirm && (
        <div className="absolute inset-0 bg-white z-10 flex flex-col items-center justify-center p-4">
          <p className="text-sm text-gray-700 mb-4 text-center">
            ลบคอลเล็กชัน &quot;{collection.name}&quot;?
          </p>
          <div className="flex gap-2">
            <Button
              onClick={confirmDelete}
              variant="destructive"
              size="sm"
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? "กำลังลบ..." : "ลบ"}
            </Button>
            <Button
              onClick={cancelDelete}
              variant="outline"
              size="sm"
              disabled={deleteMutation.isPending}
            >
              ยกเลิก
            </Button>
          </div>
        </div>
      )}

      {/* Header with icon */}
      <div className="bg-gradient-to-br from-primary/10 to-primary/5 p-6 flex items-center justify-between">
        <Folder className="w-12 h-12 text-primary" />

        {/* Menu button */}
        <div className="relative">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setShowMenu(!showMenu);
            }}
            className="p-2 hover:bg-white/50 rounded-lg transition-colors"
          >
            <MoreVertical className="w-5 h-5 text-gray-600" />
          </button>

          {/* Dropdown menu */}
          {showMenu && (
            <div className="absolute right-0 top-full mt-1 bg-white border rounded-lg shadow-lg py-1 min-w-[120px] z-20">
              <button
                onClick={handleEdit}
                className="w-full px-3 py-2 text-left text-sm hover:bg-gray-50 flex items-center gap-2"
              >
                <Edit2 className="w-4 h-4" />
                แก้ไข
              </button>
              <button
                onClick={handleDelete}
                className="w-full px-3 py-2 text-left text-sm hover:bg-gray-50 flex items-center gap-2 text-red-600"
              >
                <Trash2 className="w-4 h-4" />
                ลบ
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        <h3 className="font-semibold text-lg mb-1 truncate">{collection.name}</h3>
        {collection.description && (
          <p className="text-sm text-gray-600 mb-3 line-clamp-2">
            {collection.description}
          </p>
        )}

        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center gap-1">
            <FileIcon className="w-3 h-3" />
            <span>{collection.file_count || 0} ไฟล์</span>
          </div>
          <span>{formatRelativeTime(collection.created_at)}</span>
        </div>
      </div>

      {/* Click outside to close menu */}
      {showMenu && (
        <div
          className="fixed inset-0 z-10"
          onClick={(e) => {
            e.stopPropagation();
            setShowMenu(false);
          }}
        />
      )}
    </div>
  );
}
