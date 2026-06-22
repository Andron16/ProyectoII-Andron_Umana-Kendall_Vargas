# torre.py
# Torre defensiva del DEFENSOR. Solo datos + dibujo. Hay 4 tipos (basica,
# pesada, magica, soporte); cada uno tiene stats y silueta propias, y la
# silueta cambia ademas por faccion. La habilidad de cada tipo se ejecuta
# en juego.py (aqui solo se guarda su nombre y su cooldown).

import constantes


class Torre:

    # Stats por tipo (provisionales, a balancear en pareja).
    # alcance esta en casillas; cooldown_ms es el tiempo para activar la habilidad.
    STATS = {
        "basica":  {"nombre": "Torre basica",  "costo": 100, "vida": 150,
                    "dano": 15, "alcance": 3, "habilidad": "disparo_doble",
                    "cooldown_ms": 3000, "cooldown_ataque_ms": 1000},
        "pesada":  {"nombre": "Torre pesada",  "costo": 250, "vida": 400,
                    "dano": 40, "alcance": 2, "habilidad": "dano_area",
                    "cooldown_ms": 5000, "cooldown_ataque_ms": 2000},
        "magica":  {"nombre": "Torre magica",  "costo": 180, "vida": 120,
                    "dano": 8,  "alcance": 4, "habilidad": "congelar",
                    "cooldown_ms": 6000, "cooldown_ataque_ms": 1500},
        "soporte": {"nombre": "Torre soporte", "costo": 150, "vida": 130,
                    "dano": 5,  "alcance": 3, "habilidad": "reparar",
                    "cooldown_ms": 7000, "cooldown_ataque_ms": 2000},
    }

    #E: tipo (str: "basica"/"pesada"/"magica"/"soporte"), fila (int), columna (int), faccion (Faccion)
    #S: instancia de Torre con los stats de su tipo y vida completa
    #R: tipo debe existir en Torre.STATS y (fila, columna) ser casilla valida
    def __init__(self, tipo, fila, columna, faccion):
        if tipo not in Torre.STATS:
            raise ValueError("Tipo de torre no valido: " + str(tipo))
        s = Torre.STATS[tipo]
        self.tipo = tipo
        self.nombre = s["nombre"]
        self.costo = s["costo"]
        self.vida = s["vida"]
        self.vida_max = s["vida"]
        self.dano = s["dano"]
        self.alcance = s["alcance"]            # en casillas
        self.habilidad = s["habilidad"]        # juego.py lo usa para despachar
        self.cooldown_ms = s["cooldown_ms"]
        self.tiempo_restante = s["cooldown_ms"]  # juego.py lo descuenta; al llegar a 0, habilidad lista
        self.tiempo_ataque_restante = s["cooldown_ataque_ms"]  # cooldown del disparo basico
        self.cooldown_ataque_ms = s["cooldown_ataque_ms"]
        self.fila = fila
        self.columna = columna
        self.faccion = faccion
        self.id_items = []

    #E: (usa su propia vida)
    #S: True si la torre fue destruida, False si sigue en pie
    #R: ninguna
    def esta_destruida(self):
        return self.vida <= 0

    #E: canvas (Canvas de Tkinter), tam_celda (int, lado de la casilla en px)
    #S: lista con los IDs dibujados (tambien en self.id_items)
    #R: tam_celda > 0
    def dibujar(self, canvas, tam_celda):
        # Esquina de la casilla y helpers de escalado (columna -> x, fila -> y).
        ox = self.columna * tam_celda
        oy = self.fila * tam_celda
        gr = max(1, tam_celda * 0.025)
        fn = max(1, tam_celda * 0.015)
        p = lambda px, py: constantes.punto(ox, oy, tam_celda, px, py)
        poli = lambda pts: constantes.poligono(ox, oy, tam_celda, pts)
        col = self.faccion.obtener("torre")

        ids = []
        # Despacho por tipo: cada tipo dibuja su propia silueta.
        dibujos = {
            "basica":  self._dibujar_basica,
            "pesada":  self._dibujar_pesada,
            "magica":  self._dibujar_magica,
            "soporte": self._dibujar_soporte,
        }
        dibujos[self.tipo](canvas, p, poli, gr, fn, col, ids)

        self.id_items = ids
        return ids

    #E: canvas, p, poli (helpers de escalado), gr, fn (grosores), col (colores de torre), ids (lista a llenar)
    #S: no retorna; agrega a 'ids' la silueta de la torre basica segun la faccion
    #R: ninguna
    def _dibujar_basica(self, canvas, p, poli, gr, fn, col, ids):
        principal, secundario, borde = col["principal"], col["secundario"], col["borde"]
        if self.faccion.nombre == "Medieval":
            # Torreta de piedra con almenas y banda dorada.
            ids.append(canvas.create_rectangle(*p(37, 46), *p(63, 86), fill=principal, outline=borde, width=gr))
            for (x1, x2) in [(37, 44), (46, 54), (56, 63)]:
                ids.append(canvas.create_rectangle(*p(x1, 40), *p(x2, 47), fill=principal, outline=borde, width=fn))
            ids.append(canvas.create_rectangle(*p(37, 68), *p(63, 72), fill=secundario, outline=""))
            ids.append(canvas.create_rectangle(*p(46, 54), *p(54, 64), fill=borde, outline=""))
        elif self.faccion.nombre == "Futurista":
            # Torreta troncoconica con canon y nucleo.
            ids.append(canvas.create_polygon(poli([(40, 86), (60, 86), (56, 58), (44, 58)]),
                                             fill=principal, outline=borde, width=gr))
            ids.append(canvas.create_rectangle(*p(42, 72), *p(58, 76), fill=secundario, outline=""))
            ids.append(canvas.create_rectangle(*p(47, 40), *p(53, 58), fill=principal, outline=borde, width=fn))
            ids.append(canvas.create_line(*p(50, 40), *p(50, 28), fill=secundario, width=fn))
            ids.append(canvas.create_oval(*p(43, 31), *p(57, 45), fill=secundario, outline=borde, width=fn))
            ids.append(canvas.create_oval(*p(47, 23), *p(53, 29), fill="#46E5FF", outline=""))  # destello
        elif self.faccion.nombre == "Naturaleza":
            # Hongo-torreta: tallo y sombrero con motas.
            ids.append(canvas.create_rectangle(*p(44, 56), *p(56, 86), fill=secundario, outline=borde, width=gr))
            ids.append(canvas.create_oval(*p(27, 37), *p(73, 67), fill=principal, outline=borde, width=gr))
            for (cx, cy, r) in [(40, 48, 3.5), (56, 46, 3), (50, 55, 2.5)]:
                ids.append(canvas.create_oval(*p(cx - r, cy - r), *p(cx + r, cy + r), fill="#A7C25A", outline=""))

    #E: canvas, p, poli, gr, fn, col, ids (igual que _dibujar_basica)
    #S: no retorna; agrega a 'ids' la silueta de la torre pesada (propuesta, no en preview)
    #R: ninguna
    def _dibujar_pesada(self, canvas, p, poli, gr, fn, col, ids):
        principal, secundario, borde = col["principal"], col["secundario"], col["borde"]
        if self.faccion.nombre == "Medieval":
            # Bombarda: base ancha reforzada y canon grueso.
            ids.append(canvas.create_rectangle(*p(26, 62), *p(74, 86), fill=principal, outline=borde, width=gr))
            ids.append(canvas.create_rectangle(*p(26, 72), *p(74, 76), fill=secundario, outline=""))
            for (x1, x2) in [(28, 37), (46, 55), (63, 72)]:
                ids.append(canvas.create_rectangle(*p(x1, 56), *p(x2, 63), fill=principal, outline=borde, width=fn))
            ids.append(canvas.create_rectangle(*p(42, 28), *p(58, 64), fill=principal, outline=borde, width=gr))
            ids.append(canvas.create_rectangle(*p(40, 28), *p(60, 33), fill=secundario, outline=""))
        elif self.faccion.nombre == "Futurista":
            # Torreta pesada de doble canon con nucleo de energia.
            ids.append(canvas.create_polygon(poli([(30, 86), (70, 86), (64, 60), (36, 60)]),
                                             fill=principal, outline=borde, width=gr))
            for x in [39, 54]:
                ids.append(canvas.create_rectangle(*p(x, 30), *p(x + 7, 60), fill=principal, outline=borde, width=fn))
                ids.append(canvas.create_rectangle(*p(x, 30), *p(x + 7, 34), fill=secundario, outline=""))
            ids.append(canvas.create_oval(*p(44, 64), *p(56, 76), fill=secundario, outline=borde, width=fn))
            ids.append(canvas.create_oval(*p(47, 67), *p(53, 73), fill="#46E5FF", outline=""))
        elif self.faccion.nombre == "Naturaleza":
            # Bulbo pesado con espinas sobre tronco grueso.
            ids.append(canvas.create_rectangle(*p(40, 62), *p(60, 86), fill=principal, outline=borde, width=gr))
            ids.append(canvas.create_oval(*p(32, 34), *p(68, 66), fill=principal, outline=borde, width=gr))
            ids.append(canvas.create_polygon(poli([(50, 34), (46, 24), (54, 24)]), fill=secundario, outline=borde, width=fn))
            ids.append(canvas.create_polygon(poli([(34, 50), (24, 47), (34, 44)]), fill=secundario, outline=borde, width=fn))
            ids.append(canvas.create_polygon(poli([(66, 50), (76, 47), (66, 44)]), fill=secundario, outline=borde, width=fn))
            for (cx, cy) in [(44, 52), (58, 50)]:
                ids.append(canvas.create_oval(*p(cx - 3, cy - 3), *p(cx + 3, cy + 3), fill=secundario, outline=""))

    #E: canvas, p, poli, gr, fn, col, ids (igual que _dibujar_basica)
    #S: no retorna; agrega a 'ids' la silueta de la torre magica segun la faccion
    #R: ninguna
    def _dibujar_magica(self, canvas, p, poli, gr, fn, col, ids):
        principal, secundario, borde = col["principal"], col["secundario"], col["borde"]
        if self.faccion.nombre == "Medieval":
            # Torre del mago: cuerpo, techo conico y orbe brillante.
            ids.append(canvas.create_rectangle(*p(40, 50), *p(60, 86), fill=principal, outline=borde, width=gr))
            ids.append(canvas.create_polygon(poli([(37, 50), (63, 50), (50, 26)]), fill=secundario, outline=borde, width=gr))
            ids.append(canvas.create_oval(*p(41, 13), *p(59, 31), fill="#FFE9A8", outline="", stipple="gray25"))
            ids.append(canvas.create_oval(*p(45.5, 17.5), *p(54.5, 26.5), fill="#FFE9A8", outline=secundario, width=fn))
            ids.append(canvas.create_arc(*p(45, 59), *p(55, 69), start=0, extent=180,
                                         style="pieslice", fill=borde, outline=""))
            ids.append(canvas.create_rectangle(*p(45, 64), *p(55, 74), fill=borde, outline=""))
        elif self.faccion.nombre == "Futurista":
            # Cristal de energia sobre base, con orbe flotante.
            ids.append(canvas.create_rectangle(*p(43, 78), *p(57, 86), fill=principal, outline=borde, width=fn))
            ids.append(canvas.create_polygon(poli([(50, 30), (62, 58), (50, 78), (38, 58)]),
                                             fill=principal, outline=secundario, width=gr))
            ids.append(canvas.create_polygon(poli([(50, 40), (56, 58), (50, 70), (44, 58)]),
                                             fill="#46E5FF", outline="", stipple="gray50"))
            ids.append(canvas.create_oval(*p(42, 14), *p(58, 30), fill="#46E5FF", outline="", stipple="gray25"))
            ids.append(canvas.create_oval(*p(46, 18), *p(54, 26), fill="#46E5FF", outline=""))
        elif self.faccion.nombre == "Naturaleza":
            # Flor magica: tallo, hojas, petalos y centro brillante.
            ids.append(canvas.create_rectangle(*p(48, 52), *p(52, 86), fill=principal, outline=borde, width=fn))
            ids.append(canvas.create_polygon(poli([(48, 68), (38, 62), (48, 60)]), fill=secundario, outline=borde, width=fn))
            ids.append(canvas.create_polygon(poli([(52, 74), (62, 68), (52, 66)]), fill=secundario, outline=borde, width=fn))
            for (cx, cy, rx, ry) in [(50, 30, 6, 11), (50, 58, 6, 11), (36, 44, 11, 6), (64, 44, 11, 6)]:
                ids.append(canvas.create_oval(*p(cx - rx, cy - ry), *p(cx + rx, cy + ry),
                                              fill=secundario, outline=borde, width=fn))
            ids.append(canvas.create_oval(*p(41, 35), *p(59, 53), fill="#C58A2E", outline="", stipple="gray25"))
            ids.append(canvas.create_oval(*p(44, 38), *p(56, 50), fill="#C58A2E", outline=borde, width=fn))

    #E: canvas, p, poli, gr, fn, col, ids (igual que _dibujar_basica)
    #S: no retorna; agrega a 'ids' la silueta de la torre soporte (propuesta, no en preview)
    #R: ninguna
    def _dibujar_soporte(self, canvas, p, poli, gr, fn, col, ids):
        principal, secundario, borde = col["principal"], col["secundario"], col["borde"]
        if self.faccion.nombre == "Medieval":
            # Santuario con aura de apoyo y emblema en cruz.
            ids.append(canvas.create_oval(*p(26, 46), *p(74, 90), fill=secundario, outline="", stipple="gray12"))
            ids.append(canvas.create_rectangle(*p(40, 54), *p(60, 86), fill=principal, outline=borde, width=gr))
            ids.append(canvas.create_polygon(poli([(37, 54), (63, 54), (50, 40)]), fill=secundario, outline=borde, width=gr))
            ids.append(canvas.create_line(*p(50, 62), *p(50, 74), fill=secundario, width=gr))
            ids.append(canvas.create_line(*p(45, 67), *p(55, 67), fill=secundario, width=gr))
        elif self.faccion.nombre == "Futurista":
            # Antena de soporte con campo de energia pulsante.
            ids.append(canvas.create_rectangle(*p(42, 74), *p(58, 86), fill=principal, outline=borde, width=fn))
            ids.append(canvas.create_rectangle(*p(48, 44), *p(52, 74), fill=principal, outline=borde, width=fn))
            ids.append(canvas.create_oval(*p(38, 32), *p(62, 52), fill=secundario, outline="", stipple="gray12"))
            ids.append(canvas.create_oval(*p(34, 28), *p(66, 56), fill="", outline=secundario, width=gr))
            ids.append(canvas.create_oval(*p(46, 38), *p(54, 46), fill="#46E5FF", outline=borde, width=fn))
        elif self.faccion.nombre == "Naturaleza":
            # Flor curativa que emite esporas, con aura de apoyo.
            ids.append(canvas.create_oval(*p(30, 30), *p(70, 70), fill=secundario, outline="", stipple="gray12"))
            ids.append(canvas.create_rectangle(*p(47, 56), *p(53, 86), fill=principal, outline=borde, width=fn))
            ids.append(canvas.create_oval(*p(34, 40), *p(66, 64), fill=principal, outline=borde, width=gr))
            ids.append(canvas.create_oval(*p(44, 44), *p(56, 56), fill="#C58A2E", outline=borde, width=fn))
            for (cx, cy) in [(40, 38), (60, 40), (50, 32)]:
                ids.append(canvas.create_oval(*p(cx - 2, cy - 2), *p(cx + 2, cy + 2), fill=secundario, outline=""))

    #E: canvas (Canvas de Tkinter)
    #S: no retorna; borra del Canvas las figuras de esta torre
    #R: ninguna
    def borrar(self, canvas):
        for item in self.id_items:
            canvas.delete(item)
        self.id_items = []