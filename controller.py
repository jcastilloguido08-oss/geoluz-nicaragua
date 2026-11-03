# Archivo: controller.py
import re
from datetime import datetime, timedelta

from database import obtener_conexion, inicializar_base_datos
from models import ReporteFalla, Usuario


def rango_periodo(clave, ref=None):
    """
    Devuelve (inicio, fin_exclusivo) del período que contiene a `ref` (por defecto, ahora).
    clave: 'hoy' | 'semana' (lunes a domingo) | 'mes' | 'anio'
    """
    ref = ref or datetime.now()
    inicio_dia = datetime(ref.year, ref.month, ref.day)
    if clave == "hoy":
        return inicio_dia, inicio_dia + timedelta(days=1)
    if clave == "semana":
        lunes = inicio_dia - timedelta(days=inicio_dia.weekday())
        return lunes, lunes + timedelta(days=7)
    if clave == "mes":
        inicio = datetime(ref.year, ref.month, 1)
        siguiente = datetime(ref.year + (ref.month == 12), ref.month % 12 + 1, 1)
        return inicio, siguiente
    if clave == "anio":
        return datetime(ref.year, 1, 1), datetime(ref.year + 1, 1, 1)
    raise ValueError(f"Período desconocido: {clave}")


class ReporteController:
    def __init__(self):
        inicializar_base_datos()

    # ---------- utilidades internas ----------
    def _consultar(self, sql, params=(), uno=False):
        conn = obtener_conexion()
        if not conn:
            return None if uno else []
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, params)
            return cursor.fetchone() if uno else cursor.fetchall()
        finally:
            conn.close()

    def _modificar(self, sql, params=()):
        conn = obtener_conexion()
        if not conn:
            raise RuntimeError("No se pudo conectar a la base de datos MySQL.")
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def _a_reporte(r):
        return ReporteFalla(
            r["id_reporte"], r["usuario"], r["telefono"], r["comarca_ubicacion"],
            r["tipo_falla"], r["descripcion"], r["estado"], r["fecha_hora"]
        )

    # ---------- autenticación ----------
    def autenticar_usuario(self, username, password):
        row = self._consultar(
            "SELECT * FROM usuarios WHERE username = %s AND password = %s",
            (username.strip(), password.strip()), uno=True
        )
        if row:
            return Usuario(row["username"], row["password"], row["nombre_completo"], row["proveedor"])
        return None

    def autenticar_oauth(self, proveedor):
        return Usuario(
            username=f"admin_{proveedor.lower()}",
            password="",
            nombre_completo=f"Administrador ({proveedor})",
            proveedor=proveedor
        )

    # ---------- CRUD ----------
    def siguiente_id(self):
        """Sugiere el próximo ID con formato REP-###."""
        filas = self._consultar("SELECT id_reporte FROM reportes")
        mayor = 0
        for f in filas:
            m = re.fullmatch(r"REP-(\d+)", f["id_reporte"].strip(), re.IGNORECASE)
            if m:
                mayor = max(mayor, int(m.group(1)))
        return f"REP-{mayor + 1}"

    def agregar_reporte(self, id_reporte, cuadrilla, telefono_lider, comarca_ubicacion,
                        tipo_falla, solucion_aplicada, estado, fecha_hora=None):
        if self.buscar_por_id(id_reporte) is not None:
            raise ValueError(f"El ID de reporte '{id_reporte}' ya se encuentra registrado.")

        fecha_hora = (fecha_hora or datetime.now()).replace(microsecond=0)
        self._modificar("""
            INSERT INTO reportes (id_reporte, usuario, telefono, comarca_ubicacion, tipo_falla, descripcion, estado, fecha_hora)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (id_reporte, cuadrilla, telefono_lider, comarca_ubicacion, tipo_falla,
              solucion_aplicada, estado, fecha_hora))
        return ReporteFalla(id_reporte, cuadrilla, telefono_lider, comarca_ubicacion,
                            tipo_falla, solucion_aplicada, estado, fecha_hora)

    def obtener_todos(self):
        rows = self._consultar("SELECT * FROM reportes ORDER BY fecha_hora DESC")
        return [self._a_reporte(r) for r in rows]

    def buscar_por_id(self, id_reporte):
        row = self._consultar(
            "SELECT * FROM reportes WHERE LOWER(id_reporte) = %s",
            (str(id_reporte).strip().lower(),), uno=True
        )
        return self._a_reporte(row) if row else None

    def actualizar_reporte(self, id_reporte, cuadrilla, telefono_lider, comarca_ubicacion,
                           tipo_falla, solucion_aplicada, estado, fecha_hora=None):
        if self.buscar_por_id(id_reporte) is None:
            raise ValueError("El reporte que intenta actualizar no existe.")

        fecha_hora = (fecha_hora or datetime.now()).replace(microsecond=0)
        self._modificar("""
            UPDATE reportes
            SET usuario = %s, telefono = %s, comarca_ubicacion = %s, tipo_falla = %s,
                descripcion = %s, estado = %s, fecha_hora = %s
            WHERE LOWER(id_reporte) = %s
        """, (cuadrilla, telefono_lider, comarca_ubicacion, tipo_falla, solucion_aplicada,
              estado, fecha_hora, str(id_reporte).strip().lower()))

    def eliminar_reporte(self, id_reporte):
        if self.buscar_por_id(id_reporte) is None:
            raise ValueError("El reporte que desea eliminar no existe.")
        self._modificar("DELETE FROM reportes WHERE LOWER(id_reporte) = %s",
                        (str(id_reporte).strip().lower(),))

    # ---------- estadísticas ----------
    def estadisticas(self):
        """Totales de reportes: hoy, esta semana, este mes, este año y total general."""
        claves = ("hoy", "semana", "mes", "anio")
        rangos = {k: rango_periodo(k) for k in claves}

        sql = "SELECT COUNT(*) AS total, " + ", ".join(
            f"COALESCE(SUM(fecha_hora >= %s AND fecha_hora < %s), 0) AS {k}" for k in claves
        ) + " FROM reportes"
        params = []
        for k in claves:
            params += [rangos[k][0], rangos[k][1]]

        row = self._consultar(sql, tuple(params), uno=True) or {}
        resultado = {"total": int(row.get("total") or 0), "rangos": rangos}
        for k in claves:
            resultado[k] = int(row.get(k) or 0)
        return resultado

    def conteo_por_tipo(self):
        rows = self._consultar("SELECT tipo_falla, COUNT(*) AS c FROM reportes GROUP BY tipo_falla")
        return {r["tipo_falla"]: int(r["c"]) for r in rows}

    def conteo_por_estado(self):
        rows = self._consultar("SELECT estado, COUNT(*) AS c FROM reportes GROUP BY estado")
        return {r["estado"]: int(r["c"]) for r in rows}

    def conteo_por_dia(self):
        """{date: cantidad} para resaltar días con reportes en el calendario."""
        rows = self._consultar(
            "SELECT DATE(fecha_hora) AS d, COUNT(*) AS c FROM reportes GROUP BY DATE(fecha_hora)"
        )
        return {r["d"]: int(r["c"]) for r in rows}