# ventana_fin.py
# Pantalla de FIN DE PARTIDA: anuncia al jugador ganador y su rol, muestra el
# marcador final y permite volver al menu principal.

import tkinter as tk


class PantallaFin(tk.Frame):

    #E: parent (contenedor), controlador (App), ganador_nombre (str),
    #   rol_ganador (str: "defensor" o "atacante"), marcador_def (int), marcador_atk (int)
    #S: instancia de la pantalla de fin de partida lista para mostrar
    #R: rol_ganador debe ser "defensor" o "atacante"
    def __init__(self, parent, controlador, ganador_nombre, rol_ganador,
                 marcador_def, marcador_atk):
        super().__init__(parent, bg=controlador.COLORES["fondo"])
        self.controlador = controlador
        self.ganador_nombre = ganador_nombre
        self.rol_ganador = rol_ganador
        self.marcador_def = marcador_def
        self.marcador_atk = marcador_atk
        self._construir()

    #E: (usa los datos del ganador y el controlador)
    #S: no retorna; arma el anuncio del ganador, el marcador y el boton de volver
    #R: ninguna
    def _construir(self):
        c = self.controlador.COLORES

        tk.Label(self, text="Partida terminada",
                 font=("Trebuchet MS", 18),
                 bg=c["fondo"], fg=c["tenue"]).pack(pady=(90, 10))

        # Anuncio principal del ganador.
        tk.Label(self, text=self.ganador_nombre + " gana",
                 font=("Trebuchet MS", 38, "bold"),
                 bg=c["fondo"], fg=c["acento"]).pack(pady=(0, 2))
        tk.Label(self, text="como " + self.rol_ganador.capitalize(),
                 font=("Trebuchet MS", 18),
                 bg=c["fondo"], fg=c["texto"]).pack(pady=(0, 40))

        # Marcador final.
        marcador = str(self.marcador_def) + "  —  " + str(self.marcador_atk)
        tk.Label(self, text=marcador,
                 font=("Trebuchet MS", 30, "bold"),
                 bg=c["fondo"], fg=c["texto"]).pack()
        tk.Label(self, text="Defensor                Atacante",
                 font=("Trebuchet MS", 10),
                 bg=c["fondo"], fg=c["tenue"]).pack(pady=(0, 50))

        # Boton para volver al menu.
        self.controlador.boton(self, "Volver al menú", self._volver).pack()

    #E: (no recibe parametros)
    #S: no retorna; limpia el estado de la partida y vuelve al menu principal
    #R: ninguna
    def _volver(self):
        # Limpiamos los datos de la partida para empezar una nueva desde cero.
        self.controlador.jugador_defensor = None
        self.controlador.jugador_atacante = None
        self.controlador.faccion_defensor = None
        self.controlador.faccion_atacante = None
        from ventana_menu import PantallaMenu
        self.controlador.mostrar(PantallaMenu)