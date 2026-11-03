# Archivo: models.py
from datetime import datetime

DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
         "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

TIPOS_FALLA = [
    "Luminaria Fundida",
    "Cable Caído / Chispeando",
    "Transformador Averiado",
    "Comarca Completa Sin Luz",
    "Baja Tensión / Inestabilidad",
]
ESTADOS = ["Resuelto", "En Verificación", "Pendiente de Cierre"]


def formatear_fecha_hora(dt: datetime) -> str:
    """dd/mm/aaaa hh:mm:ss AM/PM (fecha y hora exacta)."""
    h = dt.hour % 12 or 12
    sufijo = "AM" if dt.hour < 12 else "PM"
    return f"{dt.day:02d}/{dt.month:02d}/{dt.year} {h:02d}:{dt.minute:02d}:{dt.second:02d} {sufijo}"


def fecha_larga(dt: datetime) -> str:
    """Ej: Domingo, 1 de Noviembre de 2026"""
    return f"{DIAS[dt.weekday()]}, {dt.day} de {MESES[dt.month - 1]} de {dt.year}"


def calcular_prioridad(tipo_falla: str) -> str:
    falla_lower = str(tipo_falla).lower()
    if any(k in falla_lower for k in ["transformador", "chispeando", "caído"]):
        return "Alta / Urgente"
    elif any(k in falla_lower for k in ["comarca completa", "baja tensión"]):
        return "Media-Alta"
    return "Normal"


def _a_datetime(valor) -> datetime:
    if valor is None:
        return datetime.now().replace(microsecond=0)
    if isinstance(valor, datetime):
        return valor.replace(microsecond=0)
    return datetime.strptime(str(valor)[:19], "%Y-%m-%d %H:%M:%S")


class Usuario:
    def __init__(self, username, password, nombre_completo, proveedor="Local"):
        self.username = str(username).strip()
        self.password = str(password).strip()
        self.nombre_completo = str(nombre_completo).strip()
        self.proveedor = str(proveedor).strip()


class ReporteFalla:
    def __init__(self, id_reporte, cuadrilla, telefono_lider, comarca_ubicacion,
                 tipo_falla, solucion_aplicada, estado="Resuelto", fecha_hora=None):
        self.id_reporte = str(id_reporte).strip()
        self.cuadrilla = str(cuadrilla).strip()
        self.telefono_lider = str(telefono_lider).strip()
        self.comarca_ubicacion = str(comarca_ubicacion).strip()
        self.tipo_falla = str(tipo_falla).strip()
        self.solucion_aplicada = str(solucion_aplicada).strip()
        self.estado = str(estado).strip()
        self.fecha_hora = _a_datetime(fecha_hora)

    def calcular_prioridad_atencion(self):
        return calcular_prioridad(self.tipo_falla)

    def fecha_formateada(self):
        return formatear_fecha_hora(self.fecha_hora)

    def to_lista(self):
        return [
            self.id_reporte,
            self.fecha_formateada(),
            self.cuadrilla,
            self.telefono_lider,
            self.comarca_ubicacion,
            self.tipo_falla,
            self.calcular_prioridad_atencion(),
            self.solucion_aplicada,
            self.estado,
        ]