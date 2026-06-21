# gestor_jugadores.py
# Administra a los jugadores: registro, login, guardado/lectura en JSON
# y los rankings (top defensores / top atacantes).

import json
import os
from jugador import Jugador


class GestorJugadores:

    #E: ruta_archivo (str) -> archivo JSON donde se guardan los jugadores
    #S: instancia lista, con los jugadores ya cargados en memoria
    #R: ninguna
    def __init__(self, ruta_archivo="jugadores.json"):
        self.ruta_archivo = ruta_archivo
        self.jugadores = {}      # {nombre: objeto Jugador}
        self.cargar()

    #E: (usa self.ruta_archivo)
    #S: no retorna; llena self.jugadores con lo que haya en el archivo
    #R: si el archivo no existe o esta danado, arranca con diccionario vacio
    def cargar(self):
        # Si aun no existe el archivo, no hay nada que cargar.
        if not os.path.exists(self.ruta_archivo):
            self.jugadores = {}
            return
        try:
            with open(self.ruta_archivo, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
            # Cada entrada del JSON se vuelve un objeto Jugador.
            self.jugadores = {n: Jugador.desde_diccionario(n, info)
                              for n, info in datos.items()}
        except (json.JSONDecodeError, KeyError):
            # Archivo corrupto: evitamos que el programa se caiga.
            self.jugadores = {}

    #E: (usa self.jugadores)
    #S: no retorna; escribe todos los jugadores en el archivo JSON
    #R: ninguna
    def guardar(self):
        # Convertimos cada Jugador a diccionario antes de escribir.
        datos = {n: j.a_diccionario() for n, j in self.jugadores.items()}
        with open(self.ruta_archivo, "w", encoding="utf-8") as archivo:
            # indent=4 -> legible; ensure_ascii=False -> conserva acentos.
            json.dump(datos, archivo, indent=4, ensure_ascii=False)

    #E: nombre (str)
    #S: True si el jugador ya existe, False si no
    #R: ninguna
    def existe(self, nombre):
        return nombre in self.jugadores

    #E: nombre (str), contrasena (str)
    #S: tupla (exito: bool, mensaje: str)
    #R: nombre y contrasena no pueden estar vacios; el nombre no puede repetirse
    def registrar(self, nombre, contrasena):
        # strip() evita registros con solo espacios.
        if not nombre.strip() or not contrasena.strip():
            return (False, "El usuario y la contrasena no pueden estar vacios.")
        if self.existe(nombre):
            return (False, "Ese nombre de usuario ya esta registrado.")
        # Creamos, agregamos y persistimos de una vez.
        self.jugadores[nombre] = Jugador(nombre, contrasena)
        self.guardar()
        return (True, "Registro exitoso.")

    #E: nombre (str), contrasena (str)
    #S: el objeto Jugador si las credenciales son correctas, o None si no
    #R: ninguna
    def iniciar_sesion(self, nombre, contrasena):
        jugador = self.jugadores.get(nombre)
        # Solo lo devolvemos si existe y la contrasena coincide.
        if jugador is not None and jugador.contrasena == contrasena:
            return jugador
        return None

    #E: nombre (str), rol (str) -> "defensor" o "atacante"
    #S: True si se actualizo la victoria; False si el jugador no existe o el rol es invalido
    #R: rol debe ser exactamente "defensor" o "atacante"
    def actualizar_victoria(self, nombre, rol):
        jugador = self.jugadores.get(nombre)
        if jugador is None:
            return False
        # Sumamos al contador segun el rol con el que gano.
        if rol == "defensor":
            jugador.victorias_defensor += 1
        elif rol == "atacante":
            jugador.victorias_atacante += 1
        else:
            return False
        self.guardar()
        return True

    #E: cantidad (int) -> cuantos mostrar (5 por defecto)
    #S: lista de Jugador ordenada de mayor a menor por victorias como defensor
    #R: ninguna
    def top_defensores(self, cantidad=5):
        # sorted con reverse=True -> de mas a menos victorias.
        ordenados = sorted(self.jugadores.values(),
                           key=lambda j: j.victorias_defensor, reverse=True)
        return ordenados[:cantidad]

    #E: cantidad (int) -> cuantos mostrar (5 por defecto)
    #S: lista de Jugador ordenada de mayor a menor por victorias como atacante
    #R: ninguna
    def top_atacantes(self, cantidad=5):
        ordenados = sorted(self.jugadores.values(),
                           key=lambda j: j.victorias_atacante, reverse=True)
        return ordenados[:cantidad]