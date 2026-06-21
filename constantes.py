# preview_facciones.py
# -------------------------------------------------------------------
# SCRIPT DE VISTA PREVIA (no es parte de la entrega del proyecto).
# Sirve para ver, en un Canvas real de Tkinter, como se veria el render
# vectorial de las entidades en cada faccion (color + forma distinta).
# Dibuja dos elementos (Base central y Torre magica) en las 3 facciones.
#
# Para ejecutarlo:  python preview_facciones.py
# -------------------------------------------------------------------

import tkinter as tk

# Colores de fondo del mapa por faccion (mismos tonos del faccion.py del proyecto).
FONDOS = {
    "Medieval":   "#5E6B3F",
    "Futurista":  "#10182B",
    "Naturaleza": "#41562E",
}


#E: ox, oy (esquina superior-izquierda de la celda en px), lado (tamano de la celda en px),
#   px, py (coordenadas de diseno en un sistema de 0 a 100)
#S: una tupla (x, y) con la coordenada ya convertida al sistema real del Canvas
#R: px y py deberian estar en el rango 0..100 para quedar dentro de la celda
def punto(ox, oy, lado, px, py):
    # Convertimos un punto "de diseno" (0..100) a la posicion real dentro de la celda.
    # Asi podemos disenar todas las figuras en una rejilla comoda de 0 a 100 y que
    # se escalen solas a cualquier tamano de celda (igual que hara TAM_CELDA en el juego).
    x = ox + (px / 100.0) * lado
    y = oy + (py / 100.0) * lado
    return (x, y)


#E: ox, oy, lado (igual que en punto), puntos (lista de tuplas (px, py) en diseno 0..100)
#S: una lista plana [x1, y1, x2, y2, ...] lista para pasarle a create_polygon
#R: 'puntos' debe tener al menos 3 vertices para formar un poligono
def poligono(ox, oy, lado, puntos):
    # Convertimos cada vertice de diseno a coordenadas reales y los aplanamos en una
    # sola lista, que es el formato que espera canvas.create_polygon(...).
    coords = []
    for (px, py) in puntos:
        x, y = punto(ox, oy, lado, px, py)
        coords.append(x)
        coords.append(y)
    return coords


#E: canvas (Canvas de Tkinter), ox, oy (esquina de la celda), lado (tamano),
#   color_fondo (str con el color de relleno de la celda)
#S: no retorna nada; dibuja el fondo de la celda, una rejilla tenue y un borde
#R: ninguna
def dibujar_fondo_celda(canvas, ox, oy, lado, color_fondo):
    # Rectangulo de fondo: simula el color del mapa de esa faccion.
    canvas.create_rectangle(ox, oy, ox + lado, oy + lado,
                            fill=color_fondo, outline="")
    # Rejilla tenue: lineas cada ~1/5 de la celda para recordar la cuadricula del juego.
    # Usamos 'stipple' (patron de puntos) para simular transparencia, ya que el Canvas
    # de Tkinter no maneja opacidad real.
    paso = lado / 5.0
    i = 1
    while i < 5:
        # Linea vertical de la rejilla.
        canvas.create_line(ox + i * paso, oy, ox + i * paso, oy + lado,
                           fill="#FFFFFF", stipple="gray12")
        # Linea horizontal de la rejilla.
        canvas.create_line(ox, oy + i * paso, ox + lado, oy + i * paso,
                           fill="#FFFFFF", stipple="gray12")
        i += 1
    # Borde de la celda para separarla visualmente de las demas.
    canvas.create_rectangle(ox, oy, ox + lado, oy + lado,
                            fill="", outline="#2A3240", width=1)


#E: canvas, ox, oy, lado (celda donde dibujar), faccion (str: "Medieval"/"Futurista"/"Naturaleza")
#S: no retorna nada; dibuja la BASE CENTRAL de la faccion indicada
#R: faccion debe ser una de las 3 facciones validas
def dibujar_base(canvas, ox, oy, lado, faccion):
    # Grosores de linea proporcionales al tamano de la celda (asi escalan solos).
    grueso = lado * 0.025   # contorno principal
    fino = lado * 0.015     # detalles

    if faccion == "Medieval":
        # --- Castillo (torreon con almenas, puerta en arco y bandera) ---
        # Asta y bandera roja.
        p1 = punto(ox, oy, lado, 50, 40)
        p2 = punto(ox, oy, lado, 50, 20)
        canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill="#322A20", width=grueso)
        canvas.create_polygon(poligono(ox, oy, lado, [(50, 20), (67, 24), (50, 31)]),
                              fill="#A12E2E", outline="#322A20", width=fino)
        # Cuerpo del torreon.
        b1 = punto(ox, oy, lado, 26, 42)
        b2 = punto(ox, oy, lado, 74, 86)
        canvas.create_rectangle(b1[0], b1[1], b2[0], b2[1],
                               fill="#8C7B63", outline="#322A20", width=grueso)
        # Almenas (los "dientes" de arriba).
        for ax in [(26, 35), (41, 50), (56, 65), (66, 74)]:
            a1 = punto(ox, oy, lado, ax[0], 36)
            a2 = punto(ox, oy, lado, ax[1], 44)
            canvas.create_rectangle(a1[0], a1[1], a2[0], a2[1],
                                   fill="#8C7B63", outline="#322A20", width=fino)
        # Puerta en arco: un semicirculo arriba + un rectangulo abajo.
        arco1 = punto(ox, oy, lado, 43, 57)
        arco2 = punto(ox, oy, lado, 57, 71)
        canvas.create_arc(arco1[0], arco1[1], arco2[0], arco2[1],
                         start=0, extent=180, style="pieslice",
                         fill="#322A20", outline="")
        pr1 = punto(ox, oy, lado, 43, 64)
        pr2 = punto(ox, oy, lado, 57, 86)
        canvas.create_rectangle(pr1[0], pr1[1], pr2[0], pr2[1], fill="#322A20", outline="")
        # Ventanas.
        for vx in [(33, 39), (61, 67)]:
            v1 = punto(ox, oy, lado, vx[0], 50)
            v2 = punto(ox, oy, lado, vx[1], 58)
            canvas.create_rectangle(v1[0], v1[1], v2[0], v2[1], fill="#322A20", outline="")

    elif faccion == "Futurista":
        # --- Reactor (plataforma hexagonal con nucleo de energia) ---
        # Antenas.
        for (x1, y1, x2, y2) in [(40, 44, 36, 30), (60, 44, 64, 30)]:
            a = punto(ox, oy, lado, x1, y1)
            b = punto(ox, oy, lado, x2, y2)
            canvas.create_line(a[0], a[1], b[0], b[1], fill="#2BD6E0", width=fino)
        # Plataforma hexagonal.
        canvas.create_polygon(
            poligono(ox, oy, lado, [(30, 50), (50, 40), (70, 50), (70, 72), (50, 82), (30, 72)]),
            fill="#1E2C50", outline="#0B1426", width=grueso)
        # Panel superior (cara iluminada del hexagono).
        canvas.create_polygon(
            poligono(ox, oy, lado, [(50, 40), (70, 50), (50, 58), (30, 50)]),
            fill="#243456", outline="#0B1426", width=fino)
        # Halo del nucleo (stipple para simular brillo translucido).
        g1 = punto(ox, oy, lado, 38, 50)
        g2 = punto(ox, oy, lado, 62, 74)
        canvas.create_oval(g1[0], g1[1], g2[0], g2[1],
                          fill="#2BD6E0", outline="", stipple="gray25")
        # Anillo del nucleo.
        r1 = punto(ox, oy, lado, 39, 51)
        r2 = punto(ox, oy, lado, 61, 73)
        canvas.create_oval(r1[0], r1[1], r2[0], r2[1],
                          fill="", outline="#2BD6E0", width=grueso)
        # Centro brillante.
        c1 = punto(ox, oy, lado, 45.5, 57.5)
        c2 = punto(ox, oy, lado, 54.5, 66.5)
        canvas.create_oval(c1[0], c1[1], c2[0], c2[1], fill="#46E5FF", outline="")

    elif faccion == "Naturaleza":
        # --- Arbol-base (tronco con copa frondosa y frutos) ---
        # Tronco.
        t1 = punto(ox, oy, lado, 44, 58)
        t2 = punto(ox, oy, lado, 56, 86)
        canvas.create_rectangle(t1[0], t1[1], t2[0], t2[1],
                               fill="#5A4A30", outline="#233D22", width=grueso)
        # Copa: tres ovalos que se solapan.
        for (x1, y1, x2, y2) in [(22, 34, 54, 66), (46, 34, 78, 66), (32, 20, 68, 56)]:
            o1 = punto(ox, oy, lado, x1, y1)
            o2 = punto(ox, oy, lado, x2, y2)
            canvas.create_oval(o1[0], o1[1], o2[0], o2[1],
                             fill="#3E6B3A", outline="#233D22", width=grueso)
        # Frutos.
        for (fx, fy) in [(44, 40), (58, 46), (50, 52)]:
            f1 = punto(ox, oy, lado, fx - 3, fy - 3)
            f2 = punto(ox, oy, lado, fx + 3, fy + 3)
            canvas.create_oval(f1[0], f1[1], f2[0], f2[1], fill="#C58A2E", outline="")


#E: canvas, ox, oy, lado (celda donde dibujar), faccion (str con la faccion)
#S: no retorna nada; dibuja la TORRE MAGICA de la faccion indicada
#R: faccion debe ser una de las 3 facciones validas
def dibujar_torre_magica(canvas, ox, oy, lado, faccion):
    grueso = lado * 0.025
    fino = lado * 0.015

    if faccion == "Medieval":
        # --- Torre del mago: cuerpo de piedra, techo conico y orbe ---
        cu1 = punto(ox, oy, lado, 40, 50)
        cu2 = punto(ox, oy, lado, 60, 86)
        canvas.create_rectangle(cu1[0], cu1[1], cu2[0], cu2[1],
                               fill="#7E6E58", outline="#322A20", width=grueso)
        # Techo conico dorado.
        canvas.create_polygon(poligono(ox, oy, lado, [(37, 50), (63, 50), (50, 26)]),
                              fill="#C9A227", outline="#322A20", width=grueso)
        # Halo del orbe (brillo translucido con stipple).
        h1 = punto(ox, oy, lado, 41, 13)
        h2 = punto(ox, oy, lado, 59, 31)
        canvas.create_oval(h1[0], h1[1], h2[0], h2[1],
                          fill="#FFE9A8", outline="", stipple="gray25")
        # Orbe magico.
        o1 = punto(ox, oy, lado, 45.5, 17.5)
        o2 = punto(ox, oy, lado, 54.5, 26.5)
        canvas.create_oval(o1[0], o1[1], o2[0], o2[1],
                          fill="#FFE9A8", outline="#C9A227", width=fino)
        # Ventana.
        vw1 = punto(ox, oy, lado, 45, 64)
        vw2 = punto(ox, oy, lado, 55, 74)
        canvas.create_rectangle(vw1[0], vw1[1], vw2[0], vw2[1], fill="#322A20", outline="")

    elif faccion == "Futurista":
        # --- Cristal de energia sobre una base ---
        ba1 = punto(ox, oy, lado, 43, 78)
        ba2 = punto(ox, oy, lado, 57, 86)
        canvas.create_rectangle(ba1[0], ba1[1], ba2[0], ba2[1],
                               fill="#243456", outline="#0B1426", width=fino)
        # Cuerpo del cristal (rombo).
        canvas.create_polygon(poligono(ox, oy, lado, [(50, 30), (62, 58), (50, 78), (38, 58)]),
                              fill="#243456", outline="#36E0C8", width=grueso)
        # Nucleo interno del cristal (brillo con stipple).
        canvas.create_polygon(poligono(ox, oy, lado, [(50, 40), (56, 58), (50, 70), (44, 58)]),
                              fill="#46E5FF", outline="", stipple="gray50")
        # Halo del orbe flotante.
        hg1 = punto(ox, oy, lado, 42, 14)
        hg2 = punto(ox, oy, lado, 58, 30)
        canvas.create_oval(hg1[0], hg1[1], hg2[0], hg2[1],
                          fill="#46E5FF", outline="", stipple="gray25")
        # Orbe flotante.
        or1 = punto(ox, oy, lado, 46, 18)
        or2 = punto(ox, oy, lado, 54, 26)
        canvas.create_oval(or1[0], or1[1], or2[0], or2[1], fill="#46E5FF", outline="")

    elif faccion == "Naturaleza":
        # --- Flor magica: tallo, hojas, petalos y centro brillante ---
        ta1 = punto(ox, oy, lado, 48, 52)
        ta2 = punto(ox, oy, lado, 52, 86)
        canvas.create_rectangle(ta1[0], ta1[1], ta2[0], ta2[1],
                               fill="#436E3C", outline="#233D22", width=fino)
        # Hojas.
        canvas.create_polygon(poligono(ox, oy, lado, [(48, 68), (38, 62), (48, 60)]),
                              fill="#8FB04A", outline="#233D22", width=fino)
        canvas.create_polygon(poligono(ox, oy, lado, [(52, 74), (62, 68), (52, 66)]),
                              fill="#8FB04A", outline="#233D22", width=fino)
        # Petalos (cuatro ovalos alrededor del centro).
        for (x1, y1, x2, y2) in [(44, 19, 56, 41), (44, 47, 56, 69), (25, 38, 47, 50), (53, 38, 75, 50)]:
            pe1 = punto(ox, oy, lado, x1, y1)
            pe2 = punto(ox, oy, lado, x2, y2)
            canvas.create_oval(pe1[0], pe1[1], pe2[0], pe2[1],
                             fill="#8FB04A", outline="#233D22", width=fino)
        # Halo del centro.
        hc1 = punto(ox, oy, lado, 41, 35)
        hc2 = punto(ox, oy, lado, 59, 53)
        canvas.create_oval(hc1[0], hc1[1], hc2[0], hc2[1],
                          fill="#C58A2E", outline="", stipple="gray25")
        # Centro de la flor.
        ce1 = punto(ox, oy, lado, 44, 38)
        ce2 = punto(ox, oy, lado, 56, 50)
        canvas.create_oval(ce1[0], ce1[1], ce2[0], ce2[1],
                          fill="#C58A2E", outline="#233D22", width=fino)


#E: (no recibe parametros)
#S: no retorna nada; abre la ventana y dibuja la galeria de facciones
#R: ninguna
def main():
    # Medidas de la galeria.
    LADO = 190        # tamano de cada celda en px
    GAP = 16          # separacion entre celdas
    MX = 96           # margen izquierdo (para las etiquetas de fila)
    MY = 46           # margen superior (para los nombres de faccion)

    facciones = ["Medieval", "Futurista", "Naturaleza"]
    # Cada elemento se asocia a su funcion de dibujo (asi se agrega/quita facil).
    elementos = [("Base\ncentral", dibujar_base),
                 ("Torre\nmagica", dibujar_torre_magica)]

    ancho = MX + len(facciones) * LADO + (len(facciones) - 1) * GAP + 16
    alto = MY + len(elementos) * LADO + (len(elementos) - 1) * GAP + 16

    root = tk.Tk()
    root.title("Vista previa - Facciones (render vectorial en Tkinter)")
    root.configure(bg="#0E131B")

    canvas = tk.Canvas(root, width=ancho, height=alto, bg="#0E131B", highlightthickness=0)
    canvas.pack()

    # Encabezados con el nombre de cada faccion.
    for j, fac in enumerate(facciones):
        cx = MX + j * (LADO + GAP) + LADO / 2
        canvas.create_text(cx, MY - 22, text=fac, fill="#E9EFF6",
                          font=("Helvetica", 13, "bold"))

    # Recorremos elementos (filas) y facciones (columnas) para dibujar cada celda.
    for i, (nombre_el, funcion_dibujo) in enumerate(elementos):
        oy = MY + i * (LADO + GAP)
        # Etiqueta de la fila (a la izquierda).
        canvas.create_text(MX - 12, oy + LADO / 2, text=nombre_el, fill="#8696A8",
                          font=("Helvetica", 11), anchor="e", justify="right")
        for j, fac in enumerate(facciones):
            ox = MX + j * (LADO + GAP)
            # Primero el fondo de la celda, luego la figura encima.
            dibujar_fondo_celda(canvas, ox, oy, LADO, FONDOS[fac])
            funcion_dibujo(canvas, ox, oy, LADO, fac)

    root.mainloop()


# Punto de entrada del script.
main()