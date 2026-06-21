import { BrowserRouter, Routes, Route } from "react-router-dom";

import Clientes from "../pages/Clientes";
import Productos from "../pages/Productos";
import Ingredientes from "../pages/Ingredientes";
import Ventas from "../pages/Ventas";

export default function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Clientes />} />
        <Route path="/productos" element={<Productos />} />
        <Route path="/ingredientes" element={<Ingredientes />} />
        <Route path="/ventas" element={<Ventas />} />
      </Routes>
    </BrowserRouter>
  );
}