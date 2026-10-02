import sys
import wx

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
        self.historial_observaciones = [] # Guardará tuplas o textos: (cliente, observacion)


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
# 2. DIÁLOGOS MODALES Y NO MODALES (wx.Dialog)
# ==========================================

class DialogoConfirmarSalida(wx.Dialog):
    """Ventana modal personalizada para confirmar la salida del sistema."""
    def __init__(self, parent=None):
        super().__init__(parent, title="Confirmar Salida", size=(380, 150))
        self.init_ui()

    def init_ui(self):
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(245, 245, 245))
        
        layout = wx.BoxSizer(wx.VERTICAL)

        lbl_mensaje = wx.StaticText(panel, label="⚠️ ¿Estás seguro que quieres salir del sistema?")
        font = lbl_mensaje.GetFont()
        font.SetPointSize(10)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        lbl_mensaje.SetFont(font)
        lbl_mensaje.Wrap(340)

        layout.Add(lbl_mensaje, 0, wx.ALIGN_CENTER | wx.ALL, 15)

        layout_botones = wx.BoxSizer(wx.HORIZONTAL)

        btn_aceptar = wx.Button(panel, label="Aceptar")
        btn_aceptar.Bind(wx.EVT_BUTTON, lambda evt: self.EndModal(wx.ID_OK))

        btn_cancelar = wx.Button(panel, label="Cancelar")
        btn_cancelar.Bind(wx.EVT_BUTTON, lambda evt: self.EndModal(wx.ID_CANCEL))

        layout_botones.Add(btn_aceptar, 0, wx.RIGHT, 10)
        layout_botones.Add(btn_cancelar, 0)

        layout.Add(layout_botones, 0, wx.ALIGN_CENTER | wx.BOTTOM, 15)
        panel.SetSizer(layout)
        self.Center()


class DialogoSobreNosotros(wx.Dialog):
    """Ventana emergente NO MODAL con la información del sistema y créditos."""
    def __init__(self, parent=None):
        super().__init__(parent, title="Sobre Nosotros", size=(320, 180), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.parent_ref = parent
        self.init_ui()
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def init_ui(self):
        panel = wx.Panel(self)
        layout = wx.BoxSizer(wx.VERTICAL)

        lbl_titulo = wx.StaticText(panel, label="🎬 Random Play - VideoClub")
        font_t = lbl_titulo.GetFont()
        font_t.SetPointSize(11)
        font_t.SetWeight(wx.FONTWEIGHT_BOLD)
        lbl_titulo.SetFont(font_t)

        lbl_descripcion = wx.StaticText(
            panel, 
            label="Sistema integral para la gestión de inventario, alquileres múltiples y control de observaciones en entregas."
        )
        lbl_descripcion.Wrap(290)

        lbl_credito = wx.StaticText(panel, label="Desarrollado por: Dario Marquez")
        font_c = lbl_credito.GetFont()
        font_c.SetWeight(wx.FONTWEIGHT_BOLD)
        lbl_credito.SetFont(font_c)

        btn_cerrar = wx.Button(panel, label="Cerrar")
        btn_cerrar.Bind(wx.EVT_BUTTON, lambda evt: self.Close())

        layout.Add(lbl_titulo, 0, wx.ALL, 10)
        layout.Add(lbl_descripcion, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        layout.Add(lbl_credito, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        layout.Add(btn_cerrar, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        panel.SetSizer(layout)
        self.Center()

    def on_close(self, event):
        if self.parent_ref and hasattr(self.parent_ref, 'dialogo_sobre'):
            self.parent_ref.dialogo_sobre = None
        event.Skip()


class DialogoRegistroAlquileres(wx.Dialog):
    """Ventana modal para visualizar el historial completo de transacciones."""
    def __init__(self, alquileres: list, parent=None):
        super().__init__(parent, title="Registro Global de Alquileres", size=(600, 380))
        self.alquileres = alquileres
        self.init_ui()

    def init_ui(self):
        panel = wx.Panel(self)
        layout = wx.BoxSizer(wx.VERTICAL)

        lbl_titulo = wx.StaticText(panel, label="📜 Historial de Clientes y Alquileres Realizados")
        layout.Add(lbl_titulo, 0, wx.ALL, 10)

        self.tabla = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.tabla.InsertColumn(0, "ID", width=50)
        self.tabla.InsertColumn(1, "Cliente", width=150)
        self.tabla.InsertColumn(2, "Película(s)", width=240)
        self.tabla.InsertColumn(3, "Total Pagado", width=100)

        for fila, alq in enumerate(self.alquileres):
            self.tabla.InsertItem(fila, str(alq.id_alquiler))
            self.tabla.SetItem(fila, 1, alq.cliente.nombre)
            
            peliculas_str = ", ".join([f"{p.titulo} (${p.precio_alquiler:.2f})" for p in alq.peliculas])
            self.tabla.SetItem(fila, 2, peliculas_str)
            self.tabla.SetItem(fila, 3, f"${alq.total_pagado:.2f}")

        layout.Add(self.tabla, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        btn_cerrar = wx.Button(panel, label="Cerrar")
        btn_cerrar.Bind(wx.EVT_BUTTON, lambda evt: self.EndModal(wx.ID_OK))
        layout.Add(btn_cerrar, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        panel.SetSizer(layout)
        self.Center()


class DialogoAlquiler(wx.Dialog):
    """Ventana emergente para procesar el alquiler de una o múltiples películas."""
    def __init__(self, peliculas, parent=None):
        super().__init__(parent, title="Registrar Nuevo Alquiler", size=(400, 320))
        self.peliculas = [p for p in peliculas if p.disponible]
        self.peliculas_seleccionadas = []
        self.nombre_cliente = ""
        self.init_ui()

    def init_ui(self):
        panel = wx.Panel(self)
        layout = wx.BoxSizer(wx.VERTICAL)

        layout.Add(wx.StaticText(panel, label="Nombre del Cliente:"), 0, wx.LEFT | wx.TOP, 10)
        self.input_cliente = wx.TextCtrl(panel)
        layout.Add(self.input_cliente, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        layout.Add(wx.StaticText(panel, label="Seleccionar Películas (Selección múltiple con Ctrl/Shift):"), 0, wx.LEFT, 10)
        
        nombres_pelis = [f"[{p.id_pelicula}] {p.titulo} - ${p.precio_alquiler:.2f}" for p in self.peliculas]
        if not nombres_pelis:
            nombres_pelis = ["No hay películas disponibles"]
            
        self.lista_peliculas = wx.ListBox(panel, choices=nombres_pelis, style=wx.LB_EXTENDED)
        if not self.peliculas:
            self.lista_peliculas.Enable(False)

        layout.Add(self.lista_peliculas, 1, wx.EXPAND | wx.ALL, 10)

        btn_confirmar = wx.Button(panel, label="🚀 Confirmar y Alquilar")
        btn_confirmar.Bind(wx.EVT_BUTTON, self.confirmar)
        layout.Add(btn_confirmar, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        panel.SetSizer(layout)
        self.Center()

    def confirmar(self, event):
        cliente_texto = self.input_cliente.GetValue().strip()
        if not cliente_texto:
            wx.MessageBox("Por favor ingresa el nombre del cliente.", "Atención", wx.OK | wx.ICON_WARNING)
            return

        indices = self.lista_peliculas.GetSelections()
        if not indices or not self.lista_peliculas.IsEnabled():
            wx.MessageBox("Debes seleccionar al menos una película.", "Atención", wx.OK | wx.ICON_WARNING)
            return

        self.peliculas_seleccionadas = [self.peliculas[i] for i in indices]
        self.nombre_cliente = cliente_texto
        self.EndModal(wx.ID_OK)


class DialogoDevolucion(wx.Dialog):
    """Ventana emergente para confirmar devolución y añadir observaciones."""
    def __init__(self, pelicula: Pelicula, parent=None):
        super().__init__(parent, title="Devolver Película", size=(380, 260))
        self.pelicula = pelicula
        self.nota_ingresada = ""
        self.init_ui()

    def init_ui(self):
        panel = wx.Panel(self)
        layout = wx.BoxSizer(wx.VERTICAL)

        lbl_info = wx.StaticText(panel, label=f"Devolución de: {self.pelicula.titulo}")
        layout.Add(lbl_info, 0, wx.ALL, 10)

        layout.Add(wx.StaticText(panel, label="Reseña u observación del último cliente (Opcional):"), 0, wx.LEFT, 10)
        self.txt_observacion = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        self.txt_observacion.SetHint("Ej. Excelente película, muy entretenida...")
        layout.Add(self.txt_observacion, 1, wx.EXPAND | wx.ALL, 10)

        btn_confirmar = wx.Button(panel, label="🔄 Confirmar Devolución")
        btn_confirmar.Bind(wx.EVT_BUTTON, self.confirmar)
        layout.Add(btn_confirmar, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        panel.SetSizer(layout)
        self.Center()

    def confirmar(self, event):
        self.nota_ingresada = self.txt_observacion.GetValue().strip()
        self.EndModal(wx.ID_OK)


class DialogoHistorial(wx.Dialog):
    """Ventana modal para visualizar las reseñas y observaciones de los últimos alquileres."""
    def __init__(self, pelicula: Pelicula, parent=None):
        super().__init__(parent, title=f"Historial y Reseñas - {pelicula.titulo}", size=(450, 320))
        self.pelicula = pelicula
        self.init_ui()

    def init_ui(self):
        panel = wx.Panel(self)
        layout = wx.BoxSizer(wx.VERTICAL)

        lbl_titulo = wx.StaticText(panel, label=f"📜 Reseñas de los últimos clientes para: {self.pelicula.titulo}")
        layout.Add(lbl_titulo, 0, wx.ALL, 10)

        self.txt_historial = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)

        if self.pelicula.historial_observaciones:
            contenido = ""
            for i, item in enumerate(self.pelicula.historial_observaciones, 1):
                if isinstance(item, tuple):
                    cliente, nota = item
                    contenido += f"Cliente: {cliente}\nReseña #{i}: {nota}\n" + "─"*40 + "\n"
                else:
                    contenido += f"Reseña #{i}: {item}\n" + "─"*40 + "\n"
            self.txt_historial.SetValue(contenido)
        else:
            self.txt_historial.SetValue("No hay reseñas registradas por los últimos clientes para esta película.")

        layout.Add(self.txt_historial, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        btn_cerrar = wx.Button(panel, label="Cerrar")
        btn_cerrar.Bind(wx.EVT_BUTTON, lambda evt: self.EndModal(wx.ID_OK))
        layout.Add(btn_cerrar, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        panel.SetSizer(layout)
        self.Center()


# ==========================================
# 3. VENTANA PRINCIPAL DE LA APLICACIÓN
# ==========================================

class VideoClubWindow(wx.Frame):
    """Ventana principal del sistema de gestión del VideoClub."""
    def __init__(self):
        super().__init__(None, title="Random Play - VideoClub", size=(950, 620))

        self.peliculas = []
        self.alquileres = []
        self.dialogo_sobre = None

        self.cargar_datos_ejemplo()
        self.init_ui()
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Center()

    def on_close(self, event):
        """Intercepta el evento de cierre para mostrar la confirmación."""
        dialogo = DialogoConfirmarSalida(self)
        if dialogo.ShowModal() == wx.ID_OK:
            event.Skip()
        else:
            event.Veto()

    def cargar_datos_ejemplo(self):
        p1 = Pelicula(1, "Matrix", "Ciencia Ficción", 3.50)
        p1.historial_observaciones.append(("Carlos Gómez", "Excelente película de acción y ciencia ficción, muy recomendada."))
        
        p2 = Pelicula(2, "El Padrino", "Drama", 4.00)
        p3 = Pelicula(3, "Toy Story", "Animación", 2.50)

        self.peliculas.extend([p1, p2, p3])

    def init_ui(self):
        panel = wx.Panel(self)
        layout_principal = wx.BoxSizer(wx.VERTICAL)

        # Header
        layout_header = wx.BoxSizer(wx.HORIZONTAL)
        lbl_titulo = wx.StaticText(panel, label="🎬 Random Play - VideoClub")
        font = lbl_titulo.GetFont()
        font.SetPointSize(14)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        lbl_titulo.SetFont(font)

        btn_sobre = wx.Button(panel, label="ℹ️ Sobre Nosotros")
        btn_sobre.Bind(wx.EVT_BUTTON, self.abrir_sobre_nosotros)

        layout_header.Add(lbl_titulo, 0, wx.ALIGN_CENTER_VERTICAL)
        layout_header.AddStretchSpacer()
        layout_header.Add(btn_sobre, 0, wx.ALIGN_CENTER_VERTICAL)

        layout_principal.Add(layout_header, 0, wx.EXPAND | wx.ALL, 10)

        self.lbl_estadisticas = wx.StaticText(panel, label="")
        layout_principal.Add(self.lbl_estadisticas, 0, wx.LEFT | wx.BOTTOM, 10)

        # Formulario para agregar película
        layout_form = wx.BoxSizer(wx.HORIZONTAL)

        self.input_titulo = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        self.input_titulo.SetHint("Título de la película")

        self.combo_genero = wx.ComboBox(panel, choices=["Acción", "Comedia", "Drama", "Terror", "Infantil", "Ciencia Ficción", "Romance", "Animación"], style=wx.CB_READONLY)
        self.combo_genero.SetSelection(0)

        self.input_precio = wx.TextCtrl(panel)
        self.input_precio.SetHint("Precio ($)")

        btn_agregar = wx.Button(panel, label="＋ Agregar Película")
        btn_agregar.Bind(wx.EVT_BUTTON, self.registrar_pelicula)

        layout_form.Add(self.input_titulo, 1, wx.RIGHT, 5)
        layout_form.Add(self.combo_genero, 1, wx.RIGHT, 5)
        layout_form.Add(self.input_precio, 1, wx.RIGHT, 5)
        layout_form.Add(btn_agregar, 0)

        layout_principal.Add(layout_form, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # Buscador
        layout_busqueda = wx.BoxSizer(wx.HORIZONTAL)
        lbl_buscar = wx.StaticText(panel, label="🔍 Buscar:")
        self.input_buscar = wx.TextCtrl(panel)
        self.input_buscar.SetHint("Filtrar por título...")
        self.input_buscar.Bind(wx.EVT_TEXT, self.filtrar_peliculas)

        layout_busqueda.Add(lbl_buscar, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        layout_busqueda.Add(self.input_buscar, 1, wx.EXPAND)
        layout_principal.Add(layout_busqueda, 0, wx.EXPAND | wx.ALL, 10)

        # Tabla de inventario
        self.tabla_peliculas = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.tabla_peliculas.InsertColumn(0, "ID", width=60)
        self.tabla_peliculas.InsertColumn(1, "Título", width=220)
        self.tabla_peliculas.InsertColumn(2, "Género", width=140)
        self.tabla_peliculas.InsertColumn(3, "Precio", width=100)
        self.tabla_peliculas.InsertColumn(4, "Estado", width=120)
        self.tabla_peliculas.InsertColumn(5, "Historial", width=120)
        
        self.tabla_peliculas.Bind(wx.EVT_LEFT_DOWN, self.on_tabla_left_down)

        layout_principal.Add(self.tabla_peliculas, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # Acciones inferiores
        layout_acciones = wx.BoxSizer(wx.HORIZONTAL)

        btn_alquilar = wx.Button(panel, label="🎟 Registrar Nuevo Alquiler")
        btn_alquilar.Bind(wx.EVT_BUTTON, self.abrir_dialogo_alquiler)

        btn_devolver = wx.Button(panel, label="🔄 Devolver Película Seleccionada")
        btn_devolver.Bind(wx.EVT_BUTTON, self.devolver_pelicula)

        btn_registro_global = wx.Button(panel, label="📋 Ver Registro de Alquileres")
        btn_registro_global.Bind(wx.EVT_BUTTON, self.abrir_registro_alquileres)

        layout_acciones.Add(btn_alquilar, 0, wx.RIGHT, 5)
        layout_acciones.Add(btn_devolver, 0, wx.RIGHT, 5)
        layout_acciones.Add(btn_registro_global, 0)

        layout_principal.Add(layout_acciones, 0, wx.ALL, 10)

        panel.SetSizer(layout_principal)
        self.actualizar_tabla()

    def abrir_sobre_nosotros(self, event):
        if self.dialogo_sobre is None:
            self.dialogo_sobre = DialogoSobreNosotros(self)
            self.dialogo_sobre.Show()
        else:
            self.dialogo_sobre.Raise()

    def abrir_registro_alquileres(self, event):
        if not self.alquileres:
            wx.MessageBox("Aún no se han registrado alquileres.", "Registro Vacío", wx.OK | wx.ICON_INFORMATION)
            return

        dialogo = DialogoRegistroAlquileres(self.alquileres, self)
        dialogo.ShowModal()

    def registrar_pelicula(self, event):
        titulo = self.input_titulo.GetValue().strip()
        genero = self.combo_genero.GetStringSelection()
        precio_texto = self.input_precio.GetValue().strip()

        if not titulo or not precio_texto:
            wx.MessageBox("Ingresa el título y el precio.", "Error", wx.OK | wx.ICON_ERROR)
            return

        try:
            precio = float(precio_texto)
            if precio <= 0:
                raise ValueError
        except ValueError:
            wx.MessageBox("El precio debe ser un número positivo.", "Error", wx.OK | wx.ICON_ERROR)
            return

        nuevo_id = len(self.peliculas) + 1
        nueva_pelicula = Pelicula(nuevo_id, titulo, genero, precio)
        self.peliculas.append(nueva_pelicula)

        self.input_titulo.Clear()
        self.input_precio.Clear()
        self.actualizar_tabla()
        wx.MessageBox(f"Película '{titulo}' agregada correctamente.", "Éxito", wx.OK | wx.ICON_INFORMATION)

    def actualizar_tabla(self, lista_mostrar=None):
        self.tabla_peliculas.DeleteAllItems()
        
        if lista_mostrar is None:
            lista_mostrar = self.peliculas

        for fila, pelicula in enumerate(lista_mostrar):
            self.tabla_peliculas.InsertItem(fila, str(pelicula.id_pelicula))
            self.tabla_peliculas.SetItem(fila, 1, pelicula.titulo)
            self.tabla_peliculas.SetItem(fila, 2, pelicula.genero)
            self.tabla_peliculas.SetItem(fila, 3, f"${pelicula.precio_alquiler:.2f}")
            
            estado_str = "Disponible" if pelicula.disponible else "Alquilada"
            self.tabla_peliculas.SetItem(fila, 4, estado_str)
            self.tabla_peliculas.SetItem(fila, 5, "Ver Historial")

        total = len(self.peliculas)
        disponibles = sum(1 for p in self.peliculas if p.disponible)
        alquiladas = total - disponibles
        self.lbl_estadisticas.SetLabel(
            f"📊 Total: {total} | Disponibles: {disponibles} | Alquiladas: {alquiladas}"
        )

    def filtrar_peliculas(self, event):
        texto_busqueda = self.input_buscar.GetValue().lower().strip()
        peliculas_filtradas = [
            p for p in self.peliculas if texto_busqueda in p.titulo.lower()
        ]
        self.actualizar_tabla(peliculas_filtradas)

    def on_tabla_left_down(self, event):
        """Detecta si se hace clic específicamente en la celda 'Ver Historial' (Columna 5)."""
        pos = event.GetPosition()
        fila, flags = self.tabla_peliculas.HitTest(pos)
        
        if fila != wx.NOT_FOUND:
            columna = -1
            ancho_acumulado = 0
            for col in range(self.tabla_peliculas.GetColumnCount()):
                ancho_acumulado += self.tabla_peliculas.GetColumnWidth(col)
                if pos.x < ancho_acumulado:
                    columna = col
                    break
            
            if columna == 5:
                id_pelicula = int(self.tabla_peliculas.GetItemText(fila, 0))
                pelicula = next((p for p in self.peliculas if p.id_pelicula == id_pelicula), None)
                if pelicula:
                    dialogo = DialogoHistorial(pelicula, self)
                    dialogo.ShowModal()
                    return

        event.Skip()

    def abrir_dialogo_alquiler(self, event):
        dialogo = DialogoAlquiler(self.peliculas, self)
        if dialogo.ShowModal() == wx.ID_OK:
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
                wx.MessageBox(
                    f"Cliente: {cliente_nombre}\n"
                    f"Películas alquiladas ({len(pelis_seleccionadas)}):\n{titulos}\n"
                    f"Total a pagar: ${nuevo_alquiler.total_pagado:.2f}",
                    "Alquiler Exitoso",
                    wx.OK | wx.ICON_INFORMATION
                )

    def devolver_pelicula(self, event):
        fila_seleccionada = self.tabla_peliculas.GetFirstSelected()

        if fila_seleccionada < 0:
            wx.MessageBox("Por favor selecciona una película de la tabla.", "Atención", wx.OK | wx.ICON_INFORMATION)
            return

        id_pelicula = int(self.tabla_peliculas.GetItemText(fila_seleccionada, 0))
        pelicula = next((p for p in self.peliculas if p.id_pelicula == id_pelicula), None)

        if pelicula:
            if pelicula.disponible:
                wx.MessageBox("Esta película ya se encuentra disponible.", "Información", wx.OK | wx.ICON_INFORMATION)
                return

            dialogo_dev = DialogoDevolucion(pelicula, self)
            if dialogo_dev.ShowModal() == wx.ID_OK:
                pelicula.disponible = True
                if dialogo_dev.nota_ingresada:
                    cliente_ultimo = self.alquileres[-1].cliente.nombre if self.alquileres else "Cliente Anónimo"
                    pelicula.historial_observaciones.append((cliente_ultimo, dialogo_dev.nota_ingresada))

                self.actualizar_tabla()
                wx.MessageBox(f"La película '{pelicula.titulo}' ha sido devuelta.", "Devolución", wx.OK | wx.ICON_INFORMATION)


# ==========================================
# 4. PUNTO DE ENTRADA DE LA APLICACIÓN
# ==========================================

if __name__ == "__main__":
    app = wx.App(False)
    ventana = VideoClubWindow()
    ventana.Show()
    app.MainLoop()