# Auditoría de `cfdi-pdf`

Revisión técnica completa del repositorio `xmltopdf` (paquete `cfdi-pdf`, v0.1.3),
realizada el 2026-08-09 sobre la rama `develop`.

> **Actualización**: se implementaron las mejoras fiscales principales: cadena
> original oficial con los XSLT del SAT, verificación de sellos, validación XSD,
> complementos de Nómina 1.2 y Carta Porte 3.1, tests de CLI y el patrón FastAPI.
> Estado de cada hallazgo en [hallazgos.md](hallazgos.md).

## Resumen ejecutivo

`cfdi-pdf` es una biblioteca Python 3.12+ que convierte comprobantes **CFDI 4.0**
(XML del SAT mexicano) en PDF en tamaño **carta**, siempre nombrado por el
**UUID del timbre fiscal** (`{uuid}.pdf`).

**Estado general: sólido.** 151 tests pasan, ruff y mypy sin errores, cobertura
85%. Además de PDF, ahora genera la **cadena original oficial** (XSLT del SAT),
**verifica sellos**, **valida contra el XSD** y modela **Pagos 2.0, Nómina 1.2 y
Carta Porte 3.1**.

**Veredicto por área:**

| Área | Estado | Detalle |
|---|---|---|
| Arquitectura | ✅ Muy buena | Separación clara parser / modelos / render / QR / SAT / crypto |
| Correctitud fiscal | ✅ Corregido | Cadena original oficial + verificación de sellos |
| Robustez | ✅ Corregido | Campos opcionales Pagos20, `_get_int`, Totales, XSD opcional |
| Complementos | ✅ Ampliado | Pagos 2.0, Nómina 1.2, Carta Porte 3.1 (modelos + templates) |
| Seguridad | ✅ Buena | XXE/BOM/sandbox correctos; XSD validate opcional |
| Calidad de código | ✅ Excelente | mypy strict + ruff limpios, cobertura 85% |
| CI/CD | ✅ Corregido | Job `pip-audit` funcional |
| Versionado | ✅ Corregido | Fuente única vía `importlib.metadata` |

## Documentos

| Documento | Contenido |
|---|---|
| [analisis.md](analisis.md) | Para qué sirve, arquitectura, flujo de datos, decisiones de diseño |
| [hallazgos.md](hallazgos.md) | Bugs y defectos priorizados por severidad (con estado) |
| [mejoras.md](mejoras.md) | Mejoras recomendadas a corto/medio/largo plazo |
| [seguridad.md](seguridad.md) | Análisis de seguridad (parser, templates, sandbox) |
| [calidad.md](calidad.md) | Estado de tests, cobertura, CI/CD y calidad de código |

## Hallazgos resueltos en esta iteración

1. **Cadena original oficial del SAT** — XSLT `cadenaoriginal_4_0.xslt` y
   `cadenaoriginal_TFD_1_1.xslt` empaquetados y ejecutados con lxml.
2. **Campos opcionales del Pagos20** — `EquivalenciaDR` y `TipoCambioP` ahora
   son `Decimal | None`; los templates muestran `1` cuando están ausentes.
3. **Versiones inconsistentes** — `__version__` y `cli --version` se leen de
   `importlib.metadata` (única fuente: `pyproject.toml`).
4. **Auditoría `pip-audit` no auditada** — el job CI instala `pip-tools`.
5. **`NumParcialidad` sin protección** — nuevo helper `_get_int`.
6. **Pagos sin `Totales` descartados** — ahora lanza `InvalidCFDIError`.
7. **Atributos tipo `P`** — `Certificado` opcional según el XSD.
8. **CLI `--list-templates` rota** — `files` opcional + suite `test_cli.py`.
9. **Verificación de sellos** — `SelloVerifier` valida SelloCFD/SelloSAT.

