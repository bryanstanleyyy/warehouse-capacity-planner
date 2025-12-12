export interface Zone {
  id?: number;
  warehouse_id?: number;
  name: string;
  zone_order?: number;
  area: number;
  height: number;
  strength?: number;
  volume?: number;
  climate_controlled?: boolean;
  temperature_min?: number;
  temperature_max?: number;
  special_handling?: boolean;
  container_capacity?: number;
  is_weather_zone?: boolean;
  created_at?: string;
}

export interface Warehouse {
  id?: number;
  name: string;
  warehouse_type?: string;
  description?: string;
  total_area?: number;
  total_volume?: number;
  is_custom?: boolean;
  zone_count?: number;
  zones?: Zone[];
  created_at?: string;
  updated_at?: string;
}

export interface WarehouseInput {
  name: string;
  warehouse_type?: string;
  description?: string;
  is_custom?: boolean;
}

export interface ZoneInput {
  name: string;
  zone_order?: number;
  area: number;
  height: number;
  strength?: number;
  climate_controlled?: boolean;
  temperature_min?: number;
  temperature_max?: number;
  special_handling?: boolean;
  container_capacity?: number;
  is_weather_zone?: boolean;
}
