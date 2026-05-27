# Changelog

Todos los cambios notables de este proyecto se documentarán en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto se adhiere a [Semantic Versioning](https://semver.org/lang/es/).

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

### Documentación
- README completo con ejemplos
- Guía de instalación
- API básica y avanzada
- Creación de templates personalizados
- Guía de desarrollo
- Ejemplos de código

[0.1.0]: https://github.com/yourusername/cfdi-pdf/releases/tag/v0.1.0
