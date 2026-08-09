# CFDI PDF - Guía de Seguridad

## Reportar Vulnerabilidades

**NO abras un issue público para vulnerabilidades de seguridad.**

Si descubres una vulnerabilidad de seguridad:

1. Envía un email a: jesusmarcos81@gmail.com
2. Incluye:
   - Descripción de la vulnerabilidad
   - Pasos para reproducirla
   - Posible impacto
   - Sugerencia de fix (si tienes)
3. Espera confirmación (24-48 horas)
4. No divulgues públicamente hasta que se publique el fix

## Medidas de Seguridad Implementadas

### 1. Protección contra XXE (XML External Entity)

```python
# Parser configurado para prevenir XXE
parser = etree.XMLParser(
    resolve_entities=False,  # No resuelve entidades externas
    no_network=True,         # Sin acceso a red
    dtd_validation=False     # Sin validación DTD
)
```

### 2. Sanitización UTF-8

- Validación de caracteres XML válidos
- Escape automático de caracteres especiales
- Manejo seguro de caracteres Unicode

### 3. Protección contra XML Bombs

- Límites de profundidad
- Validación de tamaño
- Timeout en parsing

### 4. Sandboxing de Templates

```python
# Jinja2 SandboxedEnvironment
env = SandboxedEnvironment(
    loader=loader,
    autoescape=True  # Escape automático de HTML
)
```

### 5. Validación de Rutas

- Prevención de path traversal
- Validación de archivos existentes
- Sanitización de nombres de archivo

### 6. Validación de Datos

- Pydantic para validación estricta
- Type hints en toda la API
- Validación de namespaces SAT

## Mejores Prácticas para Usuarios

### 1. Validar XML antes de procesar

```python
from cfdi_pdf import CFDIPDF

pdf = CFDIPDF()

try:
    cfdi = pdf.parse("factura.xml")
    # XML válido, proceder
except XMLParseError as e:
    # XML inválido, manejar error
    print(f"Error: {e}")
```

### 2. Usar rutas absolutas

```python
from pathlib import Path

# ✅ Bueno
output = Path("/tmp/output.pdf").resolve()
pdf.render(xml_path=xml_file, output=output)

# ❌ Evitar
output = "../../../etc/passwd"  # Path traversal risk
```

### 3. Validar origen del XML

```python
# Solo procesar XML de fuentes confiables
if not xml_path.startswith("/trusted/path"):
    raise SecurityError("Untrusted XML source")
```

### 4. Limitar tamaño de archivos

```python
MAX_SIZE = 10 * 1024 * 1024  # 10 MB

if xml_path.stat().st_size > MAX_SIZE:
    raise ValueError("File too large")
```

### 5. Sanitizar entrada de usuario

```python
# Si aceptas XML de usuarios, valida primero
import xml.etree.ElementTree as ET

try:
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Verificar namespace
    if not root.tag.startswith("{http://www.sat.gob.mx/cfd/4}"):
        raise ValueError("Invalid CFDI namespace")
        
except ET.ParseError:
    raise ValueError("Invalid XML")
```

## Dependencias de Seguridad

Mantenemos dependencias actualizadas:

- WeasyPrint: Última versión estable
- lxml: Con parches de seguridad
- Jinja2: Con SandboxedEnvironment
- Pydantic: Validación estricta

## Auditorías de Seguridad

El código es revisado regularmente para:

- Inyecciones XML
- Path traversal
- Template injection
- Desbordamientos
- Uso inseguro de APIs

## Responsabilidades del Usuario

El usuario es responsable de:

1. **Validar CFDIs**: Verificar validez en el portal del SAT
2. **Datos sensibles**: No incluir datos personales innecesarios
3. **Almacenamiento**: Guardar PDFs de forma segura
4. **Distribución**: Compartir solo con autorizados
5. **Backup**: Mantener respaldos seguros

## Compliance

### Datos Personales

CFDI PDF no:
- Almacena datos personales
- Envía datos a terceros
- Hace logging de contenido sensible
- Requiere conexión a internet

### SAT Compliance

- Sigue especificaciones oficiales del SAT
- Usa namespaces correctos
- Genera QR según especificación
- Respeta estructura del Anexo 20

## Actualizaciones de Seguridad

### Mantenerse Actualizado

```bash
# Actualizar a última versión
pip install --upgrade cfdi-pdf

# Verificar vulnerabilidades conocidas
pip-audit
```

### Notificaciones

- Suscríbete a releases en GitHub
- Sigue @cfdi_pdf en Twitter
- Revisa CHANGELOG.md regularmente

## Contacto de Seguridad

- **Email**: jesusmarcos81@gmail.com
- **PGP Key**: Disponible en keyservers
- **Respuesta**: 24-48 horas hábiles

## Reconocimientos

Agradecemos a quienes reportan vulnerabilidades de forma responsable. Los contribuyentes de seguridad serán reconocidos en:

- CHANGELOG.md
- SECURITY_HALL_OF_FAME.md
- Notas de release

---

**Última actualización**: 2026-02-18
**Versión**: 0.1.0
