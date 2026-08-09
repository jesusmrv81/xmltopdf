# Mejoras recomendadas

Organizadas por horizonte temporal. Las que resuelven hallazgos de
[hallazgos.md](hallazgos.md) están marcadas con `[H#]`.

## Corto plazo (alta prioridad, bajo esfuerzo)

1. **[H1] Corregir la cadena original del TFD**
   Quitar `SelloSAT` y respetar el orden oficial. Agregar test que compare con
   la cadena esperada del SAT para un XML conocido.

2. **[H3/H7] Unificar la versión**
   Fuente única en `pyproject.toml` + `importlib.metadata` en runtime. Evita
   el desfase actual (0.1.3 vs 0.1.0).

3. **[H4] Arreglar el job de `pip-audit` en CI**
   Instalar `pip-tools` o auditar el entorno instalado. Considerar auditar
   también en PRs (no solo en `main`).

4. **[H2] Volver opcionales `EquivalenciaDR` y `TipoCambioP`**
   Cambiar parser + modelos + templates (usar `format_number(tipo_cambio_p, 4)
   if pago.tipo_cambio_p else "-"` en el template de pagos).

5. **[H5/H6] Robustez del parser de Pagos**
   Helper `_get_int` para `NumParcialidad`; lanzar `InvalidCFDIError` si hay
   `Pagos` sin `Totales` en vez de descartar silenciosamente.

6. **Tests para la CLI** (`tests/test_cli.py`)
   Actualmente `cli.py` tiene **0% de cobertura** y es la única pieza sin
   tests. Cubrir: conversión simple, batch, `--list-templates`, `--version`,
   error de archivo inexistente, código de salida.

## Medio plazo

7. **[H11] Tratar CFDI tipo `P` con atributos opcionales**
   `Certificado`, `DomicilioFiscalReceptor`, `UsoCFDI` opcionales cuando
   `TipoDeComprobante == "P"`, según el XSD.

8. **Validación de catálogos SAT en parse-time**
   Opción `validate_catalogs: bool = False` que valide las claves de catálogos
   (moneda, forma pago, uso CFDI…) contra los catálogos oficiales, con errores
   informativos. La descripción `"Desconocido (clave)"` ya da tolerancia, pero
   la validación explícita ayuda a detectar CFDIs corruptos.

9. **Soporte de complementos comunes (parcial)**
   El `_parse_complementos` convierte todo a `dict` genérico. Dar modelos
   tipados para los más usados:
   - **Nómina 1.2** (roadmap del README)
   - **Carta Porte 3.1** (roadmap del README)
   - **IEPS / LeyendasFiscales / InformaciónGlobal**

10. **Formatear fechas con zona horaria**
    `Formatters.format_date` no maneja offset (`2024-01-15T10:30:00-06:00`).
    El SAT emite con zona; parsear con `datetime.fromisoformat` y mostrar
    en hora local o mantener el offset explícitamente.

11. **`Addenda` del comprobante**
    Los CFDIs pueden traer `cfdi:Addenda` (XML arbitrario del emisor). Hoy el
    parser no lo contempla. Decidir si ignorarlo explícitamente (recomendado
    por seguridad) o parsearlo.

## Largo plazo / roadmap

12. **Validación contra XSD del SAT**
    Empacar `cfdv40.xsd` + `cadenaoriginal_TFD_1_1.xslt` como recursos del
    paquete y ofrecer `validate=True` (roadmap del README). Resuelve H1 de raíz.

13. **API REST / servidor**
    El README lo lista en roadmap. Con `render_bytes()` la capa HTTP sería
    mínima (FastAPI con endpoint POST de XML → PDF).

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
