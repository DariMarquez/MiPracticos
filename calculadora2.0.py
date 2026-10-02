import sys
import math
import re
import wx

class ScientificCalculator(wx.Frame):
    """
    Calculadora Científica Virtual construida con wxPython y wx.Frame.
    Ofrece funciones matemáticas avanzadas, historial de expresiones y diseño personalizado.
    """
    def __init__(self):
        super().__init__(None, title="Calculadora Científica Virtual", size=(480, 770))
        self.SetMinSize(wx.Size(400, 660))
        
        # Variables de estado
        self.current_expression = ""
        self.angle_mode = "DEG"  # 'DEG' o 'RAD'
        self.calculation_history = []  # Almacena hasta las últimas 5 operaciones

        # Panel principal contenedor
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour(wx.Colour(15, 23, 42))

        # Layout principal vertical
        self.main_layout = wx.BoxSizer(wx.VERTICAL)
        
        # Construir elementos de la interfaz
        self.setup_header()
        self.setup_display()
        self.setup_keypad()
        self.setup_footer()
        self.setup_keyboard_shortcuts()

        self.panel.SetSizer(self.main_layout)
        self.Center()

    def setup_header(self):
        """Crea la barra superior con información del modo de ángulo y opción de limpiar historial."""
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        title_label = wx.StaticText(self.panel, label="CIENTÍFICA")
        title_label.SetForegroundColour(wx.Colour(148, 163, 184))
        title_font = title_label.GetFont()
        title_font.SetPointSize(9)
        title_font.SetWeight(wx.FONTWEIGHT_BOLD)
        title_label.SetFont(title_font)
        
        self.clear_hist_btn = wx.Button(self.panel, label="🗑 Historial", size=(-1, 28))
        self.clear_hist_btn.SetToolTip("Limpiar historial de operaciones")
        self.clear_hist_btn.Bind(wx.EVT_BUTTON, self.clear_history)

        self.mode_btn = wx.Button(self.panel, label="DEG", size=(-1, 28))
        self.mode_btn.SetToolTip("Cambiar entre Grados (DEG) y Radianes (RAD)")
        self.mode_btn.Bind(wx.EVT_BUTTON, self.toggle_angle_mode)

        header_sizer.Add(title_label, 0, wx.ALIGN_CENTER_VERTICAL)
        header_sizer.AddStretchSpacer(1)
        header_sizer.Add(self.clear_hist_btn, 0, wx.RIGHT, 6)
        header_sizer.Add(self.mode_btn, 0)
        
        self.main_layout.Add(header_sizer, 0, wx.EXPAND | wx.ALL, 16)

    def setup_display(self):
        """Crea la sección de pantalla (Historial múltiple + Pantalla de entrada/resultado)."""
        display_panel = wx.Panel(self.panel)
        display_panel.SetBackgroundColour(wx.Colour(15, 23, 42, 165))
        
        display_layout = wx.BoxSizer(wx.VERTICAL)

        self.history_list_widget = wx.ListBox(display_panel, style=wx.LB_SINGLE | wx.LB_NEEDED_SB)
        self.history_list_widget.SetMinSize(wx.Size(-1, 85))
        self.history_list_widget.SetBackgroundColour(wx.Colour(15, 23, 42))
        self.history_list_widget.SetForegroundColour(wx.Colour(100, 116, 139))
        self.history_list_widget.Bind(wx.EVT_LISTBOX, self.load_from_history)

        self.input_display = wx.TextCtrl(display_panel, value="0", style=wx.TE_RIGHT | wx.TE_READONLY)
        disp_font = self.input_display.GetFont()
        disp_font.SetPointSize(22)
        disp_font.SetWeight(wx.FONTWEIGHT_BOLD)
        self.input_display.SetFont(disp_font)
        self.input_display.SetBackgroundColour(wx.Colour(15, 23, 42))
        self.input_display.SetForegroundColour(wx.Colour(248, 250, 252))

        display_layout.Add(self.history_list_widget, 0, wx.EXPAND | wx.ALL, 8)
        display_layout.Add(self.input_display, 0, wx.EXPAND | wx.ALL, 8)
        
        display_panel.SetSizer(display_layout)
        self.main_layout.Add(display_panel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 16)

    def setup_keypad(self):
        """Crea la cuadrícula de botones numéricos y científicos."""
        grid_sizer = wx.GridBagSizer(8, 8)

        buttons = [
            ('C', 0, 0, 1, 1), ('DEL', 0, 1, 1, 1), ('(', 0, 2, 1, 1), (')', 0, 3, 1, 1), ('mod', 0, 4, 1, 1),
            ('sin', 1, 0, 1, 1), ('cos', 1, 1, 1, 1), ('tan', 1, 2, 1, 1), ('π', 1, 3, 1, 1), ('e', 1, 4, 1, 1),
            ('log', 2, 0, 1, 1), ('ln', 2, 1, 1, 1), ('√', 2, 2, 1, 1), ('x²', 2, 3, 1, 1), ('^', 2, 4, 1, 1),
            ('7', 3, 0, 1, 1), ('8', 3, 1, 1, 1), ('9', 3, 2, 1, 1), ('÷', 3, 3, 1, 1), ('1/x', 3, 4, 1, 1),
            ('4', 4, 0, 1, 1), ('5', 4, 1, 1, 1), ('6', 4, 2, 1, 1), ('×', 4, 3, 1, 1), ('n!', 4, 4, 1, 1),
            ('1', 5, 0, 1, 1), ('2', 5, 1, 1, 1), ('3', 5, 2, 1, 1), ('-', 5, 3, 1, 1), ('=', 5, 4, 2, 1), # spans 2 rows
            ('0', 6, 0, 1, 2), ('.', 6, 2, 1, 1), ('+', 6, 3, 1, 1)
        ]

        for item in buttons:
            text, row, col, rowspan, colspan = item[0], item[1], item[2], item[3], item[4]
            btn = wx.Button(self.panel, label=text, size=(-1, 42))
            
            # Asignar evento de clic
            btn.Bind(wx.EVT_BUTTON, lambda evt, t=text: self.on_button_click(t))
            
            grid_sizer.Add(btn, pos=(row, col), span=(rowspan, colspan), flag=wx.EXPAND)

        # Ajustar proporciones de la cuadrícula para que los botones crezcan equitativamente
        for r in range(7):
            grid_sizer.AddGrowableRow(r, 1)
        for c in range(5):
            grid_sizer.AddGrowableCol(c, 1)

        self.main_layout.Add(grid_sizer, 1, wx.EXPAND | wx.ALL, 16)

    def setup_footer(self):
        """Crea la etiqueta inferior con los créditos del desarrollador."""
        footer_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.signature_label = wx.StaticText(self.panel, label="Desarrollado por Dario Marquez", style=wx.ALIGN_CENTRE_HORIZONTAL)
        self.signature_label.SetForegroundColour(wx.Colour(148, 163, 184, 120))
        sig_font = self.signature_label.GetFont()
        sig_font.SetPointSize(8)
        self.signature_label.SetFont(sig_font)
        
        footer_sizer.Add(self.signature_label, 1, wx.ALIGN_CENTER)
        self.main_layout.Add(footer_sizer, 0, wx.EXPAND | wx.BOTTOM, 10)

    def setup_keyboard_shortcuts(self):
        """Asigna atajos de teclado estándar para escribir rápidamente."""
        self.Bind(wx.EVT_CHAR_HOOK, self.handle_key_press)

    def handle_key_press(self, event):
        """Maneja eventos de teclado globales en wxPython."""
        keycode = event.GetKeyCode()
        if keycode in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            self.calculate_result()
        elif keycode == wx.WXK_ESCAPE:
            self.clear_all()
        elif keycode == wx.WXK_BACK:
            self.backspace()
        else:
            event.Skip()

    def toggle_angle_mode(self, event=None):
        """Alterna entre grados (DEG) y radianes (RAD)."""
        self.angle_mode = "RAD" if self.angle_mode == "DEG" else "DEG"
        self.mode_btn.SetLabel(self.angle_mode)

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

    def clear_history(self, event=None):
        """Limpia por completo el historial de operaciones."""
        self.calculation_history.clear()
        self.history_list_widget.Clear()

    def backspace(self):
        """Elimina el último carácter."""
        self.current_expression = self.current_expression[:-1]
        self.update_display()

    def update_display(self):
        """Actualiza el control de texto con el valor procesado."""
        if not self.current_expression:
            self.input_display.SetValue("0")
        else:
            self.input_display.SetValue(self.current_expression)

    def load_from_history(self, event):
        """Permite cargar el resultado o expresión previa al hacer clic en el historial."""
        selection = self.history_list_widget.GetSelection()
        if selection != wx.NOT_FOUND:
            text = self.history_list_widget.GetString(selection)
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

            self.history_list_widget.Clear()
            for hist_item in self.calculation_history:
                self.history_list_widget.Append(hist_item)
            
            if self.calculation_history:
                self.history_list_widget.SetSelection(len(self.calculation_history) - 1)

            self.input_display.SetValue(result_str)
            self.current_expression = result_str

        except ZeroDivisionError:
            self.input_display.SetValue("Error: división por cero")
            self.current_expression = ""
            wx.CallLater(2000, self.reset_after_error)
        except Exception as e:
            self.input_display.SetValue("Error")
            self.current_expression = ""

    def reset_after_error(self):
        """Restablece la pantalla a '0' tras mostrar el error temporalmente."""
        if self.input_display.GetValue() == "Error: división por cero":
            self.input_display.SetValue("0")

if __name__ == "__main__":
    app = wx.App(False)
    calc = ScientificCalculator()
    calc.Show()
    app.MainLoop()