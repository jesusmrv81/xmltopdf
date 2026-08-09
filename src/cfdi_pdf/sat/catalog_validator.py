"""Validación de claves de catálogo SAT en un CFDI (sin exigir el XSD completo).

Verifica que las claves usadas (moneda, régimen fiscal, uso CFDI, impuestos,
forma de pago, etc.) existan en los catálogos oficiales. Es más ligero que la
validación XSD y detecta CFDIs con claves fuera de catálogo.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .catalogs import SATCatalogs

if TYPE_CHECKING:
    from ..models import CFDI


def validate_catalogs(cfdi: CFDI) -> list[str]:
    """
    Valida las claves de catálogo de un CFDI.

    Returns:
        Lista de errores (vacía si todas las claves son válidas).
    """
    errors: list[str] = []
    catalogs = SATCatalogs

    checks: list[tuple[str, str, dict[str, str]]] = [
        ("moneda", cfdi.moneda, catalogs.MONEDA),
        ("tipo_comprobante", cfdi.tipo_comprobante, catalogs.TIPO_COMPROBANTE),
        ("exportacion", cfdi.exportacion, catalogs.EXPORTACION),
        ("emisor.regimen_fiscal", cfdi.emisor.regimen_fiscal, catalogs.REGIMEN_FISCAL),
        ("receptor.regimen_fiscal", cfdi.receptor.regimen_fiscal, catalogs.REGIMEN_FISCAL),
        ("receptor.uso_cfdi", cfdi.receptor.uso_cfdi, catalogs.USO_CFDI),
    ]
    for field, value, catalog in checks:
        if value not in catalog:
            errors.append(f"{field}={value!r} no existe en el catálogo SAT")

    if cfdi.forma_pago and cfdi.forma_pago not in catalogs.FORMA_PAGO:
        errors.append(f"forma_pago={cfdi.forma_pago!r} no existe en c_FormaPago")
    if cfdi.metodo_pago and cfdi.metodo_pago not in catalogs.METODO_PAGO:
        errors.append(f"metodo_pago={cfdi.metodo_pago!r} no existe en c_MetodoPago")

    for index, concepto in enumerate(cfdi.conceptos):
        if concepto.objeto_imp not in catalogs.OBJETO_IMPUESTO:
            errors.append(
                f"conceptos[{index}].objeto_imp={concepto.objeto_imp!r} no existe en c_ObjetoImp"
            )

    if cfdi.impuestos is not None:
        for traslado in cfdi.impuestos.traslados:
            if traslado.impuesto not in catalogs.IMPUESTO:
                errors.append(
                    f"impuestos.traslados.impuesto={traslado.impuesto!r} no existe en c_Impuesto"
                )
        for retencion in cfdi.impuestos.retenciones:
            if retencion.impuesto not in catalogs.IMPUESTO:
                errors.append(
                    f"impuestos.retenciones.impuesto={retencion.impuesto!r} no existe en c_Impuesto"
                )

    if cfdi.pagos is not None:
        for pago in cfdi.pagos.pago:
            if pago.moneda_p not in catalogs.MONEDA:
                errors.append(f"pagos.pago.moneda_p={pago.moneda_p!r} no existe en c_Moneda")
            if pago.forma_de_pago_p not in catalogs.FORMA_PAGO_P:
                errors.append(
                    f"pagos.pago.forma_de_pago_p={pago.forma_de_pago_p!r} no existe en c_FormaPagoP"
                )
            for docto in pago.docto_relacionado:
                if docto.moneda_dr not in catalogs.MONEDA:
                    errors.append(
                        f"pagos.pago.docto_relacionado.moneda_dr={docto.moneda_dr!r} "
                        "no existe en c_Moneda"
                    )

    return errors
