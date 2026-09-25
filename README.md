# Gestor de Gastos Avanzado 🚀

Un gestor de gastos avanzado multiplataforma con un potente motor de amortización de créditos. Diseñado para ofrecer control financiero total, calculando cuotas de préstamos y organizando el flujo de caja diario.

## 🛠️ Stack Tecnológico
* **Backend:** Python + FastAPI
* **Base de Datos:** PostgreSQL + SQLAlchemy
* **Frontend:** HTML, Vanilla JavaScript, Tailwind CSS (PWA)

## 📁 Estructura del Proyecto

El proyecto se divide principalmente en dos entornos: `backend` y `frontend`.

```
gestor-gastos/
├── backend/            # API RESTful, modelos de BD, lógica de negocio
│   ├── app/
│   │   ├── api/        # Endpoints y rutas
│   │   ├── core/       # Configuraciones y seguridad
│   │   ├── db/         # Conexión a la base de datos
│   │   ├── models/     # Modelos de SQLAlchemy
│   │   ├── schemas/    # Esquemas Pydantic
│   │   └── services/   # Lógica financiera (motor de amortización)
│   ├── main.py         # Punto de entrada de FastAPI
│   └── requirements.txt
├── frontend/           # PWA (Progressive Web App)
│   ├── index.html
│   ├── app.js
│   ├── styles.css
│   ├── manifest.json   # Configuración PWA
│   ├── sw.js           # Service Worker para funcionamiento offline
│   └── assets/
└── README.md
```

## 🚀 Fases de Desarrollo

- [x] **Fase 1:** Setup y Repositorio.
- [ ] **Fase 2:** Backend - Base de Datos y Modelos.
- [ ] **Fase 3:** Lógica Financiera (El Core).
- [ ] **Fase 4:** API REST con FastAPI.
- [ ] **Fase 5:** Frontend y Conversión a App (PWA).

## 💻 Instalación Local

*(Instrucciones de instalación próximamente)*
