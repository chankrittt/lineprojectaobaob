import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { formatDistanceToNow, format } from "date-fns";
import { th } from "date-fns/locale";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 B";

  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

export function formatDate(date: string | Date): string {
  return format(new Date(date), "d MMM yyyy", { locale: th });
}

export function formatRelativeTime(date: string | Date): string {
  return formatDistanceToNow(new Date(date), { addSuffix: true, locale: th });
}

export function getFileIcon(mimeType: string): string {
  if (mimeType.startsWith("image/")) return "🖼️";
  if (mimeType.startsWith("video/")) return "🎬";
  if (mimeType === "application/pdf") return "📄";
  if (mimeType.includes("word")) return "📝";
  if (mimeType.includes("excel") || mimeType.includes("spreadsheet"))
    return "📊";
  if (mimeType.includes("powerpoint") || mimeType.includes("presentation"))
    return "📊";
  return "📁";
}

export function getFileTypeColor(mimeType: string): string {
  if (mimeType.startsWith("image/")) return "bg-blue-100 text-blue-800";
  if (mimeType.startsWith("video/")) return "bg-purple-100 text-purple-800";
  if (mimeType === "application/pdf") return "bg-red-100 text-red-800";
  if (mimeType.includes("word")) return "bg-blue-100 text-blue-800";
  if (mimeType.includes("excel") || mimeType.includes("spreadsheet"))
    return "bg-green-100 text-green-800";
  return "bg-gray-100 text-gray-800";
}

export function truncate(str: string, length: number): string {
  if (str.length <= length) return str;
  return str.slice(0, length) + "...";
}
