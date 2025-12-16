import apiClient from './client';
import type {
  InventoryUpload,
  InventoryItem,
  InventoryUploadInput,
  InventorySummary,
  BSFUpdateInput,
} from '../types/inventory';

const BASE_URL = '/inventory';

export const inventoryApi = {
  // Upload inventory from Excel file
  uploadInventory: async (data: InventoryUploadInput): Promise<InventoryUpload> => {
    const formData = new FormData();
    formData.append('file', data.file);

    if (data.upload_name) {
      formData.append('upload_name', data.upload_name);
    }
    if (data.site) {
      formData.append('site', data.site);
    }
    if (data.site2) {
      formData.append('site2', data.site2);
    }
    if (data.bsf_factor !== undefined) {
      formData.append('bsf_factor', data.bsf_factor.toString());
    }

    const response = await apiClient.post<InventoryUpload>(`${BASE_URL}/uploads`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Get all uploads
  getUploads: async (): Promise<InventoryUpload[]> => {
    const response = await apiClient.get<InventoryUpload[]>(`${BASE_URL}/uploads`);
    return response.data;
  },

  // Get specific upload
  getUpload: async (uploadId: number): Promise<InventoryUpload> => {
    const response = await apiClient.get<InventoryUpload>(`${BASE_URL}/uploads/${uploadId}`);
    return response.data;
  },

  // Delete upload
  deleteUpload: async (uploadId: number): Promise<void> => {
    await apiClient.delete(`${BASE_URL}/uploads/${uploadId}`);
  },

  // Get items for an upload
  getUploadItems: async (
    uploadId: number,
    params?: { category?: string; limit?: number; offset?: number }
  ): Promise<InventoryItem[]> => {
    const response = await apiClient.get<InventoryItem[]>(
      `${BASE_URL}/uploads/${uploadId}/items`,
      { params }
    );
    return response.data;
  },

  // Get upload summary statistics
  getUploadSummary: async (uploadId: number): Promise<InventorySummary> => {
    const response = await apiClient.get<InventorySummary>(
      `${BASE_URL}/uploads/${uploadId}/summary`
    );
    return response.data;
  },

  // Update BSF factor
  updateBSF: async (uploadId: number, data: BSFUpdateInput): Promise<InventoryUpload> => {
    const response = await apiClient.patch<InventoryUpload>(
      `${BASE_URL}/uploads/${uploadId}/bsf`,
      data
    );
    return response.data;
  },

  // Export inventory upload as XLSX
  exportXLSX: async (uploadId: number): Promise<Blob> => {
    const response = await apiClient.get(`${BASE_URL}/uploads/${uploadId}/export/xlsx`, {
      responseType: 'blob',
    });
    return response.data;
  },
};
