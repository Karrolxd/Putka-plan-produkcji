export const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export type Product = {
  id: number;
  name: string;
  category: string;
  unit_price: string;
};

export type PlanProduct = {
  product_id: number;
  name: string;
  quantity: number;
};

export type PlanCategory = {
  category: string;
  total: number;
  products: PlanProduct[];
};

export type ProductionPlan = {
  date: string;
  categories: PlanCategory[];
};

async function errorMessage(response: Response): Promise<string> {
  const text = await response.text();
  try {
    const { detail } = JSON.parse(text);
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) return detail.map((e: { msg: string }) => e.msg).join(", ");
  } catch {
    // odpowiedź nie jest JSON-em – zostaje surowy tekst
  }
  return `HTTP ${response.status}: ${text}`;
}

export async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, init);
  if (!response.ok) {
    throw new Error(await errorMessage(response));
  }
  return response.json() as Promise<T>;
}
