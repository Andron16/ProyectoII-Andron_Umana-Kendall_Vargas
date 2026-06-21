# juego.py
# Clase principal del juego: orquesta una PARTIDA completa. Maneja el estado
# (ronda, marcador, dinero), el flujo por fases (construccion -> colocacion ->
# combate en tiempo real -> fin de ronda), las condiciones de victoria y las
# habilidades. Trabaja sobre la PantallaJuego (su Canvas y sus entidades).

import constantes


class Juego:

    # --- Fases de una ronda (el combate es la unica en tiempo real) ---
    FASE_CONSTRUCCION = "construccion"   # el defensor coloca torres y muros
    FASE_COLOCACION = "colocacion"       # el atacante coloca sus unidades
    FASE_COMBATE = "combate"             # combate automatico en tiempo real
    FASE_FIN = "fin_ronda"               # se evalua el ganador de la ronda

    # --- Parametros de economia y partida (balance provisional) ---
    DINERO_INICIAL = 500       # dinero al empezar la partida (ronda 1)
    DINERO_POR_RONDA = 150     # se suma al inicio de cada ronda siguiente
    RONDAS_PARA_GANAR = 3      # primero en ganar 3 rondas gana la partida

    # Recompensas por tipo de unidad eliminada (defensor gana esto al matar cada tipo).
    RECOMPENSA_UNIDAD = {
        "soldado": 25,
        "tanque":  60,
        "rapida":  35,
        "sanador": 40,
    }

    #E: pantalla (PantallaJuego) -> la pantalla con el Canvas y las entidades
    #S: instancia de Juego lista, en la ronda 1 y fase de construccion
    #R: pantalla debe tener .controlador (App) con los jugadores y facciones
    def __init__(self, pantalla):
        self.pantalla = pantalla
        self.controlador = pantalla.controlador

        # Estado de la partida.
        self.ronda = 1
        self.victorias_defensor = 0
        self.victorias_atacante = 0

        # Economia de cada jugador.
        self.dinero_defensor = Juego.DINERO_INICIAL
        self.dinero_atacante = Juego.DINERO_INICIAL

        # Dano que hace el atacante (para el bono de dinero de la ronda siguiente).
        self.dano_ronda_actual = 0
        self.dano_ronda_anterior = 0

        # Fase actual de la ronda.
        self.fase = Juego.FASE_CONSTRUCCION

        # Control del bucle de combate en tiempo real.
        self.combate_activo = False

    #E: (usa self.ronda y el dano de la ronda anterior)
    #S: no retorna; aplica los ingresos de inicio de ronda a ambos jugadores
    #R: en la ronda 1 no hace nada (el dinero inicial ya se asigno al crear el juego)
    def ingresos_inicio_ronda(self):
        # La ronda 1 ya arranca con el dinero inicial fijado en __init__.
        if self.ronda == 1:
            return
        # Ingreso fijo de inicio de ronda para ambos jugadores.
        self.dinero_defensor += Juego.DINERO_POR_RONDA
        self.dinero_atacante += Juego.DINERO_POR_RONDA
        # Bono del atacante segun el dano que hizo en la ronda anterior (1 por cada 5).
        self.dinero_atacante += self.dano_ronda_anterior // 5

    #E: costo (int), rol (str: "defensor" o "atacante")
    #S: True si ese jugador tiene dinero suficiente, False si no
    #R: rol debe ser "defensor" o "atacante"
    def puede_pagar(self, costo, rol):
        dinero = self.dinero_defensor if rol == "defensor" else self.dinero_atacante
        return dinero >= costo

    #E: costo (int), rol (str: "defensor" o "atacante")
    #S: True si se pudo cobrar el costo, False si no alcanzaba el dinero
    #R: rol debe ser "defensor" o "atacante"
    def gastar(self, costo, rol):
        # Solo cobramos si hay dinero suficiente.
        if not self.puede_pagar(costo, rol):
            return False
        if rol == "defensor":
            self.dinero_defensor -= costo
        else:
            self.dinero_atacante -= costo
        return True
    
    #E: unidad (Unidad que acaba de morir)
    #S: no retorna; suma al defensor la recompensa segun el tipo de unidad
    #R: unidad.tipo debe existir en RECOMPENSA_UNIDAD
    def recompensa_por_eliminar(self, unidad):
        ganado = Juego.RECOMPENSA_UNIDAD.get(unidad.tipo, 0)
        self.dinero_defensor += ganado

    #E: cantidad (int/float, dano aplicado en este tick a una torre o a la base)
    #S: no retorna; acumula el dano del atacante y le suma dinero (1 por cada 5)
    #R: cantidad >= 0
    def registrar_dano_atacante(self, cantidad):
        self.dano_ronda_actual += cantidad
        # El atacante cobra 1 moneda por cada 5 puntos de dano aplicado.
        self.dinero_atacante += int(cantidad) // 5

    #E: (no recibe parametros)
    #S: no retorna; suma al atacante la recompensa por destruir una torre
    #R: ninguna
    def recompensa_destruir_torre(self):
        self.dinero_atacante += 50
    
    #E: (lee el estado de la pantalla: unidades vivas, dinero atacante, base)
    #S: "defensor", "atacante" o None si la ronda aun no termino
    #R: ninguna
    def evaluar_fin_de_ronda(self):
        # El atacante gana la ronda si destruyo la base central.
        if self.pantalla.base.esta_destruida():
            return "atacante"
        # El defensor gana si no quedan unidades vivas en el campo.
        unidades_vivas = [u for u in self.pantalla.unidades if not u.esta_muerta()]
        if len(unidades_vivas) == 0 and self.fase == Juego.FASE_COMBATE:
            return "defensor"
        # El defensor gana si el atacante se quedo sin dinero antes de lanzar unidades.
        if self.dinero_atacante <= 0 and self.fase == Juego.FASE_COLOCACION:
            return "defensor"
        return None   # ronda en curso

    #E: ganador (str: "defensor" o "atacante")
    #S: no retorna; actualiza el marcador y prepara la siguiente ronda o cierra la partida
    #R: ganador debe ser "defensor" o "atacante"
    def registrar_victoria_ronda(self, ganador):
        if ganador == "defensor":
            self.victorias_defensor += 1
        else:
            self.victorias_atacante += 1
        # Guardamos el dano de esta ronda para el bono de la siguiente.
        self.dano_ronda_anterior = self.dano_ronda_actual
        self.dano_ronda_actual = 0
        self.fase = Juego.FASE_FIN

    #E: (usa el marcador actual)
    #S: "defensor", "atacante" o None si la partida sigue
    #R: ninguna
    def evaluar_fin_de_partida(self):
        # El primero en llegar a RONDAS_PARA_GANAR gana la partida.
        if self.victorias_defensor >= Juego.RONDAS_PARA_GANAR:
            return "defensor"
        if self.victorias_atacante >= Juego.RONDAS_PARA_GANAR:
            return "atacante"
        return None

    #E: ganador_partida (str: "defensor" o "atacante")
    #S: no retorna; actualiza victorias en el JSON segun el rol ganador
    #R: el controlador debe tener jugador_defensor y jugador_atacante definidos
    def cerrar_partida(self, ganador_partida):
        jd = self.controlador.jugador_defensor
        ja = self.controlador.jugador_atacante
        gestor = self.controlador.gestor
        # Actualizamos las victorias del ganador segun el rol que uso en esta partida.
        if ganador_partida == "defensor":
            gestor.actualizar_victoria(jd.nombre, "defensor")
        else:
            gestor.actualizar_victoria(ja.nombre, "atacante")