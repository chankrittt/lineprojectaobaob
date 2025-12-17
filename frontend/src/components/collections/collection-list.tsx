"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { Folder, Loader2, Plus } from "lucide-react";
import { apiClient } from "@/lib/api-client";
import type { Collection } from "@/lib/types";
import { CollectionCard } from "./collection-card";
import { Button } from "@/components/ui/button";

interface CollectionListProps {
  onCreateClick: () => void;
  onEditClick: (collection: Collection) => void;
}

export function CollectionList({ onCreateClick, onEditClick }: CollectionListProps) {
  const router = useRouter();

  const { data: collections, isLoading, error } = useQuery({
    queryKey: ["collections"],
    queryFn: () => apiClient.getCollections(),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12 text-red-600">
        เกิดข้อผิดพลาดในการโหลดคอลเล็กชัน
      </div>
    );
  }

  if (!collections || collections.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <Folder className="w-16 h-16 mx-auto mb-4 text-gray-400" />
        <p className="mb-4">ยังไม่มีคอลเล็กชัน</p>
        <Button onClick={onCreateClick}>
          <Plus className="w-4 h-4 mr-2" />
          สร้างคอลเล็กชันแรก
        </Button>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {collections.map((collection: Collection) => (
        <CollectionCard
          key={collection.id}
          collection={collection}
          onClick={() => router.push(`/collections/${collection.id}`)}
          onEdit={onEditClick}
        />
      ))}
    </div>
  );
}
