"""Template manager for CFDI PDF."""

import logging
from pathlib import Path

from jinja2 import FileSystemLoader, Template, select_autoescape
from jinja2.sandbox import SandboxedEnvironment

from ..exceptions import TemplateNotFoundError

logger = logging.getLogger(__name__)


class TemplateManager:
    """Manages Jinja2 templates for PDF rendering."""

    BUILTIN_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

    def __init__(self, custom_template_paths: list[Path] | None = None) -> None:
        """
        Initialize template manager.

        Args:
            custom_template_paths: Additional paths to search for templates
        """
        self._template_paths: list[Path] = []

        # Add custom paths first (higher priority)
        if custom_template_paths:
            for path in custom_template_paths:
                if path.exists() and path.is_dir():
                    self._template_paths.append(path)
                else:
                    logger.warning(f"Custom template path does not exist: {path}")

        # Add built-in templates
        if self.BUILTIN_TEMPLATES_DIR.exists():
            self._template_paths.append(self.BUILTIN_TEMPLATES_DIR)

        if not self._template_paths:
            raise TemplateNotFoundError("No template directories found")

        # Create sandboxed Jinja2 environment
        self._env = SandboxedEnvironment(
            loader=FileSystemLoader([str(p) for p in self._template_paths]),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def get_template(self, template_name: str) -> Template:
        """
        Get Jinja2 template by name.

        Args:
            template_name: Template name (e.g., "minimal")

        Returns:
            Jinja2 Template object

        Raises:
            TemplateNotFoundError: If template not found
        """
        # Try to find template.html in the template directory
        template_path = f"{template_name}/template.html"

        try:
            return self._env.get_template(template_path)
        except Exception as e:
            raise TemplateNotFoundError(
                f"Template '{template_name}' not found. "
                f"Searched in: {[str(p) for p in self._template_paths]}"
            ) from e

    def template_exists(self, template_name: str) -> bool:
        """Check if template exists."""
        template_path = f"{template_name}/template.html"
        try:
            self._env.get_template(template_path)
            return True
        except Exception:
            return False

    def list_templates(self) -> list[str]:
        """List all available templates."""
        templates = []

        for template_dir in self._template_paths:
            if template_dir.exists():
                for item in template_dir.iterdir():
                    if item.is_dir():
                        template_file = item / "template.html"
                        if template_file.exists():
                            templates.append(item.name)

        return sorted(set(templates))

    def get_template_dir(self, template_name: str) -> Path | None:
        """Get the directory path for a template."""
        for template_dir in self._template_paths:
            template_path = template_dir / template_name
            if template_path.exists() and (template_path / "template.html").exists():
                return template_path

        return None
