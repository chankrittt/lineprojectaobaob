"use client";

import { useQuery } from "@tanstack/react-query";
import { User, LogOut } from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { formatDate } from "@/lib/utils";

export function AccountSettings() {
  const { data: user, isLoading } = useQuery({
    queryKey: ["user"],
    queryFn: () => apiClient.getCurrentUser(),
  });

  const handleLogout = () => {
    // Clear LIFF token and reload
    if (typeof window !== "undefined" && window.liff) {
      window.liff.logout();
      window.location.href = "/";
    }
  };

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-gray-200 rounded-full" />
          <div className="flex-1">
            <div className="h-4 bg-gray-200 rounded w-1/3 mb-2" />
            <div className="h-3 bg-gray-200 rounded w-1/4" />
          </div>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="text-center py-8 text-gray-500">
        <User className="w-12 h-12 mx-auto mb-2 text-gray-400" />
        <p className="text-sm">กรุณาเข้าสู่ระบบ</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Profile section */}
      <div className="flex items-center gap-4">
        <div className="w-16 h-16 bg-gradient-to-br from-primary to-primary/70 rounded-full flex items-center justify-center">
          {user.profile_picture ? (
            <img
              src={user.profile_picture}
              alt={user.display_name}
              className="w-full h-full rounded-full object-cover"
            />
          ) : (
            <User className="w-8 h-8 text-white" />
          )}
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-lg">{user.display_name}</h3>
          <p className="text-sm text-gray-600">LINE User ID: {user.line_user_id}</p>
        </div>
      </div>

      {/* Account info */}
      <div className="space-y-3 pt-4 border-t">
        <div className="flex items-center justify-between py-2">
          <span className="text-sm text-gray-600">สมัครเมื่อ</span>
          <span className="text-sm font-medium">
            {formatDate(user.created_at)}
          </span>
        </div>
        <div className="flex items-center justify-between py-2">
          <span className="text-sm text-gray-600">อัปเดตล่าสุด</span>
          <span className="text-sm font-medium">
            {formatDate(user.last_login || user.created_at)}
          </span>
        </div>
      </div>

      {/* Actions */}
      <div className="pt-4 border-t">
        <Button
          onClick={handleLogout}
          variant="outline"
          className="w-full justify-center gap-2"
        >
          <LogOut className="w-4 h-4" />
          ออกจากระบบ
        </Button>
      </div>
    </div>
  );
}
