import { useEffect, useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { fetchJson, type OrderOut, type Product, type Store } from "./api";
import { tomorrow } from "./dates";

export default function OrderForm() {
  const [stores, setStores] = useState<Store[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [storeId, setStoreId] = useState("");
  const [date, setDate] = useState(tomorrow);
  const [quantities, setQuantities] = useState<Record<number, string>>({});

  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [created, setCreated] = useState<OrderOut | null>(null);

  useEffect(() => {
    Promise.all([fetchJson<Store[]>("/stores"), fetchJson<Product[]>("/products")])
      .then(([stores, products]) => {
        setStores(stores);
        setProducts(products);
        if (stores.length > 0) setStoreId(String(stores[0].id));
      })
      .catch((e: Error) => setLoadError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const items = products
    .map((p) => ({ product: p, quantity: Number(quantities[p.id] || 0) }))
    .filter((i) => i.quantity > 0);
  const total = items.reduce((sum, i) => sum + i.quantity * Number(i.product.unit_price), 0);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setSubmitError(null);
    setCreated(null);
    if (items.length === 0) {
      setSubmitError("Dodaj co najmniej jeden produkt.");
      return;
    }
    setSubmitting(true);
    try {
      const order = await fetchJson<OrderOut>("/orders", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          store_id: Number(storeId),
          delivery_date: date,
          items: items.map((i) => ({ product_id: i.product.id, quantity: i.quantity })),
        }),
      });
      setCreated(order);
      setQuantities({});
    } catch (e) {
      setSubmitError((e as Error).message);
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <p>Ładowanie…</p>;
  if (loadError) return <p className="error">Nie udało się pobrać danych: {loadError}</p>;

  return (
    <section>
      <h2>Nowe zamówienie</h2>
      <form onSubmit={submit}>
        <div className="form-row">
          <label>
            Sklep{" "}
            <select value={storeId} onChange={(e) => setStoreId(e.target.value)}>
              {stores.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Dzień dostawy{" "}
            <input type="date" value={date} onChange={(e) => setDate(e.target.value)} required />
          </label>
        </div>

        <table>
          <thead>
            <tr>
              <th>Produkt</th>
              <th>Kategoria</th>
              <th className="num">Cena</th>
              <th className="num">Ilość</th>
            </tr>
          </thead>
          <tbody>
            {products.map((p) => (
              <tr key={p.id}>
                <td>{p.name}</td>
                <td>{p.category}</td>
                <td className="num">{Number(p.unit_price).toFixed(2)} zł</td>
                <td className="num">
                  <input
                    className="qty"
                    type="number"
                    min={0}
                    step={1}
                    value={quantities[p.id] ?? ""}
                    onChange={(e) => setQuantities({ ...quantities, [p.id]: e.target.value })}
                  />
                </td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr>
              <th colSpan={3}>Razem</th>
              <th className="num">{total.toFixed(2)} zł</th>
            </tr>
          </tfoot>
        </table>

        <div className="form-actions">
          <button type="submit" disabled={submitting}>
            {submitting ? "Wysyłanie…" : "Złóż zamówienie"}
          </button>
        </div>
      </form>

      {submitError && <p className="error">{submitError}</p>}
      {created && (
        <p className="success">
          Zamówienie nr {created.id} na {created.delivery_date} przyjęte.{" "}
          <Link to={`/plan?date=${created.delivery_date}`}>Zobacz plan na ten dzień</Link>
        </p>
      )}
    </section>
  );
}
