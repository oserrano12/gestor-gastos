# 🚀 Plan de Expansión: Funcionalidades "Nivel Pro"

Para implementar **todas** estas funcionalidades, necesitamos rediseñar la base de datos para que sea capaz de soportar esta nueva complejidad. Lo haremos en este orden estricto para no romper nada:

### Fase 1: Expansión del "Cerebro" (Base de Datos)
Necesitamos crear nuevas tablas y conectar las existentes:
1. **Tabla `Cuentas` (Billeteras):** Para manejar Efectivo, Tarjetas, Bancos. Cada transacción deberá apuntar a una de estas cuentas.
2. **Tabla `MetasAhorro` (Metas):** Para registrar el nombre de la meta, el monto objetivo, el dinero ahorrado hasta el momento y la fecha límite.
3. **Tabla `Presupuestos`:** Para establecer un límite de dinero por cada Categoría al mes.
4. **Tablas de Historial de Pagos:** Para registrar cuándo pagas exactamente la cuota 3 de un crédito o el mes de Netflix, y de qué cuenta salió el dinero.

### Fase 2: Actualización de la API (Python)
Crear todas las rutas (endpoints) para que el Frontend pueda pedir y guardar la información de las nuevas cuentas, metas y presupuestos.

### Fase 3: Lógica de Filtros y Pagos
Modificar las consultas de la base de datos para que acepten un `mes` y `año`. Programar la función automática que reste el dinero de tu saldo cuando presiones "Pagar Cuota".

### Fase 4: Rediseño Visual (Frontend)
1. **Barra Superior:** Añadir el selector de Mes/Año.
2. **Dashboard:** Añadir barras de progreso circulares para tus **Metas de Ahorro** y **Presupuestos**.
3. **Pestañas:** Añadir la sección de "Billeteras/Cuentas".

---
> [!WARNING] Impacto en Base de Datos
> Como vamos a modificar la estructura profunda de la base de datos en internet (Supabase) añadiendo relaciones complejas, la forma más limpia y libre de errores de hacerlo es "reiniciar" las tablas actuales. Esto borrará el usuario de prueba que acabas de crear. Como la app está en desarrollo, esto es normal.
