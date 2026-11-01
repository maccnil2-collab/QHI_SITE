export type Car = { id: number; slug: string; brand: string; model: string; trim: string | null; year: number; price_cny: string; price_usd?: string | null; price_tjs?: string | null; price_note?: string | null; price_source?: string | null; range_km: number | null; fuel_consumption_l_100km: string | null; battery_kwh: string | null; power_kw: number | null; drivetrain: string | null; category: string | null; engine_type: string | null; fuel_type?: string | null; engine_cc: number | null; torque_nm?: number | null; acceleration_0_100_s?: string | null; max_speed_kmh?: number | null; seats?: number | null; doors?: number | null; length_mm?: number | null; width_mm?: number | null; height_mm?: number | null; wheelbase_mm?: number | null; advantages?: string | null; specification_source?: string | null; transmission: string | null; mileage_km: number | null; exterior_color: string | null; equipment: string | null; specifications: string | null; is_demo: boolean; availability: string; localized_title: string | null; localized_description: string | null; images: string[]; image_details?: {url:string;alt:string|null;attribution:string|null;license_name:string|null;source_url:string|null}[] };
const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";
export async function fetchCars(filters: URLSearchParams, signal?: AbortSignal): Promise<Car[]> {
  const response = await fetch(`${apiBase}/cars?${filters.toString()}`, { signal, cache: "no-store" });
  if (!response.ok) throw new Error(`Catalog request failed: ${response.status}`);
  return response.json() as Promise<Car[]>;
}

export async function fetchCar(slug: string, locale: string, signal?: AbortSignal): Promise<Car> {
  const query = new URLSearchParams({ locale });
  const response = await fetch(`${apiBase}/cars/${encodeURIComponent(slug)}?${query}`, { signal, cache: "no-store" });
  if (!response.ok) throw new Error(`Vehicle request failed: ${response.status}`);
  return response.json() as Promise<Car>;
}
