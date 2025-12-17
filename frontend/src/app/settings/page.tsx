"use client";

import { useQuery } from "@tanstack/react-query";
import { StorageStats } from "@/components/settings/storage-stats";
import { FileTypeBreakdown } from "@/components/settings/file-type-breakdown";
import { AccountSettings } from "@/components/settings/account-settings";
import { apiClient } from "@/lib/api-client";

export default function SettingsPage() {
  const { data: stats } = useQuery({
    queryKey: ["stats"],
    queryFn: () => apiClient.getStats(),
  });

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <h1 className="text-2xl font-bold">การตั้งค่า</h1>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 py-6 space-y-6">
        {/* Storage Stats */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-semibold mb-4">พื้นที่เก็บข้อมูล</h2>
          <StorageStats stats={stats} />
        </div>

        {/* File Type Breakdown */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-semibold mb-4">ประเภทไฟล์</h2>
          <FileTypeBreakdown stats={stats} />
        </div>

        {/* Account Settings */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-semibold mb-4">บัญชี</h2>
          <AccountSettings />
        </div>
      </div>
    </div>
  );
}
