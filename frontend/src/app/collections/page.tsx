"use client";

import { useState } from "react";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { CollectionList } from "@/components/collections/collection-list";
import { CreateCollectionDialog } from "@/components/collections/create-collection-dialog";
import type { Collection } from "@/lib/types";

export default function CollectionsPage() {
  const [showDialog, setShowDialog] = useState(false);
  const [editingCollection, setEditingCollection] = useState<Collection | null>(null);

  const handleCreate = () => {
    setEditingCollection(null);
    setShowDialog(true);
  };

  const handleEdit = (collection: Collection) => {
    setEditingCollection(collection);
    setShowDialog(true);
  };

  const handleCloseDialog = () => {
    setShowDialog(false);
    setEditingCollection(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold">คอลเล็กชัน</h1>
            <Button onClick={handleCreate}>
              <Plus className="w-4 h-4 mr-2" />
              สร้างคอลเล็กชัน
            </Button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <CollectionList onCreateClick={handleCreate} onEditClick={handleEdit} />
      </div>

      {/* Create/Edit Dialog */}
      <CreateCollectionDialog
        open={showDialog}
        onClose={handleCloseDialog}
        collection={editingCollection}
      />
    </div>
  );
}
