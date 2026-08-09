# Hallazgos (bugs y defectos)

Priorizados por severidad. Cada hallazgo incluye: descripción, evidencia,
impacto, fix sugerido y **estado** (✅ implementado en `develop` / ⬜ pendiente).

---

## 🔴 Alta

### H1. Cadena original del Timbre Fiscal incorrecta — ✅ Implementado

- **Dónde**: `src/cfdi_pdf/parser/xml_parser.py:327-343` (`_build_cadena_original`)
  y su fallback en `src/cfdi_pdf/sat/helpers.py:12-40`.
- **Problema**: El código construye la cadena original del TFD 1.1 como
  `||Version|UUID|FechaTimbrado|RfcProvCertif|SelloCFD|SelloSAT|NoCertificadoSAT||`
  **incluyendo `SelloSAT`**.
- **Evidencia**: La cadena oficial del SAT (`cadenaoriginal_TFD_1_1.xslt`) es:
  `||1.1|<UUID>|<FechaTimbrado>|<RfcProvCertif>|<SelloCFD>|<NoCertificadoSAT>||`
  — es decir, **sin `SelloSAT`**.
- **Impacto**: La cadena que se muestra en el PDF (variable `cadena_original`)
  es fiscalmente incorrecta. Si alguien intenta **verificar el sello** del CFDI
  contra esta cadena (re-hash SHA-256 + RSA), la verificación **fallará**.
  Además, el fallback `SATHelpers.build_cadena_original` construye una cadena
  *distinta* (la del Comprobante, no la del TFD), y ni siquiera se usa en el
  render normal (se prefiere `timbre_fiscal.cadena_origen`).
- **Fix sugerido**:
  ```python
  parts = [
      self._get_attr(tfd_elem, "Version"),
      self._get_attr(tfd_elem, "UUID"),
      self._get_attr(tfd_elem, "FechaTimbrado"),
      self._get_attr(tfd_elem, "RfcProvCertif"),
      self._get_attr(tfd_elem, "SelloCFD"),
      self._get_attr(tfd_elem, "NoCertificadoSAT"),
  ]
  return "||" + "|".join(parts) + "||"
  ```
  Idealmente usar la XSLT oficial del SAT y empaquetarla como recurso.

### H2. Campos opcionales de Pagos20 tratados como obligatorios — ✅ Implementado

- **Dónde**: `src/cfdi_pdf/parser/xml_parser.py:473-484` y `:489-495`.
- **Problema**: `EquivalenciaDR` (en `DoctoRelacionado`) y `TipoCambioP` (en
  `Pago`) se leen con `_get_decimal` (obligatorio). Según el Anexo 20:
  - `EquivalenciaDR` **solo debe existir** cuando `MonedaDR != MonedaP`.
  - `TipoCambioP` **solo debe existir** cuando `MonedaP != "MXN"`.
- **Impacto**: Se **rechazan CFDIs tipo P válidos** del SAT que omiten estos
  atributos (error `Missing required attribute: EquivalenciaDR`), justo los
  casos más comunes (pago en MXN con documento en MXN).
- **Fix sugerido**: Volverlos opcionales en el parser y en los modelos:
  ```python
  EquivalenciaDR: Decimal | None = Field(None, alias="EquivalenciaDR", ...)
  TipoCambioP: Decimal | None = Field(None, alias="TipoCambioP", ...)
  ```
  y en el parser usar `_get_optional_decimal`.

---

## 🟠 Media

### H3. Versión del paquete inconsistente (3 fuentes) — ✅ Implementado

- **Dónde**: `pyproject.toml:7` (`0.1.3`), `src/cfdi_pdf/__init__.py:15`
  (`0.1.0`), `src/cfdi_pdf/cli.py:103` (`0.1.0`).
- **Problema**: Hay **tres** definiciones de versión y están desincronizadas.
  El smoke test del CI (`python -c "import cfdi_pdf; print(cfdi_pdf.__version__)"`)
  imprimirá `0.1.0` aunque el wheel sea `0.1.3`.
- **Impacto**: Reportes de versión engañosos, soporte confuso, releases mal
  etiquetados.
- **Fix sugerido**: Fuente única de verdad en `pyproject.toml` y lectura en
  runtime:
  ```python
  # __init__.py
  from importlib.metadata import version, PackageNotFoundError
  try:
      __version__ = version("cfdi-pdf")
  except PackageNotFoundError:
      __version__ = "0.0.0+dev"
  ```
  Y en CLI: `parser.add_argument("--version", action="version",
  version=f"%(prog)s {__version__}")`.

### H4. Job de auditoría `pip-audit` del CI es un no-op — ✅ Implementado

- **Dónde**: `.github/workflows/ci.yml` (job `audit`).
- **Problema**:
  ```yaml
  pip-audit --desc -r <(pip-compile pyproject.toml --quiet 2>/dev/null || echo "")
  ```
  `pip-compile` **no está instalado** (solo se instala `pip-audit`). El
  `|| echo ""` oculta el error y se le pasa a `pip-audit` una lista de
  requisitos **vacía**.
- **Impacto**: La auditoría de vulnerabilidades de dependencias no audita nada,
  pero el job pasa y el release continúa — falsa sensación de seguridad.
- **Fix sugerido**: O instalar `pip-tools`, o auditar directo contra el entorno
  instalado:
  ```yaml
  - name: Install pip-audit
    run: pip install pip-audit pip-tools
  - name: Audit dependencies
    run: |
      pip-compile pyproject.toml --quiet -o /tmp/req.txt
      pip-audit --desc -r /tmp/req.txt
  ```

### H5. `int()` sin protección en `NumParcialidad` — ✅ Implementado

- **Dónde**: `src/cfdi_pdf/parser/xml_parser.py:477`.
  ```python
  NumParcialidad=int(self._get_attr(doc_elem, "NumParcialidad")),
  ```
- **Problema**: Si el atributo no es un entero (o es `"1.0"`), lanza
  `ValueError` crudo, que escapa como excepción genérica en vez de
  `InvalidCFDIError`.
- **Impacto**: API menos predecible; el resto de errores del parser sí se
  traducen a `InvalidCFDIError`.
- **Fix sugerido**: helper `_get_int` que use `int()` y convierta
  `ValueError` → `InvalidCFDIError`.

### H6. `_parse_pagos` descarta datos silenciosamente si falta `Totales` — ✅ Implementado

- **Dónde**: `src/cfdi_pdf/parser/xml_parser.py:429-431`.
  ```python
  totales_elem = pagos_elem.find(f"{{{PAGOS20_NS}}}Totales")
  if totales_elem is None:
      return None
  ```
- **Problema**: Si un XML trae `Pagos` (con `Pago`) pero sin `Totales`, el
  parser devuelve `None` y **pierde toda la información de pagos** sin aviso.
  En el render, el complemento simplemente no aparece.
- **Impacto**: CFDI tipo P renderizado incompleto silenciosamente.
- **Fix sugerido**: Distinguir "no hay complemento" (→ `None`) de "hay
  complemento mal formado" (→ lanzar `InvalidCFDIError("Missing Totales in
  Pagos complement")`).

### H7. `--version` de la CLI hardcodeado — ✅ Implementado

- **Dónde**: `src/cfdi_pdf/cli.py:100-104`.
  ```python
  parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
  ```
- **Impacto**: Mismo problema de H3 — la CLI reporta `0.1.0` mientras el
  paquete instalado es `0.1.3`.

---

## 🟡 Baja

### H8. `logger.warning(f"...")` con f-string — ✅ Implementado

- **Dónde**: `src/cfdi_pdf/render/template.py:34`.
  ```python
  logger.warning(f"Custom template path does not exist: {path}")
  ```
- **Problema**: Usa interpolación eager en vez de lazy (`%s`). No es bug
  funcional pero rompe la convención de logging y no está cubierto por la
  regla `G` de ruff.
- **Fix**: `logger.warning("Custom template path does not exist: %s", path)`.

### H9. README desactualizado en requisitos de lxml

- **Dónde**: `README.md:296` dice `lxml >= 4.9.0`; `pyproject.toml:46` exige
  `lxml>=5.0.0`. Además `README.md:361` menciona `tests/test_parser.py` (no
  existe; los tests son `test_parser.py` — sí existe). Verificar referencias.

### H10. Artifactos generados en el directorio raíz

- **Dónde**: `*.pdf`, `/*.xml`, `htmlcov/`, `.coverage`, `junit.xml` en la raíz.
- **Problema**: No están versionados (`.gitignore` correcto), pero ensucian el
  repo. Sugerencia: mover los PDFs de prueba a `tests/artifacts/` o un `tmp/`.

### H11. Atributos requeridos en el parser más estrictos que el XSD para tipo `P` — ✅ Implementado

- **Dónde**: `src/cfdi_pdf/parser/xml_parser.py:152` (`Certificado` vía
  `_get_attr`) y `:185-187` (`DomicilioFiscalReceptor`, `UsoCFDI`, etc.).
- **Problema**: En CFDI tipo `P`, el XSD define `Certificado` como opcional y
  el receptor de un pago puede no incluir `UsoCFDI`. El parser los exige
  siempre, lo que puede rechazar documentos `P` válidos de algunos PACs.
- **Fix sugerido**: Cuando `TipoDeComprobante == "P"`, leer `Certificado`,
  `DomicilioFiscalReceptor` y `UsoCFDI` como opcionales.

---

## No considerados bug (decisiones con riesgo documentado)

### D1. QR sin percent-encoding del parámetro `fe`

- `src/cfdi_pdf/qr/generator.py:113-133` construye la URL sin encoding, y el
  test `test_url_no_encoding` (`tests/test_qr.py:54-80`) lo fija como
  comportamiento intencional. Los últimos 8 chars del sello son base64 y pueden
  incluir `+/=`, que en un query string tienen significado especial. Es un
  **riesgo**: si el portal SAT no tolera esos caracteres, la verificación QR
  podría fallar para esos CFDI. Se recomienda validar contra el portal oficial
  y, si es necesario, aplicar `urllib.parse.quote` solo al valor de `fe`.

### D2. Cadena original "simplificada" de `SATHelpers.build_cadena_original`

- `src/cfdi_pdf/sat/helpers.py:12-40`. Es la del **Comprobante**, no la del TFD,
  y tampoco coincide con la XSLT oficial (la real incluye mucho más: emisor,
  receptor, conceptos, impuestos…). En el flujo normal no se usa (se usa
  `timbre_fiscal.cadena_origen`), pero es confusa. Considerar eliminarla o
  marcarla claramente como no-fiscal.
