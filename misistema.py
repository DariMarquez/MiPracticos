import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QDialog, QHeaderView, QTextEdit, QListWidget,
    QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCloseEvent

# ==========================================
# 1. CAPA DE MODELO Y LÓGICA DE DATOS (POO)
# ==========================================

class Pelicula:
    """Clase que representa una película en el inventario."""
    def __init__(self, id_pelicula: int, titulo: str, genero: str, precio_alquiler: float):
        self.id_pelicula = id_pelicula
        self.titulo = titulo
        self.genero = genero
        self.precio_alquiler = precio_alquiler
        self.disponible = True
        self.historial_observaciones = []


class Cliente:
    """Clase que representa a un cliente registrado."""
    def __init__(self, id_cliente: int, nombre: str, telefono: str = ""):
        self.id_cliente = id_cliente
        self.nombre = nombre
        self.telefono = telefono


class Alquiler:
    """Clase que relaciona a un cliente con una o más películas alquiladas."""
    def __init__(self, id_alquiler: int, cliente: Cliente, peliculas: list):
        self.id_alquiler = id_alquiler
        self.cliente = cliente
        self.peliculas = peliculas  # Lista de películas alquiladas
        self.total_pagado = sum(p.precio_alquiler for p in peliculas)


# ==========================================
# 2. DIÁLOGOS MODALES Y NO MODALES (QDialog)
# ==========================================

class DialogoConfirmarSalida(QDialog):
    """Ventana modal personalizada para confirmar la salida del sistema."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirmar Salida")
        self.resize(320, 140)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        lbl_mensaje = QLabel("⚠️ ¿Estás seguro que quieres salir del sistema?")
        lbl_mensaje.setStyleSheet("font-size: 13px; font-weight: bold; color: #F8FAFC;")
        lbl_mensaje.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_mensaje)

        layout_botones = QHBoxLayout()

        btn_aceptar = QPushButton("Aceptar")
        btn_aceptar.setObjectName("btnConfirmar")
        btn_aceptar.clicked.connect(self.accept)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("btnCancelar")
        btn_cancelar.clicked.connect(self.reject)

        layout_botones.addWidget(btn_aceptar)
        layout_botones.addWidget(btn_cancelar)

        layout.addLayout(layout_botones)
        self.setLayout(layout)


class DialogoSobreNosotros(QDialog):
    """Ventana emergente NO MODAL con la información del sistema y créditos."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sobre Nosotros")
        self.resize(320, 180)
        self.setModal(False)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        lbl_titulo = QLabel("🎬 <b>Random Play - VideoClub</b>")
        lbl_titulo.setStyleSheet("font-size: 15px; color: #38BDF8;")

        lbl_descripcion = QLabel(
            "Sistema integral para la gestión de inventario, "
            "alquileres múltiples y control de observaciones en entregas."
        )
        lbl_descripcion.setWordWrap(True)

        lbl_credito = QLabel("<b>Desarrollado por:</b> Dario Marquez")
        lbl_credito.setStyleSheet("color: #10B981; font-weight: bold; margin-top: 5px;")

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.close)

        layout.addWidget(lbl_titulo)
        layout.addWidget(lbl_descripcion)
        layout.addWidget(lbl_credito)
        layout.addWidget(btn_cerrar)

        self.setLayout(layout)


class DialogoRegistroAlquileres(QDialog):
    """Ventana modal para visualizar el historial completo de transacciones."""
    def __init__(self, alquileres: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registro Global de Alquileres")
        self.resize(600, 380)
        self.alquileres = alquileres

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        lbl_titulo = QLabel("📜 <b>Historial de Clientes y Alquileres Realizados</b>")
        lbl_titulo.setStyleSheet("font-size: 14px; color: #38BDF8;")
        layout.addWidget(lbl_titulo)

        tabla = QTableWidget()
        tabla.setColumnCount(4)
        tabla.setHorizontalHeaderLabels(["ID", "Cliente", "Película(s)", "Total Pagado"])
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        tabla.setRowCount(0)
        for fila, alq in enumerate(self.alquileres):
            tabla.insertRow(fila)

            tabla.setItem(fila, 0, QTableWidgetItem(str(alq.id_alquiler)))
            tabla.setItem(fila, 1, QTableWidgetItem(alq.cliente.nombre))

            # Lista desplegable (QComboBox) para desplegar todas las películas alquiladas
            combo_peliculas = QComboBox()
            for p in alq.peliculas:
                combo_peliculas.addItem(f"🎬 {p.titulo} (${p.precio_alquiler:.2f})")
            
            # Asignamos el QComboBox a la celda de la columna Película(s)
            tabla.setCellWidget(fila, 2, combo_peliculas)

            tabla.setItem(fila, 3, QTableWidgetItem(f"${alq.total_pagado:.2f}"))

        layout.addWidget(tabla)

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.accept)
        layout.addWidget(btn_cerrar)

        self.setLayout(layout)


class DialogoAlquiler(QDialog):
    """Ventana emergente para procesar el alquiler de una o múltiples películas."""
    def __init__(self, peliculas, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Nuevo Alquiler")
        self.resize(400, 320)
        self.peliculas = [p for p in peliculas if p.disponible]
        self.peliculas_seleccionadas = []
        self.nombre_cliente = ""

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Nombre del Cliente:"))
        self.input_cliente = QLineEdit()
        self.input_cliente.setPlaceholderText("Ej. Juan Pérez")
        layout.addWidget(self.input_cliente)

        layout.addWidget(QLabel("Seleccionar Películas (Mantén Ctrl para selección múltiple):"))
        
        self.lista_peliculas = QListWidget()
        self.lista_peliculas.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        if not self.peliculas:
            self.lista_peliculas.addItem("No hay películas disponibles")
            self.lista_peliculas.setEnabled(False)
        else:
            for p in self.peliculas:
                self.lista_peliculas.addItem(f"[{p.id_pelicula}] {p.titulo} - ${p.precio_alquiler:.2f}")

        layout.addWidget(self.lista_peliculas)

        btn_confirmar = QPushButton("🚀 Confirmar y Alquilar")
        btn_confirmar.setObjectName("btnConfirmar")
        btn_confirmar.clicked.connect(self.confirmar)
        layout.addWidget(btn_confirmar)

        self.setLayout(layout)

    def confirmar(self):
        cliente_texto = self.input_cliente.text().strip()
        if not cliente_texto:
            QMessageBox.warning(self, "Atención", "Por favor ingresa el nombre del cliente.")
            return

        filas_seleccionadas = self.lista_peliculas.selectedIndexes()
        if not filas_seleccionadas or not self.lista_peliculas.isEnabled():
            QMessageBox.warning(self, "Atención", "Debes seleccionar al menos una película.")
            return

        indices = [item.row() for item in filas_seleccionadas]
        self.peliculas_seleccionadas = [self.peliculas[i] for i in indices]
        self.nombre_cliente = cliente_texto
        self.accept()


class DialogoDevolucion(QDialog):
    """Ventana emergente para confirmar devolución y añadir observaciones."""
    def __init__(self, pelicula: Pelicula, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Devolver Película")
        self.resize(380, 260)
        self.pelicula = pelicula
        self.nota_ingresada = ""

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        lbl_info = QLabel(f"<b>Devolución de:</b> {self.pelicula.titulo}")
        lbl_info.setStyleSheet("font-size: 14px;")
        layout.addWidget(lbl_info)

        layout.addWidget(QLabel("Observación o estado de entrega (Opcional):"))
        self.txt_observacion = QTextEdit()
        self.txt_observacion.setPlaceholderText("Ej. Disco en buen estado, caja rayada, etc...")
        layout.addWidget(self.txt_observacion)

        btn_confirmar = QPushButton("🔄 Confirmar Devolución")
        btn_confirmar.setObjectName("btnDevolver")
        btn_confirmar.clicked.connect(self.confirmar)
        layout.addWidget(btn_confirmar)

        self.setLayout(layout)

    def confirmar(self):
        self.nota_ingresada = self.txt_observacion.toPlainText().strip()
        self.accept()


class DialogoHistorial(QDialog):
    """Ventana modal para visualizar los comentarios anteriores de la película."""
    def __init__(self, pelicula: Pelicula, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Historial - {pelicula.titulo}")
        self.resize(420, 300)
        self.pelicula = pelicula

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        lbl_titulo = QLabel(f"📜 Historial de Observaciones de: <b>{self.pelicula.titulo}</b>")
        layout.addWidget(lbl_titulo)

        self.txt_historial = QTextEdit()
        self.txt_historial.setReadOnly(True)

        if self.pelicula.historial_observaciones:
            contenido = ""
            for i, obs in enumerate(self.pelicula.historial_observaciones, 1):
                contenido += f"<b>Entrada #{i}:</b> {obs}\n" + "─"*35 + "\n"
            self.txt_historial.setHtml(contenido.replace("\n", "<br>"))
        else:
            self.txt_historial.setPlainText("No hay observaciones registradas para esta película.")

        layout.addWidget(self.txt_historial)

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.accept)
        layout.addWidget(btn_cerrar)

        self.setLayout(layout)


# ==========================================
# 3. VENTANA PRINCIPAL DE LA APLICACIÓN
# ==========================================

class VideoClubWindow(QMainWindow):
    """Ventana principal del sistema de gestión del VideoClub."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Random Play - VideoClub")
        self.resize(950, 620)

        self.peliculas = []
        self.alquileres = []
        self.dialogo_sobre = None

        self.cargar_datos_ejemplo()
        self.aplicar_estilos()
        self.init_ui()

    def aplicar_estilos(self):
        """Aplica un tema personalizado (QSS)."""
        estilo = """
            QMainWindow {
                background-color: #0F172A;
            }
            QWidget {
                color: #F8FAFC;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
            }
            QLabel {
                color: #E2E8F0;
            }
            QLineEdit, QComboBox, QTextEdit, QListWidget {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 6px;
                color: #F8FAFC;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
                border: 1px solid #0EA5E9;
            }
            QTableWidget {
                background-color: #1E293B;
                border: 1px solid #334155;
                gridline-color: #334155;
                border-radius: 6px;
            }
            QHeaderView::section {
                background-color: #0F172A;
                color: #38BDF8;
                font-weight: bold;
                padding: 5px;
                border: none;
            }
            QPushButton {
                background-color: #0284C7;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 7px 12px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0369A1;
            }
            #btnConfirmar {
                background-color: #10B981;
            }
            #btnConfirmar:hover {
                background-color: #059669;
            }
            #btnCancelar {
                background-color: #EF4444;
            }
            #btnCancelar:hover {
                background-color: #DC2626;
            }
            #btnDevolver {
                background-color: #F59E0B;
            }
            #btnDevolver:hover {
                background-color: #D97706;
            }
            #btnHistorial {
                background-color: #6366F1;
                padding: 3px;
                font-size: 11px;
            }
            #btnHistorial:hover {
                background-color: #4F46E5;
            }
            #btnSobreNosotros {
                background-color: #0EA5E9;
            }
            #btnSobreNosotros:hover {
                background-color: #0284C7;
            }
            #btnRegistroGlobal {
                background-color: #8B5CF6;
            }
            #btnRegistroGlobal:hover {
                background-color: #7C3AED;
            }
        """
        self.setStyleSheet(estilo)

    def closeEvent(self, event: QCloseEvent):
        """Intercepta el evento de cierre para mostrar la confirmación."""
        dialogo = DialogoConfirmarSalida(self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            event.accept()
        else:
            event.ignore()

    def cargar_datos_ejemplo(self):
        p1 = Pelicula(1, "Matrix", "Ciencia Ficción", 3.50)
        p1.historial_observaciones.append("Devuelto con un leve rayón en el estuche.")
        
        p2 = Pelicula(2, "El Padrino", "Drama", 4.00)
        p3 = Pelicula(3, "Toy Story", "Animación", 2.50)

        self.peliculas.extend([p1, p2, p3])

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout_principal = QVBoxLayout()

        layout_header = QHBoxLayout()
        lbl_titulo = QLabel("🎬 Random Play - VideoClub")
        lbl_titulo.setStyleSheet("font-size: 22px; font-weight: bold; color: #38BDF8;")

        btn_sobre = QPushButton("ℹ️ Sobre Nosotros")
        btn_sobre.setObjectName("btnSobreNosotros")
        btn_sobre.clicked.connect(self.abrir_sobre_nosotros)

        layout_header.addWidget(lbl_titulo)
        layout_header.addStretch()
        layout_header.addWidget(btn_sobre)

        layout_principal.addLayout(layout_header)

        self.lbl_estadisticas = QLabel()
        self.lbl_estadisticas.setStyleSheet("font-size: 13px; color: #94A3B8; font-weight: bold;")
        layout_principal.addWidget(self.lbl_estadisticas)

        # Formulario para agregar película
        layout_form = QHBoxLayout()

        self.input_titulo = QLineEdit()
        self.input_titulo.setPlaceholderText("Título de la película")

        self.combo_genero = QComboBox()
        self.combo_genero.addItems(["Acción", "Comedia", "Drama", "Terror", "Infantil", "Ciencia Ficción", "Romance", "Animación"])

        self.input_precio = QLineEdit()
        self.input_precio.setPlaceholderText("Precio ($)")

        btn_agregar = QPushButton("＋ Agregar Película")
        btn_agregar.clicked.connect(self.registrar_pelicula)

        layout_form.addWidget(self.input_titulo)
        layout_form.addWidget(self.combo_genero)
        layout_form.addWidget(self.input_precio)
        layout_form.addWidget(btn_agregar)

        layout_principal.addLayout(layout_form)

        # Buscador
        layout_busqueda = QHBoxLayout()
        lbl_buscar = QLabel("🔍 Buscar:")
        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Filtrar por título...")
        self.input_buscar.textChanged.connect(self.filtrar_peliculas)

        layout_busqueda.addWidget(lbl_buscar)
        layout_busqueda.addWidget(self.input_buscar)
        layout_principal.addLayout(layout_busqueda)

        # Tabla de inventario
        self.tabla_peliculas = QTableWidget()
        self.tabla_peliculas.setColumnCount(6)
        self.tabla_peliculas.setHorizontalHeaderLabels(["ID", "Título", "Género", "Precio", "Estado", "Historial"])
        self.tabla_peliculas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout_principal.addWidget(self.tabla_peliculas)

        # Acciones inferiores
        layout_acciones = QHBoxLayout()

        btn_alquilar = QPushButton("🎟️ Registrar Nuevo Alquiler")
        btn_alquilar.setObjectName("btnConfirmar")
        btn_alquilar.clicked.connect(self.abrir_dialogo_alquiler)

        btn_devolver = QPushButton("🔄 Devolver Película Seleccionada")
        btn_devolver.setObjectName("btnDevolver")
        btn_devolver.clicked.connect(self.devolver_pelicula)

        btn_registro_global = QPushButton("📋 Ver Registro de Alquileres")
        btn_registro_global.setObjectName("btnRegistroGlobal")
        btn_registro_global.clicked.connect(self.abrir_registro_alquileres)

        layout_acciones.addWidget(btn_alquilar)
        layout_acciones.addWidget(btn_devolver)
        layout_acciones.addWidget(btn_registro_global)

        layout_principal.addLayout(layout_acciones)

        central_widget.setLayout(layout_principal)
        self.actualizar_tabla()

    def abrir_sobre_nosotros(self):
        if self.dialogo_sobre is None or not self.dialogo_sobre.isVisible():
            self.dialogo_sobre = DialogoSobreNosotros(self)
            self.dialogo_sobre.show()
        else:
            self.dialogo_sobre.raise_()
            self.dialogo_sobre.activateWindow()

    def abrir_registro_alquileres(self):
        if not self.alquileres:
            QMessageBox.information(self, "Registro Vacío", "Aún no se han registrado alquileres.")
            return

        dialogo = DialogoRegistroAlquileres(self.alquileres, self)
        dialogo.exec()

    def registrar_pelicula(self):
        titulo = self.input_titulo.text().strip()
        genero = self.combo_genero.currentText()
        precio_texto = self.input_precio.text().strip()

        if not titulo or not precio_texto:
            QMessageBox.warning(self, "Error", "Ingresa el título y el precio.")
            return

        try:
            precio = float(precio_texto)
            if precio <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Error", "El precio debe ser un número positivo.")
            return

        nuevo_id = len(self.peliculas) + 1
        nueva_pelicula = Pelicula(nuevo_id, titulo, genero, precio)
        self.peliculas.append(nueva_pelicula)

        self.input_titulo.clear()
        self.input_precio.clear()
        self.actualizar_tabla()
        QMessageBox.information(self, "Éxito", f"Película '{titulo}' agregada correctamente.")

    def actualizar_tabla(self, lista_mostrar=None):
        self.tabla_peliculas.setRowCount(0)
        
        if lista_mostrar is None:
            lista_mostrar = self.peliculas

        for fila, pelicula in enumerate(lista_mostrar):
            self.tabla_peliculas.insertRow(fila)

            estado_str = "Disponible" if pelicula.disponible else "Alquilada"

            self.tabla_peliculas.setItem(fila, 0, QTableWidgetItem(str(pelicula.id_pelicula)))
            self.tabla_peliculas.setItem(fila, 1, QTableWidgetItem(pelicula.titulo))
            self.tabla_peliculas.setItem(fila, 2, QTableWidgetItem(pelicula.genero))
            self.tabla_peliculas.setItem(fila, 3, QTableWidgetItem(f"${pelicula.precio_alquiler:.2f}"))
            self.tabla_peliculas.setItem(fila, 4, QTableWidgetItem(estado_str))

            btn_ver_historial = QPushButton("📜 Ver Historial")
            btn_ver_historial.setObjectName("btnHistorial")
            btn_ver_historial.clicked.connect(lambda _, p=pelicula: self.mostrar_historial(p))
            self.tabla_peliculas.setCellWidget(fila, 5, btn_ver_historial)

        total = len(self.peliculas)
        disponibles = sum(1 for p in self.peliculas if p.disponible)
        alquiladas = total - disponibles
        self.lbl_estadisticas.setText(
            f"📊 Total: {total} | Disponibles: {disponibles} | Alquiladas: {alquiladas}"
        )

    def filtrar_peliculas(self):
        texto_busqueda = self.input_buscar.text().lower().strip()
        peliculas_filtradas = [
            p for p in self.peliculas if texto_busqueda in p.titulo.lower()
        ]
        self.actualizar_tabla(peliculas_filtradas)

    def mostrar_historial(self, pelicula: Pelicula):
        dialogo = DialogoHistorial(pelicula, self)
        dialogo.exec()

    def abrir_dialogo_alquiler(self):
        dialogo = DialogoAlquiler(self.peliculas, self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            pelis_seleccionadas = dialogo.peliculas_seleccionadas
            cliente_nombre = dialogo.nombre_cliente

            if pelis_seleccionadas:
                for p in pelis_seleccionadas:
                    p.disponible = False

                nuevo_cliente = Cliente(len(self.alquileres) + 1, cliente_nombre)
                nuevo_alquiler = Alquiler(len(self.alquileres) + 1, nuevo_cliente, pelis_seleccionadas)
                self.alquileres.append(nuevo_alquiler)

                self.actualizar_tabla()
                titulos = ", ".join([p.titulo for p in pelis_seleccionadas])
                QMessageBox.information(
                    self, "Alquiler Exitoso", 
                    f"Cliente: {cliente_nombre}\n"
                    f"Películas alquiladas ({len(pelis_seleccionadas)}):\n{titulos}\n"
                    f"Total a pagar: ${nuevo_alquiler.total_pagado:.2f}"
                )

    def devolver_pelicula(self):
        fila_seleccionada = self.tabla_peliculas.currentRow()

        if fila_seleccionada < 0:
            QMessageBox.warning(self, "Atención", "Por favor selecciona una película de la tabla.")
            return

        id_pelicula = int(self.tabla_peliculas.item(fila_seleccionada, 0).text())
        pelicula = next((p for p in self.peliculas if p.id_pelicula == id_pelicula), None)

        if pelicula:
            if pelicula.disponible:
                QMessageBox.information(self, "Información", "Esta película ya se encuentra disponible.")
                return

            dialogo_dev = DialogoDevolucion(pelicula, self)
            if dialogo_dev.exec() == QDialog.DialogCode.Accepted:
                pelicula.disponible = True
                if dialogo_dev.nota_ingresada:
                    pelicula.historial_observaciones.append(dialogo_dev.nota_ingresada)

                self.actualizar_tabla()
                QMessageBox.information(self, "Devolución", f"La película '{pelicula.titulo}' ha sido devuelta.")


# ==========================================
# 4. PUNTO DE ENTRADA DE LA APLICACIÓN
# ==========================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VideoClubWindow()
    ventana.show()
    sys.exit(app.exec())