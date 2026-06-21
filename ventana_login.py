# ventana_login.py
# Pantalla de LOGIN reutilizable: primero la usa el defensor (J1) y luego
# el atacante (J2). Un titulo dinamico indica de quien es el turno.
# Solo datos + visual en este archivo; la logica de sesion va en los metodos.

import tkinter as tk
from tkinter import messagebox


class PantallaLogin(tk.Frame):

    #E: parent (contenedor), controlador (App), turno (int: 1 para defensor, 2 para atacante)
    #S: instancia de la pantalla de login lista para mostrar
    #R: turno debe ser 1 o 2
    def __init__(self, parent, controlador, turno=1):
        super().__init__(parent, bg=controlador.COLORES["fondo"])
        self.controlador = controlador
        self.turno = turno       # 1 = defensor, 2 = atacante
        self._construir()

    #E: (usa el controlador y el turno)
    #S: no retorna; arma los widgets de la pantalla
    #R: ninguna
    def _construir(self):
        c = self.controlador.COLORES

        # Titulo principal (siempre igual).
        tk.Label(self, text="Defensa y Asalto de Base",
                 font=("Trebuchet MS", 22, "bold"),
                 bg=c["fondo"], fg=c["acento"]).pack(pady=(50, 4))

        # Subtitulo dinamico: indica de quien es el turno.
        if self.turno == 1:
            subtitulo = "Inicio de sesión — Jugador 1 (Defensor)"
        else:
            subtitulo = "Inicio de sesión — Jugador 2 (Atacante)"

        tk.Label(self, text=subtitulo,
                 font=("Trebuchet MS", 14),
                 bg=c["fondo"], fg=c["tenue"]).pack(pady=(0, 36))

        # Panel central que agrupa los campos.
        panel = tk.Frame(self, bg=c["panel"], padx=40, pady=30)
        panel.pack()

        # Campo: nombre de usuario.
        tk.Label(panel, text="Usuario", font=("Trebuchet MS", 12),
                 bg=c["panel"], fg=c["texto"]).grid(row=0, column=0,
                 sticky="w", pady=(0, 4))
        self.campo_usuario = tk.Entry(panel, font=("Trebuchet MS", 13),
                                      width=26, bg=c["boton"], fg=c["texto"],
                                      insertbackground=c["texto"],
                                      relief="flat", bd=6)
        self.campo_usuario.grid(row=1, column=0, pady=(0, 18))

        # Campo: contrasena (show="*" oculta los caracteres con asteriscos).
        tk.Label(panel, text="Contraseña", font=("Trebuchet MS", 12),
                 bg=c["panel"], fg=c["texto"]).grid(row=2, column=0,
                 sticky="w", pady=(0, 4))
        self.campo_contrasena = tk.Entry(panel, font=("Trebuchet MS", 13),
                                          width=26, show="*",
                                          bg=c["boton"], fg=c["texto"],
                                          insertbackground=c["texto"],
                                          relief="flat", bd=6)
        self.campo_contrasena.grid(row=3, column=0, pady=(0, 6))
        # Botones de accion.
        frame_botones = tk.Frame(self, bg=c["fondo"])
        frame_botones.pack(pady=24)

        self.controlador.boton(frame_botones, "Iniciar sesión",
                               self._iniciar_sesion).pack(pady=6)
        self.controlador.boton(frame_botones, "Registrarse",
                               self._registrarse).pack(pady=6)
        self.controlador.boton(frame_botones, "Volver",
                               self._volver).pack(pady=6)
    #E: (lee los campos de usuario y contrasena)
    #S: no retorna; inicia sesion si las credenciales son correctas y avanza al siguiente paso
    #R: los campos no pueden estar vacios
    def _iniciar_sesion(self):
        nombre = self.campo_usuario.get().strip()
        contrasena = self.campo_contrasena.get().strip()

        if not nombre or not contrasena:
            messagebox.showwarning("Campos vacios", "Completa usuario y contraseña.")
            return

        jugador = self.controlador.gestor.iniciar_sesion(nombre, contrasena)
        if jugador is None:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
            return

        # Guardamos al jugador en el estado compartido segun su turno.
        if self.turno == 1:
            self.controlador.jugador_defensor = jugador
            messagebox.showinfo("Bienvenido", f"Bienvenido, {jugador.nombre}.\nAhora inicia sesión el Jugador 2.")
            # Reutilizamos la misma pantalla para el segundo jugador.
            self.controlador.mostrar(lambda p, c: PantallaLogin(p, c, turno=2))
        else:
            # Validamos que los dos jugadores sean distintos.
            if jugador.nombre == self.controlador.jugador_defensor.nombre:
                messagebox.showerror("Error", "Los dos jugadores deben ser distintos.")
                return
            self.controlador.jugador_atacante = jugador
            messagebox.showinfo("Bienvenido", f"Bienvenido, {jugador.nombre}.\n¡Listos para jugar!")
            from ventana_facciones import PantallaFacciones
            self.controlador.mostrar(lambda p, c: PantallaFacciones(p, c, turno=1))

    #E: (lee los campos de usuario y contrasena)
    #S: no retorna; registra al jugador si los datos son validos
    #R: los campos no pueden estar vacios; el nombre no puede estar repetido
    def _registrarse(self):
        nombre = self.campo_usuario.get().strip()
        contrasena = self.campo_contrasena.get().strip()
        exito, mensaje = self.controlador.gestor.registrar(nombre, contrasena)
        if exito:
            messagebox.showinfo("Registro exitoso", f"{mensaje}\nYa puedes iniciar sesión.")
        else:
            messagebox.showerror("Error", mensaje)

    #E: (no recibe parametros)
    #S: no retorna; regresa al menu principal y limpia el estado de la partida
    #R: ninguna
    def _volver(self):
        # Limpiamos los jugadores guardados para que no queden datos de una
        # partida anterior si el usuario vuelve al menu y empieza de nuevo.
        self.controlador.jugador_defensor = None
        self.controlador.jugador_atacante = None
        from ventana_menu import PantallaMenu
        self.controlador.mostrar(PantallaMenu)