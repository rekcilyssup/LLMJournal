export interface JournalEntry {
  id: string;
  userId: string;
  ambience: string;
  text: string;
  date: string;
  emotion?: string;
  keywords?: string[];
  summary?: string;
}

export interface AnalysisResult {
  emotion: string;
  keywords: string[];
  summary: string;
}

export interface Insights {
  totalEntries: number;
  topEmotion: string;
  mostUsedAmbience: string;
  recentKeywords: string[];
}

export interface TimelineMentalStateInsights {
  entryCount: number;
  fromDate: string;
  toDate: string;
  emotion: string;
  keywords: string[];
  summary: string;
}

const runtimeApiBaseUrl =
  typeof window !== 'undefined'
    ? `${window.location.protocol}//${window.location.hostname}:8000`
    : 'http://localhost:8000';

const configuredApiUrl = (import.meta as { env?: { VITE_API_URL?: string } }).env?.VITE_API_URL;

const API_BASE_URL = configuredApiUrl || runtimeApiBaseUrl;

export const api = {
  saveEntry: async (entry: { userId: string; ambience: string; text: string }): Promise<JournalEntry> => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/journal`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(entry),
      });
      if (!res.ok) throw new Error('Failed to save entry');
      return await res.json();
    } catch (error) {
      console.error('Error saving entry:', error);
      throw error;
    }
  },
  
  getHistory: async (userId: string): Promise<JournalEntry[]> => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/journal/${userId}`);
      if (!res.ok) throw new Error('Failed to fetch history');
      return await res.json();
    } catch (error) {
      console.error('Error fetching history:', error);
      throw error;
    }
  },
  
  analyzeText: async (text: string): Promise<AnalysisResult> => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/journal/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });
      if (!res.ok) throw new Error('Failed to analyze text');
      return await res.json();
    } catch (error) {
      console.error('Error analyzing text:', error);
      throw error;
    }
  },
  
  getInsights: async (userId: string): Promise<Insights> => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/journal/insights/${userId}`);
      if (!res.ok) throw new Error('Failed to fetch insights');
      return await res.json();
    } catch (error) {
      console.error('Error fetching insights:', error);
      throw error;
    }
  },

  analyzeTimeline: async (userId: string): Promise<TimelineMentalStateInsights> => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/journal/insights/${userId}/analyze-timeline`, {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to analyze timeline');
      return await res.json();
    } catch (error) {
      console.error('Error analyzing timeline:', error);
      throw error;
    }
  }
};
