# Mejoras recomendadas

Organizadas por horizonte temporal. Las que resuelven hallazgos de
[hallazgos.md](hallazgos.md) están marcadas con `[H#]`.

> **Actualización (2026-08-09)**: implementados los items 1, 2, 3 (cadena
> original oficial + XSLT, validación XSD y Nómina/Carta Porte), los hallazgos
> H1–H8 y H11–H13, los tests de CLI (item 6), la **descarga en runtime de los
> recursos SAT** (H13) y los items 4/5 (examples arreglados con la API actual
> y release **0.2.0**). Además `recover=False` en el parser (item 1 de
> seguridad). Ver estado en cada sección.

## Arquitectura de recursos SAT (resuelta en H13)

Los XSLT/XSD del SAT ya no se empaquetan. `SATResourceManager` los descarga del
SAT (mirror verificado como fallback), los cachea en `~/.cache/cfdi-pdf` y
verifica su SHA-256 contra un manifiesto canónico. Ventajas: wheel pequeño y
los cambios del SAT se absorben sin re-publicar (se detectan por hash). Ver
`doc/seguridad.md` para procedencia y actualización del manifiesto.

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

8. ✅ **Validación de catálogos SAT standalone**
   `validate_catalogs=True` en `CFDIParser`/`CFDIPDF`: valida las claves SAT
   (moneda, régimen, uso CFDI, impuestos, forma de pago…) sin exigir el XSD.

9. ✅ **Soporte de complementos comunes**
   Nómina 1.2, Carta Porte 3.1, **Leyendas Fiscales**, **IEPS** e
   **Información Global** (modelos + parser + templates). La `Addenda` se
   detecta (`has_addenda`) e **ignora** por seguridad.

10. ✅ **Formatear fechas con zona horaria**
    `format_date` ahora parsea con `datetime.fromisoformat` y formatea el offset
    (`15/01/2024 10:30:00 -06:00`, `Z`, fecha sola).

11. ✅ **`Addenda` del comprobante**
    Se ignora explícitamente (recomendado por seguridad): el parser la detecta
    (`cfdi.has_addenda`) sin parsear su contenido arbitrario.

### Fiscales resueltos

- ✅ **QR `fe` percent-encoded**: el parámetro base64 (`+/=`) se codifica con
  `urllib.parse.quote`, evitando que un query string lo altere en el portal SAT.
- ✅ **Store de certificados SAT**: `verify_sello_sat(cfdi)` sin certificado
  busca automáticamente por `NoCertificadoSAT` en
  `~/.cache/cfdi-pdf/certs/` (o `CFDI_PDF_SAT_CERTS_DIR`).

## Largo plazo / roadmap

12. ✅ **Validación contra XSD del SAT**
    `cfdv40.xsd` + catálogos descargados en runtime; `validate_xsd=True` en
    parser y API.

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

17. ✅ `logger.warning(f"...")` → lazy formatting `[H8]`.
18. Actualizar `README.md` (requisito lxml, comandos de tests, estructura) `[H9]`.
19. Añadir `doc/` al árbol de estructura del README o un enlace.
20. Mover PDFs/XMLs de prueba fuera de la raíz `[H10]`.
21. ✅ `pip-audit` en PRs + caché de recursos SAT + pin del action de PyPI.
