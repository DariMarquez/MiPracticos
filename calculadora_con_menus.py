import sys
import math
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QAction, QFont, QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QGridLayout, QLineEdit, QPushButton,
    QTextEdit, QLabel, QFrame, QSizePolicy, QListWidget,
    QListWidgetItem, QMessageBox, QStyle
)

class ScientificCalculator(QMainWindow):
    """
    Calculadora Científica Virtual construida con PySide6 y QMainWindow.
    Ofrece funciones matemáticas avanzadas, historial de expresiones y un diseño con estilo QSS.
    """
    APP_NAME = "Calculadora Científica Virtual"
    APP_VERSION = "1.0.0"

    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.APP_NAME)
        self.resize(480, 750)  
        self.setMinimumSize(400, 640)
        
        # Variables de estado
        self.current_expression = ""
        self.angle_mode = "DEG"  # 'DEG' o 'RAD'
        self.calculation_history = []  # Almacena hasta las últimas 5 operaciones

        # Contenedor principal
        self.central_widget = QWidget(self)
        self.central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(14, 6, 14, 10)  # Márgenes mínimos arriba y abajo
        self.main_layout.setSpacing(6)  # Espaciado compacto entre elementos

        # Build UI Elements
        self.setup_menu_bar()
        self.setup_header()
        self.setup_display()
        self.setup_keypad()
        self.setup_footer()  
        self.setup_keyboard_shortcuts()

        # Apply QSS Styling
        self.apply_custom_stylesheet()

    def setup_menu_bar(self):
        """
        Crea el menú principal de la barra de menús de forma limpia y visible.
        """
        menu_archivo = self.menuBar().addMenu("Menú")
        menu_archivo.setIcon(self.style().standardIcon(QStyle.SP_TitleBarMenuButton))
        menu_archivo.setToolTip("Menú principal de la aplicación")

        # "Acerca de" -> ícono de ayuda del sistema
        self.action_acerca_de = QAction(
            self.style().standardIcon(QStyle.SP_DialogHelpButton),
            "Acerca de",
            self
        )
        self.action_acerca_de.setToolTip("Muestra información sobre la aplicación")
        self.action_acerca_de.triggered.connect(self.show_about_dialog)
        menu_archivo.addAction(self.action_acerca_de)

        menu_archivo.addSeparator()

        # "Salir" -> ícono de cierre + atajo Ctrl+Q
        self.action_salir = QAction(
            self.style().standardIcon(QStyle.SP_DialogCloseButton),
            "Salir",
            self
        )
        self.action_salir.setShortcut(QKeySequence("Ctrl+Q"))
        self.action_salir.setShortcutContext(Qt.ApplicationShortcut)
        self.action_salir.setToolTip("Cierra la aplicación (Ctrl+Q)")
        self.action_salir.triggered.connect(self.close)
        menu_archivo.addAction(self.action_salir)

    def show_about_dialog(self):
        """Muestra un QMessageBox con el nombre y la versión de la aplicación."""
        QMessageBox.about(
            self,
            "Acerca de",
            f"<b>{self.APP_NAME}</b><br>"
            f"Versión: {self.APP_VERSION}<br><br>"
            "Calculadora científica con historial de operaciones.<br>"
            "Desarrollado por Dario Marquez."
        )

    def setup_header(self):
        """Crea la barra superior con información del modo de ángulo y opción de limpiar historial."""
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("CIENTÍFICA")
        title_label.setObjectName("HeaderTitle")
        
        self.clear_hist_btn = QPushButton("🗑 Historial")
        self.clear_hist_btn.setObjectName("ClearHistoryButton")
        self.clear_hist_btn.setCursor(Qt.PointingHandCursor)
        self.clear_hist_btn.setToolTip("Limpiar historial de operaciones")
        self.clear_hist_btn.clicked.connect(self.clear_history)

        self.mode_btn = QPushButton("DEG")
        self.mode_btn.setObjectName("ModeButton")
        self.mode_btn.setCursor(Qt.PointingHandCursor)
        self.mode_btn.setToolTip("Cambiar entre Grados (DEG) y Radianes (RAD)")
        self.mode_btn.clicked.connect(self.toggle_angle_mode)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.clear_hist_btn)
        header_layout.addWidget(self.mode_btn)
        
        self.main_layout.addLayout(header_layout)

    def setup_display(self):
        """Crea la sección de pantalla (Historial múltiple + Pantalla de entrada/resultado)."""
        display_frame = QFrame()
        display_frame.setObjectName("DisplayFrame")
        display_layout = QVBoxLayout(display_frame)
        display_layout.setContentsMargins(10, 8, 10, 8)
        display_layout.setSpacing(2)

        self.history_list_widget = QListWidget()
        self.history_list_widget.setObjectName("HistoryListWidget")
        self.history_list_widget.setMaximumHeight(75)
        self.history_list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.history_list_widget.setFocusPolicy(Qt.NoFocus)
        self.history_list_widget.itemClicked.connect(self.load_from_history)

        self.input_display = QLineEdit("0")
        self.input_display.setObjectName("InputDisplay")
        self.input_display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.input_display.setReadOnly(True) 

        display_layout.addWidget(self.history_list_widget)
        display_layout.addWidget(self.input_display)

        self.main_layout.addWidget(display_frame)

    def setup_keypad(self):
        """Crea la cuadrícula de botones numéricos y científicos."""
        grid_layout = QGridLayout()
        grid_layout.setSpacing(6)  # Espaciado interno más compacto entre botones

        buttons = [
            ('C', 0, 0, 'danger'), ('DEL', 0, 1, 'secondary'), ('(', 0, 2, 'func'), (')', 0, 3, 'func'), ('mod', 0, 4, 'func'),
            ('sin', 1, 0, 'func'), ('cos', 1, 1, 'func'), ('tan', 1, 2, 'func'), ('π', 1, 3, 'constant'), ('e', 1, 4, 'constant'),
            ('log', 2, 0, 'func'), ('ln', 2, 1, 'func'), ('√', 2, 2, 'func'), ('x²', 2, 3, 'func'), ('^', 2, 4, 'operator'),
            ('7', 3, 0, 'num'), ('8', 3, 1, 'num'), ('9', 3, 2, 'num'), ('÷', 3, 3, 'operator'), ('1/x', 3, 4, 'func'),
            ('4', 4, 0, 'num'), ('5', 4, 1, 'num'), ('6', 4, 2, 'num'), ('×', 4, 3, 'operator'), ('n!', 4, 4, 'func'),
            ('1', 5, 0, 'num'), ('2', 5, 1, 'num'), ('3', 5, 2, 'num'), ('-', 5, 3, 'operator'), ('=', 5, 4, 'accent_tall'),
            ('0', 6, 0, 'num', 2), ('.', 6, 2, 'num'), ('+', 6, 3, 'operator')
        ]

        for item in buttons:
            text = item[0]
            row = item[1]
            col = item[2]
            btn_type = item[3]
            colspan = item[4] if len(item) > 4 else 1

            btn = QPushButton(text)
            btn.setObjectName(f"Btn_{btn_type}")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            btn.clicked.connect(lambda checked, t=text: self.on_button_click(t))

            if btn_type == 'accent_tall':
                grid_layout.addWidget(btn, row, col, 2, colspan)
            else:
                grid_layout.addWidget(btn, row, col, 1, colspan)

        self.main_layout.addLayout(grid_layout)

    def setup_footer(self):
        """Crea la etiqueta inferior con los créditos del desarrollador."""
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 0, 0, 0)
        
        self.signature_label = QLabel("Desarrollado por Dario Marquez")
        self.signature_label.setObjectName("FooterSignature")
        self.signature_label.setAlignment(Qt.AlignCenter)
        
        footer_layout.addWidget(self.signature_label)
        self.main_layout.addLayout(footer_layout)

    def setup_keyboard_shortcuts(self):
        """Asigna atajos de teclado estándar para escribir rápidamente."""
        QShortcut(QKeySequence(Qt.Key_Return), self, self.calculate_result)
        QShortcut(QKeySequence(Qt.Key_Enter), self, self.calculate_result)
        QShortcut(QKeySequence(Qt.Key_Escape), self, self.clear_all)
        QShortcut(QKeySequence(Qt.Key_Backspace), self, self.backspace)

    def toggle_angle_mode(self):
        """Alterna entre grados (DEG) y radianes (RAD)."""
        self.angle_mode = "RAD" if self.angle_mode == "DEG" else "DEG"
        self.mode_btn.setText(self.angle_mode)

    def on_button_click(self, char):
        """Maneja la acción de cada botón presionado."""
        if char == 'C':
            self.clear_all()
        elif char == 'DEL':
            self.backspace()
        elif char == '=':
            self.calculate_result()
        elif char in ('sin', 'cos', 'tan', 'log', 'ln', '√'):
            self.append_function(char)
        elif char == 'x²':
            self.current_expression += "^2"
            self.update_display()
        elif char == '1/x':
            self.current_expression += "^(-1)"
            self.update_display()
        elif char == 'n!':
            self.current_expression += "!"
            self.update_display()
        elif char == 'mod':
            self.current_expression += " % "
            self.update_display()
        else:
            self.current_expression += char
            self.update_display()

    def append_function(self, func_name):
        """Añade funciones matemáticas con paréntesis de apertura."""
        self.current_expression += f"{func_name}("
        self.update_display()

    def clear_all(self):
        """Limpia la pantalla y la expresión activa."""
        self.current_expression = ""
        self.update_display()

    def clear_history(self):
        """Limpia por completo el historial de operaciones."""
        self.calculation_history.clear()
        self.history_list_widget.clear()

    def backspace(self):
        """Elimina el último carácter."""
        self.current_expression = self.current_expression[:-1]
        self.update_display()

    def update_display(self):
        """Actualiza la caja QLineEdit con el texto procesado."""
        if not self.current_expression:
            self.input_display.setText("0")
        else:
            self.input_display.setText(self.current_expression)

    def load_from_history(self, item):
        """Permite cargar el resultado o expresión previa al hacer clic en el historial."""
        text = item.text()
        if "=" in text:
            _, res = text.split("=")
            self.current_expression = res.strip()
            self.update_display()

    def calculate_result(self):
        """Evalúa la expresión matemática actual y actualiza el historial (últimas 5)."""
        if not self.current_expression:
            return

        expression_str = self.current_expression
        
        try:
            parsed_expr = expression_str.replace('×', '*').replace('÷', '/').replace('^', '**')
            parsed_expr = parsed_expr.replace('π', 'math.pi').replace('e', 'math.e').replace('√', 'math.sqrt')

            import re
            def parse_factorial(match):
                num = match.group(1)
                return f"math.factorial({num})"
            
            parsed_expr = re.sub(r'(\d+)!', parse_factorial, parsed_expr)

            def deg_sin(x): return math.sin(math.radians(x) if self.angle_mode == "DEG" else x)
            def deg_cos(x): return math.cos(math.radians(x) if self.angle_mode == "DEG" else x)
            def deg_tan(x): return math.tan(math.radians(x) if self.angle_mode == "DEG" else x)

            safe_dict = {
                'math': math,
                'sin': deg_sin,
                'cos': deg_cos,
                'tan': deg_tan,
                'log': math.log10,
                'ln': math.log,
                'sqrt': math.sqrt,
                'abs': abs
            }

            result = eval(parsed_expr, {"__builtins__": None}, safe_dict)

            if isinstance(result, float):
                if result.is_integer():
                    result_str = str(int(result))
                else:
                    result_str = f"{result:.8g}"
            else:
                result_str = str(result)

            record = f"{expression_str} = {result_str}"
            
            self.calculation_history.append(record)
            if len(self.calculation_history) > 5:
                self.calculation_history.pop(0)

            self.history_list_widget.clear()
            for hist_item in self.calculation_history:
                self.history_list_widget.addItem(hist_item)
            self.history_list_widget.scrollToBottom()

            self.input_display.setText(result_str)
            self.current_expression = result_str

        except ZeroDivisionError:
            self.input_display.setText("Error: división por cero")
            self.current_expression = ""
            QTimer.singleShot(2000, self.reset_after_error)
        except Exception as e:
            self.input_display.setText("Error")
            self.current_expression = ""

    def reset_after_error(self):
        """Restablece la pantalla a '0' tras mostrar el error temporalmente."""
        if self.input_display.text() == "Error: división por cero":
            self.input_display.setText("0")

    def apply_custom_stylesheet(self):
        """Aplica los estilos QSS con estética futurista neón a la interfaz."""
        qss_style = """
        QMainWindow {
            background-color: #05010f;
        }

        #CentralWidget {
            background: qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 #05010f,
                stop: 0.45 #14032e,
                stop: 0.75 #0b1039,
                stop: 1 #1a0433
            );
        }

        #HeaderTitle {
            color: #67e8f9;
            font-size: 11px;
            font-weight: bold;
            letter-spacing: 2px;
        }

        QMenuBar {
            background-color: #08041a;
            color: #c4b5fd;
            border-bottom: 1px solid #22d3ee;
            padding: 2px;
        }
        QMenuBar::item {
            padding: 4px 10px;
            background: transparent;
            border-radius: 4px;
        }
        QMenuBar::item:selected {
            background-color: rgba(34, 211, 238, 0.22);
            color: #ffffff;
        }

        QMenu {
            background-color: #0d0626;
            color: #e9d5ff;
            border: 1px solid #a855f7;
            border-radius: 6px;
            padding: 4px;
        }
        QMenu::item {
            padding: 8px 30px 8px 36px;
            border-radius: 4px;
        }
        QMenu::item:selected {
            background-color: rgba(236, 72, 153, 0.35);
            color: #ffffff;
        }
        QMenu::separator {
            height: 1px;
            background: rgba(34, 211, 238, 0.4);
            margin: 6px 8px;
        }

        #ModeButton, #ClearHistoryButton {
            background-color: rgba(34, 211, 238, 0.10);
            color: #22d3ee;
            border: 1px solid rgba(34, 211, 238, 0.55);
            border-radius: 6px;
            font-size: 11px;
            font-weight: bold;
            padding: 3px 8px;
        }
        #ModeButton:hover, #ClearHistoryButton:hover {
            background-color: rgba(34, 211, 238, 0.25);
            color: #a5f3fc;
        }

        #DisplayFrame {
            background-color: rgba(5, 1, 15, 0.72);
            border: 1px solid #ec4899;
            border-radius: 12px;
        }

        #HistoryListWidget {
            color: #7dd3fc;
            font-size: 11px;
            background: transparent;
            border: none;
        }
        #HistoryListWidget::item {
            padding: 1px 4px;
            color: #7dd3fc;
        }
        #HistoryListWidget::item:hover {
            color: #f0abfc;
            background: rgba(168, 85, 247, 0.18);
            border-radius: 4px;
        }

        #InputDisplay {
            color: #5eead4;
            font-size: 28px;
            font-weight: 600;
            background: transparent;
            border: none;
            selection-background-color: #ec4899;
        }

        QPushButton {
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            color: #e0f2fe;
            background-color: rgba(99, 102, 241, 0.14);
            border: 1px solid rgba(129, 140, 248, 0.35);
        }

        #Btn_num {
            background-color: rgba(99, 102, 241, 0.16);
            border-color: rgba(129, 140, 248, 0.35);
        }
        #Btn_num:hover {
            background-color: rgba(34, 211, 238, 0.28);
            border-color: #22d3ee;
            color: #ffffff;
        }
        #Btn_num:pressed {
            background-color: rgba(34, 211, 238, 0.45);
        }

        #Btn_func, #Btn_constant {
            background-color: rgba(168, 85, 247, 0.18);
            color: #d8b4fe;
            font-size: 12px;
            border-color: rgba(192, 132, 252, 0.40);
        }
        #Btn_func:hover, #Btn_constant:hover {
            background-color: rgba(236, 72, 153, 0.30);
            color: #ffffff;
        }

        #Btn_operator {
            background-color: rgba(236, 72, 153, 0.20);
            color: #f9a8d4;
            font-size: 16px;
            border-color: rgba(236, 72, 153, 0.50);
        }
        #Btn_operator:hover {
            background-color: rgba(236, 72, 153, 0.42);
            color: #ffffff;
        }

        #Btn_danger {
            background-color: rgba(244, 63, 94, 0.20);
            color: #fda4af;
            border-color: rgba(251, 113, 133, 0.50);
        }
        #Btn_danger:hover {
            background-color: rgba(244, 63, 94, 0.45);
            color: #ffffff;
        }

        #Btn_secondary {
            background-color: rgba(45, 212, 191, 0.16);
            color: #99f6e4;
            border-color: rgba(45, 212, 191, 0.45);
        }
        #Btn_secondary:hover {
            background-color: rgba(45, 212, 191, 0.35);
            color: #ffffff;
        }

        #Btn_accent_tall {
            background: qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 #06b6d4,
                stop: 0.5 #7c3aed,
                stop: 1 #ec4899
            );
            color: #ffffff;
            font-size: 18px;
            border: 1px solid rgba(255, 255, 255, 0.35);
        }
        #Btn_accent_tall:hover {
            background: qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 #22d3ee,
                stop: 0.5 #a855f7,
                stop: 1 #f472b6
            );
        }
        #Btn_accent_tall:pressed {
            background: #4c1d95;
        }

        #FooterSignature {
            color: rgba(103, 232, 249, 0.55);
            font-size: 10px;
            font-weight: 500;
            background: transparent;
            border: none;
        }
        """
        self.setStyleSheet(qss_style)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    calc = ScientificCalculator()
    calc.show()

    sys.exit(app.exec())