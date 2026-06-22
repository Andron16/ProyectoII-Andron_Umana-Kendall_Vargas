# ventana_menu.py
# Pantalla de MENU principal. Fondo animado con haces de luz suaves (azul/blanco)
# que aparecen y se desvanecen. El titulo y los botones van sobre un Canvas.

import math
import random
import tkinter as tk
from tkinter import messagebox


class PantallaMenu(tk.Frame):

    ANCHO = 1000    # ancho del area de dibujo (coincide con la ventana)
    ALTO = 720      # alto del area de dibujo
    NUM_HACES = 7   # cantidad de haces simultaneos (pocos = sutil)

    #E: parent (contenedor), controlador (App)
    #S: instancia de la pantalla de menu con su fondo animado
    #R: ninguna
    def __init__(self, parent, controlador):
        super().__init__(parent, bg=controlador.COLORES["fondo"])
        self.controlador = controlador
        self.haces = []          # lista de haces activos (cada uno es un dict)
        self._construir()
        self._animar()           # arranca el bucle de animacion
        self.controlador.reproducir_musica("assets/sonidos/menu.wav")

    #E: (usa el controlador)
    #S: no retorna; arma el Canvas, los haces y los widgets del menu
    #R: ninguna
    def _construir(self):
        c = self.controlador.COLORES

        # Canvas que ocupa toda la ventana: aqui se dibuja el fondo animado.
        self.canvas = tk.Canvas(self, width=self.ANCHO, height=self.ALTO,
                                bg=c["fondo"], highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Creamos los haces PRIMERO para que queden por DEBAJO del texto/botones.
        for _ in range(self.NUM_HACES):
            self.haces.append(self._crear_haz())

        # Titulo y subtitulo (texto dibujado sobre el Canvas).
        cx = self.ANCHO / 2
        self.canvas.create_text(cx, 150, text="Clash No Royale",
                                fill=c["acento"], font=("Trebuchet MS", 40, "bold"))
        self.canvas.create_text(cx, 200, text="By Andron y Palma",
                                fill=c["tenue"], font=("Trebuchet MS", 16))

        # Botones: son widgets reales incrustados en el Canvas con create_window.
        b_jugar = self.controlador.boton(self.canvas, "Jugar", self._jugar)
        b_ranking = self.controlador.boton(self.canvas, "Ranking", self._ranking)
        b_salir = self.controlador.boton(self.canvas, "Salir", self.controlador.destroy)
        self.canvas.create_window(cx, 320, window=b_jugar)
        self.canvas.create_window(cx, 410, window=b_ranking)
        self.canvas.create_window(cx, 500, window=b_salir)

    # ===================================================================
    # FONDO ANIMADO: haces de luz
    # ===================================================================

    #E: c1 (hex "#rrggbb"), c2 (hex "#rrggbb"), t (float 0..1)
    #S: color hex intermedio entre c1 y c2 segun t (0 = c1, 1 = c2)
    #R: t debe estar entre 0 y 1
    def _mezclar(self, c1, c2, t):
        # Interpolamos cada componente RGB por separado para simular el "fundido".
        r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
        r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
        r = round(r1 + (r2 - r1) * t)
        g = round(g1 + (g2 - g1) * t)
        b = round(b1 + (b2 - b1) * t)
        return f"#{r:02x}{g:02x}{b:02x}"

    #E: haz (dict al que se le asignan geometria y tiempos)
    #S: no retorna; define posicion, direccion y ritmo del haz
    #R: ninguna
    def _geometria_haz(self, haz):
        # Direccion diagonal (hacia arriba-derecha) y largo aleatorio.
        ang = math.radians(random.uniform(28, 52))
        largo = random.uniform(280, 460)
        x1 = random.uniform(-120, self.ANCHO)
        y1 = random.uniform(160, self.ALTO + 120)
        haz["x1"], haz["y1"] = x1, y1
        haz["x2"] = x1 + largo * math.cos(ang)
        haz["y2"] = y1 - largo * math.sin(ang)
        # 'fase' recorre 0..pi: el brillo = sin(fase), suave al entrar y al salir.
        haz["fase"] = 0.0
        haz["vel"] = random.uniform(0.022, 0.045)     # velocidad del fundido
        haz["brillo_max"] = random.uniform(0.30, 0.50)  # tope tenue (sutil)
        haz["retraso"] = random.randint(0, 60)        # espera inicial (escalona)

    #E: (no recibe parametros)
    #S: un dict de haz con sus dos lineas ya creadas en el Canvas
    #R: ninguna
    def _crear_haz(self):
        haz = {}
        self._geometria_haz(haz)
        fondo = self.controlador.COLORES["fondo"]
        # Dos lineas: una ancha y tenue (halo) y una fina y brillante (nucleo).
        # Empiezan del color de fondo (invisibles) y se iran aclarando.
        haz["id_halo"] = self.canvas.create_line(haz["x1"], haz["y1"], haz["x2"], haz["y2"],
                                                 fill=fondo, width=7, capstyle="round")
        haz["id_nucleo"] = self.canvas.create_line(haz["x1"], haz["y1"], haz["x2"], haz["y2"],
                                                   fill=fondo, width=2, capstyle="round")
        return haz

    #E: haz (dict ya existente)
    #S: no retorna; le da nueva posicion y reinicia su ciclo de brillo
    #R: ninguna
    def _reiniciar_haz(self, haz):
        fondo = self.controlador.COLORES["fondo"]
        self._geometria_haz(haz)
        # Reposicionamos las dos lineas y las apagamos para que vuelvan a aparecer.
        self.canvas.coords(haz["id_halo"], haz["x1"], haz["y1"], haz["x2"], haz["y2"])
        self.canvas.coords(haz["id_nucleo"], haz["x1"], haz["y1"], haz["x2"], haz["y2"])
        self.canvas.itemconfig(haz["id_halo"], fill=fondo)
        self.canvas.itemconfig(haz["id_nucleo"], fill=fondo)

    #E: (no recibe parametros)
    #S: no retorna; actualiza el brillo de cada haz y se reprograma solo
    #R: se detiene si la pantalla ya fue destruida
    def _animar(self):
        # Si cambiamos de pantalla, el Frame se destruye: cortamos el bucle.
        if not self.winfo_exists():
            return

        c = self.controlador.COLORES
        for haz in self.haces:
            # Espera inicial para que no aparezcan todos a la vez.
            if haz["retraso"] > 0:
                haz["retraso"] -= 1
                continue
            haz["fase"] += haz["vel"]
            # Termino su ciclo: lo reubicamos y empieza otro haz.
            if haz["fase"] >= math.pi:
                self._reiniciar_haz(haz)
                continue
            # Brillo suave (0 -> 1 -> 0) limitado por brillo_max.
            brillo = math.sin(haz["fase"]) * haz["brillo_max"]
            self.canvas.itemconfig(haz["id_nucleo"], fill=self._mezclar(c["fondo"], "#FFFFFF", brillo))
            self.canvas.itemconfig(haz["id_halo"], fill=self._mezclar(c["fondo"], c["acento2"], brillo * 0.5))

        # ~20 cuadros por segundo: fluido y muy liviano.
        self.after(50, self._animar)

    # ACCIONES DE LOS BOTONES

    #E: (no recibe parametros)
    #S: no retorna; inicia el flujo de partida (dos inicios de sesion)
    #R: ninguna
    def _jugar(self):
        from ventana_login import PantallaLogin
        self.controlador.mostrar(lambda p, c: PantallaLogin(p, c, turno=1))

    #E: (no recibe parametros)
    #S: no retorna; abre la pantalla de ranking
    #R: ninguna
    def _ranking(self):
        from ventana_ranking import PantallaRanking
        self.controlador.mostrar(PantallaRanking)