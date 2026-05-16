export interface Emergency {
  id: number;
  reporter_name: string;
  reporter_phone: string;
  emergency_type: string;
  severity: string;
  lat: number;
  lng: number;
  notes?: string;
  status: string;
  ambulance_id?: number;
  hospital_id?: number;
  eta_minutes?: number;
  route_polyline?: string;
  priority_score: number;
  auto_assigned: boolean;
  created_at: string;
}

export interface Ambulance {
  id: number;
  plate_number: string;
  lat: number;
  lng: number;
  status: string;
  city: string;
  driver_id?: number;
}

export interface Hospital {
  id: number;
  name: string;
  name_ar?: string;
  city: string;
  lat: number;
  lng: number;
  capacity: number;
  current_load: number;
  emergency_available: boolean;
  hospital_type: string;
  load_percent?: number;
}

export interface TrafficZone {
  id: number;
  name: string;
  city: string;
  center_lat: number;
  center_lng: number;
  radius_km: number;
  level: string;
}
