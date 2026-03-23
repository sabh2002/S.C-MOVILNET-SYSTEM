# Plan de Desarrollo — S.C. MOVILNET SYSTEM

> Última actualización: 2026-03-05
> Fase actual: **Fase 1 — Correcciones críticas de lógica de negocio**

---

## Descripción General del Sistema

Sistema de gestión de inventario, compras y ventas para Movilnet. Permite administrar
productos, proveedores, clientes, movimientos de inventario, cotizaciones a proveedores,
órdenes de compra y notas de entrega a clientes.

**Stack:** Django 6 · Python 3.13 · SQLite · HTML/CSS (diseño propio)

---

## Objetivos Generales del Proyecto

- [x] Autenticación de usuarios con roles (Admin / Empleado)
- [x] CRUD de catálogos base: Marcas, Proveedores, Clientes, Productos
- [x] Registro de movimientos de inventario
- [ ] Movimientos de inventario correctamente conectados al stock real
- [x] Flujo de cotizaciones a proveedores (estructura básica)
- [ ] Cotizaciones con precio por línea y total calculado automáticamente
- [x] Flujo de órdenes de compra (estructura básica)
- [ ] Órdenes de compra con estado y actualización automática de stock al recibir
- [x] Flujo de notas de entrega a clientes (estructura básica)
- [ ] Notas de entrega que descuenten stock automáticamente
- [ ] Vista de estado actual de inventario (Stock Actual)
- [ ] Bitácora de auditoría operativa
- [ ] Dashboard con métricas reales del negocio
- [ ] Numeración automática de documentos (OC, NE)

---

## Estado por Módulo

---

### MÓDULO: Autenticación y Empleados

**Estado:** ✅ Funcional con advertencia de seguridad

#### Implementado
- [x] Login / Logout
- [x] Cambio de contraseña
- [x] Registro de empleados (solo Admin)
- [x] Lista de empleados (solo Admin)
- [x] Perfil de usuario
- [x] Recuperación de contraseña por preguntas de seguridad
- [x] Dos roles: Administrador y Empleado

#### Pendiente — Fase 5 (Seguridad)
- [ ] Reemplazar preguntas de seguridad (animal/color favorito) por mecanismo seguro
- [ ] Agregar rate limiting al endpoint de recuperación de contraseña
- [ ] Validar fortaleza mínima de contraseña al registrar empleado
- [ ] Agregar campo `activo` para desactivar empleados sin borrarlos

---

### MÓDULO: Catálogos (Marcas, Proveedores, Clientes)

**Estado:** ✅ Funcional

#### Implementado
- [x] CRUD completo de Marcas con estado activo/inactivo
- [x] CRUD completo de Proveedores con validación de RIF venezolano
- [x] CRUD completo de Clientes con validación de cédula venezolana
- [x] Búsqueda en listados
- [x] Paginación
- [x] Eliminación restringida a Administradores

#### Pendiente — Fase 4
- [ ] Vista de detalle de Proveedor con historial de cotizaciones
- [ ] Vista de detalle de Cliente con historial de notas de entrega
- [ ] Exportar listados a CSV

---

### MÓDULO: Productos

**Estado:** ⚠️ Funcional pero incompleto

#### Implementado
- [x] CRUD completo de Productos
- [x] Asociación con Marca
- [x] Campos de stock: actual, mínimo, máximo
- [x] Validación: stock mínimo ≤ stock máximo
- [x] Estado del stock (Sin Stock, Stock Bajo, Normal, Máximo)
- [x] Alerta de bajo stock en el dashboard
- [x] Búsqueda por nombre y marca

#### Pendiente — Fase 2 y 4
- [ ] Vista de detalle de producto con historial de movimientos
- [ ] El `stock_actual` debería ser de solo lectura en el formulario (solo modificable via movimientos)
- [ ] Exportar productos a CSV
- [ ] Filtro por estado de stock en el listado

---

### MÓDULO: Inventario — Tipos de Movimiento

**Estado:** 🔴 Defectuoso

#### Implementado
- [x] CRUD de tipos de movimiento
- [x] Campos: nombre y categoría (ambos texto libre)

#### Problemas críticos
- [x] ~~La lógica de si el movimiento suma o resta stock depende del nombre del tipo~~
      → **CORREGIDO en Fase 1 (ver abajo)**
- [x] ~~No hay restricción de unicidad — pueden crearse tipos duplicados~~
      → **CORREGIDO en Fase 1**

#### Pendiente — Completado en Fase 1
- [x] Agregar campo `dirección` (ENTRADA / SALIDA) como opciones fijas
- [x] Restricción de unicidad por nombre + dirección

---

### MÓDULO: Inventario — Movimientos

**Estado:** 🔴 Defectuoso (lógica de stock rota)

#### Implementado
- [x] Registro manual de movimientos
- [x] Asociación con Producto, Tipo, Empleado
- [x] Listado con búsqueda

#### Problemas críticos corregidos en Fase 1
- [x] ~~Detección de ENTRADA/SALIDA por string matching del nombre del tipo~~
      → Usa `tipo.direccion`
- [x] ~~Sin indicador visual de si el movimiento sumó o restó stock~~

#### Pendiente — Fase 1 y 2
- [x] Mostrar indicador +/- en la lista de movimientos según dirección
- [ ] Agregar filtro por fecha y por dirección (ENTRADA/SALIDA) en el listado
- [ ] Mostrar el stock resultante después de cada movimiento
- [ ] Historial de movimientos filtrado por producto (desde la ficha del producto)

---

### MÓDULO: Inventario — Stock Actual *(NUEVA VISTA)*

**Estado:** 🔴 No existe

#### Pendiente — Fase 2
- [x] Crear vista "Stock Actual" con tabla de todos los productos
- [x] Columnas: Producto, Marca, Stock Mín, Stock Actual, Stock Máx, Estado
- [x] Barra de progreso visual del nivel de stock
- [ ] Filtros por estado de stock y por marca
- [ ] Exportar a CSV

---

### MÓDULO: Cotizaciones

**Estado:** ✅ Corregido

#### Implementado
- [x] CRUD completo de cotizaciones
- [x] Detalles de cotización (productos, cantidades y **precio unitario**)
- [x] Estados: Pendiente, Aprobada, Rechazada, Vencida
- [x] Vista de detalle
- [x] Formulario con formset inline
- [x] **`precio_unitario` en `DetalleCotizacion`** — corregido en Fase 1
- [x] **`total` se calcula automáticamente** desde los detalles — corregido en Fase 1
- [x] **Formset inválido ya no guarda el padre** — corregido en Fase 1

#### Pendiente — Fase 4
- [ ] Mostrar total calculado en el formulario en tiempo real (JS)

---

### MÓDULO: Órdenes de Compra

**Estado:** 🔴 Incompleto — flujo de recepción desconectado

#### Implementado
- [x] CRUD completo de órdenes de compra
- [x] Detalles con cantidad solicitada y cantidad recibida
- [x] Asociación con cotización base
- [x] Vista de detalle

#### Corregido en Fase 1
- [x] **Campo `estado`** agregado: Pendiente / Parcialmente Recibida / Recibida / Cancelada
- [x] **Recibir mercancía actualiza stock** automáticamente (diferencia al editar)
- [x] **Solo cotizaciones aprobadas** disponibles al crear OC
- [x] **Formset inválido ya no guarda el padre**
- [x] **Estado se actualiza automáticamente** según cantidades recibidas vs solicitadas

#### Pendiente — Fase 3
- [ ] Agregar `precio_unitario` a `DetalleOrdenCompra`
- [ ] Numeración automática de órdenes (OC-2026-001)
- [ ] Pre-poblar detalles de OC desde la cotización base

---

### MÓDULO: Notas de Entrega (Ventas)

**Estado:** ✅ Corregido

#### Implementado
- [x] CRUD completo de notas de entrega
- [x] Detalles con cantidad, precio unitario, descuento
- [x] Vista de detalle

#### Corregido en Fase 1
- [x] **Crear NE descuenta el stock** de los productos vendidos
- [x] **Validación de stock disponible** antes de confirmar la venta
- [x] **`DetalleNotaEntrega.subtotal` se calcula y guarda** correctamente
- [x] **Descuento por línea validado** para no superar el valor de la línea
- [x] **Al editar NE**, se ajusta la diferencia de stock (devuelve previo, descuenta nuevo)
- [x] **Al eliminar NE**, se devuelve el stock de todos los productos

#### Pendiente — Fase 3
- [ ] Numeración automática de notas (NE-2026-001)

---

### MÓDULO: Bitácora de Auditoría

**Estado:** 🔴 Modelo existe, completamente sin implementar

#### Implementado
- [x] Modelo `Bitacora` en base de datos

#### Pendiente — Fase 2
- [ ] Crear función auxiliar `registrar_en_bitacora(empleado, tabla, accion, id, descripcion)`
- [ ] Llamar a esta función en cada operación CRUD del sistema
- [ ] Vista de consulta de bitácora (solo Admin)
- [ ] Filtros: por fecha, por usuario, por módulo, por acción
- [ ] Agregar enlace en el menú de Administración

---

### MÓDULO: Dashboard

**Estado:** ⚠️ Funcional pero con datos limitados

#### Implementado
- [x] Contadores: productos activos, clientes, proveedores, marcas
- [x] Alerta de productos con stock bajo
- [x] Accesos rápidos a formularios
- [x] Información del usuario activo

#### Pendiente — Fase 4
- [ ] Cotizaciones pendientes de aprobar
- [ ] Órdenes de compra pendientes de recibir
- [ ] Notas de entrega del día / de la semana
- [ ] Gráfico de movimientos del último mes (entradas vs salidas)
- [ ] Top 5 productos más movidos
- [ ] Valor total del inventario (suma de precio × stock_actual)

---

## Roadmap de Fases

```
FASE 1 — Correcciones críticas (EN PROGRESO)
├── ✅ TipoInventario: campo dirección fijo (ENTRADA/SALIDA)
├── ✅ Vista Stock Actual
├── ✅ Mejoras visuales de movimientos
├── ⬜ NotaEntrega: descuento de stock + validaciones
├── ⬜ Cotización: precio por línea + total calculado
├── ⬜ OrdenCompra: estado + recepción actualiza stock
└── ⬜ Corregir guardado de formsets inválidos

FASE 2 — Funcionalidades faltantes
├── ⬜ Bitácora operativa
├── ⬜ Historial de movimientos por producto
├── ⬜ Filtros avanzados en movimientos y stock
└── ⬜ Exportar listados a CSV

FASE 3 — Flujo de compras coherente
├── ⬜ OC solo desde cotizaciones aprobadas
├── ⬜ Pre-poblar detalles de OC desde cotización
├── ⬜ Precio en detalles de OC
└── ⬜ Numeración automática OC y NE

FASE 4 — Usabilidad y dashboard
├── ⬜ Dashboard con métricas reales
├── ⬜ Vistas de detalle de Producto, Cliente, Proveedor
└── ⬜ Exportar a CSV

FASE 5 — Seguridad
├── ⬜ Reemplazar preguntas de seguridad
├── ⬜ Rate limiting en recuperación de contraseña
└── ⬜ Validación de fortaleza de contraseña
```

---

## Notas Técnicas

- Las migraciones se aplican con `python manage.py migrate`
- El entorno virtual está en `./env/`
- Base de datos SQLite: `./db.sqlite3`
- Archivos estáticos: `movilnet/static/style.css`
