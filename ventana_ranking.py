# ventana_ranking.py
# Pantalla de RANKING: muestra el top 5 de defensores y atacantes.

import tkinter as tk


class PantallaRanking(tk.Frame):

    #E: parent (contenedor), controlador (App)
    #S: instancia de la pantalla de ranking lista para mostrar
    #R: ninguna
    def __init__(self, parent, controlador):
        super().__init__(parent, bg=controlador.COLORES["fondo"])
        self.controlador = controlador
        self._construir()

    #E: (usa el controlador)
    #S: no retorna; arma los widgets de la pantalla
    #R: ninguna
    def _construir(self):
        c = self.controlador.COLORES

        tk.Label(self, text="Ranking de Jugadores",
                 font=("Trebuchet MS", 28, "bold"),
                 bg=c["fondo"], fg=c["acento"]).pack(pady=(50, 6))
        tk.Label(self, text="Los mejores defensores y atacantes",
                 font=("Trebuchet MS", 13),
                 bg=c["fondo"], fg=c["tenue"]).pack(pady=(0, 30))

        # Contenedor de las dos tablas lado a lado.
        marco = tk.Frame(self, bg=c["fondo"])
        marco.pack()

        self._tabla(marco, "Defensores", self.controlador.gestor.top_defensores(), 0)
        self._tabla(marco, "Atacantes", self.controlador.gestor.top_atacantes(), 1)

        self.controlador.boton(self, "Volver",
                               self._volver).pack(pady=30)

    #E: parent (Frame), titulo (str), jugadores (lista de Jugador), columna (int)
    #S: no retorna; dibuja una tabla con el top de jugadores en la columna indicada
    #R: ninguna
    def _tabla(self, parent, titulo, jugadores, columna):
        c = self.controlador.COLORES

        # Panel de cada tabla.
        panel = tk.Frame(parent, bg=c["panel"], padx=30, pady=20)
        panel.grid(row=0, column=columna, padx=20)

        tk.Label(panel, text=titulo, font=("Trebuchet MS", 15, "bold"),
                 bg=c["panel"], fg=c["acento2"]).pack(pady=(0, 12))

        # Encabezado de columnas.
        enc = tk.Frame(panel, bg=c["panel"])
        enc.pack(fill="x")
        tk.Label(enc, text="#", width=3, font=("Trebuchet MS", 11, "bold"),
                 bg=c["panel"], fg=c["tenue"]).grid(row=0, column=0)
        tk.Label(enc, text="Jugador", width=16, font=("Trebuchet MS", 11, "bold"),
                 bg=c["panel"], fg=c["tenue"], anchor="w").grid(row=0, column=1)
        tk.Label(enc, text="Victorias", width=9, font=("Trebuchet MS", 11, "bold"),
                 bg=c["panel"], fg=c["tenue"]).grid(row=0, column=2)

        # Separador visual.
        tk.Frame(panel, bg=c["acento"], height=1).pack(fill="x", pady=6)

        # Filas del ranking (maximo 5).
        # Si hay menos de 5 jugadores, mostramos "---" en las posiciones vacias.
        for i in range(5):
            fila = tk.Frame(panel, bg=c["panel"])
            fila.pack(fill="x", pady=3)

            if i < len(jugadores):
                j = jugadores[i]
                # Color dorado para el primero, normal para el resto.
                color = c["acento"] if i == 0 else c["texto"]
                nombre = j.nombre
                victorias = str(j.victorias_defensor if titulo == "Defensores"
                                else j.victorias_atacante)
            else:
                color = c["tenue"]
                nombre = "---"
                victorias = "-"

            tk.Label(fila, text=str(i + 1), width=3,
                     font=("Trebuchet MS", 12), bg=c["panel"], fg=color).grid(row=0, column=0)
            tk.Label(fila, text=nombre, width=16, anchor="w",
                     font=("Trebuchet MS", 12), bg=c["panel"], fg=color).grid(row=0, column=1)
            tk.Label(fila, text=victorias, width=9,
                     font=("Trebuchet MS", 12), bg=c["panel"], fg=color).grid(row=0, column=2)

    #E: (no recibe parametros)
    #S: no retorna; regresa al menu principal
    #R: ninguna
    def _volver(self):
        from ventana_menu import PantallaMenu
        self.controlador.mostrar(PantallaMenu)