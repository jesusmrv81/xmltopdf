# Contributing to CFDI PDF

¡Gracias por tu interés en contribuir a CFDI PDF! Este documento proporciona las pautas para contribuir al proyecto.

## Código de Conducta

Este proyecto sigue un código de conducta basado en el respeto y la colaboración. Esperamos que todos los contribuyentes lo sigan.

## ¿Cómo Contribuir?

### Reportar Bugs

Si encuentras un bug:

1. Verifica si ya existe un issue reportado
2. Si no existe, crea uno nuevo con:
   - Descripción clara del problema
   - Pasos para reproducirlo
   - Comportamiento esperado vs actual
   - Versión de Python y sistema operativo
   - XML de ejemplo (si aplica, sin datos sensibles)

### Sugerir Mejoras

Las sugerencias son bienvenidas:

1. Crea un issue describiendo la mejora
2. Explica el caso de uso
3. Si es posible, incluye ejemplos de código

### Contribuir con Código

#### Configuración del Entorno

```bash
# Fork y clona el repositorio
git clone https://github.com/tu-usuario/cfdi-pdf.git
cd cfdi-pdf

# Crea una rama para tu feature
git checkout -b feature/nombre-descriptivo

# Instala dependencias de desarrollo
pip install -e ".[dev]"
```

#### Desarrollo

1. **Escribe código limpio y documentado**
   - Sigue PEP 8
   - Usa type hints
   - Documenta funciones y clases

2. **Añade tests**
   - Coverage mínimo: 80%
   - Tests unitarios y de integración
   - Usa fixtures para datos de prueba

3. **Ejecuta las verificaciones**
   ```bash
   # Linting
   ruff check .
   ruff format --check .
   
   # Type checking
   mypy src
   
   # Tests
   pytest --cov=cfdi_pdf
   ```

#### Commits

Usa mensajes de commit descriptivos:

```
<tipo>(<alcance>): <descripción corta>

<descripción larga>

<notas adicionales>
```

Tipos:
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Documentación
- `style`: Formato (sin cambios de código)
- `refactor`: Refactorización
- `test`: Añadir o modificar tests
- `chore`: Mantenimiento

Ejemplos:
```
feat(parser): añadir soporte para CFDI 3.3

Implementar parser para versión 3.3 con validación
de namespaces y estructura según Anexo 20.

Closes #42
```

```
fix(qr): corregir formato de total en QR SAT

El total debe tener exactamente 6 decimales según
especificación oficial del SAT.

Fixes #15
```

#### Pull Requests

1. **Actualiza tu rama con main**
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Verifica que todo funcione**
   ```bash
   pytest
   mypy src
   ruff check .
   ```

3. **Crea el Pull Request**
   - Título descriptivo
   - Descripción de los cambios
   - Referencia a issues relacionados
   - Screenshots si aplica (para templates)

4. **Responde a revisiones**
   - Atiende comentarios
   - Haz cambios solicitados
   - Mantén la conversación

## Guías de Estilo

### Python

- **Formato**: Black (configurado en `pyproject.toml`)
- **Linter**: Ruff
- **Type hints**: Obligatorio en código público
- **Docstrings**: Google style

Ejemplo:
```python
def render_cfdi(
    xml_path: str | Path,
    output: str | Path,
    template: str = "minimal"
) -> bytes | None:
    """
    Convierte un CFDI XML a PDF.
    
    Args:
        xml_path: Ruta al archivo XML del CFDI.
        output: Ruta de salida del PDF.
        template: Nombre del template a usar.
    
    Returns:
        Bytes del PDF si output es None, None si se guardó a archivo.
    
    Raises:
        XMLParseError: Si el XML es inválido.
        TemplateNotFoundError: Si el template no existe.
    
    Example:
        >>> pdf_bytes = render_cfdi("factura.xml", "factura.pdf")
    """
    pass
```

### Templates HTML/CSS

- HTML5 válido
- CSS moderno (flexbox, grid)
- Responsive design
- Accesibilidad básica
- Comentarios para secciones complejas

### Tests

```python
def test_parse_valid_cfdi():
    """Test parsing de CFDI válido."""
    xml = load_fixture("valid_cfdi.xml")
    cfdi = parser.parse(xml)
    
    assert cfdi.version == "4.0"
    assert cfdi.uuid is not None
```

## Estructura del Proyecto

```
cfdi_pdf/
├── api.py              # API pública
├── cli.py              # CLI
├── exceptions.py       # Excepciones
├── models/            # Modelos Pydantic
├── parser/            # Parser XML
├── qr/                # Generador QR
├── render/            # Motor de renderizado
├── sat/               # Catálogos SAT
├── utils/             # Utilidades
└── templates/         # Templates incluidos
```

## Añadir Nuevos Templates

1. Crea directorio en `src/cfdi_pdf/templates/`
2. Añade `template.html` y `styles.css`
3. Sigue el template `minimal` como referencia
4. Añade tests para el nuevo template
5. Documenta en README

## Añadir Catálogos SAT

1. Edita `src/cfdi_pdf/sat/catalogs.py`
2. Añade el catálogo como diccionario
3. Añade función helper
4. Actualiza tests

## Publicación

El proceso de publicación es automático:

1. Actualiza versión en `pyproject.toml`
2. Actualiza `CHANGELOG.md`
3. Crea tag: `git tag -a v0.2.0 -m "Release v0.2.0"`
4. Push tag: `git push origin v0.2.0`
5. GitHub Actions publicará a PyPI

## Preguntas Frecuentes

### ¿Puedo añadir soporte para CFDI 3.3?

Sí, pero como feature opcional. El foco principal es CFDI 4.0.

### ¿Puedo usar otra librería de PDF?

WeasyPrint es la elección por su calidad y soporte CSS. Discute alternativas en un issue primero.

### ¿Cómo añado un complemento (Pagos, Nómina, etc.)?

1. Crea modelo en `models/`
2. Extiende el parser
3. Actualiza templates
4. Añade tests
5. Documenta

## Contacto

- Issues: Para bugs y features
- Discussions: Para preguntas generales
- Email: Para temas sensibles de seguridad

## Licencia

Al contribuir, aceptas que tus contribuciones se licencien bajo MIT License.

---

¡Gracias por contribuir! 🎉
