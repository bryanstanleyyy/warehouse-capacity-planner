export interface InventoryItem {
  id: number;
  upload_id: number;
  name: string;
  description?: string;
  quantity: number;
  category?: string;
  weight?: number;
  length?: number;
  width?: number;
  height?: number;
  area?: number;
  psf?: number;
  service_branch?: string;
  priority_order?: number;
  requires_climate_control: boolean;
  requires_special_handling: boolean;
  created_at: string;
}

export interface InventoryUpload {
  id: number;
  upload_name: string;
  filename: string;
  site?: string;
  site2?: string;
  total_items: number;
  total_entries: number;
  total_weight: number;
  total_area: number;
  bsf_factor: number;
  upload_date: string;
  metadata?: Record<string, any>;
}

export interface InventoryUploadInput {
  file: File;
  upload_name?: string;
  site?: string;
  site2?: string;
  bsf_factor?: number;
}

export interface InventorySummary {
  total_items: number;
  total_entries: number;
  total_weight: number;
  total_area: number;
  categories: {
    category: string;
    count: number;
    total_weight: number;
    total_area: number;
  }[];
  climate_controlled_items: number;
  special_handling_items: number;
  average_psf: number;
  max_height: number;
}

export interface BSFUpdateInput {
  bsf_factor: number;
}
