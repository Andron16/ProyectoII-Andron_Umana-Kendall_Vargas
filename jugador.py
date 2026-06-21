# jugador.py
# Representa a un jugador: sus credenciales y su historial de victorias.

class Jugador:

    #E: nombre (str), contrasena (str), victorias_defensor (int), victorias_atacante (int)
    #S: instancia de Jugador con sus atributos inicializados
    #R: nombre y contrasena no deberian estar vacios (se valida en GestorJugadores)
    def __init__(self, nombre, contrasena, victorias_defensor=0, victorias_atacante=0):
        self.nombre = nombre
        self.contrasena = contrasena
        self.victorias_defensor = victorias_defensor   # ganadas como defensor
        self.victorias_atacante = victorias_atacante    # ganadas como atacante

    #E: (usa los atributos de la instancia)
    #S: diccionario con los datos del jugador, listo para guardar en JSON
    #R: ninguna
    def a_diccionario(self):
        # El nombre no se guarda aqui: es la clave del diccionario en el archivo.
        return {
            "contrasena": self.contrasena,
            "victorias_defensor": self.victorias_defensor,
            "victorias_atacante": self.victorias_atacante
        }

    #E: nombre (str), datos (dict con contrasena y victorias)
    #S: nueva instancia de Jugador construida desde el diccionario
    #R: 'datos' debe contener al menos la clave "contrasena"
    @classmethod
    def desde_diccionario(cls, nombre, datos):
        # .get(..., 0) evita errores si a un jugador viejo le faltara algun contador.
        return cls(
            nombre,
            datos["contrasena"],
            datos.get("victorias_defensor", 0),
            datos.get("victorias_atacante", 0)
        )

    #E: (usa los atributos de la instancia)
    #S: texto legible con nombre y victorias, util para depurar
    #R: ninguna
    def __str__(self):
        return f"{self.nombre} (Def: {self.victorias_defensor} | Atk: {self.victorias_atacante})"