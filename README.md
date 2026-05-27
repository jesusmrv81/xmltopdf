# CFDI PDF

[![PyPI version](https://img.shields.io/pypi/v/cfdi-pdf.svg)](https://pypi.org/project/cfdi-pdf/)
[![Python Version](https://img.shields.io/pypi/pyversions/cfdi-pdf.svg)](https://pypi.org/project/cfdi-pdf/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/yourusername/cfdi-pdf/workflows/Tests/badge.svg)](https://github.com/yourusername/cfdi-pdf/actions)
[![Coverage](https://img.shields.io/codecov/c/github/yourusername/cfdi-pdf)](https://codecov.io/gh/yourusername/cfdi-pdf)

Biblioteca profesional para convertir CFDI 4.0 XML a PDF con templates modernos y extensibles.

## Características

- ✅ **CFDI 4.0 Completo**: Soporte total para la versión 4.0 del SAT
- ✅ **QR SAT Oficial**: Generación del código QR con especificaciones oficiales
- ✅ **Templates Extensibles**: Sistema de templates basado en Jinja2 + HTML/CSS
- ✅ **Tipado Estricto**: Pydantic v2 para validación robusta
- ✅ **Seguridad**: Protección contra XXE, XML bombs y otros ataques
- ✅ **UTF-8 Completo**: Manejo correcto de acentos, ñ y caracteres especiales
- ✅ **Catálogos SAT**: Todos los catálogos oficiales del SAT
- ✅ **CLI Incluida**: Herramienta de línea de comandos para conversiones rápidas
- ✅ **Python 3.11+**: Aprovecha las últimas características de Python

## Instalación

```bash
pip install cfdi-pdf
```

## Uso Rápido

### API Básica

```python
from cfdi_pdf import CFDIPDF

# Inicializar con template por defecto
pdf = CFDIPDF(template="minimal")

# Convertir desde archivo
pdf.render(
    xml_path="factura.xml",
    output="factura.pdf"
)

# Convertir desde string XML
with open("factura.xml", "r") as f:
    xml_content = f.read()

pdf_bytes = pdf.render_from_string(xml_content)

# Guardar el resultado
with open("factura.pdf", "wb") as f:
    f.write(pdf_bytes)
```

### Con Logo Personalizado

```python
from cfdi_pdf import CFDIPDF

pdf = CFDIPDF()
pdf.render(
    xml_path="factura.xml",
    output="factura.pdf",
    logo_path="logo.png"
)
```

### Usando Templates Personalizados

```python
from pathlib import Path
from cfdi_pdf import CFDIPDF

# Registrar directorio de templates personalizados
pdf = CFDIPDF(template_dirs=[Path("./mis_templates")])

# Usar template personalizado
pdf.render(
    xml_path="factura.xml",
    output="factura.pdf",
    template="mi_template"
)
```

### CLI (Línea de Comandos)

```bash
# Conversión simple
cfdi-pdf factura.xml factura.pdf

# Con template específico
cfdi-pdf factura.xml factura.pdf --template minimal

# Con logo
cfdi-pdf factura.xml factura.pdf --logo logo.png

# Conversión por lotes
cfdi-pdf *.xml --output-dir ./pdfs/

# Ver información detallada
cfdi-pdf factura.xml factura.pdf --verbose
```

## Templates Disponibles

### Minimal (por defecto)

Template limpio y moderno con:
- Diseño minimalista inspirado en Stripe
- Todos los datos fiscales requeridos
- QR SAT oficial
- Sellos digitales
- Cadena original
- Tabla de conceptos
- Desglose de impuestos

## API Avanzada

### Acceso a Datos del CFDI

```python
from cfdi_pdf import CFDIPDF

pdf = CFDIPDF()
cfdi = pdf.parse("factura.xml")

# Acceder a datos
print(f"UUID: {cfdi.uuid}")
print(f"Emisor: {cfdi.emisor.nombre}")
print(f"Receptor: {cfdi.receptor.nombre}")
print(f"Total: ${cfdi.total:,.2f} {cfdi.moneda}")

# Impuestos
for impuesto in cfdi.impuestos.traslados:
    print(f"{impuesto.tipo}: {impuesto.tasa}% = ${impuesto.importe:,.2f}")
```

### Generación de QR Independiente

```python
from cfdi_pdf.qr import SATQRGenerator

qr_gen = SATQRGenerator()
qr_bytes = qr_gen.generate(
    uuid="CCE4D168-1234-5678-9ABC-DEF012345678",
    rfc_emisor="AAA010101AAA",
    rfc_receptor="XAXX010101000",
    total=1160.00,
    sello_digital="abc123def456..."
)

# Guardar QR
with open("qr.png", "wb") as f:
    f.write(qr_bytes)
```

### Crear Template Personalizado

1. Crea un directorio para tu template:
```bash
mkdir -p mi_template
```

2. Crea `template.html`:
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <h1>Factura {{ cfdi.uuid }}</h1>
    <p>Emisor: {{ cfdi.emisor.nombre }}</p>
    <p>Total: {{ format_currency(cfdi.total) }}</p>
    
    {% if qr_data %}
        <img src="data:image/png;base64,{{ qr_data }}" alt="QR SAT">
    {% endif %}
</body>
</html>
```

3. Crea `styles.css`:
```css
body {
    font-family: Arial, sans-serif;
    margin: 2cm;
}

h1 {
    color: #333;
}
```

4. Usa tu template:
```python
from pathlib import Path
from cfdi_pdf import CFDIPDF

pdf = CFDIPDF(template_dirs=[Path(".")])
pdf.render(
    xml_path="factura.xml",
    output="factura.pdf",
    template="mi_template"
)
```

## Estructura del Proyecto

```
cfdi_pdf/
├── api.py              # API principal
├── cli.py              # Interfaz de línea de comandos
├── exceptions.py       # Excepciones personalizadas
├── models/            # Modelos Pydantic
│   ├── cfdi.py
│   ├── emisor.py
│   ├── receptor.py
│   ├── concepto.py
│   ├── impuestos.py
│   └── timbre.py
├── parser/            # Parser XML
│   ├── xml_parser.py
│   └── sanitizer.py
├── qr/                # Generador QR
│   └── generator.py
├── render/            # Motor de renderizado
│   ├── engine.py
│   └── template.py
├── sat/               # Catálogos SAT
│   ├── catalogs.py
│   └── helpers.py
├── utils/             # Utilidades
│   └── formatters.py
└── templates/         # Templates incluidos
    └── minimal/
        ├── template.html
        └── styles.css
```

## Requisitos

- Python 3.11+
- WeasyPrint >= 60.0
- Pydantic >= 2.0.0
- Jinja2 >= 3.1.0
- qrcode >= 7.4
- Pillow >= 10.0.0
- lxml >= 4.9.0

## Desarrollo

### Configuración del Entorno

```bash
# Clonar repositorio
git clone https://github.com/yourusername/cfdi-pdf.git
cd cfdi-pdf

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias de desarrollo
pip install -e ".[dev]"
```

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Con coverage
pytest --cov=cfdi_pdf --cov-report=html

# Tests específicos
pytest tests/test_parser.py
```

### Linting y Formateo

```bash
# Ruff (linter)
ruff check .
ruff check --fix .

# Black (formatter)
black .

# MyPy (type checker)
mypy src
```

### Build y Publicación

```bash
# Build
python -m build

# Publicar a PyPI (requiere credenciales)
twine upload dist/*
```

## Especificaciones Técnicas

### CFDI 4.0

- **Namespace**: `http://www.sat.gob.mx/cfd/4`
- **Timbre Fiscal Digital**: Versión 1.1
- **Catálogos SAT**: Completos y actualizados
- **Validación**: Estructura y tipos de datos

### QR SAT

URL de verificación: `https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx`

Parámetros:
- `id`: UUID del CFDI
- `re`: RFC del emisor
- `rr`: RFC del receptor
- `tt`: Total con 6 decimales (ej: 1234.560000)
- `fe`: Últimos 8 caracteres del sello digital

### Seguridad

- **Protección XXE**: Deshabilitadas entidades externas
- **XML Bombs**: Validación de tamaño y profundidad
- **Path Traversal**: Sanitización de rutas de archivos
- **Inyección de Templates**: Sandboxing de Jinja2

## Ejemplos Completos

Ver directorio `examples/` para ejemplos completos:

- `basic_usage.py` - Uso básico de la API
- `custom_template.py` - Creación de templates personalizados
- `batch_processing.py` - Procesamiento por lotes

## Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Lineamientos

- Mantén el coverage > 80%
- Sigue PEP 8 y usa Black para formateo
- Añade tests para nuevas funcionalidades
- Actualiza la documentación

## Licencia

MIT License - ver archivo [LICENSE](LICENSE) para detalles.

## Soporte

- **Issues**: [GitHub Issues](https://github.com/yourusername/cfdi-pdf/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/yourusername/cfdi-pdf/discussions)

## Roadmap

- [ ] Soporte para complementos (Pagos, Nómina, Carta Porte)
- [ ] Más templates profesionales
- [ ] Validación de esquemas XSD
- [ ] Generación de XML desde datos
- [ ] API REST
- [ ] Integración con PACs

## Agradecimientos

- SAT México por las especificaciones oficiales
- Comunidad de desarrolladores de CFDI
- Contribuidores del proyecto

---

**Nota**: Esta biblioteca no está afiliada oficialmente con el SAT. Úsala bajo tu propia responsabilidad y verifica siempre la validez de los CFDIs en el portal oficial.
