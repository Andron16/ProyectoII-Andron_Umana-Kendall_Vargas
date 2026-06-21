# proyectil.py
# Proyectil disparado por una torre hacia una unidad enemiga. Solo datos +
# dibujo. Se mueve en PIXELES (x, y) en linea recta hacia su objetivo;
# el movimiento, la deteccion de impacto y el dano los maneja juego.py.

import math
import constantes


class Proyectil:

    VELOCIDAD = 6.0   # pixeles por actualizacion del game loop (propuesto)

    #E: x, y (float, posicion inicial en px), objetivo (Unidad a la que apunta),
    #   dano (int/float, dano que aplicara al impactar), faccion (Faccion de la torre que dispara)
    #S: instancia de Proyectil listo para que juego.py lo mueva cada actualizacion
    #R: ninguna
    def __init__(self, x, y, objetivo, dano, faccion):
        self.x = x
        self.y = y
        self.objetivo = objetivo   # referencia a la Unidad objetivo
        self.dano = dano
        self.faccion = faccion
        self.activo = True         # juego.py lo pone en False al impactar o si el objetivo murio
        self.id_items = []

    #E: (usa su posicion y la posicion actual de self.objetivo)
    #S: no retorna; actualiza self.x y self.y un paso hacia el objetivo
    #R: si el objetivo ya murio, no se mueve (juego.py debe desactivarlo en ese caso)
    def mover(self):
        # Vector hacia el objetivo (este recalculo a cada paso simula "homing" basico).
        dx = self.objetivo.x - self.x
        dy = self.objetivo.y - self.y
        distancia = math.hypot(dx, dy)
        if distancia == 0:
            return
        # Normalizamos el vector y avanzamos VELOCIDAD pixeles en esa direccion.
        self.x += (dx / distancia) * Proyectil.VELOCIDAD
        self.y += (dy / distancia) * Proyectil.VELOCIDAD

    #E: (usa su posicion y la del objetivo)
    #S: True si el proyectil ya alcanzo a su objetivo, False si sigue en vuelo
    #R: ninguna
    def impacto(self):
        # Distancia corta = consideramos que llego; juego.py aplica el dano cuando esto es True.
        dx = self.objetivo.x - self.x
        dy = self.objetivo.y - self.y
        return math.hypot(dx, dy) < 6

    #E: canvas (Canvas de Tkinter), tam_celda (int, usado para escalar el tamano del proyectil)
    #S: lista con los IDs dibujados (tambien en self.id_items)
    #R: tam_celda > 0
    def dibujar(self, canvas, tam_celda):
        # El proyectil usa una "celda" mas chica que la de las entidades (es un objeto pequeno).
        tam = tam_celda * 0.4
        ox = self.x - tam / 2
        oy = self.y - tam / 2
        gr = max(1, tam * 0.06)
        p = lambda px, py: constantes.punto(ox, oy, tam, px, py)
        poli = lambda pts: constantes.poligono(ox, oy, tam, pts)
        col = self.faccion.obtener("proyectil")
        principal, secundario, borde = col["principal"], col["secundario"], col["borde"]

        ids = []
        # Calculamos el angulo de vuelo para orientar la figura hacia el objetivo.
        dx = self.objetivo.x - self.x
        dy = self.objetivo.y - self.y
        angulo = math.atan2(dy, dx)

        if self.faccion.nombre == "Medieval":
            # Flecha: punta triangular y asta, rotada segun la direccion de vuelo.
            largo = tam * 0.9
            cx, cy = self.x, self.y
            pa = (cx + math.cos(angulo) * largo / 2, cy + math.sin(angulo) * largo / 2)
            pb = (cx - math.cos(angulo) * largo / 2, cy - math.sin(angulo) * largo / 2)
            ids.append(canvas.create_line(pa[0], pa[1], pb[0], pb[1], fill=borde, width=gr))
            punta_x = cx + math.cos(angulo) * largo / 2
            punta_y = cy + math.sin(angulo) * largo / 2
            ang_iz = angulo + 2.6
            ang_de = angulo - 2.6
            ala_largo = tam * 0.28
            ids.append(canvas.create_polygon(
                punta_x, punta_y,
                punta_x + math.cos(ang_iz) * ala_largo, punta_y + math.sin(ang_iz) * ala_largo,
                punta_x + math.cos(ang_de) * ala_largo, punta_y + math.sin(ang_de) * ala_largo,
                fill=principal, outline=borde, width=max(1, gr / 2)))

        elif self.faccion.nombre == "Futurista":
            # Rayo de energia: nucleo brillante con halo translucido.
            ids.append(canvas.create_oval(*p(10, 10), *p(90, 90),
                                          fill=secundario, outline="", stipple="gray25"))
            ids.append(canvas.create_oval(*p(28, 28), *p(72, 72), fill=principal, outline=borde, width=gr))
            ids.append(canvas.create_oval(*p(40, 40), *p(60, 60), fill=secundario, outline=""))

        elif self.faccion.nombre == "Naturaleza":
            # Espina vegetal: forma alargada puntiaguda, rotada hacia el objetivo.
            largo = tam * 0.8
            ancho = tam * 0.22
            cx, cy = self.x, self.y
            frente = (cx + math.cos(angulo) * largo / 2, cy + math.sin(angulo) * largo / 2)
            atras = (cx - math.cos(angulo) * largo / 2, cy - math.sin(angulo) * largo / 2)
            perp = angulo + math.pi / 2
            lado1 = (cx + math.cos(perp) * ancho / 2, cy + math.sin(perp) * ancho / 2)
            lado2 = (cx - math.cos(perp) * ancho / 2, cy - math.sin(perp) * ancho / 2)
            ids.append(canvas.create_polygon(
                frente[0], frente[1], lado1[0], lado1[1], atras[0], atras[1], lado2[0], lado2[1],
                fill=principal, outline=borde, width=max(1, gr / 2)))

        self.id_items = ids
        return ids

    #E: canvas (Canvas de Tkinter)
    #S: no retorna; borra del Canvas las figuras de este proyectil
    #R: ninguna
    def borrar(self, canvas):
        for item in self.id_items:
            canvas.delete(item)
        self.id_items = []