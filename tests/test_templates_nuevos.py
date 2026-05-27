"""Tests for templates 'corporativo' and 'clasico'."""

import re
import tempfile
from pathlib import Path

import pytest

from cfdi_pdf import CFDIPDF

CSS_EXPERIMENTAL_PATTERNS = [
    # CSS variables — el lookbehind variable-width no es soportado en Python re;
    # la detección de comentarios se hace en _get_css_lines_without_comments antes
    # de aplicar estos patrones, por eso aquí basta con buscar "var(--" directamente.
    (r"\bvar\(--", "CSS variables (var(--)"),
    # CSS Grid activo (no en comentarios)
    (r"^\s*display\s*:\s*grid\s*;", "display: grid"),
    # Container queries
    (r"@container\b", "@container query"),
    # CSS Layers
    (r"@layer\b", "@layer"),
    # :has() selector
    (r":has\(", ":has() selector"),
    # aspect-ratio activo
    (r"^\s*aspect-ratio\s*:", "aspect-ratio"),
    # backdrop-filter activo
    (r"^\s*backdrop-filter\s*:", "backdrop-filter"),
    # clip-path activo
    (r"^\s*clip-path\s*:", "clip-path"),
    # CSS subgrid
    (r"grid-template[^:]*:\s*subgrid", "CSS subgrid"),
    # animation activa
    (r"^\s*animation\s*:", "animation"),
    # transition activa
    (r"^\s*transition\s*:", "transition"),
]

TEMPLATES_DIR = Path(__file__).parent.parent / "src" / "cfdi_pdf" / "templates"


def _get_css_lines_without_comments(css_text: str) -> list[str]:
    """Elimina comentarios /* */ del CSS y retorna líneas activas."""
    # Eliminar bloques /* ... */
    no_comments = re.sub(r"/\*.*?\*/", "", css_text, flags=re.DOTALL)
    return no_comments.splitlines()


class TestTemplateCorporativo:
    """Tests para el template 'corporativo'."""

    def test_template_files_exist(self) -> None:
        """Verifica que los archivos del template existen."""
        template_dir = TEMPLATES_DIR / "corporativo"
        assert (template_dir / "template.html").exists(), "template.html no encontrado"
        assert (template_dir / "styles.css").exists(), "styles.css no encontrado"

    def test_template_listed(self) -> None:
        """El template 'corporativo' debe aparecer en list_templates()."""
        pdf = CFDIPDF()
        assert "corporativo" in pdf.list_templates()

    def test_render_produces_pdf(self, valid_cfdi_40_xml: str) -> None:
        """Renderizar con template corporativo debe producir un PDF válido."""
        pdf = CFDIPDF(template="corporativo")
        with tempfile.TemporaryDirectory() as tmpdir:
            result = pdf.render_from_string(valid_cfdi_40_xml, output_dir=tmpdir)
            content = result.read_bytes()
            assert content.startswith(b"%PDF"), "El resultado no es un PDF válido"

    def test_render_with_retenciones(self, cfdi_with_retenciones_xml: str) -> None:
        """Template corporativo debe manejar CFDI con retenciones."""
        pdf = CFDIPDF(template="corporativo")
        with tempfile.TemporaryDirectory() as tmpdir:
            result = pdf.render_from_string(cfdi_with_retenciones_xml, output_dir=tmpdir)
            assert result.read_bytes().startswith(b"%PDF")

    def test_render_with_special_chars(self, cfdi_with_special_chars_xml: str) -> None:
        """Template corporativo debe manejar caracteres especiales."""
        pdf = CFDIPDF(template="corporativo")
        with tempfile.TemporaryDirectory() as tmpdir:
            result = pdf.render_from_string(cfdi_with_special_chars_xml, output_dir=tmpdir)
            assert result.read_bytes().startswith(b"%PDF")

    def test_render_to_file(self, valid_cfdi_40_xml: str) -> None:
        """Template corporativo debe escribir PDF a archivo nombrado por UUID."""
        pdf = CFDIPDF(template="corporativo")

        with tempfile.TemporaryDirectory() as tmpdir:
            xml_path = Path(tmpdir) / "test.xml"
            xml_path.write_text(valid_cfdi_40_xml)

            result = pdf.render(xml_path=xml_path, output_dir=tmpdir)

            assert isinstance(result, Path)
            assert result.exists()
            assert result.suffix == ".pdf"
            assert result.stat().st_size > 0

    @pytest.mark.parametrize("pattern,name", CSS_EXPERIMENTAL_PATTERNS)
    def test_no_experimental_css(self, pattern: str, name: str) -> None:
        """El CSS del template corporativo no debe contener propiedades experimentales."""
        css_path = TEMPLATES_DIR / "corporativo" / "styles.css"
        css_text = css_path.read_text(encoding="utf-8")
        active_lines = _get_css_lines_without_comments(css_text)

        for line in active_lines:
            assert not re.search(pattern, line), (
                f"Propiedad experimental encontrada en corporativo/styles.css: "
                f"'{name}' en línea: {line.strip()!r}"
            )

    def test_css_uses_table_layout_for_parties(self) -> None:
        """El layout de emisor/receptor debe ser tabla HTML, no grid/flex."""
        html_path = TEMPLATES_DIR / "corporativo" / "template.html"
        html_text = html_path.read_text(encoding="utf-8")

        # Debe tener una tabla para emisor/receptor
        assert "parties-table" in html_text
        assert "<table" in html_text

    def test_html_has_required_jinja2_vars(self) -> None:
        """El template HTML debe usar las variables de contexto estándar."""
        html_path = TEMPLATES_DIR / "corporativo" / "template.html"
        html_text = html_path.read_text(encoding="utf-8")

        required_vars = [
            "formatted.uuid",
            "formatted.fecha",
            "formatted.total",
            "cfdi.emisor.nombre",
            "cfdi.receptor.nombre",
            "cfdi.emisor.rfc",
            "cfdi.receptor.rfc",
            "catalogs.tipo_comprobante",
            "catalogs.forma_pago",
            "catalogs.uso_cfdi",
            "qr_data",
        ]
        for var in required_vars:
            assert var in html_text, f"Variable Jinja2 requerida ausente: {var}"


class TestTemplateClasico:
    """Tests para el template 'clasico'."""

    def test_template_files_exist(self) -> None:
        """Verifica que los archivos del template existen."""
        template_dir = TEMPLATES_DIR / "clasico"
        assert (template_dir / "template.html").exists(), "template.html no encontrado"
        assert (template_dir / "styles.css").exists(), "styles.css no encontrado"

    def test_template_listed(self) -> None:
        """El template 'clasico' debe aparecer en list_templates()."""
        pdf = CFDIPDF()
        assert "clasico" in pdf.list_templates()

    def test_render_produces_pdf(self, valid_cfdi_40_xml: str) -> None:
        """Renderizar con template clasico debe producir un PDF válido."""
        pdf = CFDIPDF(template="clasico")
        with tempfile.TemporaryDirectory() as tmpdir:
            result = pdf.render_from_string(valid_cfdi_40_xml, output_dir=tmpdir)
            content = result.read_bytes()
            assert content.startswith(b"%PDF"), "El resultado no es un PDF válido"

    def test_render_with_retenciones(self, cfdi_with_retenciones_xml: str) -> None:
        """Template clasico debe manejar CFDI con retenciones."""
        pdf = CFDIPDF(template="clasico")
        with tempfile.TemporaryDirectory() as tmpdir:
            result = pdf.render_from_string(cfdi_with_retenciones_xml, output_dir=tmpdir)
            assert result.read_bytes().startswith(b"%PDF")

    def test_render_with_special_chars(self, cfdi_with_special_chars_xml: str) -> None:
        """Template clasico debe manejar caracteres especiales."""
        pdf = CFDIPDF(template="clasico")
        with tempfile.TemporaryDirectory() as tmpdir:
            result = pdf.render_from_string(cfdi_with_special_chars_xml, output_dir=tmpdir)
            assert result.read_bytes().startswith(b"%PDF")

    def test_render_to_file(self, valid_cfdi_40_xml: str) -> None:
        """Template clasico debe escribir PDF a archivo nombrado por UUID."""
        pdf = CFDIPDF(template="clasico")

        with tempfile.TemporaryDirectory() as tmpdir:
            xml_path = Path(tmpdir) / "test.xml"
            xml_path.write_text(valid_cfdi_40_xml)

            result = pdf.render(xml_path=xml_path, output_dir=tmpdir)

            assert isinstance(result, Path)
            assert result.exists()
            assert result.suffix == ".pdf"
            assert result.stat().st_size > 0

    @pytest.mark.parametrize("pattern,name", CSS_EXPERIMENTAL_PATTERNS)
    def test_no_experimental_css(self, pattern: str, name: str) -> None:
        """El CSS del template clasico no debe contener propiedades experimentales."""
        css_path = TEMPLATES_DIR / "clasico" / "styles.css"
        css_text = css_path.read_text(encoding="utf-8")
        active_lines = _get_css_lines_without_comments(css_text)

        for line in active_lines:
            assert not re.search(pattern, line), (
                f"Propiedad experimental encontrada en clasico/styles.css: "
                f"'{name}' en línea: {line.strip()!r}"
            )

    def test_css_no_flexbox_no_grid(self) -> None:
        """El clasico debe ser 100% layout con tablas, sin flex ni grid activos."""
        css_path = TEMPLATES_DIR / "clasico" / "styles.css"
        css_text = css_path.read_text(encoding="utf-8")
        active_lines = _get_css_lines_without_comments(css_text)

        for line in active_lines:
            assert not re.search(r"display\s*:\s*(flex|grid)\s*;", line), (
                f"flex/grid encontrado en clasico/styles.css (solo tablas permitidas): {line.strip()!r}"
            )

    def test_css_no_border_radius(self) -> None:
        """El clasico no debe usar border-radius."""
        css_path = TEMPLATES_DIR / "clasico" / "styles.css"
        css_text = css_path.read_text(encoding="utf-8")
        active_lines = _get_css_lines_without_comments(css_text)

        for line in active_lines:
            assert not re.search(r"border-radius\s*:", line), (
                f"border-radius encontrado en clasico/styles.css: {line.strip()!r}"
            )

    def test_html_no_nth_child_in_tables(self) -> None:
        """El HTML del clasico debe usar clases explícitas para zebra, no :nth-child."""
        css_path = TEMPLATES_DIR / "clasico" / "styles.css"
        css_text = css_path.read_text(encoding="utf-8")
        active_lines = _get_css_lines_without_comments(css_text)

        for line in active_lines:
            assert ":nth-child" not in line, (
                f":nth-child encontrado en clasico/styles.css (usar .row-odd/.row-even): {line.strip()!r}"
            )

    def test_html_has_required_jinja2_vars(self) -> None:
        """El template HTML debe usar las variables de contexto estándar."""
        html_path = TEMPLATES_DIR / "clasico" / "template.html"
        html_text = html_path.read_text(encoding="utf-8")

        required_vars = [
            "formatted.uuid",
            "formatted.fecha",
            "formatted.total",
            "cfdi.emisor.nombre",
            "cfdi.receptor.nombre",
            "cfdi.emisor.rfc",
            "cfdi.receptor.rfc",
            "catalogs.tipo_comprobante",
            "catalogs.forma_pago",
            "catalogs.uso_cfdi",
            "qr_data",
        ]
        for var in required_vars:
            assert var in html_text, f"Variable Jinja2 requerida ausente: {var}"

    def test_html_zebra_uses_explicit_classes(self) -> None:
        """La tabla de conceptos debe usar .row-odd y .row-even, no :nth-child."""
        html_path = TEMPLATES_DIR / "clasico" / "template.html"
        html_text = html_path.read_text(encoding="utf-8")

        assert "row-odd" in html_text, "Clase .row-odd no encontrada en clasico/template.html"
        assert "row-even" in html_text, "Clase .row-even no encontrada en clasico/template.html"


class TestAllTemplatesCompatibility:
    """Tests de compatibilidad aplicados a todos los templates incluyendo minimal."""

    @pytest.mark.parametrize("template_name", ["minimal", "corporativo", "clasico"])
    def test_template_renders_valid_pdf(self, template_name: str, valid_cfdi_40_xml: str) -> None:
        """Todos los templates deben producir PDFs válidos."""
        pdf = CFDIPDF(template=template_name)
        with tempfile.TemporaryDirectory() as tmpdir:
            result = pdf.render_from_string(valid_cfdi_40_xml, output_dir=tmpdir)
            content = result.read_bytes()
            assert content.startswith(b"%PDF"), (
                f"Template '{template_name}' no produjo un PDF válido"
            )

    @pytest.mark.parametrize("template_name", ["corporativo", "clasico"])
    def test_template_css_has_page_rule(self, template_name: str) -> None:
        """Todos los templates deben definir @page con tamaño carta (letter)."""
        css_path = TEMPLATES_DIR / template_name / "styles.css"
        css_text = css_path.read_text(encoding="utf-8")

        assert "@page" in css_text, f"@page ausente en {template_name}/styles.css"
        assert "letter" in css_text, (
            f"Tamaño carta (letter) no definido en {template_name}/styles.css"
        )

    @pytest.mark.parametrize("template_name", ["corporativo", "clasico"])
    def test_template_css_has_print_color_adjust(self, template_name: str) -> None:
        """Todos los templates deben declarar print-color-adjust para fondos de color."""
        css_path = TEMPLATES_DIR / template_name / "styles.css"
        css_text = css_path.read_text(encoding="utf-8")

        assert "print-color-adjust" in css_text, (
            f"print-color-adjust ausente en {template_name}/styles.css"
        )

    @pytest.mark.parametrize("template_name", ["corporativo", "clasico"])
    def test_template_css_no_css_variables(self, template_name: str) -> None:
        """Los templates no deben usar CSS custom properties (--var) en código activo."""
        css_path = TEMPLATES_DIR / template_name / "styles.css"
        css_text = css_path.read_text(encoding="utf-8")
        active_lines = _get_css_lines_without_comments(css_text)

        for line in active_lines:
            # Buscar "var(--" en líneas activas (no en comentarios)
            assert "var(--" not in line, (
                f"CSS variable encontrada en {template_name}/styles.css: {line.strip()!r}"
            )
