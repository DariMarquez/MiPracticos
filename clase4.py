import math
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget,
                             QDialog, QLabel, QMessageBox, QLineEdit, QTextEdit, QGridLayout, QFormLayout)
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QLinearGradient
from PyQt5.QtCore import Qt, QTimer




def crear_icono():
    pixmap = QPixmap(32, 32)
    pixmap.fill(QColor("#001f5b"))
    painter = QPainter(pixmap)
    painter.setPen(QColor("white"))
    painter.setFont(QFont("Arial", 20, QFont.Bold))
    painter.drawText(pixmap.rect(), Qt.AlignCenter, "V")
    painter.end()
    return QIcon(pixmap)




def crear_icono_boton(letra, color_fondo):
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QColor(color_fondo))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(pixmap.rect().adjusted(2, 2, -2, -2))
    painter.setPen(QColor("white"))
    painter.setFont(QFont("Arial", 14, QFont.Bold))
    painter.drawText(pixmap.rect(), Qt.AlignCenter, letra)
    painter.end()
    return QIcon(pixmap)




class FondoDinamicoMixin:
    def _iniciar_fondo(self):
        self._angulo = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animar_fondo)
        self._timer.start(30)


    def _animar_fondo(self):
        self._angulo = (self._angulo + 1) % 360
        self.update()


    def paintEvent(self, event):
        painter = QPainter(self)
        w, h = self.width(), self.height()
        rad = math.radians(self._angulo)
        gx1 = (math.cos(rad) * 0.5 + 0.5) * w
        gy1 = (math.sin(rad) * 0.5 + 0.5) * h
        gradiente = QLinearGradient(gx1, gy1, w - gx1, h - gy1)
        gradiente.setColorAt(0.0, QColor("#001f5b"))
        gradiente.setColorAt(0.5, QColor("#0052cc"))
        gradiente.setColorAt(1.0, QColor("#4fc3f7"))
        painter.fillRect(self.rect(), gradiente)




class FondoDinamico(FondoDinamicoMixin, QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._iniciar_fondo()




class VentanaSecundaria(FondoDinamicoMixin, QDialog):
    def __init__(self, parent=None, titulo="Ventana Secundaria", mensaje="¡Bienvenido!"):
        super().__init__(parent)
        self._iniciar_fondo()
        self.setWindowTitle(titulo)
        self.setFixedSize(300, 150)
        self.setWindowIcon(crear_icono())


        layout = QVBoxLayout()


        label = QLabel(mensaje)
        label.setStyleSheet("color: white; font-size: 14px;")
        layout.addWidget(label)


        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setIcon(crear_icono_boton("X", "#ee5253"))
        btn_cerrar.setStyleSheet("background-color: #ffffff; color: #001f5b; font-weight: bold; padding: 6px;")
        btn_cerrar.clicked.connect(self.close)
        layout.addWidget(btn_cerrar)


        self.setLayout(layout)




class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ventana Principal")
        self.setFixedSize(400, 900)
        self.setWindowIcon(crear_icono())


        widget_central = FondoDinamico()
        layout = QVBoxLayout()


        label = QLabel("MI MENU - Ejemplos de ventanas")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: white; font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(label)


        btn_modal = QPushButton("Abrir Dialogo MODAL")
        btn_modal.setIcon(crear_icono_boton("M", "#2e86de"))
        btn_modal.setStyleSheet("background-color: #ffffff; color: #001f5b; font-weight: bold; padding: 8px;")
        btn_modal.clicked.connect(self.abrir_modal)


        btn_no_modal = QPushButton("Abrir Dialogo NO MODAL")
        btn_no_modal.setIcon(crear_icono_boton("N", "#48dbfb"))
        btn_no_modal.setStyleSheet("background-color: #ffffff; color: #001f5b; font-weight: bold; padding: 8px;")
        btn_no_modal.clicked.connect(self.abrir_no_modal)

        layout_botones = QHBoxLayout()
        layout_botones.addWidget(btn_modal)
        layout_botones.addWidget(btn_no_modal)
        layout.addLayout(layout_botones)


        label_contador = QLabel("Contador de caracteres")
        label_contador.setAlignment(Qt.AlignCenter)
        label_contador.setStyleSheet("color: #aabbcc; font-size: 10px; padding: 5px;")
        layout.addWidget(label_contador)


        self.input_texto = QLineEdit()
        self.input_texto.setPlaceholderText("Escribe algo aqui...")
        self.input_texto.setStyleSheet("background-color: #ffffff; color: #001f5b; padding: 6px; border-radius: 4px;")


        btn_contar = QPushButton("Contar caracteres")
        btn_contar.setIcon(crear_icono_boton("C", "#10ac84"))
        btn_contar.setStyleSheet("background-color: #ffffff; color: #001f5b; font-weight: bold; padding: 8px;")
        btn_contar.clicked.connect(self.contar_caracteres)

        layout_contador = QHBoxLayout()
        layout_contador.addWidget(self.input_texto)
        layout_contador.addWidget(btn_contar)
        layout.addLayout(layout_contador)


        self.label_resultado = QLabel("")
        self.label_resultado.setAlignment(Qt.AlignCenter)
        self.label_resultado.setStyleSheet("color: #e6f2ff; font-size: 10px; padding: 5px;")
        layout.addWidget(self.label_resultado)


        label_texto_largo = QLabel("Editor de textos largos")
        label_texto_largo.setAlignment(Qt.AlignCenter)
        label_texto_largo.setStyleSheet("color: #aabbcc; font-size: 10px; padding: 5px;")
        layout.addWidget(label_texto_largo)


        self.input_texto_largo = QTextEdit()
        self.input_texto_largo.setPlaceholderText("Escribe un texto largo aqui...")
        self.input_texto_largo.setStyleSheet("background-color: #ffffff; color: #001f5b; padding: 6px; border-radius: 4px;")
        layout.addWidget(self.input_texto_largo)


        btn_analizar_largo = QPushButton("Analizar texto")
        btn_analizar_largo.setIcon(crear_icono_boton("T", "#f368e0"))
        btn_analizar_largo.setStyleSheet("background-color: #ffffff; color: #001f5b; font-weight: bold; padding: 8px;")
        btn_analizar_largo.clicked.connect(self.analizar_texto_largo)
        layout.addWidget(btn_analizar_largo)


        self.label_resultado_largo = QLabel("")
        self.label_resultado_largo.setAlignment(Qt.AlignCenter)
        self.label_resultado_largo.setStyleSheet("color: #e6f2ff; font-size: 10px; padding: 5px;")
        layout.addWidget(self.label_resultado_largo)


        label_grilla = QLabel("Entrada de datos (QGridLayout)")
        label_grilla.setAlignment(Qt.AlignCenter)
        label_grilla.setStyleSheet("color: #aabbcc; font-size: 10px; padding: 5px;")
        layout.addWidget(label_grilla)


        grilla = QGridLayout()
        self.input_nombre_grilla = QLineEdit()
        self.input_nombre_grilla.setPlaceholderText("Escribe tu nombre...")
        self.input_materia = QLineEdit()
        self.input_materia.setPlaceholderText("Escribe tu materia...")
        self.input_año = QLineEdit()
        self.input_año.setPlaceholderText("Escribe tu año...")

        campos_grilla = [
            ("Nombre", self.input_nombre_grilla),
            ("Materia", self.input_materia),
            ("Año", self.input_año),
        ]
        for fila, (clave, campo) in enumerate(campos_grilla):
            label_clave = QLabel(clave)
            label_clave.setStyleSheet("color: #e6f2ff; font-size: 12px; font-weight: bold;")
            campo.setStyleSheet("background-color: #ffffff; color: #001f5b; padding: 6px; border-radius: 4px;")
            grilla.addWidget(label_clave, fila, 0)
            grilla.addWidget(campo, fila, 1)

        btn_mostrar_formulario = QPushButton("Mostrar datos en QFormLayout")
        btn_mostrar_formulario.setIcon(crear_icono_boton("F", "#10ac84"))
        btn_mostrar_formulario.setStyleSheet("background-color: #ffffff; color: #001f5b; font-weight: bold; padding: 8px;")
        btn_mostrar_formulario.clicked.connect(self.mostrar_en_formulario)
        grilla.addWidget(btn_mostrar_formulario, len(campos_grilla), 0, 1, 2)
        grilla.setColumnStretch(1, 1)
        layout.addLayout(grilla)


        label_formulario = QLabel("Datos ordenados (QFormLayout)")
        label_formulario.setAlignment(Qt.AlignCenter)
        label_formulario.setStyleSheet("color: #aabbcc; font-size: 10px; padding: 5px;")
        layout.addWidget(label_formulario)


        formulario = QFormLayout()
        formulario.setLabelAlignment(Qt.AlignLeft)
        self.label_nombre_salida = QLabel("---")
        self.label_nombre_salida.setStyleSheet("color: #ffffff; font-size: 12px;")
        self.label_materia_salida = QLabel("---")
        self.label_materia_salida.setStyleSheet("color: #ffffff; font-size: 12px;")
        self.label_año_salida = QLabel("---")
        self.label_año_salida.setStyleSheet("color: #ffffff; font-size: 12px;")
        formulario.addRow("Nombre:", self.label_nombre_salida)
        formulario.addRow("Materia:", self.label_materia_salida)
        formulario.addRow("Año:", self.label_año_salida)
        layout.addLayout(formulario)


        btn_limpiar = QPushButton("Limpiar")
        btn_limpiar.setIcon(crear_icono_boton("L", "#f39c12"))
        btn_limpiar.setStyleSheet("background-color: #ffffff; color: #001f5b; font-weight: bold; padding: 8px;")
        btn_limpiar.clicked.connect(self.limpiar_todo)
        layout.addWidget(btn_limpiar)


        label_autor = QLabel("Desarrollado por Dario Marquez")
        label_autor.setAlignment(Qt.AlignCenter)
        label_autor.setStyleSheet("color: #aabbcc; font-size: 9px; padding: 5px;")
        layout.addWidget(label_autor)


        widget_central.setLayout(layout)
        self.setCentralWidget(widget_central)


    def abrir_modal(self):
        confirmacion = QMessageBox(self)
        confirmacion.setWindowTitle("Confirmacion")
        confirmacion.setText("Desea abrir el dialogo modal?")
        confirmacion.setIcon(QMessageBox.Question)
        confirmacion.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        confirmacion.setDefaultButton(QMessageBox.Yes)
        confirmacion.setStyleSheet("""
            QMessageBox {
                background-color: #f4a6a6;
            }
            QLabel {
                color: #333333;
                font-size: 13px;
            }
            QPushButton {
                background-color: #ffffff;
                color: #333333;
                font-weight: bold;
                padding: 5px 15px;
            }
        """)


        respuesta = confirmacion.exec_()
        if respuesta == QMessageBox.Yes:
            dialogo = VentanaSecundaria(self, "Dialogo Modal", "Este dialogo es MODAL.\nBloquea la ventana principal.")
            dialogo.exec_()


    def abrir_no_modal(self):
        dialogo = VentanaSecundaria(self, "Dialogo No Modal", "Este dialogo es NO MODAL.\nPuedes usar la ventana principal.")
        dialogo.setWindowModality(Qt.NonModal)
        dialogo.show()


    def contar_caracteres(self):
        texto = self.input_texto.text()
        self.label_resultado.setText(f"El texto '{texto}' tiene {len(texto)} caracteres.")


    def analizar_texto_largo(self):
        texto = self.input_texto_largo.toPlainText()
        caracteres = len(texto)
        palabras = len(texto.split())
        self.label_resultado_largo.setText(
            f"El texto tiene {caracteres} caracteres y {palabras} palabras.")


    def mostrar_en_formulario(self):
        nombre = self.input_nombre_grilla.text().strip()
        materia = self.input_materia.text().strip()
        año = self.input_año.text().strip()
        self.label_nombre_salida.setText(nombre or "---")
        self.label_materia_salida.setText(materia or "---")
        self.label_año_salida.setText(año or "---")


    def limpiar_todo(self):
        self.input_texto.clear()
        self.label_resultado.clear()
        self.input_texto_largo.clear()
        self.label_resultado_largo.clear()
        self.input_nombre_grilla.clear()
        self.input_materia.clear()
        self.input_año.clear()
        self.label_nombre_salida.setText("---")
        self.label_materia_salida.setText("---")
        self.label_año_salida.setText("---")




if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec_())

