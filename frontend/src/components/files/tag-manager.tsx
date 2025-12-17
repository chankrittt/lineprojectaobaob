"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { X, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { apiClient } from "@/lib/api-client";

interface TagManagerProps {
  fileId: string;
  tags: string[];
}

export function TagManager({ fileId, tags: initialTags }: TagManagerProps) {
  const [tags, setTags] = useState<string[]>(initialTags);
  const [newTag, setNewTag] = useState("");
  const [isAdding, setIsAdding] = useState(false);
  const queryClient = useQueryClient();

  const updateTagsMutation = useMutation({
    mutationFn: (newTags: string[]) =>
      apiClient.updateFile(fileId, { ai_tags: newTags }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["file", fileId] });
    },
  });

  const handleAddTag = () => {
    if (!newTag.trim()) return;

    const tag = newTag.trim().toLowerCase();
    if (tags.includes(tag)) {
      setNewTag("");
      return;
    }

    const updatedTags = [...tags, tag];
    setTags(updatedTags);
    updateTagsMutation.mutate(updatedTags);
    setNewTag("");
    setIsAdding(false);
  };

  const handleRemoveTag = (tagToRemove: string) => {
    const updatedTags = tags.filter((tag) => tag !== tagToRemove);
    setTags(updatedTags);
    updateTagsMutation.mutate(updatedTags);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleAddTag();
    } else if (e.key === "Escape") {
      setIsAdding(false);
      setNewTag("");
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2">
        {tags.map((tag) => (
          <span
            key={tag}
            className="inline-flex items-center gap-1 px-3 py-1.5 bg-blue-50 text-blue-700 rounded-full text-sm group hover:bg-blue-100 transition-colors"
          >
            #{tag}
            <button
              onClick={() => handleRemoveTag(tag)}
              className="ml-1 opacity-0 group-hover:opacity-100 transition-opacity"
            >
              <X className="w-3 h-3" />
            </button>
          </span>
        ))}

        {/* Add tag input */}
        {isAdding ? (
          <div className="inline-flex items-center gap-2">
            <input
              type="text"
              value={newTag}
              onChange={(e) => setNewTag(e.target.value)}
              onKeyDown={handleKeyPress}
              onBlur={() => {
                if (!newTag.trim()) setIsAdding(false);
              }}
              placeholder="ชื่อแท็ก..."
              className="px-3 py-1.5 border rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-primary w-32"
              autoFocus
            />
            <Button
              size="sm"
              onClick={handleAddTag}
              disabled={!newTag.trim()}
            >
              เพิ่ม
            </Button>
          </div>
        ) : (
          <button
            onClick={() => setIsAdding(true)}
            className="inline-flex items-center gap-1 px-3 py-1.5 border-2 border-dashed border-gray-300 text-gray-600 rounded-full text-sm hover:border-primary hover:text-primary transition-colors"
          >
            <Plus className="w-3 h-3" />
            เพิ่มแท็ก
          </button>
        )}
      </div>

      {tags.length === 0 && !isAdding && (
        <p className="text-sm text-gray-500">ยังไม่มีแท็ก คลิกเพื่อเพิ่ม</p>
      )}
    </div>
  );
}
