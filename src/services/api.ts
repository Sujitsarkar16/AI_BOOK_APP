/**
 * API client for backend communication
 */
import axios from 'axios';

// Use environment variable or fallback to localhost
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types matching backend schemas
export interface BookConfig {
  bookIdea: string;
  description?: string;
  targetAudience?: string;
  genre: string;
  chapters: number;
  wordsPerChapter: number;
  tone: string;
  includeImages: boolean;
  includeCitations: boolean;
}

export interface TOCItem {
  chapter: number;
  title: string;
  status: 'pending' | 'generating' | 'complete';
  outline?: string;
}

export interface ChapterResponse {
  id: number;
  book_id: number;
  chapter_number: number;
  title: string;
  outline: string;
  content_markdown: string;
  status: string;
  word_count: number;
  created_at: string;
  updated_at: string;
}

export interface BookResponse {
  id: number;
  title: string;
  book_idea: string;
  description: string;
  genre: string;
  target_audience: string;
  chapters_count: number;
  words_per_chapter: number;
  tone: string;
  include_images: boolean;
  include_citations: boolean;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ChatRequest {
  message: string;
}

export interface ChatResponse {
  response: string;
  agent_name?: string;
  actions_taken?: string[];
}

export interface GenerationStatus {
  book_id: number;
  book_status: string;
  chapters_total: number;
  chapters_complete: number;
  current_chapter: number | null;
  agents: AgentStatus[];
}

export interface AgentStatus {
  agent_name: string;
  status: 'idle' | 'active' | 'error';
  current_task?: string;
}

export interface BookIdea {
  id: string;
  title: string;
  description: string;
  genre: string;
  targetAudience: string;
  uniqueAngle: string;
  marketPotential: string;
}

export interface IdeaGenerationRequest {
  topics: string;
  keywords: string;
}

export interface IdeaGenerationResponse {
  success: boolean;
  ideas: BookIdea[];
  message?: string;
}

// API functions
export const apiService = {
  // Book operations
  async createBook(config: BookConfig): Promise<number> {
    const response = await api.post<BookResponse>('/api/books', config);
    return response.data.id;
  },

  async getBook(bookId: number): Promise<BookResponse> {
    const response = await api.get<BookResponse>(`/api/books/${bookId}`);
    return response.data;
  },

  async getBookStatus(bookId: number): Promise<GenerationStatus> {
    const response = await api.get<GenerationStatus>(`/api/books/${bookId}/status`);
    return response.data;
  },

  async deleteBook(bookId: number): Promise<void> {
    await api.delete(`/api/books/${bookId}`);
  },

  // Chapter operations
  async getChapters(bookId: number): Promise<TOCItem[]> {
    const response = await api.get<TOCItem[]>(`/api/books/${bookId}/chapters`);
    return response.data;
  },

  async getChapter(bookId: number, chapterId: number): Promise<ChapterResponse> {
    const response = await api.get<ChapterResponse>(`/api/books/${bookId}/chapters/${chapterId}`);
    return response.data;
  },

  async generateChapter(bookId: number, chapterId: number): Promise<void> {
    await api.post(`/api/books/${bookId}/chapters/${chapterId}/generate`);
  },

  async generateAllChapters(bookId: number): Promise<{ message: string; chapters: number }> {
    const response = await api.post<{ message: string; chapters: number }>(
      `/api/books/${bookId}/chapters/generate-all`
    );
    return response.data;
  },

  async updateChapter(bookId: number, chapterId: number, data: { title?: string; content_markdown?: string }): Promise<void> {
    await api.put(`/api/books/${bookId}/chapters/${chapterId}`, data);
  },

  // Chat operations
  async sendChatMessage(bookId: number, message: string): Promise<ChatResponse> {
    const response = await api.post<ChatResponse>(`/api/books/${bookId}/chat`, { message });
    return response.data;
  },

  // Export operations
  async exportMarkdown(bookId: number): Promise<Blob> {
    const response = await api.get(`/api/books/${bookId}/export/markdown`, {
      responseType: 'blob',
    });
    return response.data;
  },

  async exportHTML(bookId: number): Promise<Blob> {
    const response = await api.get(`/api/books/${bookId}/export/html`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Idea generation operations
  async generateIdeas(request: IdeaGenerationRequest): Promise<IdeaGenerationResponse> {
    const response = await api.post<IdeaGenerationResponse>('/api/generate-ideas', request);
    return response.data;
  },
};

