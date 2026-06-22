# ventana_juego.py
# Pantalla principal de la PARTIDA: barra superior de informacion, mapa
# (Canvas 15x15) y tienda de construccion/compra para defensor y atacante.

import tkinter as tk
import constantes
from base import Base
from torre import Torre
from muro import Muro
from unidad import Unidad


class PantallaJuego(tk.Frame):

    ALTO_BARRA = 100   # alto de la barra superior de informacion (px)

    #E: parent (contenedor), controlador (App)
    #S: instancia de la pantalla de juego con su estructura base
    #R: requiere que el controlador tenga faccion_defensor y faccion_atacante definidas
    def __init__(self, parent, controlador):
        super().__init__(parent, bg=controlador.COLORES["fondo"])
        self.controlador = controlador

        # Estado de construccion y tienda (Persona B - Fase 5).
        self.torres = []
        self.muros = []
        self.unidades = []
        self.proyectiles = []
        self.item_seleccionado = None
        self.fase_construccion = "defensor"

        self._construir()
        from juego import Juego
        self.juego = Juego(self)
        self._actualizar_estado()

    #E: (usa el controlador)
    #S: no retorna; arma la barra superior y el Canvas del mapa
    #R: ninguna
    def _construir(self):
        c = self.controlador.COLORES

        # --- Barra superior de informacion (se llena en un bloque posterior) ---
        self.barra = tk.Frame(self, bg=c["panel"], height=self.ALTO_BARRA)
        self.barra.pack(fill="x", side="top")
        self.barra.pack_propagate(False)   # respeta la altura fija de la barra

        self._construir_barra()

        # --- Zona del mapa: contiene el Canvas centrado ---
        zona = tk.Frame(self, bg=c["fondo"])
        zona.pack(fill="both", expand=True)

        # Color de fondo del mapa segun la faccion del defensor (si existe).
        if self.controlador.faccion_defensor:
            bg_mapa = self.controlador.faccion_defensor.obtener("fondo")["principal"]
        else:
            bg_mapa = c["fondo"]

        # Canvas del mapa: 15x15 casillas (medidas tomadas de constantes).
        self.canvas = tk.Canvas(zona, width=constantes.ANCHO, height=constantes.ALTO,
                                bg=bg_mapa, highlightthickness=0)
        self.canvas.pack(pady=10)   # sin fill -> queda centrado horizontalmente
        self._dibujar_cuadricula()
        self._dibujar_base()

        self.canvas.bind("<Button-1>", self._click_mapa)
        self._construir_tienda(zona)

    #E: (usa self.canvas y constantes)
    #S: no retorna; dibuja las lineas de la cuadricula 15x15 sobre el Canvas
    #R: self.canvas debe existir
    def _dibujar_cuadricula(self):
        # Color de linea sutil: borde de la faccion del defensor, o blanco tenue.
        if self.controlador.faccion_defensor:
            color_linea = self.controlador.faccion_defensor.obtener("fondo")["borde"]
        else:
            color_linea = "#FFFFFF"

        # Lineas verticales (una por cada columna + el borde derecho).
        for col in range(constantes.COLUMNAS + 1):
            x = col * constantes.TAM_CELDA
            self.canvas.create_line(x, 0, x, constantes.ALTO,
                                    fill=color_linea, width=1, stipple="gray25")

        # Lineas horizontales (una por cada fila + el borde inferior).
        for fila in range(constantes.FILAS + 1):
            y = fila * constantes.TAM_CELDA
            self.canvas.create_line(0, y, constantes.ANCHO, y,
                                    fill=color_linea, width=1, stipple="gray25")

    #E: (usa self.canvas y la faccion del defensor del controlador)
    #S: no retorna; crea la Base y la dibuja centrada en el mapa
    #R: controlador.faccion_defensor debe estar definida
    def _dibujar_base(self):
        # Creamos la base con la faccion del defensor y la dibujamos en el Canvas.
        self.base = Base(self.controlador.faccion_defensor)
        self.base.dibujar(self.canvas, constantes.TAM_CELDA)

    #E: (usa self.barra y el controlador)
    #S: no retorna; llena la barra superior con info de los jugadores, ronda y marcador
    #R: controlador debe tener jugador_defensor, jugador_atacante y sus facciones definidas
    def _construir_barra(self):
        c = self.controlador.COLORES
        jd = self.controlador.jugador_defensor
        ja = self.controlador.jugador_atacante
        fd = self.controlador.faccion_defensor
        fa = self.controlador.faccion_atacante

        # Tres columnas: defensor | centro (ronda/marcador) | atacante.
        self.barra.columnconfigure(0, weight=1)
        self.barra.columnconfigure(1, weight=1)
        self.barra.columnconfigure(2, weight=1)

        # --- Columna izquierda: defensor ---
        col_def = tk.Frame(self.barra, bg=c["panel"])
        col_def.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)

        tk.Label(col_def, text="DEFENSOR", font=("Trebuchet MS", 9),
                 bg=c["panel"], fg=c["tenue"]).pack(anchor="w")
        tk.Label(col_def, text=jd.nombre if jd else "---",
                 font=("Trebuchet MS", 15, "bold"),
                 bg=c["panel"], fg=c["texto"]).pack(anchor="w")
        # Color de faccion como pastilla + nombre.
        fila_fac = tk.Frame(col_def, bg=c["panel"])
        fila_fac.pack(anchor="w", pady=(2, 0))
        if fd:
            tk.Frame(fila_fac, bg=fd.obtener("torre")["principal"],
                     width=14, height=14).pack(side="left", padx=(0, 5))
            tk.Label(fila_fac, text=fd.nombre, font=("Trebuchet MS", 10),
                     bg=c["panel"], fg=c["tenue"]).pack(side="left")

        # --- Columna central: ronda y marcador ---
        col_centro = tk.Frame(self.barra, bg=c["panel"])
        col_centro.grid(row=0, column=1, sticky="nsew", pady=10)

        self.label_ronda = tk.Label(col_centro, text="RONDA 1",
                 font=("Trebuchet MS", 13, "bold"),
                 bg=c["panel"], fg=c["acento"])
        self.label_ronda.pack()

        self.label_marcador = tk.Label(col_centro, text="0  —  0",
                 font=("Trebuchet MS", 22, "bold"),
                 bg=c["panel"], fg=c["texto"])
        self.label_marcador.pack()

        # --- Columna derecha: atacante ---
        col_atk = tk.Frame(self.barra, bg=c["panel"])
        col_atk.grid(row=0, column=2, sticky="nsew", padx=20, pady=10)

        tk.Label(col_atk, text="ATACANTE", font=("Trebuchet MS", 9),
                 bg=c["panel"], fg=c["tenue"]).pack(anchor="e")
        tk.Label(col_atk, text=ja.nombre if ja else "---",
                 font=("Trebuchet MS", 15, "bold"),
                 bg=c["panel"], fg=c["texto"]).pack(anchor="e")
        fila_fac2 = tk.Frame(col_atk, bg=c["panel"])
        fila_fac2.pack(anchor="e", pady=(2, 0))
        if fa:
            tk.Label(fila_fac2, text=fa.nombre, font=("Trebuchet MS", 10),
                     bg=c["panel"], fg=c["tenue"]).pack(side="left")
            tk.Frame(fila_fac2, bg=fa.obtener("torre")["principal"],
                     width=14, height=14).pack(side="left", padx=(5, 0))

    # =================================================================
    # TIENDA Y COLOCACION (Persona B - Fase 5)
    # =================================================================

    #E: contenedor (Frame donde se monta la tienda, debajo del Canvas)
    #S: no retorna; arma los paneles de compra del defensor y del atacante
    #R: ninguna
    def _construir_tienda(self, contenedor):
        c = self.controlador.COLORES

        self.panel_tienda = tk.Frame(contenedor, bg=c["fondo"])
        self.panel_tienda.pack(fill="x", pady=(0, 10))

        # --- Panel del defensor: muro + 4 tipos de torre ---
        self.panel_defensor = tk.LabelFrame(self.panel_tienda, text="Construccion (Defensor)",
                                            bg=c["panel"], fg=c["texto"])
        self.panel_defensor.pack(side="left", expand=True, fill="both", padx=6)

        tk.Button(self.panel_defensor, text="Muro\n$" + str(Muro.COSTO),
                  command=lambda: self._seleccionar_item("muro", "muro")
                  ).pack(side="left", padx=4, pady=6)
        for tipo, datos in Torre.STATS.items():
            tk.Button(self.panel_defensor, text=datos["nombre"] + "\n$" + str(datos["costo"]),
                      command=lambda t=tipo: self._seleccionar_item(t, "torre")
                      ).pack(side="left", padx=4, pady=6)

        # --- Panel del atacante: 4 tipos de unidad ---
        self.panel_atacante = tk.LabelFrame(self.panel_tienda, text="Compra (Atacante)",
                                            bg=c["panel"], fg=c["texto"])
        self.panel_atacante.pack(side="left", expand=True, fill="both", padx=6)

        for tipo, datos in Unidad.STATS.items():
            tk.Button(self.panel_atacante, text=datos["nombre"] + "\n$" + str(datos["costo"]),
                      command=lambda t=tipo: self._seleccionar_item(t, "unidad")
                      ).pack(side="left", padx=4, pady=6)

        # --- Linea de estado: dinero, fase actual y item seleccionado ---
        self.label_estado = tk.Label(contenedor, text="", font=("Trebuchet MS", 10),
                                     bg=c["fondo"], fg=c["tenue"])
        self.label_estado.pack(pady=(0, 4))
        # _actualizar_estado se llama despues de que self.juego exista

        # Botones reales de control de fase.
        frame_botones_fase = tk.Frame(contenedor, bg=self.controlador.COLORES["fondo"])
        frame_botones_fase.pack(pady=(0, 6))

        self.controlador.boton(frame_botones_fase, "Terminar construcción",
                               self._terminar_construccion).pack(side="left", padx=6)
        self.controlador.boton(frame_botones_fase, "Terminar colocación",
                               self._terminar_colocacion).pack(side="left", padx=6)

    #E: tipo (str, clave en STATS o "muro"), categoria (str: "muro"/"torre"/"unidad")
    #S: no retorna; guarda la seleccion actual para usarla al hacer clic en el mapa
    #R: ninguna
    def _seleccionar_item(self, tipo, categoria):
        self.item_seleccionado = (tipo, categoria)
        self._actualizar_estado()

    #E: (usa dinero de juego.py, fase_construccion, item_seleccionado)
    #S: no retorna; refresca el texto de estado debajo de la tienda
    #R: ninguna
    def _actualizar_estado(self):
        sel = self.item_seleccionado[0] if self.item_seleccionado else "ninguno"
        texto = ("Fase: " + self.fase_construccion +
                 "  |  Dinero defensor: $" + str(self.juego.dinero_defensor) +
                 "  |  Dinero atacante: $" + str(self.juego.dinero_atacante) +
                 "  |  Seleccionado: " + sel)
        self.label_estado.config(text=texto)

    #E: event (clic de Tkinter, con event.x/event.y en pixeles del Canvas)
    #S: no retorna; intenta colocar el item seleccionado en la casilla clicada
    #R: requiere item seleccionado, fase correcta, casilla libre y dinero suficiente
    def _click_mapa(self, event):
        if self.item_seleccionado is None:
            return
        tipo, categoria = self.item_seleccionado
        fila, columna = constantes.pixel_a_casilla(event.x, event.y)

        if not constantes.casilla_valida(fila, columna):
            return

        # La categoria debe coincidir con la fase activa.
        if categoria in ("muro", "torre") and self.fase_construccion != "defensor":
            return
        if categoria == "unidad" and self.fase_construccion != "atacante":
            return

        if categoria == "muro":
            self._colocar_muro(fila, columna)
        elif categoria == "torre":
            self._colocar_torre(tipo, fila, columna)
        elif categoria == "unidad":
            self._colocar_unidad(tipo, fila, columna)

    #E: fila (int), columna (int)
    #S: True si la casilla esta libre (no es base, ni tiene torre o muro), False si esta ocupada
    #R: ninguna
    def _casilla_libre(self, fila, columna):
        if (fila, columna) in self.base.casillas_ocupadas():
            return False
        for t in self.torres:
            if t.fila == fila and t.columna == columna:
                return False
        for m in self.muros:
            if m.fila == fila and m.columna == columna:
                return False
        return True

    #E: fila (int), columna (int)
    #S: no retorna; coloca un Muro si la casilla esta libre y hay dinero suficiente
    #R: requiere self.dinero_defensor >= Muro.COSTO
    def _colocar_muro(self, fila, columna):
        if not self._casilla_libre(fila, columna):
            return
        if not self.juego.gastar(Muro.COSTO, "defensor"):
            return
        muro = Muro(fila, columna, self.controlador.faccion_defensor)
        muro.dibujar(self.canvas, constantes.TAM_CELDA)
        self.muros.append(muro)
        self._actualizar_estado()

    #E: tipo (str, clave en Torre.STATS), fila (int), columna (int)
    #S: no retorna; coloca una Torre si la casilla esta libre y hay dinero suficiente
    #R: requiere self.dinero_defensor >= costo de ese tipo
    def _colocar_torre(self, tipo, fila, columna):
        if not self._casilla_libre(fila, columna):
            return
        if not self.juego.gastar(Torre.STATS[tipo]["costo"], "defensor"):
            return
        torre = Torre(tipo, fila, columna, self.controlador.faccion_defensor)
        torre.dibujar(self.canvas, constantes.TAM_CELDA)
        self.torres.append(torre)
        self._actualizar_estado()

    #E: tipo (str, clave en Unidad.STATS), fila (int), columna (int)
    #S: no retorna; coloca una Unidad si la casilla es de borde y hay dinero suficiente
    #R: requiere self.dinero_atacante >= costo; solo en casillas de borde
    #   (las unidades entran por los 4 bordes hacia el centro, segun lo acordado)
    def _colocar_unidad(self, tipo, fila, columna):
        es_borde = fila in (0, constantes.FILAS - 1) or columna in (0, constantes.COLUMNAS - 1)
        if not es_borde:
            return
        if not self.juego.gastar(Unidad.STATS[tipo]["costo"], "atacante"):
            return
        x, y = constantes.casilla_a_centro(fila, columna)
        unidad = Unidad(tipo, x, y, self.controlador.faccion_atacante)
        unidad.dibujar(self.canvas, constantes.TAM_CELDA)
        self.unidades.append(unidad)
        self._actualizar_estado()

    #E: nueva_fase (str: "defensor" o "atacante")
    #S: no retorna; cambia la fase de construccion activa (la llamara juego.py)
    #R: nueva_fase debe ser "defensor" o "atacante"
    def cambiar_fase(self, nueva_fase):
        if nueva_fase not in ("defensor", "atacante"):
            raise ValueError("Fase no valida: " + str(nueva_fase))
        self.fase_construccion = nueva_fase
        self.item_seleccionado = None
        self._actualizar_estado()

    #E: (no recibe parametros)
    #S: no retorna; cierra la fase de construccion y pasa al atacante
    #R: debe estar en fase de construccion
    def _terminar_construccion(self):
        self.juego.terminar_construccion()
        self.cambiar_fase("atacante")
        self._actualizar_estado()

    #E: (no recibe parametros)
    #S: no retorna; cierra la fase de colocacion e inicia el combate
    #R: debe estar en fase de colocacion
    def _terminar_colocacion(self):
        self.juego.terminar_colocacion()
        self.juego.iniciar_combate()
    
    #E: (lee ronda y victorias de self.juego)
    #S: no retorna; actualiza el marcador y la ronda en la barra superior
    #R: self.juego debe existir
    def refrescar_barra(self):
        self.label_ronda.config(text="RONDA " + str(self.juego.ronda))
        marcador = (str(self.juego.victorias_defensor) +
                    "  —  " +
                    str(self.juego.victorias_atacante))
        self.label_marcador.config(text=marcador)