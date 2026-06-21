# Instrucciones de la creacion del Front

</>
`npm create vite@latest frontend -- --template react`
Esto va a crear las carpetas frontend y react instalando vite en el proceso si es que no se tiene.

`cd frontend` -> movernos a la carpeta frontend
`npm install `-> instalar dependencias

`npm run dev` -> levantamos el servidor viendo algo asi:
➜ Local: http://localhost:5173/
➜ Network: use --host to expose
➜ press h + enter to show help

## Dentro de la carpeta frontend

`npm install axios react-router-dom` -> Axios react permite hacer peticiones http

`npm install bootstrap` -> Bootstrap para diseñar el front con plantillas hechas

## Limpieza del React

dentro de frontend/src eliminamos los archivos

_App.css_
_index.css_
_assets/_

## Reemplazamos _App.jsx_

Solamente dejamos este bloque de codigo en _App.jsx_

```typescript
function App() {
return (

<h1>Fábrica - Sistema de Gestión</h1>
    );
}

export default App;
```

## Bootstrap

en la carpeta main.jsx importamos bootsrap agregando

```ts
import "bootstrap/dist/css/bootstrap.min.css";
```

quedandonos de esta manera

```ts
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import 'bootstrap/dist/css/bootstrap.min.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
```

## Creamos una estructura dentro del src

src/

├── components/
│
├── pages/
│ ├── Clientes.jsx
│ ├── Productos.jsx
│ ├── Ingredientes.jsx
│ └── Ventas.jsx
│
├── services/
│ └── api.js
│
├── routes/
│ └── AppRoutes.jsx
│
├── App.jsx
└── main.jsx

## Configuramos el Axios

en `src/services/api.js` ponemos:

```js
import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
});

export default api;
```

Por el momento voy a dejar el localhost, mas adelante ira el nombre del contenedor de docker.

## Creacion de paginas

como por ejemplo en Clientes.jsx

```js
export default function Clientes() {
  return (
    <div>
      <h2>Clientes</h2>
    </div>
  );
}
```

pero ahora en todos los archivos de pages/ restantes

## Configuracion de Router

en _src/routes/AppRoutes.jsx_ colocamos esto:

```js
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
```

## Conectar la app

en _App.jsx_ colocamos este bloque:

```js
import AppRoutes from "./routes/AppRoutes";

function App() {
  return <AppRoutes />;
}

export default App;
```

## Habilitamos el CORS en FastAPI

nos vamos a la parte del backend de FastAPI donde tenemos definida la app = fastapi()
en este proyecto lo tenemos en main.py y colocamos este codigo:

```py
from fastapi.middleware.cors import CORSMiddleware
```

Despues colocamos este bloque:

```py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Comprobacion de Bootsrap

en _App.jsx_

```js
function App() {
  return (
    <div className="container mt-5">
      <h1 className="text-primary">Sistema de Gestión Fábrica</h1>

      <button className="btn btn-success">Probar Bootstrap</button>
    </div>
  );
}
```
