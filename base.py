# base.py
# Base central fija del DEFENSOR (objetivo del ATACANTE). Su dibujo final
# sera un PNG por faccion (Fase 8); mientras no exista, usa un placeholder
# vectorial. Solo datos + dibujo; el combate vive en juego.py.

import os
import constantes

# Pillow es opcional aqui: si no esta instalado o el PNG aun no existe,
# se usa el placeholder vectorial y el juego corre igual.
try:
    from PIL import Image, ImageTk
    _PIL_OK = True
except ImportError:
    _PIL_OK = False


class Base:

    VIDA_MAX = 1000     # objetivo principal: mucha vida (propuesto, a balancear)
    CASILLAS = 3        # ocupa un cuadrado CASILLAS x CASILLAS centrado (propuesto)

    #E: faccion (objeto Faccion del defensor)
    #S: instancia de Base centrada en el tablero, con vida completa
    #R: CASILLAS debe ser impar para centrarse en una sola casilla
    def __init__(self, faccion):
        self.faccion = faccion
        self.vida = Base.VIDA_MAX
        self.vida_max = Base.VIDA_MAX
        # La base se ancla en el centro del tablero (definido en constantes).
        self.fila = constantes.FILA_BASE
        self.columna = constantes.COLUMNA_BASE
        self.id_items = []
        self._imagen = None     # referencia al PhotoImage (si no, Tkinter lo descarta)

    #E: (usa su propia vida)
    #S: True si la base fue destruida, False si sigue en pie
    #R: ninguna
    def esta_destruida(self):
        return self.vida <= 0

    #E: (usa su posicion y CASILLAS)
    #S: lista de tuplas (fila, columna) que ocupa la base
    #R: ninguna
    def casillas_ocupadas(self):
        # juego.py usa esto para bloquear esas casillas y dirigir alli a las unidades.
        radio = Base.CASILLAS // 2
        return [(f, c)
                for f in range(self.fila - radio, self.fila + radio + 1)
                for c in range(self.columna - radio, self.columna + radio + 1)]

    #E: canvas (Canvas de Tkinter), tam_celda (int, lado de la casilla en px)
    #S: lista con los IDs dibujados (tambien en self.id_items)
    #R: tam_celda > 0
    def dibujar(self, canvas, tam_celda):
        # Area en pixeles del cuadrado de la base (CASILLAS x CASILLAS).
        radio = Base.CASILLAS // 2
        ox = (self.columna - radio) * tam_celda
        oy = (self.fila - radio) * tam_celda
        lado = Base.CASILLAS * tam_celda

        ids = []
        ruta = os.path.join("assets", "imagenes", "base_" + self.faccion.nombre.lower() + ".png")

        if _PIL_OK and os.path.exists(ruta):
            # Dibujo final: PNG de la faccion, escalado al area de la base.
            imagen = Image.open(ruta).resize((int(lado), int(lado)))
            self._imagen = ImageTk.PhotoImage(imagen)
            ids.append(canvas.create_image(ox + lado / 2, oy + lado / 2, image=self._imagen))
        else:
            # Placeholder vectorial con el diseno definitivo del preview.
            self._dibujar_placeholder(canvas, ox, oy, lado, ids)

        self.id_items = ids
        return ids

    #E: canvas, ox, oy (esquina del area en px), lado (lado del area), ids (lista a llenar)
    #S: no retorna; agrega a 'ids' las figuras del placeholder segun la faccion
    #R: ninguna
    def _dibujar_placeholder(self, canvas, ox, oy, lado, ids):
        gr = max(1, lado * 0.025)   # grosor principal
        fn = max(1, lado * 0.015)   # grosor de detalle
        # p y poli: convierten coordenadas de diseno (0..100) a pixeles reales del area.
        p = lambda px, py: constantes.punto(ox, oy, lado, px, py)
        poli = lambda pts: constantes.poligono(ox, oy, lado, pts)

        if self.faccion.nombre == "Medieval":
            # Castillo: asta y bandera, torreon con almenas, puerta en arco, ventanas.
            ids.append(canvas.create_line(*p(50, 40), *p(50, 20), fill="#322A20", width=gr))
            ids.append(canvas.create_polygon(poli([(50, 20), (67, 24), (50, 31)]),
                                             fill="#A12E2E", outline="#322A20", width=fn))
            ids.append(canvas.create_rectangle(*p(26, 42), *p(74, 86),
                                               fill="#8C7B63", outline="#322A20", width=gr))
            for x in [26, 41, 56, 66]:
                ids.append(canvas.create_rectangle(*p(x, 36), *p(x + 8, 44),
                                                   fill="#8C7B63", outline="#322A20", width=fn))
            ids.append(canvas.create_arc(*p(43, 57), *p(57, 71), start=0, extent=180,
                                         style="pieslice", fill="#322A20", outline=""))
            ids.append(canvas.create_rectangle(*p(43, 64), *p(57, 86), fill="#322A20", outline=""))
            for x in [33, 61]:
                ids.append(canvas.create_rectangle(*p(x, 50), *p(x + 6, 58), fill="#322A20", outline=""))

        elif self.faccion.nombre == "Futurista":
            # Reactor: antenas, plataforma hexagonal, panel y nucleo de energia.
            ids.append(canvas.create_line(*p(40, 44), *p(36, 30), fill="#2BD6E0", width=gr))
            ids.append(canvas.create_line(*p(60, 44), *p(64, 30), fill="#2BD6E0", width=gr))
            ids.append(canvas.create_polygon(
                poli([(30, 50), (50, 40), (70, 50), (70, 72), (50, 82), (30, 72)]),
                fill="#1E2C50", outline="#0B1426", width=gr))
            ids.append(canvas.create_polygon(poli([(50, 40), (70, 50), (50, 58), (30, 50)]),
                                             fill="#243456", outline="#0B1426", width=fn))
            ids.append(canvas.create_oval(*p(38, 50), *p(62, 74),
                                          fill="#2BD6E0", outline="", stipple="gray12"))
            ids.append(canvas.create_oval(*p(39, 51), *p(61, 73), fill="", outline="#2BD6E0", width=gr))
            ids.append(canvas.create_oval(*p(45.5, 57.5), *p(54.5, 66.5), fill="#46E5FF", outline=""))

        elif self.faccion.nombre == "Naturaleza":
            # Arbol: tronco, copa de tres ovalos y frutos.
            ids.append(canvas.create_rectangle(*p(44, 58), *p(56, 86),
                                               fill="#5A4A30", outline="#233D22", width=gr))
            for (cx, cy, r) in [(38, 50, 16), (62, 50, 16), (50, 38, 18)]:
                ids.append(canvas.create_oval(*p(cx - r, cy - r), *p(cx + r, cy + r),
                                              fill="#3E6B3A", outline="#233D22", width=gr))
            for (cx, cy) in [(44, 40), (58, 46), (50, 52)]:
                ids.append(canvas.create_oval(*p(cx - 3, cy - 3), *p(cx + 3, cy + 3),
                                              fill="#C58A2E", outline=""))

    #E: canvas (Canvas de Tkinter)
    #S: no retorna; borra del Canvas las figuras de la base
    #R: ninguna
    def borrar(self, canvas):
        for item in self.id_items:
            canvas.delete(item)
        self.id_items = []
        