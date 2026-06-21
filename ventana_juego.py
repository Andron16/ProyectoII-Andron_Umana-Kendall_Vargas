# ventana_juego.py
# Pantalla principal de la PARTIDA: barra superior de informacion y, debajo,
# el mapa (Canvas 15x15). Por ahora solo la estructura; la cuadricula, la base
# y los datos se agregan en los siguientes bloques.

import tkinter as tk
import constantes
from base import Base


class PantallaJuego(tk.Frame):

    ALTO_BARRA = 100   # alto de la barra superior de informacion (px)

    #E: parent (contenedor), controlador (App)
    #S: instancia de la pantalla de juego con su estructura base
    #R: requiere que el controlador tenga faccion_defensor y faccion_atacante definidas
    def __init__(self, parent, controlador):
        super().__init__(parent, bg=controlador.COLORES["fondo"])
        self.controlador = controlador
        self._construir()

    #E: (usa el controlador)
    #S: no retorna; arma la barra superior y el Canvas del mapa
    #R: ninguna
    def _construir(self):
        c = self.controlador.COLORES

        # --- Barra superior de informacion (se llena en un bloque posterior) ---
        self.barra = tk.Frame(self, bg=c["panel"], height=self.ALTO_BARRA)
        self.barra.pack(fill="x", side="top")
        self.barra.pack_propagate(False)   # respeta la altura fija de la barra

        self._construir_barra()

        # --- Zona del mapa: contiene el Canvas centrado ---
        zona = tk.Frame(self, bg=c["fondo"])
        zona.pack(fill="both", expand=True)

        # Color de fondo del mapa segun la faccion del defensor (si existe).
        if self.controlador.faccion_defensor:
            bg_mapa = self.controlador.faccion_defensor.obtener("fondo")["principal"]
        else:
            bg_mapa = c["fondo"]

        # Canvas del mapa: 15x15 casillas (medidas tomadas de constantes).
        self.canvas = tk.Canvas(zona, width=constantes.ANCHO, height=constantes.ALTO,
                                bg=bg_mapa, highlightthickness=0)
        self.canvas.pack(pady=10)   # sin fill -> queda centrado horizontalmente
        self._dibujar_cuadricula()
        self._dibujar_base()
    
    #E: (usa self.canvas y constantes)
    #S: no retorna; dibuja las lineas de la cuadricula 15x15 sobre el Canvas
    #R: self.canvas debe existir
    def _dibujar_cuadricula(self):
        # Color de linea sutil: borde de la faccion del defensor, o blanco tenue.
        if self.controlador.faccion_defensor:
            color_linea = self.controlador.faccion_defensor.obtener("fondo")["borde"]
        else:
            color_linea = "#FFFFFF"

        # Lineas verticales (una por cada columna + el borde derecho).
        for col in range(constantes.COLUMNAS + 1):
            x = col * constantes.TAM_CELDA
            self.canvas.create_line(x, 0, x, constantes.ALTO,
                                    fill=color_linea, width=1, stipple="gray25")

        # Lineas horizontales (una por cada fila + el borde inferior).
        for fila in range(constantes.FILAS + 1):
            y = fila * constantes.TAM_CELDA
            self.canvas.create_line(0, y, constantes.ANCHO, y,
                                    fill=color_linea, width=1, stipple="gray25")
    #E: (usa self.canvas y la faccion del defensor del controlador)
    #S: no retorna; crea la Base y la dibuja centrada en el mapa
    #R: controlador.faccion_defensor debe estar definida
    def _dibujar_base(self):
        # Creamos la base con la faccion del defensor y la dibujamos en el Canvas.
        self.base = Base(self.controlador.faccion_defensor)
        self.base.dibujar(self.canvas, constantes.TAM_CELDA)
    
    #E: (usa self.barra y el controlador)
    #S: no retorna; llena la barra superior con info de los jugadores, ronda y marcador
    #R: controlador debe tener jugador_defensor, jugador_atacante y sus facciones definidas
    def _construir_barra(self):
        c = self.controlador.COLORES
        jd = self.controlador.jugador_defensor
        ja = self.controlador.jugador_atacante
        fd = self.controlador.faccion_defensor
        fa = self.controlador.faccion_atacante

        # Tres columnas: defensor | centro (ronda/marcador) | atacante.
        self.barra.columnconfigure(0, weight=1)
        self.barra.columnconfigure(1, weight=1)
        self.barra.columnconfigure(2, weight=1)

        # --- Columna izquierda: defensor ---
        col_def = tk.Frame(self.barra, bg=c["panel"])
        col_def.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)

        tk.Label(col_def, text="DEFENSOR", font=("Trebuchet MS", 9),
                 bg=c["panel"], fg=c["tenue"]).pack(anchor="w")
        tk.Label(col_def, text=jd.nombre if jd else "---",
                 font=("Trebuchet MS", 15, "bold"),
                 bg=c["panel"], fg=c["texto"]).pack(anchor="w")
        # Color de faccion como pastilla + nombre.
        fila_fac = tk.Frame(col_def, bg=c["panel"])
        fila_fac.pack(anchor="w", pady=(2, 0))
        if fd:
            tk.Frame(fila_fac, bg=fd.obtener("torre")["principal"],
                     width=14, height=14).pack(side="left", padx=(0, 5))
            tk.Label(fila_fac, text=fd.nombre, font=("Trebuchet MS", 10),
                     bg=c["panel"], fg=c["tenue"]).pack(side="left")

        # --- Columna central: ronda y marcador ---
        col_centro = tk.Frame(self.barra, bg=c["panel"])
        col_centro.grid(row=0, column=1, sticky="nsew", pady=10)

        tk.Label(col_centro, text="RONDA 1",
                 font=("Trebuchet MS", 13, "bold"),
                 bg=c["panel"], fg=c["acento"]).pack()
        # Marcador: victorias defensor vs atacante (de momento 0-0).
        tk.Label(col_centro, text="0  —  0",
                 font=("Trebuchet MS", 22, "bold"),
                 bg=c["panel"], fg=c["texto"]).pack()

        # --- Columna derecha: atacante ---
        col_atk = tk.Frame(self.barra, bg=c["panel"])
        col_atk.grid(row=0, column=2, sticky="nsew", padx=20, pady=10)

        tk.Label(col_atk, text="ATACANTE", font=("Trebuchet MS", 9),
                 bg=c["panel"], fg=c["tenue"]).pack(anchor="e")
        tk.Label(col_atk, text=ja.nombre if ja else "---",
                 font=("Trebuchet MS", 15, "bold"),
                 bg=c["panel"], fg=c["texto"]).pack(anchor="e")
        fila_fac2 = tk.Frame(col_atk, bg=c["panel"])
        fila_fac2.pack(anchor="e", pady=(2, 0))
        if fa:
            tk.Label(fila_fac2, text=fa.nombre, font=("Trebuchet MS", 10),
                     bg=c["panel"], fg=c["tenue"]).pack(side="left")
            tk.Frame(fila_fac2, bg=fa.obtener("torre")["principal"],
                     width=14, height=14).pack(side="left", padx=(5, 0))