# constantes.py
# -------------------------------------------------------------------
# Constantes globales y conversiones de coordenadas del juego.
#
# Modulo NEUTRAL: solo define valores fijos y funciones de conversion.
# No importa ninguna otra parte del proyecto, por lo que cualquier archivo
# (entidades, juego.py, ventana_juego.py) puede importarlo SIN riesgo de
# imports circulares.
#
# Regla de equipo: una vez fijado, NADIE vuelve a editar este archivo,
# para no chocar en los commits. Los demas modulos solo lo IMPORTAN.
# -------------------------------------------------------------------


# --- Dimensiones del tablero (en casillas) ---
FILAS = 15        # cantidad de filas de la cuadricula
COLUMNAS = 15     # cantidad de columnas de la cuadricula

# --- Tamano de cada casilla (en pixeles) ---
TAM_CELDA = 40    # lado de cada casilla; al cambiarlo, todo escala solo

# --- Tamano total del Canvas (en pixeles) ---
ANCHO = COLUMNAS * TAM_CELDA   # 600 px de ancho
ALTO = FILAS * TAM_CELDA       # 600 px de alto

# --- Posicion fija de la base central ---
# La base se ancla en la casilla central (definida por el programador, como
# pide el enunciado). Se calcula a partir de FILAS/COLUMNAS para seguir
# centrada aunque cambien. Con 15x15 -> fila 7, columna 7 (contando desde 0).
FILA_BASE = FILAS // 2          # 7
COLUMNA_BASE = COLUMNAS // 2    # 7


# Convencion de ejes (IMPORTANTE para no confundir filas con columnas):
#   - 'fila' avanza hacia ABAJO     -> coordenada Y
#   - 'columna' avanza a la DERECHA -> coordenada X
# Por eso siempre: columna -> x, fila -> y.


# ===================================================================
# CONVERSIONES CASILLA <-> PIXEL
# ===================================================================

#E: fila (int), columna (int) -> casilla del tablero
#S: tupla (x, y) del pixel de la ESQUINA superior-izquierda de esa casilla
#R: fila y columna deberian estar dentro del tablero
def casilla_a_esquina(fila, columna):
    # Esquina superior-izquierda: origen comodo para dibujar dentro de la casilla.
    x = columna * TAM_CELDA
    y = fila * TAM_CELDA
    return (x, y)


#E: fila (int), columna (int) -> casilla del tablero
#S: tupla (x, y) del pixel del CENTRO de esa casilla
#R: fila y columna deberian estar dentro del tablero
def casilla_a_centro(fila, columna):
    # Centro de la casilla: util para colocar unidades o apuntar a la base.
    x = columna * TAM_CELDA + TAM_CELDA / 2
    y = fila * TAM_CELDA + TAM_CELDA / 2
    return (x, y)


#E: x (float), y (float) -> pixel dentro del Canvas
#S: tupla (fila, columna) de la casilla que contiene ese pixel
#R: (x, y) deberian estar dentro del Canvas (0..ANCHO, 0..ALTO)
def pixel_a_casilla(x, y):
    # En que casilla cae un pixel. Lo usa juego.py para ubicar unidades (que se
    # mueven en pixeles) y detectar choques con muros/torres (que viven en casillas).
    columna = int(x // TAM_CELDA)
    fila = int(y // TAM_CELDA)
    return (fila, columna)


#E: fila (int), columna (int)
#S: True si la casilla esta dentro del tablero, False si se sale
#R: ninguna
def casilla_valida(fila, columna):
    return 0 <= fila < FILAS and 0 <= columna < COLUMNAS


# ===================================================================
# DIBUJO: ESCALADO DE FIGURAS (sistema de diseno 0..100 dentro de una celda)
# Cada entidad disena su silueta en una rejilla de 0 a 100 y estas funciones
# la escalan al tamano real de la celda. Asi queda nitida a cualquier TAM_CELDA.
# ===================================================================

#E: ox, oy (esquina de la celda en px), tam (lado de la celda en px), px, py (diseno 0..100)
#S: tupla (x, y) en pixeles reales del Canvas
#R: px y py deberian estar en 0..100 para quedar dentro de la celda
def punto(ox, oy, tam, px, py):
    # Regla de tres: (valor de diseno / 100) * tamano real, desplazado al origen.
    x = ox + (px / 100.0) * tam
    y = oy + (py / 100.0) * tam
    return (x, y)


#E: ox, oy, tam (igual que en punto), puntos (lista de tuplas (px, py) en diseno 0..100)
#S: lista plana [x1, y1, x2, y2, ...] lista para canvas.create_polygon(...)
#R: 'puntos' debe tener al menos 3 vertices
def poligono(ox, oy, tam, puntos):
    coords = []
    for (px, py) in puntos:
        x, y = punto(ox, oy, tam, px, py)
        coords.extend([x, y])
    return coords