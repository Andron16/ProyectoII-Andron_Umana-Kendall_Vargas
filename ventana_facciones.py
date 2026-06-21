# ventana_facciones.py
# Pantalla de SELECCION DE FACCION. Se reutiliza dos veces: primero el defensor
# elige, luego el atacante (con la faccion del defensor deshabilitada).

import tkinter as tk
from tkinter import messagebox
from faccion import Faccion
import constantes


class PantallaFacciones(tk.Frame):

    ANCHO_TARJETA = 220
    ALTO_TARJETA  = 300

    #E: parent (contenedor), controlador (App), turno (int: 1 defensor, 2 atacante)
    #S: instancia de la pantalla de seleccion de faccion
    #R: turno debe ser 1 o 2
    def __init__(self, parent, controlador, turno=1):
        super().__init__(parent, bg=controlador.COLORES["fondo"])
        self.controlador = controlador
        self.turno = turno
        self.seleccion = tk.StringVar(value="")  # faccion elegida en esta pantalla
        self._construir()

    #E: (usa el controlador y el turno)
    #S: no retorna; arma el titulo, las tarjetas y el boton de confirmar
    #R: ninguna
    def _construir(self):
        c = self.controlador.COLORES

        tk.Label(self, text="Selección de Facción",
                 font=("Trebuchet MS", 28, "bold"),
                 bg=c["fondo"], fg=c["acento"]).pack(pady=(44, 4))

        # Subtitulo dinamico segun el turno.
        sub = "Defensor — elige tu facción" if self.turno == 1 else "Atacante — elige tu facción"
        tk.Label(self, text=sub, font=("Trebuchet MS", 13),
                 bg=c["fondo"], fg=c["tenue"]).pack(pady=(0, 28))

        # Contenedor de las tres tarjetas.
        marco = tk.Frame(self, bg=c["fondo"])
        marco.pack()

        # Faccion bloqueada: la que ya eligio el defensor (solo aplica en turno 2).
        bloqueada = (self.controlador.faccion_defensor.nombre
                     if self.turno == 2 and self.controlador.faccion_defensor else None)

        for nombre in Faccion.DISPONIBLES:
            self._tarjeta(marco, nombre, bloqueada)

        # Boton de confirmar.
        self.controlador.boton(self, "Confirmar", self._confirmar).pack(pady=28)

    #E: parent (Frame), nombre (str con el nombre de la faccion),
    #   bloqueada (str o None, faccion que no se puede elegir)
    #S: no retorna; dibuja la tarjeta de una faccion dentro de 'parent'
    #R: ninguna
    def _tarjeta(self, parent, nombre, bloqueada):
        c = self.controlador.COLORES
        fac = Faccion(nombre)
        deshabilitada = (nombre == bloqueada)

        # Color de fondo de la tarjeta: mas oscuro si esta deshabilitada.
        bg_tarjeta = "#0D1E36" if deshabilitada else c["panel"]

        # Frame exterior que actua como tarjeta seleccionable.
        tarjeta = tk.Frame(parent, bg=bg_tarjeta, padx=12, pady=12,
                           highlightthickness=2,
                           highlightbackground=c["panel"])
        tarjeta.pack(side="left", padx=16)

        # Canvas con el preview vectorial de la torre de esta faccion.
        canvas = tk.Canvas(tarjeta, width=self.ANCHO_TARJETA,
                           height=self.ALTO_TARJETA - 100,
                           bg=fac.obtener("fondo")["principal"],
                           highlightthickness=0)
        canvas.pack()
        self._dibujar_preview(canvas, nombre, fac)

        # Nombre de la faccion.
        color_txt = c["tenue"] if deshabilitada else c["texto"]
        tk.Label(tarjeta, text=nombre, font=("Trebuchet MS", 14, "bold"),
                 bg=bg_tarjeta, fg=color_txt).pack(pady=(10, 4))

        # Muestra de los 3 colores principales de la faccion (como pastillas).
        paleta_torre = fac.obtener("torre")
        fila_colores = tk.Frame(tarjeta, bg=bg_tarjeta)
        fila_colores.pack(pady=(0, 10))
        for clave in ["principal", "secundario", "borde"]:
            tk.Frame(fila_colores, bg=paleta_torre[clave],
                     width=22, height=22).pack(side="left", padx=3)

        # Indicador de no disponible.
        if deshabilitada:
            tk.Label(tarjeta, text="No disponible", font=("Trebuchet MS", 10),
                     bg=bg_tarjeta, fg="#E85050").pack()
            return   # no ponemos radio ni eventos de seleccion

        # Radio button invisible: guarda la seleccion al hacer clic en la tarjeta.
        radio = tk.Radiobutton(tarjeta, variable=self.seleccion, value=nombre,
                               bg=bg_tarjeta, activebackground=bg_tarjeta,
                               highlightthickness=0, bd=0)
        radio.pack()

        # Clic en cualquier parte de la tarjeta activa el radio y resalta el borde.
        def al_hacer_clic(event, t=tarjeta, n=nombre, r=radio):
            self.seleccion.set(n)
            self._resaltar(t)
        for widget in (tarjeta, canvas):
            widget.bind("<Button-1>", al_hacer_clic)

    #E: tarjeta_activa (Frame de la tarjeta que se selecciono)
    #S: no retorna; resalta la tarjeta activa y apaga las demas
    #R: ninguna
    def _resaltar(self, tarjeta_activa):
        c = self.controlador.COLORES
        # Recorremos todos los hijos del contenedor de tarjetas para resetear bordes.
        for widget in tarjeta_activa.master.winfo_children():
            color = c["acento"] if widget is tarjeta_activa else c["panel"]
            widget.config(highlightbackground=color)

    #E: canvas (Canvas), nombre (str), fac (Faccion)
    #S: no retorna; dibuja un preview de la torre basica de la faccion en el canvas
    #R: ninguna
    def _dibujar_preview(self, canvas, nombre, fac):
        # Dibujamos la silueta de la torre en el centro del canvas del preview.
        # Reutilizamos exactamente el mismo sistema 0..100 del proyecto.
        ox, oy = 0, 0
        lado = self.ANCHO_TARJETA
        p = lambda px, py: constantes.punto(ox, oy, lado, px, py)
        poli = lambda pts: constantes.poligono(ox, oy, lado, pts)
        col = fac.obtener("torre")
        pr, se, bo = col["principal"], col["secundario"], col["borde"]
        gr = max(1, lado * 0.025)
        fn = max(1, lado * 0.015)

        if nombre == "Medieval":
            canvas.create_rectangle(*p(37,46), *p(63,86), fill=pr, outline=bo, width=gr)
            for x in [37, 46, 56]:
                canvas.create_rectangle(*p(x,40), *p(x+8,47), fill=pr, outline=bo, width=fn)
            canvas.create_rectangle(*p(46,54), *p(54,64), fill=bo, outline="")
            canvas.create_line(*p(37,68), *p(63,68), fill=se, width=gr)

        elif nombre == "Futurista":
            canvas.create_polygon(poli([(40,86),(60,86),(56,58),(44,58)]),
                                  fill=pr, outline=bo, width=gr)
            canvas.create_rectangle(*p(42,72), *p(58,76), fill=se, outline="")
            canvas.create_line(*p(50,58), *p(50,28), fill=pr, width=gr)
            canvas.create_oval(*p(43,28), *p(57,42), fill=se, outline=bo, width=fn)
            canvas.create_oval(*p(47,32), *p(53,38), fill="#46E5FF", outline="")

        elif nombre == "Naturaleza":
            canvas.create_rectangle(*p(44,56), *p(56,86), fill=se, outline=bo, width=gr)
            canvas.create_oval(*p(27,30), *p(73,66), fill=pr, outline=bo, width=gr)
            for (cx,cy) in [(40,44),(56,40),(50,54)]:
                canvas.create_oval(*p(cx-4,cy-4), *p(cx+4,cy+4), fill=se, outline="")

    #E: (lee self.seleccion)
    #S: no retorna; guarda la faccion elegida y avanza al siguiente paso
    #R: el jugador debe haber seleccionado una faccion
    def _confirmar(self):
        nombre = self.seleccion.get()
        if not nombre:
            messagebox.showwarning("Sin selección", "Elige una facción antes de continuar.")
            return

        fac = Faccion(nombre)
        if self.turno == 1:
            self.controlador.faccion_defensor = fac
            # Reutilizamos la pantalla para el atacante.
            self.controlador.mostrar(lambda p, c: PantallaFacciones(p, c, turno=2))
        else:
            self.controlador.faccion_atacante = fac
            # TEMPORAL: aqui ira la ventana del juego.
            messagebox.showinfo("¡Listos!", f"Defensor: {self.controlador.faccion_defensor.nombre}"
                                f"\nAtacante: {self.controlador.faccion_atacante.nombre}"
                                f"\n\n¡Comienza la partida!")