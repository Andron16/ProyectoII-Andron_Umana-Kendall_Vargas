# faccion.py
# -------------------------------------------------------------------
# Clase Faccion: guarda UNICAMENTE la identidad VISUAL de cada faccion
# (los colores de cada elemento). No tiene logica de juego ni de habilidades:
# eso vive en juego.py. Las entidades (base, muro, torre, unidad, proyectil)
# le piden a su faccion los colores que deben usar al dibujarse.
# -------------------------------------------------------------------


class Faccion:

    # Facciones permitidas. Atacante y defensor deben elegir facciones DISTINTAS;
    # esa regla se controla en la ventana de seleccion, no aqui.
    DISPONIBLES = ["Medieval", "Futurista", "Naturaleza"]

    # PALETAS: diccionario de clase. Para cada faccion y cada elemento guarda:
    #   {"principal": relleno, "secundario": acento, "borde": contorno}
    # Elementos: base, muro, torre, unidad, proyectil, fondo, emblema.
    PALETAS = {
        "Medieval": {
            "base":      {"principal": "#8C7B63", "secundario": "#A12E2E", "borde": "#322A20"},
            "muro":      {"principal": "#6E6253", "secundario": "#877A66", "borde": "#2E281F"},
            "torre":     {"principal": "#7E6E58", "secundario": "#C9A227", "borde": "#322A20"},
            "unidad":    {"principal": "#5A4632", "secundario": "#9A2B2B", "borde": "#2A2018"},
            "proyectil": {"principal": "#E8C24A", "secundario": "#FFE9A8", "borde": "#6B4E16"},
            "fondo":     {"principal": "#5E6B3F", "secundario": "#4B562F", "borde": "#39421F"},
            "emblema":   {"principal": "#C9A227", "secundario": "#A12E2E", "borde": "#322A20"},
        },
        "Futurista": {
            "base":      {"principal": "#1E2C50", "secundario": "#2BD6E0", "borde": "#0B1426"},
            "muro":      {"principal": "#33405E", "secundario": "#5BC0DE", "borde": "#141C30"},
            "torre":     {"principal": "#243456", "secundario": "#36E0C8", "borde": "#0B1426"},
            "unidad":    {"principal": "#2A3A60", "secundario": "#5AA0FF", "borde": "#0E1730"},
            "proyectil": {"principal": "#46E5FF", "secundario": "#E8FBFF", "borde": "#0E5A66"},
            "fondo":     {"principal": "#10182B", "secundario": "#161F36", "borde": "#0A1020"},
            "emblema":   {"principal": "#2BD6E0", "secundario": "#5AA0FF", "borde": "#0B1426"},
        },
        "Naturaleza": {
            "base":      {"principal": "#3E6B3A", "secundario": "#C58A2E", "borde": "#233D22"},
            "muro":      {"principal": "#5A4A30", "secundario": "#7A6440", "borde": "#2C2316"},
            "torre":     {"principal": "#436E3C", "secundario": "#8FB04A", "borde": "#233D22"},
            "unidad":    {"principal": "#5E7A36", "secundario": "#A7C25A", "borde": "#2E3D1B"},
            "proyectil": {"principal": "#A7C25A", "secundario": "#E4F0B8", "borde": "#4E5E26"},
            "fondo":     {"principal": "#41562E", "secundario": "#374A26", "borde": "#2A381D"},
            "emblema":   {"principal": "#8FB04A", "secundario": "#C58A2E", "borde": "#233D22"},
        },
    }

    #E: nombre (str) -> nombre de la faccion elegida
    #S: instancia de Faccion con su nombre y su paleta cargada
    #R: nombre debe ser uno de Faccion.DISPONIBLES
    def __init__(self, nombre):
        # Validamos que la faccion exista para no arrastrar un fallo silencioso.
        if nombre not in Faccion.DISPONIBLES:
            raise ValueError("Faccion no valida: " + str(nombre))
        self.nombre = nombre
        # Referencia directa a la paleta de ESTA faccion (acceso rapido al dibujar).
        self.paleta = Faccion.PALETAS[nombre]

    #E: elemento (str) -> "base", "muro", "torre", "unidad", "proyectil", "fondo" o "emblema"
    #S: diccionario {"principal", "secundario", "borde"} de ese elemento
    #R: elemento debe existir en la paleta de la faccion
    def obtener(self, elemento):
        return self.paleta[elemento]

    #E: (usa el estado interno)
    #S: texto representativo de la faccion, util para depurar
    #R: ninguna
    def __str__(self):
        return "Faccion(" + self.nombre + ")"