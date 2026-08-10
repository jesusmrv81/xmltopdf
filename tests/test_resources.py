"""Tests para SATResourceManager (descarga runtime + verificación de integridad)."""

from pathlib import Path

import pytest

from cfdi_pdf.exceptions import SATResourceError
from cfdi_pdf.sat.resources import MIRROR_BASE_URL, SATResourceManager, default_cache_dir

_TFD = "TimbreFiscalDigital/cadenaoriginal_TFD_1_1.xslt"


class TestSATResourceManager:
    """Test suite para el gestor de recursos del SAT."""

    def test_download_and_cache(self, tmp_path: Path) -> None:
        """Descarga el recurso desde el mirror verificado y lo deja en caché."""
        manager = SATResourceManager(cache_dir=tmp_path, base_urls=[MIRROR_BASE_URL])
        path = manager.ensure(_TFD)

        assert path.exists()
        assert path.read_bytes().startswith(b"<?xml")

    def test_second_ensure_uses_cache(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Un segundo ensure no vuelve a tocar la red (usa la caché)."""
        manager = SATResourceManager(cache_dir=tmp_path, base_urls=[MIRROR_BASE_URL])
        first = manager.ensure(_TFD)

        def boom(_url: str) -> bytes:  # pragma: no cover - nunca debe llamarse
            raise OSError("sin red")

        monkeypatch.setattr(manager, "_fetch", boom)
        second = manager.ensure(_TFD)
        assert second == first

    def test_verify_detects_corruption(self, tmp_path: Path) -> None:
        """Un archivo con contenido alterado no pasa la verificación de hash."""
        manager = SATResourceManager(cache_dir=tmp_path)
        target = tmp_path / _TFD
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"contenido alterado")
        assert manager._verify(target) is False

    def test_download_failure_raises(self, tmp_path: Path) -> None:
        """Si ninguna fuente responde, lanza SATResourceError."""
        manager = SATResourceManager(cache_dir=tmp_path, base_urls=["http://127.0.0.1:9/nope"])
        with pytest.raises(SATResourceError):
            manager.ensure(_TFD)

    def test_unregistered_resource_raises(self, tmp_path: Path) -> None:
        """Un recurso fuera del manifiesto se rechaza."""
        manager = SATResourceManager(cache_dir=tmp_path)
        with pytest.raises(SATResourceError):
            manager.ensure("algo/inesperado.xslt")

    def test_allow_unverified_skips_hash(self, tmp_path: Path) -> None:
        """Con allow_unverified=True no se exige el hash del manifiesto."""
        manager = SATResourceManager(cache_dir=tmp_path, allow_unverified=True)
        target = tmp_path / _TFD
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"cualquier cosa")
        assert manager._verify(target) is True


class TestDefaultCacheDir:
    """Test suite para el directorio de caché por defecto."""

    def test_env_override(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CFDI_PDF_CACHE_DIR", str(tmp_path / "cache"))
        assert default_cache_dir() == tmp_path / "cache"


class TestRefreshManifest:
    """Test suite para el refresco del manifiesto (mantenimiento del SAT)."""

    def test_refresh_matches_manifest(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Re-descargar desde el mirror devuelve los mismos hashes (sin cambios SAT)."""
        from cfdi_pdf.sat.resources import MANIFEST, refresh_manifest

        monkeypatch.setenv("CFDI_PDF_CACHE_DIR", str(tmp_path / "cache"))
        monkeypatch.setenv("CFDI_PDF_BASE_URLS", MIRROR_BASE_URL)

        refreshed = refresh_manifest()

        assert set(refreshed) == set(MANIFEST)
        assert refreshed == MANIFEST
