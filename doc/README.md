# Auditoría de `cfdi-pdf`

Revisión técnica completa del repositorio `xmltopdf` (paquete `cfdi-pdf`, v0.1.3),
realizada el 2026-08-09 sobre la rama `develop`.

> **Actualización**: los hallazgos H1–H8 y H11 ya están **implementados** en
> `develop` (ver estado en [hallazgos.md](hallazgos.md)). Quedan pendientes
> H9 (docs/README) y H10 (higiene de artifactos).

## Resumen ejecutivo

`cfdi-pdf` es una biblioteca Python 3.12+ que convierte comprobantes **CFDI 4.0**
(XML del SAT mexicano) en PDF en tamaño **carta**, siempre nombrado por el
**UUID del timbre fiscal** (`{uuid}.pdf`).

**Estado general: sólido.** 114 tests pasan (6 nuevos), ruff y mypy sin errores,
cobertura 77%. La arquitectura es limpia y está bien separada en módulos. El
soporte de Complemento de Pago 2.0 es un diferenciador fuerte.

**Veredicto por área:**

| Área | Estado | Detalle |
|---|---|---|
| Arquitectura | ✅ Muy buena | Separación clara parser / modelos / render / QR / SAT |
| Correctitud fiscal | ✅ Corregido | Cadena original del TFD arreglada (H1) |
| Robustez | ✅ Corregido | Campos opcionales del Pagos20, `_get_int`, Totales (H2, H5, H6) |
| Seguridad | ✅ Buena | XXE/BOM/sandbox correctos; 1 hallazgo menor |
| Calidad de código | ✅ Excelente | mypy strict + ruff limpios |
| CI/CD | ✅ Corregido | Job `pip-audit` funcional (H4) |
| Versionado | ✅ Corregido | Fuente única vía `importlib.metadata` (H3/H7) |

## Documentos

| Documento | Contenido |
|---|---|
| [analisis.md](analisis.md) | Para qué sirve, arquitectura, flujo de datos, decisiones de diseño |
| [hallazgos.md](hallazgos.md) | Bugs y defectos priorizados por severidad (con estado) |
| [mejoras.md](mejoras.md) | Mejoras recomendadas a corto/medio/largo plazo |
| [seguridad.md](seguridad.md) | Análisis de seguridad (parser, templates, sandbox) |
| [calidad.md](calidad.md) | Estado de tests, cobertura, CI/CD y calidad de código |

## Hallazgos resueltos en esta iteración

1. **Cadena original del TFD incorrecta** (Alta) — `xml_parser._build_cadena_original`
   eliminó `SelloSAT` y respeta el orden oficial `cadenaoriginal_TFD_1_1.xslt`.
2. **Campos opcionales del Pagos20 tratados como obligatorios** (Alta) —
   `EquivalenciaDR` y `TipoCambioP` ahora son `Decimal | None`; los templates
   muestran `1` cuando están ausentes.
3. **Versiones inconsistentes** (Media) — `__version__` y `cli --version`
   ahora se leen de `importlib.metadata` (única fuente: `pyproject.toml`).
4. **Auditoría `pip-audit` no auditada** (Media) — el job CI instala `pip-tools`
   y audita los requisitos compilados.
5. **`int()` sin protección en `NumParcialidad`** (Media) — nuevo helper
   `_get_int` traduce `ValueError` → `InvalidCFDIError`.
6. **Pagos sin `Totales` descartados** (Media) — ahora lanza `InvalidCFDIError`.
7. **Atributos tipo `P`** (Media) — `Certificado` opcional cuando
   `TipoDeComprobante == "P"`.

