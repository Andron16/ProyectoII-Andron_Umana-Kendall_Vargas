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
    DINERO_INICIAL = 1500       # dinero al empezar la partida (ronda 1)
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
    
    #E: (usa self.ronda)
    #S: no retorna; aplica los ingresos y cambia a FASE_CONSTRUCCION
    #R: ninguna
    def iniciar_ronda(self):
        self.fase = Juego.FASE_CONSTRUCCION
        self.ingresos_inicio_ronda()

    #E: (no recibe parametros)
    #S: no retorna; cierra la fase de construccion y pasa a FASE_COLOCACION
    #R: debe estar en FASE_CONSTRUCCION
    def terminar_construccion(self):
        if self.fase != Juego.FASE_CONSTRUCCION:
            return
        self.fase = Juego.FASE_COLOCACION

    #E: (no recibe parametros)
    #S: no retorna; cierra la fase de colocacion y pasa a FASE_COMBATE
    #R: debe estar en FASE_COLOCACION
    def terminar_colocacion(self):
        if self.fase != Juego.FASE_COLOCACION:
            return
        self.fase = Juego.FASE_COMBATE
        self.combate_activo = True   # el motor del compañero usa este flag para arrancar

    #E: (no recibe parametros)
    #S: no retorna; avanza al numero de ronda siguiente y la inicia
    #R: debe estar en FASE_FIN; solo se llama si la partida aun no termino
    def siguiente_ronda(self):
        if self.fase != Juego.FASE_FIN:
            return
        self.ronda += 1
        self.combate_activo = False
        self.iniciar_ronda()
    
    # HABILIDADES DE UNIDADES
    # Cada habilidad se activa cuando unidad.tiempo_restante llega a 0.
    # El motor del compañero llama a self.activar_habilidad_unidad(unidad)
    # y aqui se despacha segun el tipo. Una habilidad por tipo, como pide
    # el enunciado.

    #E: unidad (Unidad cuyo cooldown llego a 0)
    #S: no retorna; despacha la habilidad segun unidad.tipo y reinicia el cooldown
    #R: ninguna
    def activar_habilidad_unidad(self, unidad):
        habilidades = {
            "soldado": self._habilidad_ataque_doble,
            "tanque":  self._habilidad_escudo_temporal,
            "rapida":  self._habilidad_aumento_velocidad,
            "sanador": self._habilidad_curar_aliados,
        }
        accion = habilidades.get(unidad.tipo)
        if accion:
            accion(unidad)
        # Reiniciamos el cooldown para que la habilidad pueda volver a activarse.
        unidad.tiempo_restante = unidad.cooldown_ms

    #E: unidad (Soldado)
    #S: no retorna; duplica el dano del soldado por un breve periodo (flag en la unidad)
    #R: ninguna
    def _habilidad_ataque_doble(self, unidad):
        # Marcamos la unidad para que el motor sepa que debe aplicar el dano dos veces
        # en el proximo golpe. El motor limpia el flag despues de aplicarlo.
        unidad.ataque_doble_activo = True

    #E: unidad (Tanque)
    #S: no retorna; activa el escudo temporal del tanque
    #R: ninguna
    def _habilidad_escudo_temporal(self, unidad):
        # El escudo absorbe hasta 80 puntos de dano. El motor descuenta primero del
        # escudo y solo el exceso le pega a la vida de la unidad.
        unidad.escudo_activo = True
        unidad.escudo_hp = 80   # puntos que absorbe antes de romperse

    #E: unidad (Rapida)
    #S: no retorna; duplica la velocidad de la unidad rapida por 3 segundos
    #R: ninguna
    def _habilidad_aumento_velocidad(self, unidad):
        # Guardamos la velocidad base para restaurarla cuando expire el boost.
        if not hasattr(unidad, 'velocidad_base'):
            unidad.velocidad_base = unidad.velocidad
        unidad.velocidad = unidad.velocidad_base * 2
        # El motor descuenta este timer cada tick y restaura la velocidad al llegar a 0.
        unidad.boost_restante_ms = 3000

    #E: unidad (Sanador)
    #S: no retorna; cura 30 puntos de vida a todas las unidades aliadas en alcance (3 casillas)
    #R: ninguna
    def _habilidad_curar_aliados(self, unidad):
        CURACION = 30
        ALCANCE_PX = 3 * constantes.TAM_CELDA   # 3 casillas en pixeles
        for aliada in self.pantalla.unidades:
            if aliada is unidad or aliada.esta_muerta():
                continue
            # Distancia euclidiana entre el sanador y la aliada (en pixeles).
            dx = aliada.x - unidad.x
            dy = aliada.y - unidad.y
            distancia = (dx ** 2 + dy ** 2) ** 0.5
            if distancia <= ALCANCE_PX:
                # Curamos sin exceder la vida maxima.
                aliada.vida = min(aliada.vida + CURACION, aliada.vida_max)
    # ===================================================================
    # MOTOR DE COMBATE EN TIEMPO REAL
    # ===================================================================

    #E: (no recibe parametros)
    #S: no retorna; activa el combate y arranca el bucle
    #R: debe estar en FASE_COMBATE
    def iniciar_combate(self):
        self.combate_activo = True
        self._paso_combate()

    #E: (no recibe parametros)
    #S: no retorna; detiene el bucle de combate
    #R: ninguna
    def detener_combate(self):
        self.combate_activo = False

    #E: (no recibe parametros)
    #S: no retorna; ejecuta un tick del combate y se reprograma a si mismo
    #R: se detiene si combate_activo es False o la pantalla ya no existe
    def _paso_combate(self):
        # Guard clause: cortamos si el combate termino o la pantalla fue destruida.
        if not self.combate_activo or not self.pantalla.winfo_exists():
            return

        canvas = self.pantalla.canvas

        # --- 1. Mover unidades hacia la base ---
        cx_base, cy_base = constantes.casilla_a_centro(
            constantes.FILA_BASE, constantes.COLUMNA_BASE)

        for unidad in list(self.pantalla.unidades):
            if unidad.esta_muerta() or unidad.congelada:
                continue

            # Vector hacia el centro de la base.
            dx = cx_base - unidad.x
            dy = cy_base - unidad.y
            distancia = (dx ** 2 + dy ** 2) ** 0.5

            if distancia < constantes.TAM_CELDA:
                # La unidad llego a la base: le aplica dano.
                if unidad.tiempo_ataque_restante <= 0:
                    dano = unidad.dano * (2 if getattr(unidad, 'ataque_doble_activo', False) else 1)
                    if getattr(unidad, 'ataque_doble_activo', False):
                        unidad.ataque_doble_activo = False
                    self.pantalla.base.vida -= dano
                    self.registrar_dano_atacante(dano)
                    self._efecto_dano(cx_base, cy_base)
                    unidad.tiempo_ataque_restante = unidad.cooldown_ataque_ms
                continue

            # Revisa si la siguiente casilla esta bloqueada.
            paso = unidad.velocidad
            nx = unidad.x + (dx / distancia) * paso
            ny = unidad.y + (dy / distancia) * paso
            fila_sig, col_sig = constantes.pixel_a_casilla(nx, ny)

            obstaculo = None
            for t in self.pantalla.torres:
                if not t.esta_destruida() and t.fila == fila_sig and t.columna == col_sig:
                    obstaculo = t
                    break
            if obstaculo is None:
                for m in self.pantalla.muros:
                    if not m.esta_destruido() and m.fila == fila_sig and m.columna == col_sig:
                        obstaculo = m
                        break

            if obstaculo:
                # La unidad ataca el obstaculo en vez de avanzar.
                if unidad.tiempo_ataque_restante <= 0:
                    dano = unidad.dano * (2 if getattr(unidad, 'ataque_doble_activo', False) else 1)
                    if getattr(unidad, 'ataque_doble_activo', False):
                        unidad.ataque_doble_activo = False
                    if getattr(obstaculo, 'escudo_activo', False):
                        exceso = max(0, dano - obstaculo.escudo_hp)
                        obstaculo.escudo_hp -= dano
                        if obstaculo.escudo_hp <= 0:
                            obstaculo.escudo_activo = False
                        dano = exceso
                    obstaculo.vida -= dano
                    unidad.tiempo_ataque_restante = unidad.cooldown_ataque_ms
                    self._efecto_dano(unidad.x, unidad.y)
                    if obstaculo.vida <= 0:
                        obstaculo.borrar(canvas)
                        if obstaculo in self.pantalla.torres:
                            self.pantalla.torres.remove(obstaculo)
                            self.recompensa_destruir_torre()
                        elif obstaculo in self.pantalla.muros:
                            self.pantalla.muros.remove(obstaculo)
            else:
                # Casilla libre: avanzamos y movemos el sprite.
                for id_item in unidad.id_items:
                    canvas.move(id_item, nx - unidad.x, ny - unidad.y)
                unidad.x = nx
                unidad.y = ny

        # --- 2. Torres disparan a unidades en alcance ---
        for torre in self.pantalla.torres:
            if torre.esta_destruida():
                continue
            cx_t, cy_t = constantes.casilla_a_centro(torre.fila, torre.columna)
            alcance_px = torre.alcance * constantes.TAM_CELDA

            objetivo = None
            menor_dist = float('inf')
            for unidad in self.pantalla.unidades:
                if unidad.esta_muerta():
                    continue
                dx = unidad.x - cx_t
                dy = unidad.y - cy_t
                dist = (dx ** 2 + dy ** 2) ** 0.5
                if dist <= alcance_px and dist < menor_dist:
                    menor_dist = dist
                    objetivo = unidad

            if objetivo and torre.tiempo_ataque_restante <= 0:
                from proyectil import Proyectil
                proy = Proyectil(cx_t, cy_t, objetivo, torre.dano, torre.faccion)
                proy.dibujar(canvas, constantes.TAM_CELDA)
                self.pantalla.proyectiles.append(proy)
                torre.tiempo_ataque_restante = torre.cooldown_ataque_ms

        # --- 3. Mover proyectiles y detectar impactos ---
        for proy in list(self.pantalla.proyectiles):
            if not proy.activo:
                proy.borrar(canvas)
                self.pantalla.proyectiles.remove(proy)
                continue

            if proy.objetivo.esta_muerta():
                proy.activo = False
                proy.borrar(canvas)
                self.pantalla.proyectiles.remove(proy)
                continue

            # Guardamos la posicion anterior para mover el sprite.
            px_ant, py_ant = proy.x, proy.y
            proy.mover()
            for id_item in proy.id_items:
                canvas.move(id_item, proy.x - px_ant, proy.y - py_ant)

            if proy.impacto():
                objetivo = proy.objetivo
                dano = proy.dano
                if getattr(objetivo, 'escudo_activo', False):
                    exceso = max(0, dano - objetivo.escudo_hp)
                    objetivo.escudo_hp -= dano
                    if objetivo.escudo_hp <= 0:
                        objetivo.escudo_activo = False
                    dano = exceso
                objetivo.vida -= dano
                proy.activo = False
                self._efecto_dano(objetivo.x, objetivo.y)
                proy.borrar(canvas)
                self.pantalla.proyectiles.remove(proy)

                if objetivo.esta_muerta():
                    objetivo.borrar(canvas)
                    self.pantalla.unidades.remove(objetivo)
                    self.recompensa_por_eliminar(objetivo)

        # --- 4. Descontar cooldowns ---
        TICK = 33
        for unidad in self.pantalla.unidades:
            unidad.tiempo_restante = max(0, unidad.tiempo_restante - TICK)
            unidad.tiempo_ataque_restante = max(0, unidad.tiempo_ataque_restante - TICK)
            if unidad.tiempo_restante == 0:
                self.activar_habilidad_unidad(unidad)
            if getattr(unidad, 'boost_restante_ms', 0) > 0:
                unidad.boost_restante_ms -= TICK
                if unidad.boost_restante_ms <= 0:
                    unidad.velocidad = getattr(unidad, 'velocidad_base', unidad.velocidad)
            if unidad.congelada:
                unidad.tiempo_congelada = getattr(unidad, 'tiempo_congelada', 2000) - TICK
                if unidad.tiempo_congelada <= 0:
                    unidad.congelada = False

        for torre in self.pantalla.torres:
            torre.tiempo_restante = max(0, torre.tiempo_restante - TICK)
            torre.tiempo_ataque_restante = max(0, torre.tiempo_ataque_restante - TICK)
            if torre.tiempo_restante == 0:
                self.activar_habilidad_torre(torre)
                torre.tiempo_restante = torre.cooldown_ms

        # --- 5. Evaluar fin de ronda ---
        ganador = self.evaluar_fin_de_ronda()
        if ganador:
            self.detener_combate()
            self.registrar_victoria_ronda(ganador)
            self.pantalla.refrescar_barra()
            # Mensaje de fin de ronda.
            if ganador == "defensor":
                msg = "¡El Defensor gana la ronda!\nTodas las unidades fueron eliminadas."
            else:
                msg = "¡El Atacante gana la ronda!\nLa base fue destruida."
            from tkinter import messagebox
            messagebox.showinfo("Fin de ronda " + str(self.ronda - 1), msg)
            fin_partida = self.evaluar_fin_de_partida()
            if fin_partida:
                self.cerrar_partida(fin_partida)
                self._mostrar_fin_partida(fin_partida)
            else:
                self._limpiar_campo()
                self.siguiente_ronda()
                self.pantalla.refrescar_barra()
                self.pantalla.cambiar_fase("defensor")
            return

        # Reprogramamos el siguiente tick.
        self.controlador.after(TICK, self._paso_combate)

    #E: (no recibe parametros)
    #S: no retorna; borra todas las entidades del campo para la siguiente ronda
    #R: ninguna
    def _limpiar_campo(self):
        canvas = self.pantalla.canvas
        for t in self.pantalla.torres:
            t.borrar(canvas)
        for m in self.pantalla.muros:
            m.borrar(canvas)
        for u in self.pantalla.unidades:
            u.borrar(canvas)
        for p in self.pantalla.proyectiles:
            p.borrar(canvas)
        self.pantalla.torres.clear()
        self.pantalla.muros.clear()
        self.pantalla.unidades.clear()
        self.pantalla.proyectiles.clear()
        # Redibujamos la base para la nueva ronda.
        self.pantalla.base.vida = self.pantalla.base.vida_max
        self.pantalla.base.borrar(canvas)
        self.pantalla.base.dibujar(canvas, constantes.TAM_CELDA)
        # Rehabilitamos el boton de fase para la nueva ronda.
        self.pantalla.btn_fase.config(text="Terminar construcción", state="normal")

    #E: ganador_partida (str: "defensor" o "atacante")
    #S: no retorna; muestra la pantalla de fin de partida
    #R: ninguna
    def _mostrar_fin_partida(self, ganador_partida):
        from ventana_fin import PantallaFin
        jd = self.controlador.jugador_defensor
        ja = self.controlador.jugador_atacante
        nombre = jd.nombre if ganador_partida == "defensor" else ja.nombre
        self.controlador.mostrar(
            lambda p, c: PantallaFin(p, c, nombre, ganador_partida,
                                     self.victorias_defensor,
                                     self.victorias_atacante))
    
    # HABILIDADES DE TORRES
    # Mismo patron que activar_habilidad_unidad: se despacha por tipo.
    # Una habilidad distinta por cada tipo de torre, como pide el enunciado.

    #E: torre (Torre cuyo cooldown llego a 0)
    #S: no retorna; despacha la habilidad segun torre.tipo
    #R: ninguna
    def activar_habilidad_torre(self, torre):
        habilidades = {
            "basica":  self._habilidad_disparo_doble,
            "pesada":  self._habilidad_dano_area,
            "magica":  self._habilidad_congelar,
            "soporte": self._habilidad_reparar,
        }
        accion = habilidades.get(torre.tipo)
        if accion:
            accion(torre)

    #E: torre (Torre basica)
    #S: no retorna; dispara dos proyectiles hacia las dos unidades mas cercanas en alcance
    #R: ninguna
    def _habilidad_disparo_doble(self, torre):
        from proyectil import Proyectil
        canvas = self.pantalla.canvas
        cx_t, cy_t = constantes.casilla_a_centro(torre.fila, torre.columna)
        alcance_px = torre.alcance * constantes.TAM_CELDA

        # Ordenamos las unidades por distancia y tomamos las dos mas cercanas.
        vivas = [u for u in self.pantalla.unidades if not u.esta_muerta()]
        cercanas = sorted(vivas,
                          key=lambda u: (u.x - cx_t) ** 2 + (u.y - cy_t) ** 2)
        objetivos = [u for u in cercanas
                     if ((u.x - cx_t) ** 2 + (u.y - cy_t) ** 2) ** 0.5 <= alcance_px][:2]

        for objetivo in objetivos:
            proy = Proyectil(cx_t, cy_t, objetivo, torre.dano, torre.faccion)
            proy.dibujar(canvas, constantes.TAM_CELDA)
            self.pantalla.proyectiles.append(proy)

    #E: torre (Torre pesada)
    #S: no retorna; aplica dano a todas las unidades dentro de su alcance
    #R: ninguna
    def _habilidad_dano_area(self, torre):
        cx_t, cy_t = constantes.casilla_a_centro(torre.fila, torre.columna)
        alcance_px = torre.alcance * constantes.TAM_CELDA

        for unidad in list(self.pantalla.unidades):
            if unidad.esta_muerta():
                continue
            dist = ((unidad.x - cx_t) ** 2 + (unidad.y - cy_t) ** 2) ** 0.5
            if dist <= alcance_px:
                dano = torre.dano
                # Respeta el escudo si existe.
                if getattr(unidad, 'escudo_activo', False):
                    exceso = max(0, dano - unidad.escudo_hp)
                    unidad.escudo_hp -= dano
                    if unidad.escudo_hp <= 0:
                        unidad.escudo_activo = False
                    dano = exceso
                unidad.vida -= dano
                if unidad.esta_muerta():
                    unidad.borrar(self.pantalla.canvas)
                    self.pantalla.unidades.remove(unidad)
                    self.recompensa_por_eliminar(unidad)

    #E: torre (Torre magica)
    #S: no retorna; congela la unidad mas cercana en alcance por 2 segundos
    #R: ninguna
    def _habilidad_congelar(self, torre):
        cx_t, cy_t = constantes.casilla_a_centro(torre.fila, torre.columna)
        alcance_px = torre.alcance * constantes.TAM_CELDA

        objetivo = None
        menor_dist = float('inf')
        for unidad in self.pantalla.unidades:
            if unidad.esta_muerta() or unidad.congelada:
                continue
            dist = ((unidad.x - cx_t) ** 2 + (unidad.y - cy_t) ** 2) ** 0.5
            if dist <= alcance_px and dist < menor_dist:
                menor_dist = dist
                objetivo = unidad

        if objetivo:
            objetivo.congelada = True
            objetivo.tiempo_congelada = 2000   # 2 segundos en ms

    #E: torre (Torre soporte)
    #S: no retorna; repara 40 HP a la torre aliada mas cercana en alcance
    #R: ninguna
    def _habilidad_reparar(self, torre):
        cx_t, cy_t = constantes.casilla_a_centro(torre.fila, torre.columna)
        alcance_px = torre.alcance * constantes.TAM_CELDA

        objetivo = None
        menor_dist = float('inf')
        for aliada in self.pantalla.torres:
            if aliada is torre or aliada.esta_destruida():
                continue
            cx_a, cy_a = constantes.casilla_a_centro(aliada.fila, aliada.columna)
            dist = ((cx_a - cx_t) ** 2 + (cy_a - cy_t) ** 2) ** 0.5
            if dist <= alcance_px and dist < menor_dist:
                menor_dist = dist
                objetivo = aliada

        if objetivo:
            # Reparamos sin exceder la vida maxima.
            objetivo.vida = min(objetivo.vida + 40, objetivo.vida_max)

    #E: x, y (float, posicion en px donde aparece el efecto)
    #S: no retorna; dibuja un circulo rojo pequeno que desaparece gradualmente
    #R: ninguna
    def _efecto_dano(self, x, y):
        canvas = self.pantalla.canvas
        r = 6   # radio del circulo
        # Dibujamos el circulo rojo.
        id_circulo = canvas.create_oval(x - r, y - r, x + r, y + r,
                                        fill="#FF3333", outline="#FF0000",
                                        width=2)
        # Lo borramos despues de 350ms (efecto rapido y sutil).
        self.controlador.after(350, lambda: canvas.delete(id_circulo))