export interface AllocationRequest {
  upload_id: number;
  warehouse_id: number;
  bsf_factor?: number;
  result_name?: string;
}

export interface ZoneAllocation {
  zone_info: {
    id: number;
    name: string;
    area: number;
    height: number;
    strength: number;
    climate_controlled: boolean;
    special_handling: boolean;
  };
  remaining_area: number;
  allocated_items: AllocatedItem[];
  area_utilization: number;
  height_constrained_items: number;
  strength_constrained_items: number;
  max_equipment_psf: number;
  total_items: number;
  total_weight: number;
}

export interface AllocatedItem {
  item_id: number;
  name: string;
  category?: string;
  quantity: number;
  weight: number;
  total_weight: number;
  area: number;
  total_area: number;
  height: number;
  psf: number;
  service_branch?: string;
  requires_climate_control: boolean;
  requires_special_handling: boolean;
}

export interface AllocationFailure {
  item_id: number;
  name: string;
  category?: string;
  quantity: number;
  height: number;
  area: number;
  required_area: number;
  psf: number;
  failure_reason: string;
  can_theoretically_fit: boolean;
}

export interface ZoneStat {
  zone_name: string;
  zone_id: number;
  total_items: number;
  area_utilization: number;
  total_weight: number;
  height_constrained_items: number;
  strength_constrained_items: number;
}

export interface AllocationSummary {
  total_items: number;
  total_allocated: number;
  total_failed: number;
  allocation_rate: number;
  overall_utilization: number;
  total_warehouse_area: number;
  total_used_area: number;
  bsf_factor: number;
  zone_stats: ZoneStat[];
}

export interface AllocationResult {
  id: number;
  upload_id: number;
  warehouse_id: number;
  result_name: string;
  bsf_factor: number;
  total_allocated: number;
  total_failed: number;
  overall_fit: boolean;
  created_at: string;
  allocation_data: {
    zone_allocations: ZoneAllocation[];
    failures: AllocationFailure[];
    overall_fit: boolean;
    summary: AllocationSummary;
  };
}

export interface AllocationComparison {
  results: {
    id: number;
    name: string;
    bsf_factor: number;
    total_allocated: number;
    total_failed: number;
    overall_fit: boolean;
    allocation_rate: number;
    overall_utilization: number;
    created_at: string;
  }[];
  best_fit: any;
  best_utilization: any;
}
