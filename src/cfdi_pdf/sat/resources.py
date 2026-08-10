"""Gestor de recursos del SAT descargados en runtime.

La biblioteca no incluye los XSLT/XSD oficiales del SAT en el paquete (son
grandes y el SAT los actualiza con frecuencia). En su lugar, este módulo los
descarga bajo demanda desde el SAT (con un mirror verificado como respaldo),
los cachea en disco y verifica su integridad por SHA-256 contra un manifiesto
empaquetado.

El manifiesto se genera a partir de archivos verificados contra el SAT oficial
(ver ``doc/seguridad.md``). Si el SAT publica una versión nueva, el hash no
coincidirá y se lanzará un error claro con el hash nuevo para actualizar el
manifiesto.
"""

import hashlib
import logging
import os
import threading
import urllib.error
import urllib.request
from pathlib import Path

from ..exceptions import SATResourceError

logger = logging.getLogger(__name__)

# URLs base (la raíz equivale a .../sitio_internet/cfd del SAT).
SAT_BASE_URL = "https://www.sat.gob.mx/sitio_internet/cfd"
# Mirror verificado: copia fiel del árbol www.sat.gob.mx (validada contra el SAT).
MIRROR_BASE_URL = (
    "https://raw.githubusercontent.com/phpcfdi/resources-sat-xml/master/"
    "resources/www.sat.gob.mx/sitio_internet/cfd"
)

# Ruta relativa -> SHA-256 del contenido canónico verificado contra el SAT.
#
# El hash se calcula sobre la FORMA CANÓNICA (ver `_canonicalize`):
#   - saltos de línea normalizados a LF y sin salto final,
#   - en `4/cadenaoriginal_4_0/cadenaoriginal_4_0.xslt`, los `xsl:include`
#     absolutos del SAT se convierten a relativos y se quita `version="2.0"`
#     (adaptación necesaria para lxml/libxslt 1.0),
#   - en `4/cfdv40.xsd`, los `schemaLocation` relativos del mirror se devuelven
#     a la forma absoluta del SAT.
MANIFEST: dict[str, str] = {
    "2/cadenaoriginal_2_0/utilerias.xslt": "9237068e95220bf1b9f77c9f5750d42ca62182b1d4578156c10e4c5a6b67b652",
    "4/cadenaoriginal_4_0/cadenaoriginal_4_0.xslt": "71ca6fb1e64cc3ee7df1cad3a8c9ee5ff717eab61034b51e56ee1963438d9f6d",
    "4/cfdv40.xsd": "15ad6d874c7599324397697b440df044f6aa0ef2bf0646d84251c1046d32ff68",
    "CartaPorte/CartaPorte20.xslt": "a0236fbe49d8f80e2417f166a59725b5a248febb2cd975369b1c1f1535621b7c",
    "CartaPorte/CartaPorte30.xslt": "1a6d14f2727e27c76895466fbcc38b0dd664924dd0313d6435aca9f4d7c50994",
    "CartaPorte/CartaPorte31.xslt": "c5e349ca4a3f443489aa914516998b8f63d2c104687533d6181114efb69f2b02",
    "ComercioExterior11/ComercioExterior11.xslt": "bb9e7c3d2a2a3e8af9c65498fd1422b0f400e0787d2418b460d51ece6c988f9d",
    "ComercioExterior20/ComercioExterior20.xslt": "d1ac00ab5fd8a424e8c2e714bb998d3933cc78398260e16a451b12e6378c1802",
    "EstadoDeCuentaCombustible/ecc12.xslt": "9ce3097989da2560e3fcb6e45928cd7d90692832b2d29c0c4127732349f3dba5",
    "GastosHidrocarburos10/GastosHidrocarburos10.xslt": "1d735ccdd03040a19469795e6703fbd2c56a2c08c708111278af6d885e98621c",
    "HidrocarburosPetro/hidrocarburospetroliferos.xslt": "7abbd88e710595d4de4924dc5d08ab7561436eaabc49c6fa010227a9b7e0679c",
    "IngresosHidrocarburos10/IngresosHidrocarburos.xslt": "2d17335608f036214129210b06da1a132ec0fc06b315f97dd3e07d09641303d9",
    "Pagos/Pagos20.xslt": "c731c30e75ce92f25a30b9b29c91f8b059fb1404f3af0fb1a413d204f9b59a84",
    "TimbreFiscalDigital/cadenaoriginal_TFD_1_1.xslt": "301457c2d1d0979d60e6dd6b3d5708ce5f3410da8efedd61442a530ccda2063f",
    "TuristaPasajeroExtranjero/TuristaPasajeroExtranjero.xslt": "8c617c7e625d5f95195dfb37cf366fda8df6443c4b04efa7df468e367a2042d8",
    "aerolineas/aerolineas.xslt": "0eed27a83b7da64392414927701e8de18c15a94be1454b38e37b9c9f84b1cf13",
    "arteantiguedades/obrasarteantiguedades.xslt": "6e6e27b699fb411da36b81e3c643e1b2ddb86bd978d2e99c2a992538119cfb68",
    "catalogos/catCFDI.xsd": "21088f4189665e118a0b6681cccd4846cc6b3a5ee3bc4c27848b59abeb936c4c",
    "certificadodestruccion/certificadodedestruccion.xslt": "089751c8980fc71d16ca4d64e8d50832820f3382cc910c59d590812c3c812421",
    "cfdiregistrofiscal/cfdiregistrofiscal.xslt": "3ac837a5c9481fce3eb8d0bef6dfb3d851eb340566851aa5eef43e9f72fcd7f1",
    "consumodecombustibles/consumodeCombustibles11.xslt": "610de8017f569d6e66669fc1f8b2303c5b4ac970e9b17e44bcd5d1b0e4ef7bf1",
    "detallista/detallista.xslt": "9868659c754b42ee62760abf7105094781db4d22b3f8d31ab5eb42687efaa684",
    "divisas/divisas.xslt": "d860c9caa32b1290b008600c1e553cedf8f9b0103443bc98038d49a279839eef",
    "donat/donat11.xslt": "5c16061ea030c6af307234ccc854be6bcf0bc949ed96948893042061dfcc5668",
    "iedu/iedu.xslt": "7b67ced2ae1450a30d9f9962abc310222d8240021e90e1ab8b90518cc6a341ee",
    "implocal/implocal.xslt": "a6510449be6e04f512482cbe6e69c864568286e4076413afb9332484ff0894a8",
    "ine/ine11.xslt": "02781b96a0da332693f719f893f7a72117196b073c5d0df48e7fa6a4ed444882",
    "leyendasFiscales/leyendasFisc.xslt": "fff2e26491efd6acd408c3e24a285cf03973f10eb22b72e816050a2a1b22abb7",
    "nomina/nomina12.xslt": "a14cdb44995526aa5888036bedf7fac9f84ad0041f9393371b0bbbea0572649e",
    "notariospublicos/notariospublicos.xslt": "3c05f1034b6ac4dcad5297ecc3cefc3879ae308b911fff6276c030ab55653485",
    "pagoenespecie/pagoenespecie.xslt": "9282f758be25079c7ffe514b53b8b44b45668fb9dcd641d8bd98c0ab5acf8404",
    "pfic/pfic.xslt": "ff347a03063eadba9988e152badc0ed3edd5d5519f5a479798603edb053a341a",
    "renovacionysustitucionvehiculos/renovacionysustitucionvehiculos.xslt": "347bf6dfdae5c0b18d6a107c8c339f212763496fa4ae1fa748d0354a7c3338d2",
    "servicioparcialconstruccion/servicioparcialconstruccion.xslt": "b2b5547d28af116a96527fff089d4fa1ac8827db4323f071d9a9c25a470a041a",
    "tipoDatos/tdCFDI/tdCFDI.xsd": "70a2bae4ea1db90f81d4ada71e15d979dea9406b9d683762914e08f1190a6f0d",
    "valesdedespensa/valesdedespensa.xslt": "a1e6b54f46534c75978026fa6f571081d5860efa6f187a8894c9bb0b864655d7",
    "vehiculousado/vehiculousado.xslt": "7a035899c95f8645c2825cdbf0da1ecfa972f111faf6a75c7fb1e48f734d71ce",
    "ventavehiculos/ventavehiculos11.xslt": "e4b0f652bfafa862a71a77bece21f93e762e2cee2b20d0456ac6b04b71dc4295",
}

# Transformaciones de la forma original del SAT a la forma canónica. El mirror
# aplica estas mismas adaptaciones (por eso ambas fuentes convergen al hash).
_CANONICAL_SUBSTITUTIONS: dict[str, list[tuple[bytes, bytes]]] = {
    "4/cadenaoriginal_4_0/cadenaoriginal_4_0.xslt": [
        # includes absolutos del SAT -> relativos (desde 4/cadenaoriginal_4_0/)
        (b"http://www.sat.gob.mx/sitio_internet/cfd/", b"../../"),
        # libxslt (XSLT 1.0) tolera version=2.0 pero lo quitamos para normalizar
        (b' version="2.0"', b""),
    ],
    "4/cfdv40.xsd": [
        # el mirror relativiza los schemaLocation; devolvemos la forma absoluta del SAT
        (
            b"../catalogos/catCFDI.xsd",
            b"http://www.sat.gob.mx/sitio_internet/cfd/catalogos/catCFDI.xsd",
        ),
        (
            b"../tipoDatos/tdCFDI/tdCFDI.xsd",
            b"http://www.sat.gob.mx/sitio_internet/cfd/tipoDatos/tdCFDI/tdCFDI.xsd",
        ),
    ],
}


def _canonicalize(relative: str, data: bytes) -> bytes:
    """Convierte el contenido crudo (SAT o mirror) a la forma canónica verificada."""
    data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n").rstrip(b"\n")
    for old, new in _CANONICAL_SUBSTITUTIONS.get(relative, []):
        data = data.replace(old, new)
    return data


# Subconjuntos útiles (evitan descargar todo cuando solo se necesita una parte).
XSLT_RESOURCES = [path for path in MANIFEST if path.endswith(".xslt")]
XSD_RESOURCES = [
    "4/cfdv40.xsd",
    "catalogos/catCFDI.xsd",
    "tipoDatos/tdCFDI/tdCFDI.xsd",
]


def default_cache_dir() -> Path:
    """Directorio de caché (override con la variable CFDI_PDF_CACHE_DIR)."""
    env = os.environ.get("CFDI_PDF_CACHE_DIR")
    if env:
        return Path(env).expanduser()
    if os.name == "nt":
        base_dir = os.environ.get("LOCALAPPDATA") or str(Path.home())
        return Path(base_dir) / "cfdi-pdf" / "cache"
    xdg = os.environ.get("XDG_CACHE_HOME")
    cache_root = Path(xdg) if xdg else Path.home() / ".cache"
    return cache_root / "cfdi-pdf"


class SATResourceManager:
    """
    Descarga y cachea los recursos oficiales del SAT (XSLT/XSD).

    Args:
        cache_dir: directorio de caché (por defecto, el de usuario).
        base_urls: URLs base a probar en orden. Por defecto usa el SAT oficial
            y después el mirror verificado.
        refresh: si es True, re-descarga aunque el archivo ya exista.
        allow_unverified: si es True, no verifica el SHA-256 del manifiesto.
    """

    def __init__(
        self,
        cache_dir: str | Path | None = None,
        base_urls: list[str] | None = None,
        refresh: bool = False,
        allow_unverified: bool = False,
    ) -> None:
        self.cache_dir = Path(cache_dir) if cache_dir else default_cache_dir()
        env_bases = os.environ.get("CFDI_PDF_BASE_URLS")
        if env_bases:
            self.base_urls = [u.strip("/") for u in env_bases.split(",") if u.strip()]
        elif base_urls:
            self.base_urls = [u.rstrip("/") for u in base_urls]
        else:
            self.base_urls = [SAT_BASE_URL, MIRROR_BASE_URL]
        self.refresh = refresh
        self.allow_unverified = (
            allow_unverified or os.environ.get("CFDI_PDF_ALLOW_UNVERIFIED") == "1"
        )

        self._lock = threading.Lock()
        self._downloaded: set[str] = set()

    # ── API pública ───────────────────────────────────────────────────────────

    def ensure(self, relative: str) -> Path:
        """
        Asegura que el recurso esté descargado y verificado en caché.

        Returns:
            Ruta local del recurso.

        Raises:
            SATResourceError: si no se puede descargar o el hash no coincide.
        """
        if relative not in MANIFEST:
            raise SATResourceError(f"Recurso no registrado en el manifiesto: {relative}")

        target = self.cache_dir / relative
        with self._lock:
            if relative in self._downloaded and target.exists() and not self.refresh:
                return target

            if target.exists() and not self.refresh and self._verify(target):
                self._downloaded.add(relative)
                return target

            self._download(relative, target)
            self._downloaded.add(relative)
            return target

    def ensure_many(self, relatives: list[str]) -> None:
        """Asegura varios recursos (p. ej. un subconjunto XSLT o XSD)."""
        for relative in relatives:
            self.ensure(relative)

    def ensure_all(self) -> None:
        """Descarga y verifica todos los recursos del manifiesto."""
        self.ensure_many(list(MANIFEST))

    def path(self, relative: str) -> Path:
        """Asegura el recurso y devuelve su ruta de caché."""
        return self.ensure(relative)

    def read_bytes(self, relative: str) -> bytes:
        """Asegura el recurso y devuelve su contenido en bytes."""
        return self.path(relative).read_bytes()

    # ── internos ──────────────────────────────────────────────────────────────

    def _verify(self, path: Path) -> bool:
        """Verifica el SHA-256 (canónico) de un archivo contra el manifiesto."""
        if self.allow_unverified:
            return True
        relative = str(path.relative_to(self.cache_dir)).replace(os.sep, "/")
        expected = MANIFEST.get(relative)
        if expected is None:
            return False
        digest = hashlib.sha256(_canonicalize(relative, path.read_bytes())).hexdigest()
        return digest == expected

    def _download(self, relative: str, target: Path) -> None:
        expected = MANIFEST[relative]
        errors: list[str] = []

        for base_url in self.base_urls:
            url = f"{base_url}/{relative}"
            try:
                raw = self._fetch(url)
            except OSError as exc:
                errors.append(f"{url}: {exc}")
                continue

            data = _canonicalize(relative, raw)
            digest = hashlib.sha256(data).hexdigest()
            if not self.allow_unverified and digest != expected:
                errors.append(
                    f"{url}: hash no coincide (esperado {expected[:16]}…, obtenido "
                    f"{digest[:16]}…) — el SAT pudo actualizar el archivo"
                )
                continue

            self._write_atomic(target, data)
            logger.info("Recurso SAT descargado y verificado: %s (%d bytes)", relative, len(data))
            return

        raise SATResourceError(
            f"No se pudo descargar el recurso del SAT '{relative}': "
            + "; ".join(errors)
            + ". Usa CFDI_PDF_BASE_URLS para configurar otra fuente."
        )

    def _fetch(self, url: str) -> bytes:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "cfdi-pdf/" + __import__("cfdi_pdf").__version__},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            return bytes(response.read())

    @staticmethod
    def _write_atomic(target: Path, data: bytes) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_suffix(target.suffix + ".tmp")
        tmp.write_bytes(data)
        tmp.replace(target)


# Singleton compartido por todo el proceso.
_default_manager = SATResourceManager()


def get_manager() -> SATResourceManager:
    """Devuelve el gestor por defecto (reconfigurable vía variables de entorno)."""
    return _default_manager


def refresh_manifest() -> dict[str, str]:
    """
    Re-descarga todos los recursos del SAT y devuelve el manifiesto canónico actual.

    Utilidad de mantenimiento: si el SAT publicó archivos nuevos, los hashes
    diferirán del ``MANIFEST`` empaquetado. Devuelve el dict completo
    ``{ruta: sha256}`` (canónico) para actualizar ``MANIFEST`` en este módulo.
    """
    manager = SATResourceManager(refresh=True, allow_unverified=True)
    manager.ensure_all()

    refreshed: dict[str, str] = {}
    for relative in MANIFEST:
        data = (manager.cache_dir / relative).read_bytes()
        refreshed[relative] = hashlib.sha256(_canonicalize(relative, data)).hexdigest()
    return refreshed
