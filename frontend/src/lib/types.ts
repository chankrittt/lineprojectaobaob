export interface File {
  id: string;
  user_id: string;
  original_filename: string;
  ai_generated_filename: string | null;
  final_filename: string;
  file_path: string;
  file_size: number;
  mime_type: string;
  file_hash: string;
  thumbnail_path: string | null;
  summary: string | null;
  ai_tags: string[];
  file_metadata: Record<string, any> | null;
  processing_status: "pending" | "processing" | "completed" | "failed";
  uploaded_at: string;
  processed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface Collection {
  id: string;
  user_id: string;
  name: string;
  description: string | null;
  is_public: boolean;
  created_at: string;
  updated_at: string;
  file_count?: number;
}

export interface SearchResult {
  file: File;
  score: number;
  highlights?: string[];
}

export interface Stats {
  total_files: number;
  total_size: number;
  by_type: Record<string, number>;
  recent_uploads: number;
}

export interface User {
  id: string;
  line_user_id: string;
  display_name: string;
  picture_url: string | null;
}
