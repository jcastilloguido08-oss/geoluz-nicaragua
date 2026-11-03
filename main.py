# Archivo: main.py
import sys
import csv
import re
from datetime import datetime, timedelta

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QFormLayout, QGridLayout, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QTextEdit, QFrame, QSplitter, QScrollArea, QStackedWidget, QButtonGroup,
    QDateTimeEdit, QDateEdit, QCalendarWidget, QProgressBar, QFileDialog, QCheckBox,
    QToolButton, QAbstractItemView
)
from PySide6.QtCore import Qt, QTimer, QDate, QDateTime, QTime, Signal, Signal
from PySide6.QtGui import QColor, QFont, QTextCharFormat, QBrush, QIcon

from controller import ReporteController, rango_periodo
from geodata import DEPARTAMENTOS_NICARAGUA
from models import (
    TIPOS_FALLA, ESTADOS, MESES, calcular_prioridad, formatear_fecha_hora, fecha_larga
)

# ======================================================================
#  PALETA (un solo acento azul; verde/ámbar/rojo solo para estados)
# ======================================================================
C_FONDO = "#F1F5F9"
C_BORDE = "#D3DBE7"
C_BORDE_INPUT = "#6B7A90"
C_TEXTO = "#0F172A"
C_MUTED = "#475569"
C_ACENTO = "#1D4ED8"
C_ACENTO_OSC = "#1E40AF"
C_ACENTO_SUAVE = "#EFF6FF"
C_VERDE = "#047857"
C_AMBAR = "#B45309"
C_ROJO = "#B91C1C"
C_NAVY = "#0F172A"

ESTILO_GLOBAL = f"""
* {{ font-family: "Segoe UI", "Inter", sans-serif; }}
QWidget {{ color: {C_TEXTO}; font-size: 14px; }}
QWidget#Raiz {{ background-color: {C_FONDO}; }}
QWidget#PanelLogin {{ background-color: #FFFFFF; }}
QDialog, QMessageBox {{ background-color: #FFFFFF; }}
QMessageBox QLabel {{ color: {C_TEXTO}; font-size: 14px; }}
QLabel {{ background: transparent; }}
QToolTip {{ background-color: {C_NAVY}; color: #FFFFFF; border: 1px solid {C_NAVY}; padding: 6px; }}

/* ---- Contenedores ---- */
QFrame#Card {{ background-color: #FFFFFF; border: 1px solid {C_BORDE}; border-radius: 10px; }}
QFrame#BarraAcciones {{ background-color: #FFFFFF; border: 1px solid {C_BORDE}; border-radius: 10px; }}
QFrame#StatCard {{ background-color: #FFFFFF; border: 1px solid {C_BORDE}; border-radius: 10px; }}
QFrame#StatCard:hover {{ background-color: {C_ACENTO_SUAVE}; border: 1px solid {C_ACENTO}; }}
QFrame#StatCard:focus {{ border: 2px solid {C_ACENTO}; }}
QFrame#Sidebar {{ background-color: {C_NAVY}; border: none; }}
QFrame#UserCard {{ background-color: rgba(255, 255, 255, 0.07); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 8px; }}
QFrame#Aviso {{ background-color: {C_ACENTO_SUAVE}; border: 1px solid #BFDBFE; border-radius: 8px; }}
QFrame#PanelMarca {{ background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0F172A, stop:1 #1E293B); border: none; }}

/* ---- Textos ---- */
QLabel#CardTitle {{ font-size: 16px; font-weight: 700; color: {C_TEXTO}; }}
QLabel#PageTitle {{ font-size: 22px; font-weight: 700; color: {C_TEXTO}; }}
QLabel#Muted {{ color: {C_MUTED}; font-size: 13px; }}
QLabel#Campo {{ color: #334155; font-size: 13px; font-weight: 600; }}
QLabel#Brand {{ font-size: 22px; font-weight: 800; letter-spacing: 3px; color: #FFFFFF; }}
QLabel#Reloj {{ color: {C_MUTED}; font-size: 13px; font-weight: 600; }}

/* ---- Campos ---- */
QLineEdit, QTextEdit, QComboBox, QDateEdit, QDateTimeEdit {{
    background-color: #FFFFFF; border: 1px solid {C_BORDE_INPUT}; border-radius: 6px;
    padding: 9px 12px; color: {C_TEXTO}; selection-background-color: {C_ACENTO}; selection-color: #FFFFFF;
}}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus, QDateTimeEdit:focus {{
    border: 2px solid {C_ACENTO}; padding: 8px 11px;
}}
QLineEdit:disabled, QDateEdit:disabled, QComboBox:disabled {{ color: #64748B; background-color: #EEF2F7; border: 1px solid {C_BORDE}; }}
QComboBox::drop-down, QDateEdit::drop-down, QDateTimeEdit::drop-down {{ border: none; width: 30px; }}
QComboBox::down-arrow, QDateEdit::down-arrow, QDateTimeEdit::down-arrow {{
    width: 0; height: 0; border-left: 5px solid transparent; border-right: 5px solid transparent;
    border-top: 6px solid {C_MUTED}; margin-right: 8px;
}}
QComboBox QAbstractItemView {{
    background-color: #FFFFFF; color: {C_TEXTO}; border: 1px solid {C_BORDE_INPUT};
    selection-background-color: #DBEAFE; selection-color: {C_TEXTO}; outline: none;
}}
QCheckBox {{ color: #334155; spacing: 8px; }}
QCheckBox::indicator {{ width: 18px; height: 18px; border-radius: 4px; border: 1px solid {C_BORDE_INPUT}; background: #FFFFFF; }}
QCheckBox::indicator:checked {{ background: {C_ACENTO}; border: 1px solid {C_ACENTO}; }}

/* ---- Botones ---- */
QPushButton {{ border-radius: 6px; padding: 9px 18px; font-weight: 600; border: 1px solid #AAB6C8; background: #FFFFFF; color: #1E293B; }}
QPushButton:hover {{ background: #F1F5F9; border: 1px solid {C_BORDE_INPUT}; }}
QPushButton:pressed {{ background: #E2E8F0; }}
QPushButton:disabled {{ color: #94A3B8; background: #F1F5F9; border: 1px solid #E2E8F0; }}
QPushButton[variante="primario"] {{ background: {C_ACENTO}; color: #FFFFFF; border: 1px solid {C_ACENTO}; }}
QPushButton[variante="primario"]:hover {{ background: {C_ACENTO_OSC}; border: 1px solid {C_ACENTO_OSC}; }}
QPushButton[variante="primario"]:disabled {{ background: #B6C6EE; color: #FFFFFF; border: 1px solid #B6C6EE; }}
QPushButton[variante="peligro"] {{ background: #FEF2F2; color: #991B1B; border: 1px solid #FCA5A5; }}
QPushButton[variante="peligro"]:hover {{ background: #FEE2E2; }}
QPushButton[variante="peligro"]:disabled {{ color: #94A3B8; background: #F1F5F9; border: 1px solid #E2E8F0; }}
QPushButton[variante="fantasma"] {{ background: #FFFFFF; color: #334155; border: 1px solid #AAB6C8; }}
QPushButton[variante="fantasma"]:hover {{ background: #F1F5F9; border: 1px solid {C_BORDE_INPUT}; }}
QPushButton[variante="chip"] {{ background: #FFFFFF; color: #334155; border: 1px solid #AAB6C8; padding: 8px 16px; }}
QPushButton[variante="chip"]:hover {{ background: #F1F5F9; }}
QPushButton[variante="chip"]:checked {{ background: {C_ACENTO}; color: #FFFFFF; border: 1px solid {C_ACENTO}; }}
QPushButton[variante="lista"] {{ text-align: left; background: #FFFFFF; color: {C_TEXTO}; border: 1px solid {C_BORDE}; font-weight: 500; padding: 10px 14px; }}
QPushButton[variante="lista"]:hover {{ background: #F8FAFC; border: 1px solid {C_BORDE_INPUT}; }}
QPushButton[variante="lista"]:checked {{ background: {C_ACENTO_SUAVE}; border: 1px solid {C_ACENTO}; color: {C_ACENTO_OSC}; font-weight: 600; }}
QPushButton[variante="salir"] {{ background: transparent; color: #E2E8F0; border: 1px solid rgba(255, 255, 255, 0.30); }}
QPushButton[variante="salir"]:hover {{ background: rgba(255, 255, 255, 0.12); border: 1px solid rgba(255, 255, 255, 0.55); }}
QPushButton:focus {{ border: 2px solid {C_ACENTO}; padding: 8px 17px; }}
QPushButton[variante="salir"]:focus {{ border: 2px solid #93C5FD; }}
QPushButton#Nav {{ text-align: left; padding: 13px 18px; border: none; border-left: 4px solid transparent; border-radius: 0px; background: transparent; color: #CBD5E1; font-size: 14px; font-weight: 500; }}
QPushButton#Nav:hover {{ background: rgba(255, 255, 255, 0.08); color: #FFFFFF; border: none; border-left: 4px solid transparent; }}
QPushButton#Nav:checked {{ background: rgba(255, 255, 255, 0.13); border-left: 4px solid #60A5FA; color: #FFFFFF; font-weight: 700; }}
QPushButton#Nav:focus {{ background: rgba(255, 255, 255, 0.10); border: none; border-left: 4px solid #93C5FD; padding: 13px 18px; }}

/* ---- Tablas ---- */
QTableWidget {{
    background-color: #FFFFFF; alternate-background-color: #F8FAFC; border: 1px solid {C_BORDE};
    border-radius: 8px; gridline-color: transparent; selection-background-color: #DBEAFE;
    selection-color: {C_TEXTO}; outline: none;
}}
QTableWidget::item {{ padding: 6px; border-bottom: 1px solid #E8EDF4; }}
QHeaderView::section {{ background-color: #F1F5F9; color: #334155; padding: 12px 10px; font-weight: 700; border: none; border-bottom: 2px solid #CBD5E1; border-right: 1px solid #E2E8F0; }}
QTableCornerButton::section {{ background: #F1F5F9; border: none; }}

/* ---- Scroll ---- */
QScrollArea {{ background: transparent; border: none; }}
QScrollArea > QWidget > QWidget {{ background: transparent; }}
QScrollBar:vertical {{ background: transparent; width: 12px; margin: 2px; }}
QScrollBar::handle:vertical {{ background: #B4BFCE; border-radius: 5px; min-height: 30px; }}
QScrollBar::handle:vertical:hover {{ background: #8A99AE; }}
QScrollBar:horizontal {{ background: transparent; height: 12px; margin: 2px; }}
QScrollBar::handle:horizontal {{ background: #B4BFCE; border-radius: 5px; min-width: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}

QProgressBar {{ background: #E2E8F0; border: none; border-radius: 4px; max-height: 10px; min-height: 10px; }}
QProgressBar::chunk {{ background: {C_ACENTO}; border-radius: 4px; }}
QSplitter::handle {{ background: transparent; }}

/* ---- Filtros de período (botones segmentados) ---- */
QPushButton[variante="seg"] {{ background: #FFFFFF; color: #334155; border: 1px solid #AAB6C8; border-radius: 6px; padding: 8px 18px; font-weight: 600; }}
QPushButton[variante="seg"]:hover {{ background: #F1F5F9; border: 1px solid {C_BORDE_INPUT}; }}
QPushButton[variante="seg"]:checked {{ background: {C_ACENTO}; color: #FFFFFF; border: 1px solid {C_ACENTO}; }}
QPushButton[variante="seg"]:checked:hover {{ background: {C_ACENTO_OSC}; border: 1px solid {C_ACENTO_OSC}; }}
QPushButton[variante="seg"]:focus {{ border: 2px solid {C_ACENTO_OSC}; padding: 7px 17px; }}

/* ---- Calendario ---- */
QCalendarWidget QWidget {{ background-color: #FFFFFF; color: {C_TEXTO}; }}
QCalendarWidget QWidget#qt_calendar_navigationbar {{ background-color: #F1F5F9; border-radius: 6px; }}
QCalendarWidget QToolButton {{ color: {C_TEXTO}; background: transparent; border: none; padding: 6px 10px; font-weight: 700; border-radius: 6px; }}
QCalendarWidget QToolButton:hover {{ background: #E2E8F0; }}
QCalendarWidget QToolButton::menu-indicator {{ image: none; }}
QCalendarWidget QSpinBox {{ background: #FFFFFF; color: {C_TEXTO}; border: 1px solid {C_BORDE_INPUT}; border-radius: 6px; padding: 2px 6px; }}
QCalendarWidget QMenu {{ background-color: #FFFFFF; color: {C_TEXTO}; border: 1px solid {C_BORDE}; }}
QCalendarWidget QAbstractItemView {{
    background-color: #FFFFFF; color: {C_TEXTO}; selection-background-color: {C_ACENTO};
    selection-color: #FFFFFF; outline: none; border: none;
}}
QCalendarWidget QAbstractItemView:disabled {{ color: #94A3B8; }}
"""


# ======================================================================
#  UTILIDADES DE INTERFAZ
# ======================================================================
def crear_boton(texto, variante="secundario", checkable=False, alto=40):
    b = QPushButton(texto)
    b.setProperty("variante", variante)
    b.setCursor(Qt.PointingHandCursor)
    b.setMinimumHeight(alto)
    b.setCheckable(checkable)
    return b


def crear_tarjeta(titulo=None, subtitulo=None):
    marco = QFrame()
    marco.setObjectName("Card")
    lay = QVBoxLayout(marco)
    lay.setContentsMargins(22, 20, 22, 20)
    lay.setSpacing(14)
    if titulo:
        lbl = QLabel(titulo)
        lbl.setObjectName("CardTitle")
        lay.addWidget(lbl)
    if subtitulo:
        sub = QLabel(subtitulo)
        sub.setObjectName("Muted")
        sub.setWordWrap(True)
        lay.addWidget(sub)
    return marco, lay


def etiqueta_campo(texto, ancho=None):
    l = QLabel(texto)
    l.setObjectName("Campo")
    if ancho:
        l.setMinimumWidth(ancho)
    return l


def crear_formulario():
    f = QFormLayout()
    f.setHorizontalSpacing(16)
    f.setVerticalSpacing(14)
    f.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    f.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
    return f


def limpiar_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        w = item.widget()
        if w:
            w.deleteLater()
        elif item.layout():
            limpiar_layout(item.layout())


def estilizar_calendario(cal: QCalendarWidget):
    """Hace legibles las flechas del calendario y deja una cuadrícula limpia."""
    cal.setFirstDayOfWeek(Qt.Monday)
    cal.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
    cal.setHorizontalHeaderFormat(QCalendarWidget.ShortDayNames)
    cal.setGridVisible(False)
    for nombre, simbolo in (("qt_calendar_prevmonth", "‹"), ("qt_calendar_nextmonth", "›")):
        btn = cal.findChild(QToolButton, nombre)
        if btn:
            btn.setIcon(QIcon())
            btn.setText(simbolo)
            btn.setFont(QFont("Segoe UI", 14, QFont.Bold))


COLOR_ESTADO = {"Resuelto": C_VERDE, "En Verificación": C_AMBAR, "Pendiente de Cierre": C_ROJO}
COLOR_PRIORIDAD = {"Alta / Urgente": C_ROJO, "Media-Alta": C_AMBAR}


def llenar_tabla(tabla: QTableWidget, reportes, indices=None):
    """Llena la tabla. `indices` elige qué columnas de to_lista() mostrar."""
    tabla.setRowCount(len(reportes))
    for fila, rep in enumerate(reportes):
        datos = rep.to_lista()
        if indices is not None:
            datos = [datos[i] for i in indices]
        for col, texto in enumerate(datos):
            item = QTableWidgetItem(str(texto))
            item.setTextAlignment(Qt.AlignCenter)
            color = COLOR_ESTADO.get(texto) or COLOR_PRIORIDAD.get(texto)
            if color:
                item.setForeground(QColor(color))
                f = item.font()
                f.setBold(True)
                item.setFont(f)
            tabla.setItem(fila, col, item)


def configurar_tabla(tabla: QTableWidget, stretch_col=None):
    tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
    tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
    tabla.setSelectionMode(QAbstractItemView.SingleSelection)
    tabla.setAlternatingRowColors(True)
    tabla.setShowGrid(False)
    tabla.setFocusPolicy(Qt.StrongFocus)
    tabla.verticalHeader().setVisible(False)
    tabla.verticalHeader().setDefaultSectionSize(44)
    hh = tabla.horizontalHeader()
    hh.setSectionResizeMode(QHeaderView.ResizeToContents)
    if stretch_col is not None:
        hh.setSectionResizeMode(stretch_col, QHeaderView.Stretch)
    hh.setStretchLastSection(False)
    # Dentro de una tarjeta la tabla no necesita un segundo borde
    tabla.setStyleSheet("QTableWidget { border: none; }")


# ======================================================================
#  TARJETA DE TOTAL (clicable)
# ======================================================================
class TarjetaStat(QFrame):
    """Tarjeta de total. Al hacer clic (o con Enter / Espacio) emite `clicked`."""
    clicked = Signal()

    def __init__(self, titulo, color=None):
        super().__init__()
        color = color or C_ACENTO
        self.setObjectName("StatCard")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMinimumHeight(132)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setToolTip("Clic para ver los reportes de este período")
        self.setStyleSheet(
            f"QFrame#StatCard {{ border-top: 4px solid {color}; }}"
            f"QFrame#StatCard:hover {{ background-color: #F8FAFC; border: 1px solid {color}; border-top: 4px solid {color}; }}"
            f"QFrame#StatCard:focus {{ border: 2px solid {color}; border-top: 4px solid {color}; }}"
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 16, 20, 14)
        lay.setSpacing(2)

        lbl_t = QLabel(titulo)
        lbl_t.setObjectName("Campo")
        self.lbl_valor = QLabel("0")
        self.lbl_valor.setStyleSheet(f"font-size: 36px; font-weight: 700; color: {C_TEXTO};")
        self.lbl_detalle = QLabel("")
        self.lbl_detalle.setObjectName("Muted")
        lbl_ver = QLabel("Ver reportes  ›")
        lbl_ver.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: 700;")

        lay.addWidget(lbl_t)
        lay.addWidget(self.lbl_valor)
        lay.addWidget(self.lbl_detalle)
        lay.addStretch()
        lay.addWidget(lbl_ver)

    def set_datos(self, valor, detalle):
        self.lbl_valor.setText(str(valor))
        self.lbl_detalle.setText(detalle)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton and self.rect().contains(e.position().toPoint()):
            self.clicked.emit()
        super().mouseReleaseEvent(e)

    def keyPressEvent(self, e):
        if e.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self.clicked.emit()
        else:
            super().keyPressEvent(e)


# ======================================================================
#  LOGIN
# ======================================================================
class VentanaLogin(QWidget):
    def __init__(self, controlador: ReporteController):
        super().__init__()
        self.controlador = controlador
        self.ventana_principal = None
        self.inicializar_interfaz()

    def inicializar_interfaz(self):
        self.setObjectName("Raiz")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setWindowTitle("GeoLuz - Acceso Administrativo")
        self.setFixedSize(920, 540)

        raiz = QHBoxLayout(self)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.setSpacing(0)

        # ---- Panel de marca (izquierda)
        marca = QFrame()
        marca.setObjectName("PanelMarca")
        lm = QVBoxLayout(marca)
        lm.setContentsMargins(52, 52, 52, 44)
        lm.setSpacing(10)

        sello = QLabel("G")
        sello.setFixedSize(56, 56)
        sello.setAlignment(Qt.AlignCenter)
        sello.setStyleSheet(f"background: {C_ACENTO}; color: #FFFFFF; border-radius: 12px; font-size: 26px; font-weight: 800;")
        lm.addWidget(sello, 0, Qt.AlignLeft)
        lm.addSpacing(16)

        t = QLabel("GEOLUZ")
        t.setStyleSheet("color: #FFFFFF; font-size: 32px; font-weight: 800; letter-spacing: 4px;")
        lm.addWidget(t)
        s = QLabel("Sistema de registro y control de fallas eléctricas en barrios, comarcas y zonas alejadas de Nicaragua.")
        s.setWordWrap(True)
        s.setStyleSheet("color: #CBD5E1; font-size: 14px;")
        lm.addWidget(s)
        lm.addSpacing(22)
        for texto in ("Registro de reportes con fecha y hora exacta",
                      "Totales diarios, semanales, mensuales y anuales",
                      "Selector geográfico por departamento y barrio"):
            l = QLabel("•   " + texto)
            l.setStyleSheet("color: #E2E8F0; font-size: 14px;")
            lm.addWidget(l)
        lm.addStretch()
        pie = QLabel("Panel de Control de Cuadrillas")
        pie.setStyleSheet("color: #93C5FD; font-size: 13px; font-weight: 600;")
        lm.addWidget(pie)

        # ---- Formulario (derecha)
        der = QWidget()
        der.setObjectName("PanelLogin")
        der.setAttribute(Qt.WA_StyledBackground, True)
        ld = QVBoxLayout(der)
        ld.setContentsMargins(56, 56, 56, 56)
        ld.setSpacing(8)

        h = QLabel("Iniciar sesión")
        h.setObjectName("PageTitle")
        ld.addWidget(h)
        hs = QLabel("Ingrese sus credenciales de administrador")
        hs.setObjectName("Muted")
        ld.addWidget(hs)
        ld.addSpacing(22)

        ld.addWidget(etiqueta_campo("Usuario"))
        self.txt_usuario = QLineEdit()
        self.txt_usuario.setPlaceholderText("Nombre de usuario")
        self.txt_usuario.setMinimumHeight(46)
        self.txt_usuario.setAccessibleName("Usuario")
        ld.addWidget(self.txt_usuario)
        ld.addSpacing(8)

        ld.addWidget(etiqueta_campo("Contraseña"))
        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Contraseña")
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setMinimumHeight(46)
        self.txt_password.setAccessibleName("Contraseña")
        ld.addWidget(self.txt_password)

        chk = QCheckBox("Mostrar contraseña")
        chk.toggled.connect(lambda v: self.txt_password.setEchoMode(QLineEdit.Normal if v else QLineEdit.Password))
        ld.addWidget(chk)
        ld.addSpacing(16)

        btn = crear_boton("Ingresar al sistema", "primario", alto=48)
        btn.clicked.connect(self.login_tradicional)
        ld.addWidget(btn)
        ld.addStretch()

        self.txt_usuario.returnPressed.connect(self.txt_password.setFocus)
        self.txt_password.returnPressed.connect(self.login_tradicional)

        raiz.addWidget(marca, 5)
        raiz.addWidget(der, 6)

    def login_tradicional(self):
        user = self.txt_usuario.text().strip()
        pas = self.txt_password.text().strip()
        if not user or not pas:
            QMessageBox.warning(self, "Campos vacíos", "Ingresa tu usuario y contraseña.")
            return
        usuario = self.controlador.autenticar_usuario(user, pas)
        if usuario:
            self.abrir_ventana_principal(usuario)
        else:
            QMessageBox.warning(self, "Acceso denegado",
                                "Credenciales incorrectas.\n(Verifica también que MySQL esté encendido.)")

    def abrir_ventana_principal(self, usuario):
        self.ventana_principal = VentanaGeoLuz(self.controlador, usuario, self)
        self.ventana_principal.show()
        self.hide()

    def mostrar_de_nuevo(self):
        self.txt_password.clear()
        self.show()
        self.txt_usuario.setFocus()


# ======================================================================
#  VENTANA PRINCIPAL
# ======================================================================
PERIODOS = [
    ("Todos", "todos"),
    ("Hoy", "hoy"),
    ("Esta semana", "semana"),
    ("Este mes", "mes"),
    ("Este año", "anio"),
    ("Fecha específica", "fecha"),
]
TITULO_PERIODO = {
    "todos": "Todos los reportes",
    "hoy": "Reportes de hoy",
    "semana": "Reportes de esta semana",
    "mes": "Reportes de este mes",
    "anio": "Reportes de este año",
    "fecha": "Reportes de una fecha",
}

TITULOS_PAGINAS = [
    ("Panel de control", "Resumen general de reportes y actividad"),
    ("Registro de reporte", "Crear, modificar o eliminar un reporte de falla"),
    ("Reportes registrados", "Consulta, filtra y exporta los reportes guardados"),
    ("Selector geográfico", "Elige el departamento y el barrio o comarca afectada"),
]


def texto_reportes(n):
    return "1 reporte" if n == 1 else f"{n} reportes"


class VentanaGeoLuz(QWidget):
    def __init__(self, controlador: ReporteController, usuario, ventana_login=None):
        super().__init__()
        self.controlador = controlador
        self.usuario_actual = usuario
        self.ventana_login = ventana_login
        self.reportes_cache = []
        self.reportes_visibles = []
        self.id_en_edicion = None
        self.periodo_actual = "todos"
        self.inicializar_interfaz()
        self.cargar_datos_iniciales()

        self.timer_reloj = QTimer(self)
        self.timer_reloj.timeout.connect(self.actualizar_reloj)
        self.timer_reloj.start(1000)
        self.actualizar_reloj()

    # ------------------------------------------------------------------
    #  ESTRUCTURA GENERAL
    # ------------------------------------------------------------------
    def inicializar_interfaz(self):
        self.setObjectName("Raiz")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setWindowTitle(f"GeoLuz | Conectado como: {self.usuario_actual.nombre_completo}")
        self.resize(1440, 880)
        self.setMinimumSize(1200, 720)

        raiz = QHBoxLayout(self)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.setSpacing(0)
        raiz.addWidget(self._crear_sidebar())

        contenido = QWidget()
        lc = QVBoxLayout(contenido)
        lc.setContentsMargins(32, 26, 32, 24)
        lc.setSpacing(20)

        # Cabecera de página (sin caja: título a la izquierda, reloj a la derecha)
        cab = QHBoxLayout()
        col = QVBoxLayout()
        col.setSpacing(2)
        self.lbl_titulo_pagina = QLabel("")
        self.lbl_titulo_pagina.setObjectName("PageTitle")
        self.lbl_sub_pagina = QLabel("")
        self.lbl_sub_pagina.setObjectName("Muted")
        col.addWidget(self.lbl_titulo_pagina)
        col.addWidget(self.lbl_sub_pagina)
        cab.addLayout(col)
        cab.addStretch()
        self.lbl_reloj = QLabel("")
        self.lbl_reloj.setObjectName("Reloj")
        cab.addWidget(self.lbl_reloj, 0, Qt.AlignTop)
        lc.addLayout(cab)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._crear_pagina_dashboard())
        self.stack.addWidget(self._crear_pagina_formulario())
        self.stack.addWidget(self._crear_pagina_registros())
        self.stack.addWidget(self._crear_pagina_selector())
        lc.addWidget(self.stack, 1)

        raiz.addWidget(contenido, 1)
        self.ir_a_pagina(0)

    def _crear_sidebar(self):
        side = QFrame()
        side.setObjectName("Sidebar")
        side.setFixedWidth(264)
        ls = QVBoxLayout(side)
        ls.setContentsMargins(0, 28, 0, 20)
        ls.setSpacing(2)

        cab = QVBoxLayout()
        cab.setContentsMargins(26, 0, 26, 0)
        cab.setSpacing(2)
        marca = QLabel("GEOLUZ")
        marca.setObjectName("Brand")
        marca.setStyleSheet("color: #FFFFFF; font-size: 22px; font-weight: 800; letter-spacing: 3px;")
        sub = QLabel("Control de fallas eléctricas")
        sub.setStyleSheet("color: #94A3B8; font-size: 12px;")
        cab.addWidget(marca)
        cab.addWidget(sub)
        ls.addLayout(cab)
        ls.addSpacing(30)

        etiqueta = QLabel("NAVEGACIÓN")
        etiqueta.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: 700; letter-spacing: 2px; padding-left: 26px; padding-bottom: 6px;")
        ls.addWidget(etiqueta)

        self.grupo_nav = QButtonGroup(self)
        self.grupo_nav.setExclusive(True)
        self.botones_nav = []
        for i, texto in enumerate(["Panel de control", "Nuevo reporte",
                                   "Reportes registrados", "Selector geográfico"]):
            b = QPushButton(texto)
            b.setObjectName("Nav")
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda checked=False, idx=i: self.ir_a_pagina(idx))
            self.grupo_nav.addButton(b)
            self.botones_nav.append(b)
            ls.addWidget(b)

        ls.addStretch()

        pie = QVBoxLayout()
        pie.setContentsMargins(16, 0, 16, 0)
        pie.setSpacing(10)
        tj = QFrame()
        tj.setObjectName("UserCard")
        lt = QVBoxLayout(tj)
        lt.setContentsMargins(14, 12, 14, 12)
        lt.setSpacing(2)
        lbl_rol = QLabel("ADMINISTRADOR")
        lbl_rol.setStyleSheet("color: #93C5FD; font-size: 11px; font-weight: 700; letter-spacing: 1px;")
        lbl_nom = QLabel(self.usuario_actual.nombre_completo)
        lbl_nom.setWordWrap(True)
        lbl_nom.setStyleSheet("color: #FFFFFF; font-weight: 600;")
        lt.addWidget(lbl_rol)
        lt.addWidget(lbl_nom)
        pie.addWidget(tj)

        btn_salir = crear_boton("Cerrar sesión", "salir")
        btn_salir.clicked.connect(self.cerrar_sesion)
        pie.addWidget(btn_salir)
        ls.addLayout(pie)
        return side

    def ir_a_pagina(self, idx):
        self.stack.setCurrentIndex(idx)
        self.botones_nav[idx].setChecked(True)
        titulo, sub = TITULOS_PAGINAS[idx]
        self.lbl_titulo_pagina.setText(titulo)
        self.lbl_sub_pagina.setText(sub)
        if idx in (0, 2):
            self.refrescar_todo()

    def actualizar_reloj(self):
        ahora = datetime.now()
        hora = formatear_fecha_hora(ahora).split(" ", 1)[1]
        self.lbl_reloj.setText(f"{fecha_larga(ahora)}   |   {hora}")

    def cerrar_sesion(self):
        self.timer_reloj.stop()
        if self.ventana_login:
            self.ventana_login.mostrar_de_nuevo()
        self.close()

    # ------------------------------------------------------------------
    #  PÁGINA 0: PANEL DE CONTROL
    # ------------------------------------------------------------------
    def _crear_pagina_dashboard(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        cont = QWidget()
        lay = QVBoxLayout(cont)
        lay.setContentsMargins(0, 0, 8, 0)
        lay.setSpacing(18)

        # Totales por período (cada tarjeta abre la lista filtrada)
        fila = QHBoxLayout()
        fila.setSpacing(16)
        self.stat_hoy = TarjetaStat("HOY")
        self.stat_semana = TarjetaStat("ESTA SEMANA")
        self.stat_mes = TarjetaStat("ESTE MES")
        self.stat_anio = TarjetaStat("ESTE AÑO")
        self.stat_total = TarjetaStat("TOTAL GENERAL", C_NAVY)
        for tarjeta, clave in ((self.stat_hoy, "hoy"), (self.stat_semana, "semana"),
                               (self.stat_mes, "mes"), (self.stat_anio, "anio"),
                               (self.stat_total, "todos")):
            tarjeta.clicked.connect(lambda c=clave: self.abrir_periodo(c))
            fila.addWidget(tarjeta, 1)
        lay.addLayout(fila)

        # Tipos de falla + calendario
        media = QHBoxLayout()
        media.setSpacing(18)

        card_tipo, l_tipo = crear_tarjeta("Reportes por tipo de falla",
                                          "Distribución de todos los reportes registrados.")
        self.layout_barras = QVBoxLayout()
        self.layout_barras.setSpacing(14)
        l_tipo.addSpacing(4)
        l_tipo.addLayout(self.layout_barras)
        l_tipo.addStretch()
        self.lbl_estados = QLabel("")
        self.lbl_estados.setTextFormat(Qt.RichText)
        self.lbl_estados.setWordWrap(True)
        l_tipo.addWidget(self.lbl_estados)
        media.addWidget(card_tipo, 3)

        card_cal, l_cal = crear_tarjeta("Calendario de reportes",
                                        "Los días en azul tienen reportes. Haz clic en uno para verlos.")
        self.calendario = QCalendarWidget()
        estilizar_calendario(self.calendario)
        self.calendario.setMinimumHeight(260)
        self.calendario.clicked.connect(lambda qd: self.abrir_periodo("fecha", qd))
        l_cal.addWidget(self.calendario)
        media.addWidget(card_cal, 2)
        lay.addLayout(media)

        # Últimos reportes
        card_rec, l_rec = crear_tarjeta("Últimos reportes registrados")
        self.tabla_recientes = QTableWidget()
        self.tabla_recientes.setColumnCount(5)
        self.tabla_recientes.setHorizontalHeaderLabels(
            ["ID", "Fecha y hora", "Ubicación", "Tipo de falla", "Estado"])
        configurar_tabla(self.tabla_recientes, stretch_col=2)
        self.tabla_recientes.setMinimumHeight(300)
        l_rec.addWidget(self.tabla_recientes)
        pie = QHBoxLayout()
        pie.addStretch()
        btn_todos = crear_boton("Ver todos los reportes", "fantasma", alto=38)
        btn_todos.clicked.connect(lambda: self.abrir_periodo("todos"))
        pie.addWidget(btn_todos)
        l_rec.addLayout(pie)
        lay.addWidget(card_rec)
        lay.addStretch()

        scroll.setWidget(cont)
        return scroll

    def refrescar_dashboard(self):
        est = self.controlador.estadisticas()
        r = est["rangos"]
        self.stat_hoy.set_datos(est["hoy"], fecha_larga(r["hoy"][0]))
        sem_ini, sem_fin = r["semana"][0], r["semana"][1] - timedelta(days=1)
        self.stat_semana.set_datos(est["semana"], f"{sem_ini:%d/%m} al {sem_fin:%d/%m/%Y}")
        self.stat_mes.set_datos(est["mes"], f"{MESES[r['mes'][0].month - 1]} {r['mes'][0].year}")
        self.stat_anio.set_datos(est["anio"], f"Año {r['anio'][0].year}")
        self.stat_total.set_datos(est["total"], "Todos los registros")

        # Barras por tipo de falla
        por_tipo = self.controlador.conteo_por_tipo()
        tipos = list(TIPOS_FALLA) + [t for t in por_tipo if t not in TIPOS_FALLA]
        total = max(est["total"], 1)
        limpiar_layout(self.layout_barras)
        for t in tipos:
            n = por_tipo.get(t, 0)
            fila = QHBoxLayout()
            fila.setContentsMargins(0, 0, 0, 0)
            nombre = QLabel(t)
            nombre.setMinimumWidth(200)
            barra = QProgressBar()
            barra.setMaximum(total)
            barra.setValue(n)
            barra.setTextVisible(False)
            cant = QLabel(f"{n}")
            cant.setMinimumWidth(32)
            cant.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            cant.setStyleSheet(f"font-weight: 700; color: {C_TEXTO};")
            fila.addWidget(nombre)
            fila.addWidget(barra, 1)
            fila.addWidget(cant)
            caja = QWidget()
            caja.setLayout(fila)
            self.layout_barras.addWidget(caja)

        por_estado = self.controlador.conteo_por_estado()
        self.lbl_estados.setText("&nbsp;&nbsp;|&nbsp;&nbsp;".join(
            f'<span style="color:{COLOR_ESTADO[e]};"><b>{e}:</b> {por_estado.get(e, 0)}</span>' for e in ESTADOS))

        # Calendario: resaltar días con reportes
        self.calendario.setDateTextFormat(QDate(), QTextCharFormat())
        fmt = QTextCharFormat()
        fmt.setBackground(QBrush(QColor("#BFDBFE")))
        fmt.setForeground(QBrush(QColor("#1E3A8A")))
        fmt.setFontWeight(QFont.Bold)
        for dia in self.controlador.conteo_por_dia():
            self.calendario.setDateTextFormat(QDate(dia.year, dia.month, dia.day), fmt)

        llenar_tabla(self.tabla_recientes, self.reportes_cache[:6], indices=[0, 1, 4, 5, 8])

    def abrir_periodo(self, clave, fecha=None):
        """Abre la lista de reportes filtrada por período ('hoy', 'semana', 'mes', 'anio', 'fecha', 'todos')."""
        self.set_periodo(clave, fecha)
        self.ir_a_pagina(2)

    # ------------------------------------------------------------------
    #  PÁGINA 1: FORMULARIO
    # ------------------------------------------------------------------
    def _crear_pagina_formulario(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        cont = QWidget()
        lay = QVBoxLayout(cont)
        lay.setContentsMargins(0, 0, 8, 0)
        lay.setSpacing(16)

        # Aviso de modo (nuevo / edición)
        self.aviso_modo = QFrame()
        self.aviso_modo.setObjectName("Aviso")
        la = QHBoxLayout(self.aviso_modo)
        la.setContentsMargins(18, 12, 18, 12)
        self.lbl_modo = QLabel("")
        self.lbl_modo.setStyleSheet("color: #1E3A8A; font-weight: 600;")
        la.addWidget(self.lbl_modo)
        lay.addWidget(self.aviso_modo)

        # Campos
        self.txt_id = QLineEdit()
        self.txt_id.setPlaceholderText("Ej: REP-203")
        self.txt_cuadrilla = QLineEdit()
        self.txt_cuadrilla.setPlaceholderText("Nombre de la cuadrilla")
        self.txt_telefono = QLineEdit()
        self.txt_telefono.setPlaceholderText("Mínimo 8 dígitos")
        self.txt_telefono.setMaxLength(15)

        self.dt_fecha = QDateTimeEdit(QDateTime.currentDateTime())
        self.dt_fecha.setCalendarPopup(True)
        self.dt_fecha.setDisplayFormat("dd/MM/yyyy   hh:mm:ss AP")
        estilizar_calendario(self.dt_fecha.calendarWidget())
        self.dt_fecha.dateTimeChanged.connect(self.actualizar_fecha_larga)
        self.lbl_fecha_larga = QLabel("")
        self.lbl_fecha_larga.setObjectName("Muted")
        btn_ahora = crear_boton("Fecha actual", "fantasma", alto=40)
        btn_ahora.clicked.connect(self.poner_fecha_ahora)

        self.cb_departamento = QComboBox()
        self.cb_departamento.addItems(list(DEPARTAMENTOS_NICARAGUA.keys()))
        self.cb_departamento.currentIndexChanged.connect(self.actualizar_barrios)
        self.cb_barrio = QComboBox()

        self.cb_tipo_falla = QComboBox()
        self.cb_tipo_falla.addItems(TIPOS_FALLA)
        self.cb_tipo_falla.currentTextChanged.connect(self.actualizar_prioridad)
        self.lbl_prioridad = QLabel("")
        self.lbl_prioridad.setStyleSheet("font-weight: 700;")
        self.cb_estado = QComboBox()
        self.cb_estado.addItems(ESTADOS)
        self.txt_solucion = QTextEdit()
        self.txt_solucion.setMinimumHeight(130)
        self.txt_solucion.setPlaceholderText("Detalle del trabajo realizado por la cuadrilla...")

        def nuevo_form():
            f = QFormLayout()
            f.setContentsMargins(0, 4, 0, 0)
            f.setVerticalSpacing(10)
            f.setRowWrapPolicy(QFormLayout.WrapAllRows)
            f.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
            return f

        # Tarjeta 1: datos del reporte
        c1, l1 = crear_tarjeta("Datos del reporte")
        f1 = nuevo_form()
        f1.addRow(etiqueta_campo("ID del reporte"), self.txt_id)
        f1.addRow(etiqueta_campo("Cuadrilla"), self.txt_cuadrilla)
        f1.addRow(etiqueta_campo("Teléfono del líder"), self.txt_telefono)
        fila_fecha = QHBoxLayout()
        fila_fecha.setSpacing(8)
        fila_fecha.addWidget(self.dt_fecha, 1)
        fila_fecha.addWidget(btn_ahora)
        caja_fecha = QWidget()
        lf = QVBoxLayout(caja_fecha)
        lf.setContentsMargins(0, 0, 0, 0)
        lf.setSpacing(4)
        lf.addLayout(fila_fecha)
        lf.addWidget(self.lbl_fecha_larga)
        f1.addRow(etiqueta_campo("Fecha y hora exacta"), caja_fecha)
        l1.addLayout(f1)

        # Tarjeta 2: ubicación
        c2, l2 = crear_tarjeta("Ubicación")
        f2 = nuevo_form()
        f2.addRow(etiqueta_campo("Departamento"), self.cb_departamento)
        f2.addRow(etiqueta_campo("Barrio, comarca o sector"), self.cb_barrio)
        l2.addLayout(f2)
        btn_sel = crear_boton("Elegir en el selector geográfico", "fantasma", alto=40)
        btn_sel.clicked.connect(lambda: self.ir_a_pagina(3))
        l2.addWidget(btn_sel)

        # Tarjeta 3: detalle de la falla
        c3, l3 = crear_tarjeta("Detalle de la falla")
        f3 = nuevo_form()
        f3.addRow(etiqueta_campo("Tipo de falla"), self.cb_tipo_falla)
        f3.addRow(etiqueta_campo("Prioridad"), self.lbl_prioridad)
        f3.addRow(etiqueta_campo("Estado"), self.cb_estado)
        f3.addRow(etiqueta_campo("Solución aplicada"), self.txt_solucion)
        l3.addLayout(f3)

        izq = QVBoxLayout()
        izq.setSpacing(16)
        izq.addWidget(c1)
        izq.addWidget(c2)
        izq.addStretch()
        der = QVBoxLayout()
        der.setSpacing(16)
        der.addWidget(c3)
        der.addStretch()
        cols = QHBoxLayout()
        cols.setSpacing(16)
        cols.addLayout(izq, 1)
        cols.addLayout(der, 1)
        lay.addLayout(cols)

        # Botonera alineada a la derecha
        self.btn_guardar = crear_boton("Guardar reporte", "primario", alto=44)
        self.btn_guardar.clicked.connect(self.evento_guardar)
        self.btn_actualizar = crear_boton("Guardar cambios", "exito", alto=44)
        self.btn_actualizar.clicked.connect(self.evento_actualizar)
        self.btn_eliminar = crear_boton("Eliminar", "peligro", alto=44)
        self.btn_eliminar.clicked.connect(self.evento_eliminar)
        self.btn_limpiar = crear_boton("Limpiar / Nuevo", "fantasma", alto=44)
        self.btn_limpiar.clicked.connect(self.limpiar_campos)
        botones = QHBoxLayout()
        botones.setSpacing(10)
        botones.addStretch()
        for b in (self.btn_limpiar, self.btn_eliminar, self.btn_actualizar, self.btn_guardar):
            b.setMinimumWidth(160)
            botones.addWidget(b)
        lay.addLayout(botones)
        lay.addStretch()

        scroll.setWidget(cont)
        self.actualizar_barrios()
        self.actualizar_prioridad()
        self.actualizar_fecha_larga()
        self._actualizar_modo()
        return scroll

    def actualizar_fecha_larga(self):
        d = self.dt_fecha.dateTime().toPython()
        self.lbl_fecha_larga.setText(fecha_larga(d))

    def poner_fecha_ahora(self):
        self.dt_fecha.setDateTime(QDateTime.currentDateTime())

    def actualizar_prioridad(self):
        p = calcular_prioridad(self.cb_tipo_falla.currentText())
        color = C_ROJO if "Alta" in p else (C_AMBAR if "Media" in p else C_VERDE)
        self.lbl_prioridad.setText(p)
        self.lbl_prioridad.setStyleSheet(f"font-weight: 700; color: {color};")

    def actualizar_barrios(self):
        self.cb_barrio.clear()
        depto = self.cb_departamento.currentText()
        if depto in DEPARTAMENTOS_NICARAGUA:
            self.cb_barrio.addItems(DEPARTAMENTOS_NICARAGUA[depto])

    def _actualizar_modo(self):
        editando = self.id_en_edicion is not None
        self.txt_id.setEnabled(not editando)
        self.btn_guardar.setEnabled(not editando)
        self.btn_actualizar.setEnabled(editando)
        self.btn_eliminar.setEnabled(editando)
        if editando:
            self.lbl_modo.setText(f"Editando el reporte {self.id_en_edicion}")
        else:
            self.lbl_modo.setText("Nuevo reporte")

    def _leer_formulario(self):
        """Valida y devuelve los datos del formulario, o None si hay errores."""
        id_rep = self.txt_id.text().strip()
        cuadrilla = self.txt_cuadrilla.text().strip()
        tel = self.txt_telefono.text().strip()
        depto = self.cb_departamento.currentText()
        barrio = self.cb_barrio.currentText().strip()

        if not id_rep or not cuadrilla or not tel or not barrio:
            QMessageBox.warning(self, "Campos incompletos",
                                "Completa ID, cuadrilla, teléfono y selecciona el barrio o sector.")
            return None
        if not re.fullmatch(r"[0-9+\-\s]{8,15}", tel):
            QMessageBox.warning(self, "Teléfono inválido",
                                "El teléfono debe tener entre 8 y 15 dígitos (puede incluir + o -).")
            return None
        return {
            "id_reporte": id_rep,
            "cuadrilla": cuadrilla,
            "telefono_lider": tel,
            "comarca_ubicacion": f"{depto} - {barrio}",
            "tipo_falla": self.cb_tipo_falla.currentText(),
            "solucion_aplicada": self.txt_solucion.toPlainText().strip(),
            "estado": self.cb_estado.currentText(),
            "fecha_hora": self.dt_fecha.dateTime().toPython().replace(microsecond=0),
        }

    def evento_guardar(self):
        datos = self._leer_formulario()
        if not datos:
            return
        try:
            self.controlador.agregar_reporte(**datos)
            QMessageBox.information(self, "Éxito", "Reporte registrado correctamente en la base de datos.")
            self.limpiar_campos()
            self.refrescar_todo()
        except Exception as e:
            QMessageBox.critical(self, "Error de base de datos", str(e))

    def evento_actualizar(self):
        if self.id_en_edicion is None:
            QMessageBox.warning(self, "Aviso", "Selecciona un reporte en «Reportes registrados» para modificarlo.")
            return
        datos = self._leer_formulario()
        if not datos:
            return
        try:
            self.controlador.actualizar_reporte(**datos)
            QMessageBox.information(self, "Éxito", "Reporte actualizado correctamente.")
            self.limpiar_campos()
            self.refrescar_todo()
        except Exception as e:
            QMessageBox.critical(self, "Error de base de datos", str(e))

    def evento_eliminar(self):
        if self.id_en_edicion is None:
            QMessageBox.warning(self, "Aviso", "Selecciona un reporte para eliminarlo.")
            return
        self._eliminar_id(self.id_en_edicion)

    def _eliminar_id(self, id_rep):
        resp = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Está seguro de eliminar el reporte «{id_rep}»?\nEsta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if resp != QMessageBox.Yes:
            return
        try:
            self.controlador.eliminar_reporte(id_rep)
            QMessageBox.information(self, "Éxito", "Registro eliminado correctamente.")
            if self.id_en_edicion and self.id_en_edicion.lower() == id_rep.lower():
                self.limpiar_campos()
            self.refrescar_todo()
        except Exception as e:
            QMessageBox.critical(self, "Error de base de datos", str(e))

    def limpiar_campos(self):
        self.id_en_edicion = None
        self.txt_id.setText(self.controlador.siguiente_id())
        self.txt_cuadrilla.clear()
        self.txt_telefono.clear()
        self.cb_departamento.setCurrentIndex(0)
        self.actualizar_barrios()
        self.cb_tipo_falla.setCurrentIndex(0)
        self.cb_estado.setCurrentIndex(0)
        self.txt_solucion.clear()
        self.poner_fecha_ahora()
        self.tabla.clearSelection()
        self._actualizar_modo()

    def cargar_en_formulario(self, reporte):
        self.id_en_edicion = reporte.id_reporte
        self.txt_id.setText(reporte.id_reporte)
        self.txt_cuadrilla.setText(reporte.cuadrilla)
        self.txt_telefono.setText(reporte.telefono_lider)

        partes = reporte.comarca_ubicacion.split(" - ", 1)
        if len(partes) == 2:
            depto, barrio = partes
            idx = self.cb_departamento.findText(depto)
            if idx >= 0:
                self.cb_departamento.setCurrentIndex(idx)
            idx_b = self.cb_barrio.findText(barrio)
            if idx_b < 0:                      # ubicación antigua que no está en la lista
                self.cb_barrio.addItem(barrio)
                idx_b = self.cb_barrio.count() - 1
            self.cb_barrio.setCurrentIndex(idx_b)

        self.cb_tipo_falla.setCurrentText(reporte.tipo_falla)
        self.cb_estado.setCurrentText(reporte.estado)
        self.txt_solucion.setPlainText(reporte.solucion_aplicada)
        f = reporte.fecha_hora
        self.dt_fecha.setDateTime(QDateTime(QDate(f.year, f.month, f.day), QTime(f.hour, f.minute, f.second)))
        self._actualizar_modo()
        self.ir_a_pagina(1)

    # ------------------------------------------------------------------
    #  PÁGINA 2: REPORTES REGISTRADOS
    # ------------------------------------------------------------------
    COLUMNAS_TABLA = [0, 1, 2, 4, 5, 6, 8]     # ID, fecha, cuadrilla, ubicación, tipo, prioridad, estado

    def _crear_pagina_registros(self):
        self.periodo_actual = "todos"
        pagina = QWidget()
        lay = QVBoxLayout(pagina)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(16)

        card, lc = crear_tarjeta()
        lc.setSpacing(14)

        # Fila 1: período
        fila_p = QHBoxLayout()
        fila_p.setSpacing(8)
        lbl_p = etiqueta_campo("PERÍODO")
        lbl_p.setMinimumWidth(70)
        fila_p.addWidget(lbl_p)
        self.grupo_periodo = QButtonGroup(self)
        self.grupo_periodo.setExclusive(True)
        self.botones_periodo = {}
        for texto, clave in (("Todos", "todos"), ("Hoy", "hoy"), ("Semana", "semana"),
                             ("Mes", "mes"), ("Año", "anio"), ("Fecha", "fecha")):
            b = crear_boton(texto, "seg", checkable=True, alto=40)
            b.clicked.connect(lambda checked=False, c=clave: self.set_periodo(c))
            self.grupo_periodo.addButton(b)
            self.botones_periodo[clave] = b
            fila_p.addWidget(b)
        self.botones_periodo["todos"].setChecked(True)

        self.de_dia = QDateEdit(QDate.currentDate())
        self.de_dia.setCalendarPopup(True)
        self.de_dia.setDisplayFormat("dd/MM/yyyy")
        self.de_dia.setMinimumHeight(40)
        self.de_dia.setMinimumWidth(140)
        self.de_dia.setEnabled(False)
        estilizar_calendario(self.de_dia.calendarWidget())
        self.de_dia.dateChanged.connect(self.aplicar_filtros)
        fila_p.addWidget(self.de_dia)
        fila_p.addStretch()
        lc.addLayout(fila_p)

        # Fila 2: búsqueda y acciones
        fila_b = QHBoxLayout()
        fila_b.setSpacing(10)
        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Buscar por ID, cuadrilla, ubicación, tipo o estado...")
        self.txt_buscar.setMinimumHeight(42)
        self.txt_buscar.setClearButtonEnabled(True)
        self.txt_buscar.textChanged.connect(self.aplicar_filtros)
        btn_editar = crear_boton("Editar", "exito", alto=42)
        btn_editar.clicked.connect(self.editar_seleccionado)
        btn_borrar = crear_boton("Eliminar", "peligro", alto=42)
        btn_borrar.clicked.connect(self.eliminar_seleccionado)
        btn_csv = crear_boton("Exportar CSV", "fantasma", alto=42)
        btn_csv.clicked.connect(self.exportar_csv)
        fila_b.addWidget(self.txt_buscar, 1)
        fila_b.addWidget(btn_editar)
        fila_b.addWidget(btn_borrar)
        fila_b.addWidget(btn_csv)
        lc.addLayout(fila_b)
        lay.addWidget(card)

        # Resumen del filtro
        self.lbl_conteo = QLabel("")
        self.lbl_conteo.setStyleSheet(f"color: {C_TEXTO}; font-size: 14px; font-weight: 600;")
        lay.addWidget(self.lbl_conteo)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(len(self.COLUMNAS_TABLA))
        self.tabla.setHorizontalHeaderLabels(
            ["ID", "Fecha y hora", "Cuadrilla", "Ubicación", "Tipo de falla", "Prioridad", "Estado"])
        configurar_tabla(self.tabla, stretch_col=3)
        self.tabla.itemDoubleClicked.connect(lambda _item: self.editar_seleccionado())
        lay.addWidget(self.tabla, 1)

        hint = QLabel("Doble clic en una fila para editarla. Pasa el cursor sobre una fila para ver el teléfono y la solución aplicada.")
        hint.setObjectName("Muted")
        lay.addWidget(hint)
        self.reportes_visibles = []
        return pagina

    def set_periodo(self, clave, fecha=None):
        """Cambia el filtro de período y actualiza botones, selector de fecha y tabla."""
        self.periodo_actual = clave
        self.botones_periodo[clave].setChecked(True)
        if fecha is not None:
            self.de_dia.blockSignals(True)
            self.de_dia.setDate(fecha)
            self.de_dia.blockSignals(False)
        self.de_dia.setEnabled(clave == "fecha")
        self.aplicar_filtros()

    def aplicar_filtros(self, *_):
        texto = self.txt_buscar.text().strip().lower()
        clave = self.periodo_actual
        ini = fin = None
        if clave == "fecha":
            d = self.de_dia.date().toPython()
            ini = datetime(d.year, d.month, d.day)
            fin = ini + timedelta(days=1)
        elif clave in ("hoy", "semana", "mes", "anio"):
            ini, fin = rango_periodo(clave)

        visibles = []
        for r in self.reportes_cache:
            if ini and not (ini <= r.fecha_hora < fin):
                continue
            if texto and texto not in " ".join(r.to_lista()).lower():
                continue
            visibles.append(r)

        self.reportes_visibles = visibles
        llenar_tabla(self.tabla, visibles, indices=self.COLUMNAS_TABLA)
        for fila, r in enumerate(visibles):
            tip = f"Teléfono del líder: {r.telefono_lider}\nSolución aplicada: {r.solucion_aplicada or '—'}"
            for col in range(self.tabla.columnCount()):
                it = self.tabla.item(fila, col)
                if it:
                    it.setToolTip(tip)

        nombres = {"todos": "Todos los registros", "hoy": "Hoy", "semana": "Esta semana",
                   "mes": "Este mes", "anio": "Este año", "fecha": "Fecha seleccionada"}
        titulo = nombres.get(clave, "")
        if ini:
            ultimo = fin - timedelta(days=1)
            rango = f"{ini:%d/%m/%Y}" if ini.date() == ultimo.date() else f"{ini:%d/%m/%Y} al {ultimo:%d/%m/%Y}"
            titulo += f"  ({rango})"
        if visibles:
            self.lbl_conteo.setText(f"{titulo}: {len(visibles)} reporte(s) de {len(self.reportes_cache)} en total")
        else:
            self.lbl_conteo.setText(f"{titulo}: no hay reportes en este período")

    def _id_seleccionado(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            return None
        item = self.tabla.item(fila, 0)
        return item.text() if item else None

    def editar_seleccionado(self):
        id_rep = self._id_seleccionado()
        if not id_rep:
            QMessageBox.warning(self, "Aviso", "Selecciona primero un reporte de la tabla.")
            return
        reporte = self.controlador.buscar_por_id(id_rep)
        if reporte:
            self.cargar_en_formulario(reporte)

    def eliminar_seleccionado(self):
        id_rep = self._id_seleccionado()
        if not id_rep:
            QMessageBox.warning(self, "Aviso", "Selecciona primero un reporte de la tabla.")
            return
        self._eliminar_id(id_rep)

    def exportar_csv(self):
        if not self.reportes_visibles:
            QMessageBox.information(self, "Sin datos", "No hay reportes en la vista actual para exportar.")
            return
        sugerido = f"reportes_geoluz_{datetime.now():%Y%m%d_%H%M%S}.csv"
        ruta, _ = QFileDialog.getSaveFileName(self, "Exportar reportes", sugerido, "Archivos CSV (*.csv)")
        if not ruta:
            return
        try:
            with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f)
                w.writerow(["ID", "Fecha y hora", "Cuadrilla", "Tel. líder", "Ubicación",
                            "Tipo de falla", "Prioridad", "Solución aplicada", "Estado"])
                for r in self.reportes_visibles:
                    w.writerow(r.to_lista())
            QMessageBox.information(self, "Exportado", f"Se exportaron {len(self.reportes_visibles)} reportes.\n{ruta}")
        except OSError as e:
            QMessageBox.critical(self, "Error al exportar", str(e))

    # ------------------------------------------------------------------
    #  PÁGINA 3: SELECTOR GEOGRÁFICO
    # ------------------------------------------------------------------
    def _crear_pagina_selector(self):
        pagina = QWidget()
        lay = QVBoxLayout(pagina)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(16)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(16)

        # Departamentos
        card_d, l_d = crear_tarjeta("1. Departamento")
        scroll_d = QScrollArea()
        scroll_d.setWidgetResizable(True)
        scroll_d.setFrameShape(QFrame.NoFrame)
        cont_d = QWidget()
        ld = QVBoxLayout(cont_d)
        ld.setContentsMargins(0, 0, 8, 0)
        ld.setSpacing(6)
        self.grupo_deptos = QButtonGroup(self)
        self.grupo_deptos.setExclusive(True)
        self.botones_deptos = {}
        for dep in DEPARTAMENTOS_NICARAGUA:
            b = crear_boton(dep, "lista", checkable=True, alto=40)
            b.clicked.connect(lambda checked=False, d=dep: self.mostrar_barrios_departamento(d))
            self.grupo_deptos.addButton(b)
            self.botones_deptos[dep] = b
            ld.addWidget(b)
        ld.addStretch()
        scroll_d.setWidget(cont_d)
        l_d.addWidget(scroll_d)

        # Barrios
        card_b, l_b = crear_tarjeta("2. Barrio, comarca o sector")
        scroll_b = QScrollArea()
        scroll_b.setWidgetResizable(True)
        scroll_b.setFrameShape(QFrame.NoFrame)
        self.cont_barrios = QWidget()
        self.layout_barrios = QGridLayout(self.cont_barrios)
        self.layout_barrios.setContentsMargins(0, 0, 8, 0)
        self.layout_barrios.setSpacing(6)
        scroll_b.setWidget(self.cont_barrios)
        l_b.addWidget(scroll_b)

        splitter.addWidget(card_d)
        splitter.addWidget(card_b)
        splitter.setSizes([340, 760])
        lay.addWidget(splitter, 1)

        # Estado de la selección
        barra = QFrame()
        barra.setObjectName("BarraAcciones")
        hb = QHBoxLayout(barra)
        hb.setContentsMargins(20, 12, 20, 12)
        self.lbl_seleccion = QLabel("Aún no has seleccionado ninguna ubicación.")
        self.lbl_seleccion.setStyleSheet(f"color: {C_ACENTO_OSC}; font-weight: 600;")
        btn_ir = crear_boton("Ir al formulario", "primario", alto=42)
        btn_ir.clicked.connect(lambda: self.ir_a_pagina(1))
        hb.addWidget(self.lbl_seleccion, 1)
        hb.addWidget(btn_ir)
        lay.addWidget(barra)

        self._mensaje_barrios_vacio()
        return pagina

    def _mensaje_barrios_vacio(self):
        limpiar_layout(self.layout_barrios)
        l = QLabel("Selecciona un departamento para ver sus barrios o sectores.")
        l.setObjectName("Muted")
        self.layout_barrios.addWidget(l, 0, 0)

    def mostrar_barrios_departamento(self, depto: str):
        idx = self.cb_departamento.findText(depto)
        if idx >= 0:
            self.cb_departamento.setCurrentIndex(idx)

        limpiar_layout(self.layout_barrios)
        self.grupo_barrios = QButtonGroup(self)
        self.grupo_barrios.setExclusive(True)

        barrios = DEPARTAMENTOS_NICARAGUA.get(depto, [])
        for i, barrio in enumerate(barrios):
            b = crear_boton(barrio, "lista", checkable=True, alto=38)
            b.clicked.connect(lambda checked=False, d=depto, br=barrio: self.seleccionar_barrio_definitivo(d, br))
            self.grupo_barrios.addButton(b)
            self.layout_barrios.addWidget(b, i // 2, i % 2)
        self.layout_barrios.setRowStretch(len(barrios) // 2 + 1, 1)

    def seleccionar_barrio_definitivo(self, depto: str, barrio: str):
        idx_depto = self.cb_departamento.findText(depto)
        if idx_depto >= 0:
            self.cb_departamento.setCurrentIndex(idx_depto)
        idx_barrio = self.cb_barrio.findText(barrio)
        if idx_barrio >= 0:
            self.cb_barrio.setCurrentIndex(idx_barrio)
        self.lbl_seleccion.setText(f"Ubicación asignada al formulario:  {depto}  /  {barrio}")

    # ------------------------------------------------------------------
    #  DATOS
    # ------------------------------------------------------------------
    def cargar_datos_iniciales(self):
        if not self.controlador.obtener_todos():
            ahora = datetime.now().replace(microsecond=0)
            self.controlador.agregar_reporte(
                "REP-201", "Cuadrilla León Sur", "88123456", "León - Comarca Lechecuagos",
                "Transformador Averiado", "Sustitución completa de transformador de 50kVA.",
                "Resuelto", ahora - timedelta(days=1, hours=3))
            self.controlador.agregar_reporte(
                "REP-202", "Cuadrilla Managua Central", "87654321", "Managua - Altagracia",
                "Cable Caído / Chispeando", "Re-tensado y aislamiento de línea secundaria.",
                "Resuelto", ahora - timedelta(hours=2))
        self.txt_id.setText(self.controlador.siguiente_id())
        self.refrescar_todo()

    def refrescar_todo(self):
        self.reportes_cache = self.controlador.obtener_todos()
        self.refrescar_dashboard()
        self.aplicar_filtros()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(ESTILO_GLOBAL)
    controlador = ReporteController()
    login = VentanaLogin(controlador)
    login.show()
    sys.exit(app.exec())