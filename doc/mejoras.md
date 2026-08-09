# Mejoras recomendadas

Organizadas por horizonte temporal. Las que resuelven hallazgos de
[hallazgos.md](hallazgos.md) están marcadas con `[H#]`.

> **Actualización (2026-08-09)**: implementados los items 1, 2, 3 (cadena
> original oficial + XSLT, validación XSD y Nómina/Carta Porte), los hallazgos
> H1–H8 y H11, y los tests de CLI (item 6). Ver estado en cada sección.

## Corto plazo (alta prioridad, bajo esfuerzo)

1. ✅ **[H1] Cadena original del TFD** — ahora se genera con la XSLT oficial
   `cadenaoriginal_TFD_1_1.xslt` (empaquetada). Además se añadió la cadena
   completa del comprobante (`cadenaoriginal_4_0.xslt`) y `SelloVerifier`.

2. ✅ **[H3/H7] Unificar la versión**
   Fuente única en `pyproject.toml` + `importlib.metadata` en runtime.

3. ✅ **[H4] Arreglar el job de `pip-audit` en CI**
   Instala `pip-tools` y audita los requisitos compilados.

4. ✅ **[H2] Volver opcionales `EquivalenciaDR` y `TipoCambioP`**
   Modelos `Decimal | None` + templates que muestran `1` cuando faltan.

5. ✅ **[H5/H6] Robustez del parser de Pagos**
   Helper `_get_int` para `NumParcialidad`; `Pagos` sin `Totales` lanzan
   `InvalidCFDIError`.

6. ✅ **Tests para la CLI** (`tests/test_cli.py`)
   `cli.py` ahora tiene cobertura: conversión simple, batch, `--list-templates`,
   `--version`, archivo inexistente e XML inválido. Se corrigió además el bug
   de `--list-templates` sin argumentos (exit 2).

## Medio plazo

7. ✅ **[H11] Tratar CFDI tipo `P` con atributos opcionales**
   `Certificado` opcional cuando `TipoDeComprobante == "P"`, según el XSD.

8. **Validación de catálogos SAT en parse-time**
   Parcialmente cubierto por `validate_xsd=True` (valida contra el XSD oficial,
   que incluye los catálogos). Pendiente: modo que solo valide catálogos sin
   exigir el esquema completo.

9. **Soporte de complementos comunes**
   ✅ Nómina 1.2 y Carta Porte 3.1 (modelos + parser + templates).
   Pendiente: **IEPS / LeyendasFiscales / InformaciónGlobal** (siguen como
   `dict` genérico en `cfdi.complementos`).

10. **Formatear fechas con zona horaria**
    `Formatters.format_date` no maneja offset (`2024-01-15T10:30:00-06:00`).
    El SAT emite con zona; parsear con `datetime.fromisoformat` y mostrar
    en hora local o mantener el offset explícitamente.

11. **`Addenda` del comprobante**
    Los CFDIs pueden traer `cfdi:Addenda` (XML arbitrario del emisor). Hoy el
    parser no lo contempla. Decidir si ignorarlo explícitamente (recomendado
    por seguridad) o parsearlo.

## Largo plazo / roadmap

12. ✅ **Validación contra XSD del SAT**
    `cfdv40.xsd` + catálogos empaquetados; `validate_xsd=True` en parser y API.

13. ✅ **API REST / servidor** — implementado como patrón de integración
    (`examples/fastapi_service.py`) + `render_bytes_from_string()`. La librería
    **sigue siendo pura** (cero dependencias web).

14. **Rendimiento**
    - `CFDIPDF` actualmente crea `CFDIParser`, `SATQRGenerator`,
      `TemplateManager` y `RenderEngine` por instancia. Para batch de miles de
      archivos, considerar reutilizar instancias y cachear catálogos (ya son
      `Final`, no se recargan).
    - WeasyPrint es el cuello de botella; evaluar batch de HTML y
      paralelización a nivel de proceso.

15. **Telemetría / observabilidad**
    Exponer `render` con logging estructurado (JSON) para entornos de
    servicio, y un hook de post-render (para registrar el UUID procesado).

16. **i18n del template**
    Los templates están en español fijo. El constructor ya acepta `locale`,
    pero los templates no lo usan. Si se quiere multi-idioma, parametrizar
    strings vía contexto.

## Higiene menor

17. `logger.warning(f"...")` → lazy formatting `[H8]`.
18. Actualizar `README.md` (requisito lxml, comandos de tests, estructura) `[H9]`.
19. Añadir `doc/` al árbol de estructura del README o un enlace.
20. Mover PDFs/XMLs de prueba fuera de la raíz `[H10]`.
