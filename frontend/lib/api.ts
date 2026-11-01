export type Car = { id: number; slug: string; brand: string; model: string; trim: string | null; year: number; price_cny: string; range_km: number | null; battery_kwh: string | null; power_kw: number | null; drivetrain: string | null; availability: string; images: string[] };
const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";
export async function fetchCars(filters: URLSearchParams, signal?: AbortSignal): Promise<Car[]> {
  const response = await fetch(`${apiBase}/cars?${filters.toString()}`, { signal, cache: "no-store" });
  if (!response.ok) throw new Error(`Catalog request failed: ${response.status}`);
  return response.json() as Promise<Car[]>;
}
