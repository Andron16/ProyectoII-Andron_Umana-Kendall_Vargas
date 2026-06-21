# muro.py
# Muro defensivo del DEFENSOR. Solo datos + dibujo; lo unico que cambia entre
# facciones es la silueta (color + forma). El combate vive en juego.py.

import constantes


class Muro:

    COSTO = 50         # costo de colocar un muro (propuesto, a balancear)
    VIDA_MAX = 200     # vida inicial; las unidades lo van rompiendo (propuesto)

    #E: fila (int), columna (int), faccion (objeto Faccion del defensor)
    #S: instancia de Muro en esa casilla, con vida completa
    #R: (fila, columna) debe ser una casilla valida del tablero
    def __init__(self, fila, columna, faccion):
        self.fila = fila
        self.columna = columna
        self.faccion = faccion
        self.vida = Muro.VIDA_MAX       # juego.py la baja al aplicar dano
        self.vida_max = Muro.VIDA_MAX
        self.id_items = []

    #E: (usa su propia vida)
    #S: True si el muro fue destruido, False si sigue en pie
    #R: ninguna
    def esta_destruido(self):
        return self.vida <= 0

    #E: canvas (Canvas de Tkinter), tam_celda (int, lado de la casilla en px)
    #S: lista con los IDs dibujados (tambien en self.id_items)
    #R: tam_celda > 0
    def dibujar(self, canvas, tam_celda):
        # Esquina de la casilla (columna -> x, fila -> y).
        ox = self.columna * tam_celda
        oy = self.fila * tam_celda

        c = self.faccion.obtener("muro")
        principal, secundario, borde = c["principal"], c["secundario"], c["borde"]

        gr = max(1, tam_celda * 0.025)
        fn = max(1, tam_celda * 0.015)
        # p: pasa coordenadas de diseno (0..100) a pixeles reales de la celda.
        p = lambda px, py: constantes.punto(ox, oy, tam_celda, px, py)

        ids = []

        if self.faccion.nombre == "Medieval":
            # Muro de piedra con almenas y juntas de ladrillo.
            ids.append(canvas.create_rectangle(*p(20, 54), *p(80, 86),
                                               fill=principal, outline=borde, width=gr))
            for x in [20, 36, 52, 68]:
                ids.append(canvas.create_rectangle(*p(x, 48), *p(x + 9, 55),
                                                   fill=principal, outline=borde, width=fn))
            for y in [65, 76]:
                ids.append(canvas.create_line(*p(20, y), *p(80, y), fill=borde, width=fn))
            for (x, y0, y1) in [(35, 54, 65), (50, 65, 76), (65, 54, 65), (35, 76, 86), (65, 76, 86)]:
                ids.append(canvas.create_line(*p(x, y0), *p(x, y1), fill=borde, width=fn))

        elif self.faccion.nombre == "Futurista":
            # Barrera de energia: dos postes, panel central y franjas luminosas.
            ids.append(canvas.create_rectangle(*p(22, 48), *p(31, 86),
                                               fill=principal, outline=borde, width=gr))
            ids.append(canvas.create_rectangle(*p(69, 48), *p(78, 86),
                                               fill=principal, outline=borde, width=gr))
            ids.append(canvas.create_rectangle(*p(31, 56), *p(69, 80),
                                               fill=principal, outline=borde, width=fn))
            for y in [63, 73]:
                ids.append(canvas.create_line(*p(31, y), *p(69, y), fill=secundario, width=gr))
            for x in [26.5, 73.5]:
                ids.append(canvas.create_oval(*p(x - 2, 50), *p(x + 2, 54), fill=secundario, outline=""))

        elif self.faccion.nombre == "Naturaleza":
            # Empalizada: troncos apilados con sus puntas de corte y hojas.
            for (y, h) in [(54, 10), (66, 10), (78, 9)]:
                ids.append(canvas.create_rectangle(*p(24, y), *p(76, y + h),
                                                   fill=principal, outline=borde, width=fn))
            for cy in [59, 71, 82]:
                ids.append(canvas.create_oval(*p(23.5, cy - 3.5), *p(30.5, cy + 3.5),
                                              fill=secundario, outline=borde, width=fn))
            for cx in [44, 60]:
                # Hoja: acento verde que no esta en la paleta de muro (del diseno definitivo).
                ids.append(canvas.create_oval(*p(cx - 5, 49), *p(cx + 5, 55), fill="#8FB04A", outline=""))

        self.id_items = ids
        return ids

    #E: canvas (Canvas de Tkinter)
    #S: no retorna; borra del Canvas las figuras de este muro
    #R: ninguna
    def borrar(self, canvas):
        for item in self.id_items:
            canvas.delete(item)
        self.id_items = []