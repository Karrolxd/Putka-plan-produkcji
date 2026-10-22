import { NavLink, Route, Routes } from "react-router-dom";
import ProductList from "./ProductList";
import ProductionPlan from "./ProductionPlan";

export default function App() {
  return (
    <main>
      <header>
        <h1>Putka</h1>
        <p className="subtitle">Plan produkcji</p>
        <nav>
          <NavLink to="/" end>
            Produkty
          </NavLink>
          <NavLink to="/plan">Plan produkcji</NavLink>
        </nav>
      </header>

      <Routes>
        <Route
          path="/"
          element={
            <section>
              <h2>Aktywne produkty</h2>
              <ProductList />
            </section>
          }
        />
        <Route path="/plan" element={<ProductionPlan />} />
      </Routes>
    </main>
  );
}
