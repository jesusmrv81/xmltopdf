"""SAT catalog data and helpers."""

from typing import Final


class SATCatalogs:
    """SAT catalog data for CFDI 4.0."""

    REGIMEN_FISCAL: Final[dict[str, str]] = {
        "601": "General de Ley Personas Morales",
        "603": "Personas Morales con Fines no Lucrativos",
        "605": "Sueldos y Salarios e Ingresos Asimilados a Salarios",
        "606": "Arrendamiento",
        "607": "Régimen de Enajenación o Adquisición de Bienes",
        "608": "Demás ingresos",
        "609": "Consolidación",
        "610": "Residentes en el Extranjero sin Establecimiento Permanente en México",
        "611": "Ingresos por Dividendos (socios y accionistas)",
        "612": "Personas Físicas con Actividades Empresariales y Profesionales",
        "614": "Ingresos por intereses",
        "615": "Régimen de los ingresos por obtención de premios",
        "616": "Sin obligaciones fiscales",
        "620": "Sociedades Cooperativas de Producción que optan por diferir sus ingresos",
        "621": "Incorporación Fiscal",
        "622": "Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras",
        "623": "Opcional para Grupos de Sociedades",
        "624": "Coordinados",
        "625": "Régimen de las Actividades Empresariales con ingresos a través de Plataformas",
        "626": "Régimen Simplificado de Confianza",
    }

    USO_CFDI: Final[dict[str, str]] = {
        "G01": "Adquisición de mercancías",
        "G02": "Devoluciones, descuentos o bonificaciones",
        "G03": "Gastos en general",
        "I01": "Construcciones",
        "I02": "Mobiliario y equipo de oficina por inversiones",
        "I03": "Equipo de transporte",
        "I04": "Equipo de computo y accesorios",
        "I05": "Dados, troqueles, moldes, matrices y herramental",
        "I06": "Comunicaciones telefónicas",
        "I07": "Comunicaciones satelitales",
        "I08": "Otra maquinaria y equipo",
        "D01": "Honorarios médicos, dentales y gastos hospitalarios",
        "D02": "Gastos médicos por incapacidad o discapacidad",
        "D03": "Gastos funerales",
        "D04": "Donativos",
        "D05": "Intereses reales efectivamente pagados por créditos hipotecarios (casa habitación)",
        "D06": "Aportaciones voluntarias al SAR",
        "D07": "Primas por seguros de gastos médicos",
        "D08": "Gastos de transportación escolar obligatoria",
        "D09": "Depósitos en cuentas para el ahorro, primas que tengan como base planes de pensiones",
        "D10": "Pagos por servicios educativos (colegiaturas)",
        "P01": "Por definir",
        "S01": "Sin efectos fiscales",
        "CP01": "Pagos",
    }

    FORMA_PAGO_P: Final[dict[str, str]] = {
        "01": "Efectivo",
        "02": "Cheque nominativo",
        "03": "Transferencia electrónica de fondos",
        "04": "Tarjeta de crédito",
        "05": "Monedero electrónico",
        "06": "Dinero electrónico",
        "08": "Vales de despensa",
        "12": "Dación en pago",
        "13": "Pago por subrogación",
        "14": "Pago por consignación",
        "15": "Condonación",
        "17": "Compensación",
        "23": "Novación",
        "24": "Confusión",
        "25": "Remisión de deuda",
        "26": "Prescripción o caducidad",
        "27": "A satisfacción del acreedor",
        "28": "Tarjeta de débito",
        "29": "Tarjeta de servicios",
        "30": "Aplicación de anticipos",
        "31": "Intermediario pagos",
        "99": "Por definir",
    }

    FORMA_PAGO: Final[dict[str, str]] = {
        "01": "Efectivo",
        "02": "Cheque nominativo",
        "03": "Transferencia electrónica de fondos",
        "04": "Tarjeta de crédito",
        "05": "Monedero electrónico",
        "06": "Dinero electrónico",
        "08": "Vales de despensa",
        "12": "Dación en pago",
        "13": "Pago por subrogación",
        "14": "Pago por consignación",
        "15": "Condonación",
        "17": "Compensación",
        "23": "Novación",
        "24": "Confusión",
        "25": "Remisión de deuda",
        "26": "Prescripción o caducidad",
        "27": "A satisfacción del acreedor",
        "28": "Tarjeta de débito",
        "29": "Tarjeta de servicios",
        "30": "Aplicación de anticipos",
        "31": "Intermediario pagos",
        "99": "Por definir",
    }

    METODO_PAGO: Final[dict[str, str]] = {
        "PUE": "Pago en una sola exhibición",
        "PPD": "Pago en parcialidades o diferido",
    }

    TIPO_COMPROBANTE: Final[dict[str, str]] = {
        "I": "Ingreso",
        "E": "Egreso",
        "T": "Traslado",
        "N": "Nómina",
        "P": "Pago",
    }

    EXPORTACION: Final[dict[str, str]] = {
        "01": "No aplica",
        "02": "Definitiva",
        "03": "Temporal",
    }

    IMPUESTO: Final[dict[str, str]] = {
        "001": "ISR",
        "002": "IVA",
        "003": "IEPS",
    }

    OBJETO_IMPUESTO: Final[dict[str, str]] = {
        "01": "No objeto de impuesto",
        "02": "Sí objeto de impuesto",
        "03": "Sí objeto del impuesto y no obligado al desglose",
        "04": "Sí objeto del impuesto y no causa impuesto",
    }

    MONEDA: Final[dict[str, str]] = {
        "MXN": "Peso Mexicano",
        "USD": "Dolar americano",
        "EUR": "Euro",
        "GBP": "Libra Esterlina",
        "CAD": "Dolar Canadiense",
        "JPY": "Yen",
        "XXX": "Los códigos asignados para las transacciones en que intervenga ninguna moneda",
    }

    @classmethod
    def get_regimen_fiscal(cls, clave: str) -> str:
        """Get régimen fiscal description."""
        return cls.REGIMEN_FISCAL.get(clave, f"Desconocido ({clave})")

    @classmethod
    def get_uso_cfdi(cls, clave: str) -> str:
        """Get uso CFDI description."""
        return cls.USO_CFDI.get(clave, f"Desconocido ({clave})")

    @classmethod
    def get_forma_pago(cls, clave: str) -> str:
        """Get forma de pago description."""
        return cls.FORMA_PAGO.get(clave, f"Desconocido ({clave})")

    @classmethod
    def get_forma_pago_p(cls, clave: str) -> str:
        """Get forma de pago (Pagos20) description."""
        return cls.FORMA_PAGO_P.get(clave, f"Desconocido ({clave})")

    @classmethod
    def get_metodo_pago(cls, clave: str) -> str:
        """Get método de pago description."""
        return cls.METODO_PAGO.get(clave, f"Desconocido ({clave})")

    @classmethod
    def get_tipo_comprobante(cls, clave: str) -> str:
        """Get tipo de comprobante description."""
        return cls.TIPO_COMPROBANTE.get(clave, f"Desconocido ({clave})")

    @classmethod
    def get_exportacion(cls, clave: str) -> str:
        """Get exportación description."""
        return cls.EXPORTACION.get(clave, f"Desconocido ({clave})")

    @classmethod
    def get_impuesto(cls, clave: str) -> str:
        """Get impuesto description."""
        return cls.IMPUESTO.get(clave, f"Desconocido ({clave})")

    @classmethod
    def get_objeto_impuesto(cls, clave: str) -> str:
        """Get objeto de impuesto description."""
        return cls.OBJETO_IMPUESTO.get(clave, f"Desconocido ({clave})")

    @classmethod
    def get_moneda(cls, clave: str) -> str:
        """Get moneda description."""
        return cls.MONEDA.get(clave, f"Desconocido ({clave})")
