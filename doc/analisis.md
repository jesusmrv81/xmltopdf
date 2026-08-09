# Análisis del proyecto

## ¿Para qué sirve?

`cfdi-pdf` es una biblioteca Python que convierte **Comprobantes Fiscales
Digitales por Internet (CFDI)** versión **4.0** —el formato fiscal oficial del
SAT mexicano en formato XML— en documentos **PDF** legibles.

### Casos de uso

- **Generación de PDFs fiscales** a partir de XML emitidos por un PAC o un
  sistema de facturación (facturas, notas de crédito, complementos de pago).
- **Servicios/APIs web**: el método `render_bytes()` devuelve
  `(bytes, filename)` sin tocar disco — ideal para servidores HTTP o subir a S3.
- **Procesamiento por lotes**: la CLI procesa globs de archivos
  (`cfdi-pdf enero/*.xml`) con resumen de éxitos/fallos.
- **Complemento de Pago 2.0**: soporte dedicado para CFDI tipo `P` (pagos),
  con Totales, DoctoRelacionado, ImpuestosDR e ImpuestosP.

### Reglas de negocio clave (hardcodeadas en el diseño)

1. **Nombre de archivo = UUID del timbre fiscal** en minúsculas (`{uuid}.pdf`),
   garantizando trazabilidad y no duplicados. Si el CFDI no tiene timbre, se
   lanza `CFDIPDFError`.
2. **Tamaño de página carta** (`letter`, 8.5 × 11 in), estándar fiscal en México.
3. **QR SAT oficial** incrustado, con URL de verificación del SAT.
4. **Solo CFDI 4.0**: cualquier otra versión lanza `InvalidCFDIError`.

## Arquitectura

```
┌──────────────┐   CFDIPDF (api.py)
│     CLI      │   ├── CFDIParser        → lxml seguro + XMLSanitizer
│   (cli.py)   │   │      │
└──────────────┘   │      └── Modelos Pydantic v2 (models/)
        │          │   ├── SATQRGenerator → qrcode → base64 PNG
        ▼          │   └── RenderEngine (render/engine.py)
   CFDIPDF        │          ├── TemplateManager (Jinja2 SandboxedEnvironment)
        │          │          │    └── templates/{minimal,corporativo,clasico}
        ▼          │          ├── SATCatalogs + SATHelpers
   PDF bytes/Path  │          └── WeasyPrint → PDF
                   └── Formatters (utils/formatters.py)
```

### Módulos

| Módulo | Responsabilidad | Archivos clave |
|---|---|---|
| `api.py` | Fachada pública `CFDIPDF` | `render`, `render_from_string`, `render_bytes`, `parse`, `list_templates` |
| `cli.py` | Interfaz de línea de comandos | conversión individual y por lotes, `--list-templates` |
| `parser/` | Parseo XML seguro | `xml_parser.py` (lxml, `resolve_entities=False`), `sanitizer.py` (regex XML 1.0) |
| `models/` | Modelos Pydantic v2 (frozen, `extra=forbid`) | `cfdi`, `emisor`, `receptor`, `concepto`, `impuestos`, `timbre`, `pagos` |
| `qr/` | QR SAT oficial | `generator.py` → URL de verificación → PNG |
| `render/` | Motor de render | `engine.py` (contexto + WeasyPrint), `template.py` (Jinja2 sandbox) |
| `sat/` | Catálogos SAT y helpers | `catalogs.py` (régimen, uso CFDI, forma pago, monedas…), `helpers.py` |
| `utils/` | Formateadores | `formatters.py` (moneda, tasa, fecha, UUID, sellos) |
| `templates/` | Templates Jinja2 | `minimal`, `corporativo`, `clasico` |

## Flujo de datos

1. **Entrada**: ruta XML o string. `CFDIParser.parse_*`:
   - Sanea el contenido (quita caracteres inválidos XML 1.0).
   - Parsea con lxml protegido (`resolve_entities=False`, `no_network=True`,
     `huge_tree=False`).
   - Valida que sea `Comprobante` versión `4.0`.
   - Construye los modelos Pydantic (requeridos vs opcionales).
2. **Render** (`RenderEngine.render`):
   - Carga template Jinja2 desde `TemplateManager`.
   - Construye el contexto: `cfdi`, `formatted` (valores preformateados),
     `catalogs` (descripciones legibles), `qr_data` (base64), `logo_data`,
     `cadena_original` y helpers callables.
   - Renderiza HTML y lo convierte con WeasyPrint a PDF (bytes o archivo).
3. **Salida**: `Path` al PDF (nombre = UUID), o `(bytes, filename)`.

## Decisiones de diseño relevantes

| Decisión | Comentario |
|---|---|
| Modelos `frozen` + `extra=forbid` | Inmutables e impide campos inesperados — evita typos silenciosos |
| `SandboxedEnvironment` de Jinja2 | Los templates personalizados no pueden ejecutar código arbitrario |
| `select_autoescape(["html","xml"])` | Mitiga XSS en templates |
| Pre-formatación en `formatted` | Los templates no repiten lógica de formato; la API es estable |
| Catálogos como `Final[dict]` con fallback `"Desconocido (clave)"` | Nunca rompen por clave nueva del SAT |
| Zebra striping con clases explícitas (no `:nth-child`) | Compatibilidad con wkhtmltopdf |
| `render()` escribe a disco y devuelve `Path`; `render_bytes()` no toca disco | Dos modos claros para distintos consumidores |

## Puntos fuertes

- **Soporte completo de Complemento de Pago 2.0** (modelos, parser y templates),
  algo poco común en bibliotecas open source de CFDI.
- **Tres templates** con compatibilidad CSS documentada por motor.
- **Validación estricta** desde el parser: errores tempranos y claros con
  jerarquía de excepciones (`CFDIPDFError` base).
- **Seguridad ofensiva defensiva**: XXE, XML bombs, sandbox de templates,
  sanitización UTF-8.
- **Tipado estricto** mypy `strict=true` — 25 archivos sin errores.
