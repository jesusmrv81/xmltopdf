# Changelog

Todos los cambios notables de este proyecto se documentarán en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto se adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

### Añadido
- Template `corporativo`: diseño azul corporativo `#1a3a5c`, tablas HTML para layout fiscal
- Template `clasico`: blanco/negro, tipografía Times New Roman, máxima compatibilidad (wkhtmltopdf)
- Método `render_bytes(xml_path)` → retorna `(bytes, filename)` sin escribir a disco
- Suite de tests para nuevos templates (50+ casos: CSS experimental, variables Jinja2, compatibilidad por motor)

### Cambiado
- **Tamaño de página**: todos los templates cambiaron de `A4` a `letter` (8.5 × 11 in), estándar en México
- **Nombre de archivo por UUID**: `render()` y `render_from_string()` ya no aceptan ruta de salida explícita; el PDF siempre se nombra `{uuid}.pdf` (UUID en minúsculas del timbre fiscal)
- `render(xml_path, output_dir=None, ...)` → retorna `Path` al PDF generado
- `render_from_string(xml_content, output_dir=None, ...)` → retorna `Path` al PDF generado
- CLI simplificada: eliminado argumento posicional de salida; se usa `--output-dir` para especificar directorio
- Python mínimo actualizado de 3.11 a **3.12**; `pyproject.toml`, `ruff`, `black` y `mypy` actualizados
- `parser/sanitizer.py`: reemplazado loop O(n) char-por-char por `re.sub` compilado con `_INVALID_XML_CHARS.subn()`
- `parser/xml_parser.py`: separados `_get_attr` (requerido, lanza `InvalidCFDIError`) y `_get_optional_attr` (opcional, retorna `str | None`); `_get_decimal` usa `except decimal.InvalidOperation` en lugar de `except Exception`; `_element_to_dict` tipado como `dict[str, object]`
- `render/engine.py`: `_build_context` dividido en helpers privados (`_build_qr_data`, `_build_logo_data`, `_build_cadena_original`, `_build_formatted`, `_build_catalogs`); `except Exception` acotado a `TemplateRenderError` y `PDFGenerationError`
- `cli.py`: reemplazados `logging.error/info` globales por `logger` de módulo; eliminado trailing whitespace
- `models/cfdi.py`: `complementos: dict[str, dict]` → `dict[str, dict[str, object]]`
- `qr/generator.py`: eliminado import `urllib.parse.quote` no usado
- `render/template.py`: eliminados imports `Any` y `Environment` no usados; `get_template()` retorna `Template` concreto

### Seguridad
- Sanitizador XML usa un único regex compilado para eliminar caracteres inválidos XML 1.0 (más eficiente y sin falsos positivos por lookbehind)

## [0.1.0] - 2026-02-18

### Añadido
- Soporte completo para CFDI 4.0
- Parser XML con namespaces SAT
- Modelos Pydantic v2 para todas las entidades CFDI
- Generador de código QR SAT oficial
- Sistema de templates con Jinja2
- Template "minimal" con diseño moderno
- Catálogos SAT completos
- Sanitización UTF-8 y escapes XML
- Formateadores de moneda, impuestos y fechas
- Protección contra XXE y XML bombs
- CLI para conversión por lotes
- API pública simple y extensible
- Tests comprehensivos con fixtures CFDI
- Tipado estricto con MyPy
- Configuración de Ruff, Black y MyPy
- GitHub Actions para CI/CD
- Documentación completa en español

### Características Técnicas
- Python 3.11+
- WeasyPrint para generación de PDF
- Pydantic v2 para validación
- Jinja2 + SandboxedEnvironment
- lxml para parsing seguro
- qrcode con PIL/Pillow
- Hatchling como build backend

### Seguridad
- Parser XML seguro (resolve_entities=False)
- Protección contra XML bombs (no_network=True)
- Sandboxing de templates Jinja2
- Sanitización de entrada UTF-8
- Validación de namespaces SAT

[Unreleased]: https://github.com/yourusername/cfdi-pdf/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/cfdi-pdf/releases/tag/v0.1.0

