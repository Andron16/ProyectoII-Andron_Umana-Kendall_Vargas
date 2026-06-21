# unidad.py
# Unidad del ATACANTE. Solo datos + dibujo. Hay 4 tipos (soldado, tanque,
# rapida, sanador); cada uno tiene stats y silueta propias, y la silueta
# cambia ademas por faccion. Las unidades se mueven en PIXELES (x, y); el
# movimiento y las habilidades se manejan en juego.py.

import constantes


class Unidad:

    # Stats por tipo (provisionales, a balancear en pareja).
    # velocidad: pixeles por actualizacion del game loop. cooldown_ms: tiempo
    # para activar la habilidad. La habilidad se ejecuta en juego.py.
    STATS = {
        "soldado": {"nombre": "Soldado", "costo": 75,  "vida": 100, "dano": 10,
                    "velocidad": 1.6, "habilidad": "ataque_doble",     "cooldown_ms": 4000},
        "tanque":  {"nombre": "Tanque",  "costo": 200, "vida": 350, "dano": 25,
                    "velocidad": 1.0, "habilidad": "escudo_temporal",  "cooldown_ms": 7000},
        "rapida":  {"nombre": "Rapida",  "costo": 100, "vida": 70,  "dano": 8,
                    "velocidad": 2.6, "habilidad": "aumento_velocidad","cooldown_ms": 5000},
        "sanador": {"nombre": "Sanador", "costo": 120, "vida": 90,  "dano": 0,
                    "velocidad": 1.6, "habilidad": "curar_aliados",    "cooldown_ms": 6000},
    }

    #E: tipo (str: "soldado"/"tanque"/"rapida"/"sanador"), x (float), y (float), faccion (Faccion)
    #S: instancia de Unidad en la posicion (x, y) en pixeles, con vida completa
    #R: tipo debe existir en Unidad.STATS
    def __init__(self, tipo, x, y, faccion):
        if tipo not in Unidad.STATS:
            raise ValueError("Tipo de unidad no valido: " + str(tipo))
        s = Unidad.STATS[tipo]
        self.tipo = tipo
        self.nombre = s["nombre"]
        self.costo = s["costo"]
        self.vida = s["vida"]
        self.vida_max = s["vida"]
        self.dano = s["dano"]
        self.velocidad = s["velocidad"]        # px por actualizacion (juego.py la usa al mover)
        self.habilidad = s["habilidad"]        # juego.py lo usa para despachar
        self.cooldown_ms = s["cooldown_ms"]
        self.tiempo_restante = s["cooldown_ms"]  # juego.py lo descuenta; al llegar a 0, habilidad lista
        self.x = x                             # posicion en pixeles (centro del sprite)
        self.y = y
        self.faccion = faccion
        self.congelada = False                 # juego.py la activa con la torre magica (congelar)
        self.escudo_activo = False             # juego.py lo activa con la habilidad del tanque
        self.id_items = []

    #E: (usa su propia vida)
    #S: True si la unidad murio, False si sigue viva
    #R: ninguna
    def esta_muerta(self):
        return self.vida <= 0

    #E: canvas (Canvas de Tkinter), tam_celda (int, lado del sprite en px)
    #S: lista con los IDs dibujados (tambien en self.id_items)
    #R: tam_celda > 0
    def dibujar(self, canvas, tam_celda):
        # El sprite (tamano de una celda) se centra en la posicion (x, y) de la unidad.
        ox = self.x - tam_celda / 2
        oy = self.y - tam_celda / 2
        gr = max(1, tam_celda * 0.025)
        fn = max(1, tam_celda * 0.015)
        p = lambda px, py: constantes.punto(ox, oy, tam_celda, px, py)
        poli = lambda pts: constantes.poligono(ox, oy, tam_celda, pts)
        col = self.faccion.obtener("unidad")

        ids = []
        dibujos = {
            "soldado": self._dibujar_soldado,
            "tanque":  self._dibujar_tanque,
            "rapida":  self._dibujar_rapida,
            "sanador": self._dibujar_sanador,
        }
        dibujos[self.tipo](canvas, p, poli, gr, fn, col, ids)

        self.id_items = ids
        return ids

    #E: canvas, p, poli (helpers de escalado), gr, fn (grosores), col (colores de unidad), ids (lista a llenar)
    #S: no retorna; agrega a 'ids' la silueta del soldado segun la faccion
    #R: ninguna
    def _dibujar_soldado(self, canvas, p, poli, gr, fn, col, ids):
        principal, secundario, borde = col["principal"], col["secundario"], col["borde"]
        if self.faccion.nombre == "Medieval":
            # Caballero: lanza, armadura, penacho y escudo.
            ids.append(canvas.create_line(*p(63, 42), *p(63, 82), fill=borde, width=gr))
            ids.append(canvas.create_polygon(poli([(63, 42), (67, 36), (71, 42)]), fill="#877A66", outline=borde, width=fn))
            for x in [43, 51]:
                ids.append(canvas.create_rectangle(*p(x, 72), *p(x + 6, 85), fill=borde, outline=""))
            ids.append(canvas.create_rectangle(*p(42, 54), *p(58, 74), fill=principal, outline=borde, width=gr))
            ids.append(canvas.create_oval(*p(42, 39), *p(58, 55), fill=principal, outline=borde, width=gr))
            ids.append(canvas.create_rectangle(*p(44, 45), *p(56, 48), fill=borde, outline=""))
            ids.append(canvas.create_polygon(poli([(50, 39), (53, 33), (47, 33)]), fill=secundario, outline=""))
            ids.append(canvas.create_polygon(poli([(33, 55), (41, 55), (41, 68), (37, 72), (33, 68)]), fill=secundario, outline=borde, width=gr))
        elif self.faccion.nombre == "Futurista":
            # Dron de asalto: chasis, cabina y propulsores.
            ids.append(canvas.create_oval(*p(34, 78), *p(66, 86), fill=borde, outline="", stipple="gray25"))
            ids.append(canvas.create_polygon(poli([(40, 58), (60, 58), (64, 70), (50, 78), (36, 70)]), fill=principal, outline=borde, width=gr))
            ids.append(canvas.create_rectangle(*p(44, 46), *p(56, 59), fill=principal, outline=borde, width=gr))
            ids.append(canvas.create_rectangle(*p(46, 49), *p(54, 53), fill=secundario, outline=""))
            ids.append(canvas.create_line(*p(40, 64), *p(32, 60), fill=borde, width=gr))
            ids.append(canvas.create_line(*p(60, 64), *p(68, 60), fill=borde, width=gr))
            for cx in [44, 56]:
                ids.append(canvas.create_oval(*p(cx - 2, 71), *p(cx + 2, 75), fill=secundario, outline=""))
        elif self.faccion.nombre == "Naturaleza":
            # Criatura: cuerpo, cabeza con cuerno y ojos.
            for x in [42, 52]:
                ids.append(canvas.create_rectangle(*p(x, 74), *p(x + 6, 85), fill=borde, outline=""))
            ids.append(canvas.create_oval(*p(35, 53), *p(65, 79), fill=principal, outline=borde, width=gr))
            ids.append(canvas.create_oval(*p(40, 38), *p(60, 58), fill=principal, outline=borde, width=gr))
            ids.append(canvas.create_polygon(poli([(50, 38), (47, 28), (55, 32)]), fill=secundario, outline=borde, width=fn))
            for cx in [46, 54]:
                ids.append(canvas.create_oval(*p(cx - 2.5, 44.5), *p(cx + 2.5, 49.5), fill="#E4F0B8", outline=""))
                ids.append(canvas.create_oval(*p(cx - 1.2, 45.8), *p(cx + 1.2, 48.2), fill=borde, outline=""))

    #E: canvas, p, poli, gr, fn, col, ids (igual que _dibujar_soldado)
    #S: no retorna; agrega a 'ids' la silueta del tanque (propuesta, no en preview)
    #R: ninguna
    def _dibujar_tanque(self, canvas, p, poli, gr, fn, col, ids):
        principal, secundario, borde = col["principal"], col["secundario"], col["borde"]
        if self.faccion.nombre == "Medieval":
            # Coloso acorazado: cuerpo macizo, escudo grande y maza.
            for x in [40, 52]:
                ids.append(canvas.create_rectangle(*p(x, 76), *p(x + 8, 86), fill=borde, outline=""))
            ids.append(canvas.create_rectangle(*p(38, 50), *p(62, 76), fill=principal, outline=borde, width=gr))
            ids.append(canvas.create_oval(*p(41, 36), *p(59, 54), fill=principal, outline=borde, width=gr))
            ids.append(canvas.create_rectangle(*p(43, 43), *p(57, 46), fill=borde, outline=""))
            ids.append(canvas.create_rectangle(*p(24, 48), *p(38, 78), fill=secundario, outline=borde, width=gr))
            ids.append(canvas.create_line(*p(66, 50), *p(66, 72), fill=borde, width=gr))
            ids.append(canvas.create_oval(*p(60, 40), *p(74, 54), fill=secundario, outline=borde, width=fn))
        elif self.faccion.nombre == "Futurista":
            # Mecha pesado sobre orugas con torreta y canon.
            ids.append(canvas.create_rectangle(*p(28, 74), *p(72, 86), fill=borde, outline=""))
            ids.append(canvas.create_rectangle(*p(31, 77), *p(69, 83), fill=principal, outline=""))
            for cx in [38, 50, 62]:
                ids.append(canvas.create_oval(*p(cx - 3, 77), *p(cx + 3, 83), fill=secundario, outline=""))
            ids.append(canvas.create_rectangle(*p(36, 50), *p(64, 74), fill=principal, outline=borde, width=gr))
            ids.append(canvas.create_rectangle(*p(44, 42), *p(56, 52), fill=principal, outline=borde, width=fn))
            ids.append(canvas.create_rectangle(*p(56, 45), *p(74, 50), fill=principal, outline=borde, width=fn))
            ids.append(canvas.create_rectangle(*p(46, 44), *p(54, 47), fill=secundario, outline=""))
        elif self.faccion.nombre == "Naturaleza":
            # Bestia acorazada: caparazon con placas y cabeza saliente.
            for x in [36, 56]:
                ids.append(canvas.create_rectangle(*p(x, 72), *p(x + 7, 84), fill=borde, outline=""))
            ids.append(canvas.create_oval(*p(28, 44), *p(68, 76), fill=principal, outline=borde, width=gr))
            for (x1, y1, x2, y2) in [(36, 50, 48, 60), (49, 48, 60, 58)]:
                ids.append(canvas.create_oval(*p(x1, y1), *p(x2, y2), fill=secundario, outline=borde, width=fn))
            ids.append(canvas.create_oval(*p(64, 54), *p(78, 68), fill=principal, outline=borde, width=fn))
            ids.append(canvas.create_oval(*p(72, 58), *p(76, 62), fill=borde, outline=""))

    #E: canvas, p, poli, gr, fn, col, ids (igual que _dibujar_soldado)
    #S: no retorna; agrega a 'ids' la silueta de la unidad rapida (propuesta, no en preview)
    #R: ninguna
    def _dibujar_rapida(self, canvas, p, poli, gr, fn, col, ids):
        principal, secundario, borde = col["principal"], col["secundario"], col["borde"]
        if self.faccion.nombre == "Medieval":
            # Explorador ligero: capa al viento y daga.
            for x in [44, 52]:
                ids.append(canvas.create_rectangle(*p(x, 74), *p(x + 5, 85), fill=borde, outline=""))
            ids.append(canvas.create_polygon(poli([(45, 54), (33, 58), (37, 74), (46, 70)]), fill=secundario, outline=borde, width=fn))
            ids.append(canvas.create_rectangle(*p(45, 54), *p(55, 74), fill=principal, outline=borde, width=fn))
            ids.append(canvas.create_oval(*p(44, 42), *p(56, 54), fill=principal, outline=borde, width=fn))
            ids.append(canvas.create_line(*p(55, 60), *p(64, 52), fill=secundario, width=gr))
        elif self.faccion.nombre == "Futurista":
            # Moto de combate veloz con estela de propulsion.
            ids.append(canvas.create_oval(*p(28, 72), *p(58, 80), fill=secundario, outline="", stipple="gray25"))
            ids.append(canvas.create_polygon(poli([(34, 62), (62, 56), (70, 64), (62, 72), (38, 72)]), fill=principal, outline=borde, width=fn))
            ids.append(canvas.create_oval(*p(44, 56), *p(56, 64), fill=secundario, outline=borde, width=fn))
            ids.append(canvas.create_rectangle(*p(28, 62), *p(34, 68), fill=secundario, outline=""))
        elif self.faccion.nombre == "Naturaleza":
            # Criatura veloz: cuerpo agil, orejas largas y patas saltarinas.
            for x in [42, 52]:
                ids.append(canvas.create_rectangle(*p(x, 72), *p(x + 6, 84), fill=borde, outline=""))
            ids.append(canvas.create_oval(*p(38, 52), *p(62, 74), fill=principal, outline=borde, width=fn))
            ids.append(canvas.create_oval(*p(51, 45), *p(65, 59), fill=principal, outline=borde, width=fn))
            for cx in [55, 61]:
                ids.append(canvas.create_oval(*p(cx - 2, 32), *p(cx + 2, 48), fill=principal, outline=borde, width=fn))
            ids.append(canvas.create_oval(*p(59, 50), *p(63, 54), fill=borde, outline=""))

    #E: canvas, p, poli, gr, fn, col, ids (igual que _dibujar_soldado)
    #S: no retorna; agrega a 'ids' la silueta del sanador (propuesta, no en preview)
    #R: ninguna
    def _dibujar_sanador(self, canvas, p, poli, gr, fn, col, ids):
        principal, secundario, borde = col["principal"], col["secundario"], col["borde"]
        if self.faccion.nombre == "Medieval":
            # Clerigo: tunica, baculo con orbe y emblema de cruz.
            ids.append(canvas.create_polygon(poli([(42, 54), (58, 54), (62, 84), (38, 84)]), fill=principal, outline=borde, width=gr))
            ids.append(canvas.create_oval(*p(42, 38), *p(58, 54), fill=principal, outline=borde, width=gr))
            ids.append(canvas.create_line(*p(64, 36), *p(64, 82), fill=borde, width=gr))
            ids.append(canvas.create_oval(*p(60, 30), *p(70, 40), fill=secundario, outline=borde, width=fn))
            ids.append(canvas.create_line(*p(50, 62), *p(50, 74), fill=secundario, width=gr))
            ids.append(canvas.create_line(*p(45, 67), *p(55, 67), fill=secundario, width=gr))
        elif self.faccion.nombre == "Futurista":
            # Dron medico: cupula, halo y cruz de curacion.
            ids.append(canvas.create_oval(*p(36, 76), *p(64, 84), fill=secundario, outline="", stipple="gray25"))
            ids.append(canvas.create_rectangle(*p(42, 50), *p(58, 74), fill=principal, outline=borde, width=fn))
            ids.append(canvas.create_oval(*p(43, 38), *p(57, 52), fill=principal, outline=borde, width=fn))
            ids.append(canvas.create_oval(*p(40, 54), *p(60, 72), fill="#46E5FF", outline="", stipple="gray25"))
            ids.append(canvas.create_line(*p(50, 58), *p(50, 70), fill="#46E5FF", width=gr))
            ids.append(canvas.create_line(*p(44, 64), *p(56, 64), fill="#46E5FF", width=gr))
        elif self.faccion.nombre == "Naturaleza":
            # Espiritu sanador: cuerpo de hojas, semilla brillante y esporas.
            ids.append(canvas.create_oval(*p(37, 50), *p(63, 80), fill=principal, outline=borde, width=fn))
            ids.append(canvas.create_oval(*p(43, 38), *p(57, 52), fill=principal, outline=borde, width=fn))
            ids.append(canvas.create_polygon(poli([(50, 38), (45, 30), (50, 34)]), fill=secundario, outline=borde, width=fn))
            ids.append(canvas.create_polygon(poli([(50, 38), (55, 30), (50, 34)]), fill=secundario, outline=borde, width=fn))
            ids.append(canvas.create_oval(*p(44, 56), *p(56, 68), fill="#C58A2E", outline="", stipple="gray25"))
            ids.append(canvas.create_oval(*p(47, 59), *p(53, 65), fill="#C58A2E", outline=borde, width=fn))
            for (cx, cy) in [(38, 46), (62, 48), (40, 64)]:
                ids.append(canvas.create_oval(*p(cx - 1.5, cy - 1.5), *p(cx + 1.5, cy + 1.5), fill=secundario, outline=""))

    #E: canvas (Canvas de Tkinter)
    #S: no retorna; borra del Canvas las figuras de esta unidad
    #R: ninguna
    def borrar(self, canvas):
        for item in self.id_items:
            canvas.delete(item)
        self.id_items = []