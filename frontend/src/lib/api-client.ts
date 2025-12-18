import axios, { AxiosInstance } from "axios";

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Add auth interceptor
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem("access_token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  }

  // Auth
  async login(lineToken: string) {
    const { data } = await this.client.post("/auth/line", { token: lineToken });
    return data;
  }

  // Files
  async getFiles(params?: {
    skip?: number;
    limit?: number;
    search?: string;
  }) {
    const { data } = await this.client.get("/files", { params });
    return data;
  }

  async getFile(id: string) {
    const { data } = await this.client.get(`/files/${id}`);
    return data;
  }

  async uploadFile(file: File) {
    const formData = new FormData();
    formData.append("file", file);
    const { data } = await this.client.post("/files/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return data;
  }

  async deleteFile(id: string) {
    await this.client.delete(`/files/${id}`);
  }

  async updateFile(id: string, updates: any) {
    const { data } = await this.client.patch(`/files/${id}`, updates);
    return data;
  }

  // Search
  async searchFiles(query: string, params?: any) {
    const { data } = await this.client.post("/search", { query, ...params });
    return data;
  }

  async semanticSearch(query: string, limit = 10) {
    const { data } = await this.client.post("/search/semantic", {
      query,
      limit,
    });
    return data;
  }

  // Collections
  async getCollections() {
    const { data } = await this.client.get("/collections");
    return data;
  }

  async getCollection(id: string) {
    const { data } = await this.client.get(`/collections/${id}`);
    return data;
  }

  async createCollection(collection: { name: string; description?: string }) {
    const { data } = await this.client.post("/collections", collection);
    return data;
  }

  async addFileToCollection(collectionId: string, fileId: string) {
    await this.client.post(`/collections/${collectionId}/files/${fileId}`);
  }

  async removeFileFromCollection(collectionId: string, fileId: string) {
    await this.client.delete(`/collections/${collectionId}/files/${fileId}`);
  }

  // Stats
  async getStats() {
    const { data } = await this.client.get("/files/stats");
    return data;
  }
}

export const apiClient = new APIClient();
