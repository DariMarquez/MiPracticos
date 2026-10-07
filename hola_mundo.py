import tkinter as tk
from tkinter import messagebox

def mostrar_saludo():
    nombre = entrada_nombre.get()
    if nombre:
        messagebox.showinfo("Saludo", f"¡Hola, {nombre}! Bienvenido.")
    else:
        messagebox.showwarning("Aviso", "Por favor, ingresa tu nombre.")

def cerrar_programa():
    root.destroy()

root = tk.Tk()
root.title("Saludo Personalizado")
root.geometry("350x180")
root.resizable(False, False)

tk.Label(root, text="Escribe tu nombre:", font=("Arial", 12)).pack(pady=10)

entrada_nombre = tk.Entry(root, font=("Arial", 12), width=25)
entrada_nombre.pack(pady=5)
entrada_nombre.focus()

boton_saludo = tk.Button(root, text="Saludar", font=("Arial", 11), command=mostrar_saludo)
boton_saludo.pack(pady=5)

boton_aceptar = tk.Button(root, text="Aceptar", font=("Arial", 11), command=cerrar_programa)
boton_aceptar.pack(pady=5)

root.mainloop()
