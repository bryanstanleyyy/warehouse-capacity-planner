import apiClient from './client';
import type {
  AllocationRequest,
  AllocationResult,
  AllocationComparison,
} from '../types/allocation';

const BASE_URL = '/allocation';

export const allocationApi = {
  // Run allocation analysis
  runAllocation: async (data: AllocationRequest): Promise<AllocationResult> => {
    const response = await apiClient.post<AllocationResult>(`${BASE_URL}/analyze`, data);
    return response.data;
  },

  // Get all allocation results
  getAllResults: async (params?: {
    upload_id?: number;
    warehouse_id?: number;
  }): Promise<AllocationResult[]> => {
    const response = await apiClient.get<AllocationResult[]>(`${BASE_URL}/results`, {
      params,
    });
    return response.data;
  },

  // Get specific allocation result
  getResult: async (resultId: number): Promise<AllocationResult> => {
    const response = await apiClient.get<AllocationResult>(`${BASE_URL}/results/${resultId}`);
    return response.data;
  },

  // Delete allocation result
  deleteResult: async (resultId: number): Promise<void> => {
    await apiClient.delete(`${BASE_URL}/results/${resultId}`);
  },

  // Compare multiple allocation results
  compareResults: async (resultIds: number[]): Promise<AllocationComparison> => {
    const response = await apiClient.get<AllocationComparison>(`${BASE_URL}/compare`, {
      params: { result_ids: resultIds.join(',') },
    });
    return response.data;
  },

  // Export allocation result as HTML
  exportHTML: async (resultId: number): Promise<Blob> => {
    const response = await apiClient.get(`${BASE_URL}/results/${resultId}/export/html`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Export allocation result as PDF
  exportPDF: async (resultId: number): Promise<Blob> => {
    const response = await apiClient.get(`${BASE_URL}/results/${resultId}/export/pdf`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Export allocation result as CSV
  exportCSV: async (resultId: number): Promise<Blob> => {
    const response = await apiClient.get(`${BASE_URL}/results/${resultId}/export/csv`, {
      responseType: 'blob',
    });
    return response.data;
  },
};
