import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { fetchJson, type ProductionPlan as Plan } from "./api";
import { tomorrow } from "./dates";

export default function ProductionPlan() {
  const [searchParams] = useSearchParams();
  const [date, setDate] = useState(() => searchParams.get("date") ?? tomorrow());
  const [plan, setPlan] = useState<Plan | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!date) return;
    const controller = new AbortController();
    setLoading(true);
    setError(null);
    fetchJson<Plan>(`/production-plan?date=${date}`, { signal: controller.signal })
      .then(setPlan)
      .catch((e: Error) => {
        if (e.name !== "AbortError") setError(e.message);
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [date]);

  return (
    <section>
      <h2>Plan produkcji</h2>
      <label className="date-picker">
        Dzień dostawy{" "}
        <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
      </label>
      {content()}
    </section>
  );

  function content() {
    if (!date) return <p>Wybierz dzień.</p>;
    if (loading) return <p>Ładowanie…</p>;
    if (error) return <p className="error">Nie udało się pobrać planu: {error}</p>;
    if (!plan) return null;

    const empty = plan.categories.every((c) => c.total === 0);
    return (
      <>
        {empty && <p className="muted">Brak zamówień na ten dzień.</p>}
        <table>
          <thead>
            <tr>
              <th>Produkt</th>
              <th className="num">Sztuk</th>
            </tr>
          </thead>
          {plan.categories.map((c) => (
            <tbody key={c.category}>
              <tr className="category-row">
                <th scope="rowgroup">{c.category}</th>
                <th className="num">{c.total}</th>
              </tr>
              {c.products.map((p) => (
                <tr key={p.product_id} className={p.quantity === 0 ? "muted" : undefined}>
                  <td>{p.name}</td>
                  <td className="num">{p.quantity}</td>
                </tr>
              ))}
            </tbody>
          ))}
        </table>
      </>
    );
  }
}
