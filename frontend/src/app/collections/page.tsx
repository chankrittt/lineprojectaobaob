"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { CollectionCard } from "@/components/collections/collection-card";
import { CreateCollectionDialog } from "@/components/collections/create-collection-dialog";
import { apiClient } from "@/lib/api-client";

export default function CollectionsPage() {
  const [showCreateDialog, setShowCreateDialog] = useState(false);

  const { data: collections, isLoading } = useQuery({
    queryKey: ["collections"],
    queryFn: () => apiClient.getCollections(),
  });

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold">คอลเลกชัน</h1>
            <Button onClick={() => setShowCreateDialog(true)}>
              <Plus className="w-4 h-4 mr-2" />
              สร้างคอลเลกชัน
            </Button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        {isLoading ? (
          <div className="text-center py-12">กำลังโหลด...</div>
        ) : collections && collections.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {collections.map((collection) => (
              <CollectionCard key={collection.id} collection={collection} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">
            <p className="mb-4">ยังไม่มีคอลเลกชัน</p>
            <Button onClick={() => setShowCreateDialog(true)}>
              สร้างคอลเลกชันแรก
            </Button>
          </div>
        )}
      </div>

      <CreateCollectionDialog
        open={showCreateDialog}
        onClose={() => setShowCreateDialog(false)}
      />
    </div>
  );
}
