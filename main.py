# main.py
# Punto de entrada y CONTROLADOR del juego. Una sola ventana que intercambia
# pantallas (frames): menu -> login -> facciones -> juego. Guarda el estado
# compartido de la partida (jugadores y facciones elegidas).

import tkinter as tk
from gestor_jugadores import GestorJugadores
from ventana_menu import PantallaMenu

class App(tk.Tk):

    # Tema visual centralizado: todas las pantallas usan estos colores.
    # Tema visual centralizado: todas las pantallas usan estos colores.
    COLORES = {
        "fondo": "#0A1A33",        # azul muy oscuro (navy) de fondo
        "panel": "#102A4C",        # azul oscuro para paneles/bordes
        "texto": "#FFFFFF",        # blanco
        "tenue": "#9FC0E8",        # azul claro grisaceo (texto secundario)
        "acento": "#5AA9FF",       # azul claro brillante (titulos/acentos)
        "acento2": "#BBD9FF",      # azul muy claro (halos de luz)
        "boton": "#15315A",        # azul oscuro de boton
        "boton_activo": "#1E4577", # azul al pasar el mouse
    }

    #E: (no recibe parametros)
    #S: instancia de la ventana principal, mostrando el menu
    #R: ninguna
    def __init__(self):
        super().__init__()
        self.title("Defensa y Asalto de Base")
        self.geometry("1000x790")
        self.resizable(False, False)
        self.configure(bg=self.COLORES["fondo"])

        # Acceso a los datos de jugadores (registro, login, ranking).
        self.gestor = GestorJugadores()

        # Estado compartido de la partida (se llena en el flujo de configuracion).
        self.jugador_defensor = None
        self.jugador_atacante = None
        self.faccion_defensor = None
        self.faccion_atacante = None

        # Contenedor unico donde se monta la pantalla activa.
        self.contenedor = tk.Frame(self, bg=self.COLORES["fondo"])
        self.contenedor.pack(fill="both", expand=True)
        self.pantalla_actual = None

        # Pantalla inicial: el menu principal.
        self.mostrar(PantallaMenu)

    #E: ClasePantalla (clase Frame que recibe (parent, controlador))
    #S: no retorna; quita la pantalla anterior y muestra la nueva
    #R: ClasePantalla debe heredar de tk.Frame
    def mostrar(self, ClasePantalla):
        # Frame-swapping: destruimos la pantalla previa y montamos la nueva.
        if self.pantalla_actual is not None:
            self.pantalla_actual.destroy()
        self.pantalla_actual = ClasePantalla(self.contenedor, self)
        self.pantalla_actual.pack(fill="both", expand=True)

    #E: parent (widget), texto (str), comando (funcion sin argumentos)
    #S: un boton ya estilizado con el tema del juego
    #R: ninguna
    def boton(self, parent, texto, comando):
        return tk.Button(
            parent, text=texto, command=comando, width=16,
            font=("Trebuchet MS", 18, "bold"),
            bg=self.COLORES["boton"], fg=self.COLORES["texto"],
            activebackground=self.COLORES["boton_activo"],
            activeforeground=self.COLORES["acento"],
            relief="flat", bd=0, padx=20, pady=12, cursor="hand2",
            highlightthickness=1, highlightbackground=self.COLORES["panel"]
        )

# Punto de entrada: se ejecuta todo el juego desde aqui.
if __name__ == "__main__":
    app = App()
    app.mainloop()