# Calidad de código, tests y CI

Estado verificado el 2026-08-09 en la rama `develop` con `venv/`.

## Estado actual

| Herramienta | Comando | Resultado |
|---|---|---|
| Tests | `pytest` | ✅ **114 passed** (~45 s) |
| Lint | `ruff check src tests` | ✅ Sin errores |
| Formato | `ruff format --check .` | ✅ (CI) |
| Tipos | `mypy src` (strict) | ✅ 25 archivos sin errores |
| Cobertura | `pytest --cov=cfdi_pdf` | ⚠️ **77%** (umbral CI: 70%) |

## Cobertura por módulo

| Módulo | Cobertura | Comentario |
|---|---|---|
| `models/*` | 100% | ✅ Modelos totalmente cubiertos |
| `__init__.py` (raíz) | 100% | ✅ |
| `parser/__init__`, `qr/__init__`, `render/__init__`, `sat/__init__`, `utils/__init__` | 100% | ✅ |
| `sat/catalogs.py` | 95% | Faltan 2 getters (`get_forma_pago_p`, `get_objeto_impuesto`) |
| `utils/formatters.py` | 80% | Faltan `format_percentage`, casos de error de fecha/truncate |
| `qr/generator.py` | 82% | Faltan paths de error (`_validate_inputs` parcial, `_format_total` inválido) |
| `api.py` | 82% | Faltan wraps de error genérico y casos `output_dir=None` |
| `parser/sanitizer.py` | 79% | Faltan warnings (emojis, conteo de chars inválidos) |
| `parser/xml_parser.py` | 75% | Pagos edge-cases, retenciones comprobante, errores decimales |
| `render/engine.py` | 72% | Faltan fallos de QR/logo/template → warnings y `except` |
| `render/template.py` | 64% | Faltan path inexistente, template no encontrado, list_templates |
| `sat/helpers.py` | 48% | Faltan `build_cadena_original` y `truncate_sello_for_qr` |
| `exceptions.py` | 81% | Falta `__str__` con details |
| **`cli.py`** | **0%** | 🔴 **Sin tests** — prioridad (ver [mejoras.md](mejoras.md#6)) |

> `cli.py` con 0% es la mayor brecha. Como es una pieza pública del paquete
> (`project.scripts`), debería tener al menos smoke tests.

## Suites de tests existentes

| Archivo | Cubre |
|---|---|
| `test_api.py` | `render`, `render_from_string`, `render_bytes`, `parse`, `list_templates` |
| `test_parser.py` | parseo de fixtures, errores de XML, CFDI 4.0 |
| `test_pagos.py` | Complemento de Pago 2.0 (múltiples, retenciones, timbre) |
| `test_qr.py` | generación, total a 6 decimales, validación de inputs |
| `test_catalogs.py` | catálogos SAT |
| `test_formatters.py` | moneda, tasa, fecha, UUID |
| `test_sanitizer.py` | sanitización XML |
| `test_templates_nuevos.py` | 50+ casos: CSS por motor, variables Jinja2, compatibilidad |

Fixtures XML: `tests/fixtures/{pagos20_multiple,pagos20_retenciones,sample_cfdi}.xml`
+ XMLs embebidos en `conftest.py`.

## CI/CD (`.github/workflows/ci.yml`)

**Buen diseño general:**

- Matrix Python 3.12/3.13 en push a `main` y PRs.
- Lint (`ruff`), formato (`ruff format --check`), tipos (`mypy src`).
- Tests con `--cov-fail-under=70`.
- Cobertura → Codecov (XML + junit).
- Release automático: build → `twine check --strict` → smoke test → tag → GH
  Release → PyPI con **OIDC (Trusted Publishing)** — sin tokens.
- Dependabot configurado con acciones pinneadas a SHA.

**Problemas encontrados:**

1. 🔴 **`pip-audit` es un no-op** — ver [hallazgos.md H4](hallazgos.md#h4-job-de-auditoría-pip-audit-del-ci-es-un-no-op).
2. 🟡 El smoke test del release imprime `cfdi_pdf.__version__` = `0.1.0`,
   que no coincide con la versión del wheel (ver
   [hallazgos.md H3](hallazgos.md#h3-versión-del-paquete-inconsistente-3-fuentes)).
3. 🟡 El job `audit` solo corre en push a `main`; no audita PRs.
4. 🟡 La acción `cache-apt-pkgs-action@v1.6.0` cachea paquetes apt del sistema
   para WeasyPrint — si el runner cambia de distro, podría usar caché inválida
   (riesgo bajo).
5. 🟡 `CODECOV_TOKEN` usado en `codecov-action@v5` con `fail_ci_if_error: false`
   — un fallo de subida no bloquea, aceptable.

## Configuración de calidad en `pyproject.toml`

- **mypy**: `strict=true` con opciones agresivas (`disallow_untyped_defs`,
  `warn_unreachable`, etc.). Excelente.
- **ruff**: `line-length=100`, reglas `E, W, F, I, N, UP, B, C4, SIM, TCH, RUF`.
  Sugerencia: añadir `G` (logging-format), `PIE`, `PT` (pytest-style) y
  `YTT` (single source of truth de versiones) para reforzar.
- **pytest**: `addopts` con `--strict-markers` y coverage por defecto. Bien.
- **coverage**: `branch=true` y `exclude_lines` para `__repr__`/`NotImplemented`.

## Recomendaciones de calidad

1. **Tests para `cli.py`** (0% → objetivo >70%).
2. Subir `--cov-fail-under` de 70 a 80 una vez cubierta la CLI.
3. Añadir **pre-commit** (ruff + mypy + black) para aplicar los mismos checks
   que el CI localmente.
4. Añadir **métricas de complejidad** (ej. `radon cc -s -a`) y un documento de
   referencia de arquitectura (`ADR`) para las decisiones de diseño listadas en
   [analisis.md](analisis.md).
5. Considerar **`pip-tools` / `uv` lock** para reproducibilidad de dev/CI.
6. Añadir `ruff` rule `G` y `T20` (print) — hay `print()` en `cli.py` (correcto
   para CLI, pero la regla `T201` ayudaría a evitar `print` fuera de ella).
