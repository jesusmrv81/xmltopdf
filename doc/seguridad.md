# Análisis de seguridad

La biblioteca procesa XML **no confiable** (CFDIs de terceros/PACs) y lo
convierte a PDF, por lo que el parser y el render son la superficie de ataque
principal.

## Veredicto general

**Bueno.** Las protecciones fundamentales contra los ataques clásicos de XML
están presentes y son correctas. Hay un hallazgo menor y una recomendación de
endurecimiento.

## Controles existentes (verificados en código)

| Ataque | Control | Dónde | Estado |
|---|---|---|---|
| **XXE** (entidades externas) | `resolve_entities=False` | `xml_parser.py:115` | ✅ Correcto |
| **XML Bomb** (billion laughs) | `huge_tree=False`, `no_network=True`, `load_dtd=False` | `xml_parser.py:116-119` | ✅ Correcto |
| **DTD malicioso** | `dtd_validation=False`, `load_dtd=False` | `xml_parser.py:117-118` | ✅ Correcto |
| **Exfiltración de red** | `no_network=True` | `xml_parser.py:116` | ✅ Correcto |
| **Caracteres inválidos XML 1.0** | regex compilado `_INVALID_XML_CHARS.subn()` | `sanitizer.py:12-14, 55` | ✅ Correcto |
| **XSS / inyección en templates** | `SandboxedEnvironment` + `select_autoescape(["html","xml"])` | `template.py:44-49` | ✅ Correcto |
| **Código arbitrario en templates** | Sandbox de Jinja2 | `template.py:44` | ✅ Correcto |
| **Logo malicioso** | Solo se embebe como `data:` URL base64; nunca se ejecuta | `engine.py:149-163` | ✅ Correcto |
| **Acceso a rutas** | `logo_path` solo se lee si existe y es archivo legible | `engine.py:154-157` | ✅ Correcto |
| **Templates personalizados** | `FileSystemLoader` sobre rutas explícitas; búsqueda de `template.html` | `template.py:45, 64-73` | ✅ Correcto |

## Riesgos residuales

### R1. `recover=True` en el parser lxml (Menor)

- `xml_parser.py:120` habilita `recover=True`, que hace que lxml **recupere**
  XMLs malformados omitiendo partes inválidas en vez de fallar.
- **Riesgo**: Un XML parcialmente corrupto puede parsearse "exitosamente" con
  datos incompletos, y el PDF resultante mostraría información fiscal
  incorrecta sin que nadie se dé cuenta.
- **Recomendación**: Valorar `recover=False` (default seguro) para que XMLs
  malformados fallen ruidosamente. Si se mantiene `recover=True`, al menos
  loggear un warning cuando lxml reporte recuperación de errores (se puede
  capturar con `error_log` del parser).

### R2. Parser más permisivo de lo declarado (Menor)

- El README afirma "Protección contra XXE, XML bombs y otros ataques" — es
  cierto. Pero `_parse_complementos` (`xml_parser.py:508-544`) convierte
  complementos desconocidos a `dict` sin validar su contenido. Es solo para
  render, así que el riesgo es bajo.

### R3. Cadena original incorrecta (No es vulnerabilidad, es integridad)

- Ver [hallazgos.md H1](hallazgos.md#h1-cadena-original-del-timbre-fiscal-incorrecta).
  No es un ataque, pero un PDF que muestre una cadena original inválida puede
  inducir a error en una revisión manual de integridad fiscal.

### R4. QR sin encoding (Riesgo de funcionalidad, no de seguridad)

- Ver [hallazgos.md D1](hallazgos.md#d1-qr-sin-percent-encoding-del-parámetro-fe).

## Recomendaciones de endurecimiento

1. ✅ **`recover=False`** en el parser lxml — un XML malformado ahora **falla
   ruidosamente** (`XMLParseError`) en vez de parsearse parcialmente. Un XML
   corrupto ya no puede generar un PDF con datos fiscales incompletos.
2. **Limitar tamaño máximo de XML** antes de parsear (p.ej. 10 MB) para blindar
   contra DoS de memoria más allá de `huge_tree=False` (que protege el árbol,
   no el input completo).
3. **Validar la `data:` URL del logo**: hoy se acepta cualquier extensión con
   fallback a `image/png`. Restringir extensiones a un allowlist y opcionalmente
   verificar la firma del archivo (magic bytes).
4. **Considerar límite de tamaño del logo** para evitar PDFs gigantes por
   logos de MB.
5. **Pin de dependencias con hash** (`pip-audit` real — ver
   [hallazgos.md H4](hallazgos.md#h4-job-de-auditoría-pip-audit-del-ci-es-un-no-op)),
   y añadir `pip-audit` a PRs.
6. **Revisar `SECURITY.md`** existente: tiene proceso de reporte; añadir una
   sección de "superficie de ataque" para consumidores que integren la lib con
   XML no confiable.

## Validación de integridad disponible

- **Cadena original**: el parser calcula la cadena del comprobante y del TFD
  con los XSLT oficiales del SAT (`cfdi_pdf/sat/cadena_original.py`).
- **Verificación de sellos**: `SelloVerifier.verify_sello_cfd` (certificado
  embebido) y `SelloVerifier.verify_sello_sat` (certificado SAT provisto por el
  usuario). La verificación de `SelloSAT` no viene "de fábrica" porque el
  certificado del SAT no está embebido en el XML; se debe suministrar.
- **Validación estructural**: `validate_xsd=True` valida contra `cfdv40.xsd`
  (incluye catálogos oficiales) en el parser y en `CFDIPDF`.

## Procedencia de los recursos del SAT (XSLT/XSD)

Los recursos **no se empaquetan** en la biblioteca; se descargan en runtime
(`cfdi_pdf/sat/resources.py`) y se cachean en disco (`~/.cache/cfdi-pdf`).
Esto evita inflar el paquete y permite absorber las actualizaciones del SAT.

**Verificación de integridad**: cada descarga se compara contra un **manifiesto
SHA-256 empaquetado**. El hash se calcula sobre una *forma canónica* (saltos de
línea normalizados y sin salto final). El manifiesto se generó descargando los
**38 recursos directamente del SAT** (`www.sat.gob.mx/sitio_internet/cfd`) el
2026-08-09 y verificando que la fuente secundaria los reproduzca.

**Fuentes (en orden)**: primero el **SAT oficial**; si no responde (el SAT
bloquea geo-físicamente algunas regiones) se usa un **mirror verificado**
(`phpcfdi/resources-sat-xml`), que es copia fiel del árbol del SAT. Se
configuran/desactivan con la variable `CFDI_PDF_BASE_URLS`.

**Adaptaciones documentadas** (única diferencia entre el SAT y el mirror):
- `cadenaoriginal_4_0.xslt`: el original del SAT usa `xsl:include` con URLs
  absolutas y `version="2.0"`; el mirror las convierte a rutas relativas y
  reordena el atributo `version`. El canonicalizador aplica esa transformación
  al contenido del SAT, de modo que **ambas fuentes convergen al mismo hash**.
- `cfdv40.xsd`: el mirror relativiza los `schemaLocation`; el canonicalizador
  los devuelve a la forma absoluta del SAT.

**Si el SAT actualiza un archivo** (el hash ya no coincide con el manifiesto)
se lanza `SATResourceError` con el hash nuevo; así se detecta el cambio en vez
de usar contenido no verificado. Para re-sincronizar el manifiesto, se actualiza
`MANIFEST` en `resources.py` siguiendo el proceso descrito en `doc/analisis.md`.

**Variables de entorno**:
| Variable | Efecto |
|---|---|
| `CFDI_PDF_CACHE_DIR` | Directorio de caché (por defecto `~/.cache/cfdi-pdf`) |
| `CFDI_PDF_BASE_URLS` | Lista de URLs base separadas por comas (SAT, mirror o fuente propia) |
| `CFDI_PDF_ALLOW_UNVERIFIED=1` | Desactiva la verificación SHA-256 (no recomendado) |

## Suministro de dependencias

Dependencias de runtime: `pydantic`, `Jinja2`, `WeasyPrint`, `qrcode[pil]`,
`Pillow`, `lxml`. Todas son de mantenimiento activo. El riesgo principal de
cadena de suministro está en `WeasyPrint` (C de Pango/Cairo en runtime del
deploy), no en Python. Documentar en la doc de despliegue la necesidad de las
librerías de sistema (ya presente en `ci.yml`).
