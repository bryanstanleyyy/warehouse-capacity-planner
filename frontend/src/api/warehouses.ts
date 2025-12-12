import apiClient from './client';
import type { Warehouse, WarehouseInput, Zone, ZoneInput } from '../types/warehouse';

// Warehouse API functions
export const warehouseApi = {
  // Get all warehouses
  getAll: async (): Promise<Warehouse[]> => {
    const response = await apiClient.get('/warehouses');
    return response.data;
  },

  // Get warehouse by ID
  getById: async (id: number): Promise<Warehouse> => {
    const response = await apiClient.get(`/warehouses/${id}`);
    return response.data;
  },

  // Create new warehouse
  create: async (data: WarehouseInput): Promise<Warehouse> => {
    const response = await apiClient.post('/warehouses', data);
    return response.data;
  },

  // Update warehouse
  update: async (id: number, data: WarehouseInput): Promise<Warehouse> => {
    const response = await apiClient.put(`/warehouses/${id}`, data);
    return response.data;
  },

  // Delete warehouse
  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/warehouses/${id}`);
  },

  // Get zones for a warehouse
  getZones: async (warehouseId: number): Promise<Zone[]> => {
    const response = await apiClient.get(`/warehouses/${warehouseId}/zones`);
    return response.data;
  },

  // Create zone
  createZone: async (warehouseId: number, data: ZoneInput): Promise<Zone> => {
    const response = await apiClient.post(`/warehouses/${warehouseId}/zones`, data);
    return response.data;
  },

  // Update zone
  updateZone: async (warehouseId: number, zoneId: number, data: ZoneInput): Promise<Zone> => {
    const response = await apiClient.put(`/warehouses/${warehouseId}/zones/${zoneId}`, data);
    return response.data;
  },

  // Delete zone
  deleteZone: async (warehouseId: number, zoneId: number): Promise<void> => {
    await apiClient.delete(`/warehouses/${warehouseId}/zones/${zoneId}`);
  },
};
