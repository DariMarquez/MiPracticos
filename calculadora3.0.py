import math
import threading
import dearpygui.dearpygui as dpg

# Variables de estado para la calculadora
current_expression = ""
memory_value = 0.0
last_answer = 0.0  # Variable para almacenar la última respuesta (ANS)
radians_mode = True  # True para radianes, False para grados


def evaluate_expression(expr):
    """Evalúa la expresión de manera segura reemplazando funciones matemáticas."""
    global radians_mode, last_answer
    try:
        # Reemplazos trigonométricos según el modo
        if radians_mode:
            expr = (
                expr.replace("sin(", "math.sin(")
                .replace("cos(", "math.cos(")
                .replace("tan(", "math.tan(")
            )
        else:
            expr = (
                expr.replace("sin(", "math.sin(math.radians(")
                .replace("cos(", "math.cos(math.radians(")
                .replace("tan(", "math.tan(math.radians(")
            )

        # Reemplazos generales de funciones y constantes
        expr = (
            expr.replace("log(", "math.log10(")
            .replace("ln(", "math.log(")
            .replace("sqrt(", "math.sqrt(")
            .replace("asin(", "math.asin(")
            .replace("acos(", "math.acos(")
            .replace("atan(", "math.atan(")
            .replace("sinh(", "math.sinh(")
            .replace("cosh(", "math.cosh(")
            .replace("tanh(", "math.tanh(")
            .replace("abs(", "abs(")
            .replace("^", "**")
            .replace("pi", "math.pi")
            .replace("e", "math.e")
            .replace("ANS", str(last_answer))
        )

        # Ajuste para porcentaje: transforma un número seguido de % en su expresión decimal (ej: 50% -> (50/100))
        # Nota: Esto es un reemplazo simple para casos comunes
        # Si prefieres usar una función de reemplazo por regex se puede afinar, 
        # pero aquí manejamos el símbolo básico de porcentaje dividiendo entre 100.
        expr = expr.replace("%", "/100")

        result = eval(expr)
        last_answer = result  # Guardamos el resultado en ANS
        return result
    except ZeroDivisionError:
        return "Error: división por cero"
    except Exception:
        return "Error de sintaxis"


def reset_display_after_error():
    """Restablece la pantalla a vacío después de 2 segundos."""
    global current_expression
    current_expression = ""
    if dpg.does_item_exist("display_text"):
        dpg.set_value("display_text", "")


def on_button_click(sender, app_data, user_data):
    global current_expression

    if user_data == "C":
        current_expression = ""
    elif user_data == "DEL":
        current_expression = current_expression[:-1]
    elif user_data == "=":
        if current_expression.strip() == "":
            return
        res = evaluate_expression(current_expression)

        if isinstance(res, str) and "Error" in res:
            current_expression = res
            dpg.set_value("display_text", current_expression)

            # Temporizador de 2 segundos para limpiar el error automáticamente
            timer = threading.Timer(2.0, reset_display_after_error)
            timer.daemon = True
            timer.start()
            return

        history_item = f"{current_expression} = {res}"
        dpg.add_text(history_item, parent="history_window")
        current_expression = str(res)
    else:
        current_expression += str(user_data)

    dpg.set_value("display_text", current_expression)


def memory_action(sender, app_data, user_data):
    global memory_value, current_expression
    res_val = 0.0
    try:
        if current_expression and not "Error" in current_expression:
            res_val = float(evaluate_expression(current_expression))
    except:
        res_val = 0.0

    if user_data == "MC":
        memory_value = 0.0
    elif user_data == "MR":
        current_expression += str(memory_value)
        dpg.set_value("display_text", current_expression)
    elif user_data == "M+":
        memory_value += res_val
    elif user_data == "M-":
        memory_value -= res_val

    dpg.set_value("memory_label", f"Memoria: {memory_value}")


def toggle_angle_mode(sender, app_data):
    global radians_mode
    radians_mode = app_data
    mode_text = "Modo: Radianes" if radians_mode else "Modo: Grados"
    dpg.set_value("mode_label", mode_text)


# Inicializar DearPyGui
dpg.create_context()
dpg.create_viewport(title="Calculadora Cientifica - DearPyGui", width=500, height=700)

# Aplicar un tema oscuro elegante por defecto
with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 0)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)
        dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 6, 6)

dpg.bind_theme(global_theme)

# Ventana Principal configurada como Primary Window
with dpg.window(tag="PrimaryWindow", no_title_bar=True):

    with dpg.child_window(width=-1, height=-1, border=False):

        # Pantalla de visualización (Display) adaptable en ancho completo
        with dpg.child_window(height=75, border=True, width=-1):
            dpg.add_text("Modo: Radianes", tag="mode_label", color=(150, 150, 150))
            dpg.add_text("", tag="display_text")

        dpg.add_spacer(height=5)

        # Panel superior de controles (Memoria y Ángulos)
        with dpg.group(horizontal=True):
            dpg.add_button(
                label="MC", width=45, height=30, callback=memory_action, user_data="MC"
            )
            dpg.add_button(
                label="MR", width=45, height=30, callback=memory_action, user_data="MR"
            )
            dpg.add_button(
                label="M+", width=45, height=30, callback=memory_action, user_data="M+"
            )
            dpg.add_button(
                label="M-", width=45, height=30, callback=memory_action, user_data="M-"
            )
            dpg.add_spacer(width=15)
            dpg.add_text("Memoria: 0.0", tag="memory_label", color=(200, 200, 100))

        dpg.add_spacer(height=3)
        dpg.add_checkbox(
            label="Usar Radianes (Desactivar para Grados)",
            default_value=True,
            callback=toggle_angle_mode,
        )
        dpg.add_separator()
        dpg.add_spacer(height=3)

        # Tabla responsiva de botones con altura fija estándar (42px)
        with dpg.table(
            header_row=False,
            policy=dpg.mvTable_SizingStretchSame,
            width=-1,
            borders_innerH=False,
            borders_outerH=False,
            borders_innerV=False,
            borders_outerV=False,
        ):
            for _ in range(5):
                dpg.add_table_column()

            # Fila 1: Funciones avanzadas
            with dpg.table_row():
                dpg.add_button(label="sin(", width=-1, height=42, callback=on_button_click, user_data="sin(")
                dpg.add_button(label="cos(", width=-1, height=42, callback=on_button_click, user_data="cos(")
                dpg.add_button(label="tan(", width=-1, height=42, callback=on_button_click, user_data="tan(")
                dpg.add_button(label="log(", width=-1, height=42, callback=on_button_click, user_data="log(")
                dpg.add_button(label="ln(", width=-1, height=42, callback=on_button_click, user_data="ln(")

            # Fila 2: Potencias y raíces
            with dpg.table_row():
                dpg.add_button(label="x^y", width=-1, height=42, callback=on_button_click, user_data="^")
                dpg.add_button(label="sqrt(", width=-1, height=42, callback=on_button_click, user_data="sqrt(")
                dpg.add_button(label="pi", width=-1, height=42, callback=on_button_click, user_data="pi")
                dpg.add_button(label="e", width=-1, height=42, callback=on_button_click, user_data="e")
                dpg.add_button(label="abs(", width=-1, height=42, callback=on_button_click, user_data="abs(")

            # Fila 3: Paréntesis y borrado
            with dpg.table_row():
                dpg.add_button(label="(", width=-1, height=42, callback=on_button_click, user_data="(")
                dpg.add_button(label=")", width=-1, height=42, callback=on_button_click, user_data=")")
                dpg.add_button(label="DEL", width=-1, height=42, callback=on_button_click, user_data="DEL")
                dpg.add_button(label="C", width=-1, height=42, callback=on_button_click, user_data="C")
                dpg.add_button(label="/", width=-1, height=42, callback=on_button_click, user_data="/")

            # Fila 4: Números 7, 8, 9 y multiplicación
            with dpg.table_row():
                dpg.add_button(label="7", width=-1, height=42, callback=on_button_click, user_data="7")
                dpg.add_button(label="8", width=-1, height=42, callback=on_button_click, user_data="8")
                dpg.add_button(label="9", width=-1, height=42, callback=on_button_click, user_data="9")
                dpg.add_button(label="*", width=-1, height=42, callback=on_button_click, user_data="*")
                dpg.add_button(label="^2", width=-1, height=42, callback=on_button_click, user_data="**2")

            # Fila 5: Números 4, 5, 6 y resta
            with dpg.table_row():
                dpg.add_button(label="4", width=-1, height=42, callback=on_button_click, user_data="4")
                dpg.add_button(label="5", width=-1, height=42, callback=on_button_click, user_data="5")
                dpg.add_button(label="6", width=-1, height=42, callback=on_button_click, user_data="6")
                dpg.add_button(label="-", width=-1, height=42, callback=on_button_click, user_data="-")
                dpg.add_button(label="1/x", width=-1, height=42, callback=on_button_click, user_data="1/")

            # Fila 6: Números 1, 2, 3 y suma
            with dpg.table_row():
                dpg.add_button(label="1", width=-1, height=42, callback=on_button_click, user_data="1")
                dpg.add_button(label="2", width=-1, height=42, callback=on_button_click, user_data="2")
                dpg.add_button(label="3", width=-1, height=42, callback=on_button_click, user_data="3")
                dpg.add_button(label="+", width=-1, height=42, callback=on_button_click, user_data="+")
                dpg.add_button(label="%", width=-1, height=42, callback=on_button_click, user_data="%")

            # Fila 7: Cero, punto y botón de igual
            with dpg.table_row():
                dpg.add_button(label="0", width=-1, height=42, callback=on_button_click, user_data="0")
                dpg.add_button(label="00", width=-1, height=42, callback=on_button_click, user_data="00")
                dpg.add_button(label=".", width=-1, height=42, callback=on_button_click, user_data=".")
                dpg.add_button(label="=", width=-1, height=42, callback=on_button_click, user_data="=")
                dpg.add_button(label="ANS", width=-1, height=42, callback=on_button_click, user_data="ANS")

        dpg.add_separator()
        dpg.add_text("Historial de Operaciones:")

        with dpg.child_window(
            tag="history_window",
            width=-1,
            height=-1,
            border=True,
            horizontal_scrollbar=True,
        ):
            pass

# Establecer la ventana principal
dpg.set_primary_window("PrimaryWindow", True)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()