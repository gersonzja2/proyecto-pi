import itertools
import random
from src.Constantes import *

class Punto:
    """(MODELO) Representa un punto en el tablero con sus coordenadas y posición en la grilla."""
    def __init__(self, x, y, fila, col):
        self.x = x
        self.y = y
        self.fila = fila
        self.col = col
        self.radio = RADIO_PUNTO

    def colisiona_con_coordenadas(self, pos_raton):
        """Verifica si unas coordenadas (x, y) están sobre este punto."""
        dist_sq = (self.x - pos_raton[0])**2 + (self.y - pos_raton[1])**2
        return dist_sq <= self.radio**2

    def __repr__(self):
        return f"Punto({self.fila}, {self.col})"

class Linea:
    """(MODELO) Representa una línea entre dos puntos."""
    def __init__(self, p1, p2, jugador):
        self.puntos = tuple(sorted([p1, p2], key=lambda p: (p.fila, p.col)))
        self.jugador = jugador

    def __eq__(self, other):
        return isinstance(other, Linea) and self.puntos == other.puntos

    def __hash__(self):
        return hash(self.puntos)
    
    def __repr__(self):
        return f"Linea({self.puntos[0]}, {self.puntos[1]})"

class Triangulo:
    """(MODELO) Representa un triángulo formado por 3 puntos."""
    def __init__(self, p1, p2, p3):
        self.puntos = tuple(sorted([p1, p2, p3], key=lambda p: (p.fila, p.col)))
        self.lineas_necesarias = {
            frozenset([self.puntos[0], self.puntos[1]]),
            frozenset([self.puntos[1], self.puntos[2]]),
            frozenset([self.puntos[0], self.puntos[2]])
        }
        self.jugador_propietario = None

    def comprobar_completado(self, lineas_dibujadas_totales):
        """Verifica si este triángulo ha sido completado con el conjunto total de líneas."""
        if self.jugador_propietario:
            return False
        
        lineas_dibujadas_set = {frozenset(linea.puntos) for linea in lineas_dibujadas_totales}
        if self.lineas_necesarias.issubset(lineas_dibujadas_set):
            return True
        return False

    @staticmethod
    def es_colineal(p1, p2, p3):
        """Comprueba si 3 puntos son colineales."""
        area = 0.5 * abs(p1.x * (p2.y - p3.y) + p2.x * (p3.y - p1.y) + p3.x * (p1.y - p2.y))
        return area < 1e-6

class Jugador:
    """(MODELO) Representa a un jugador."""
    def __init__(self, nombre, color):
        self.nombre = nombre
        self.color = color
        self.puntuacion = 0
        self.lineas = []

class ModeloJuego:
    """(MODELO) Clase principal que gestiona el estado y la lógica del juego."""
    def __init__(self):
        self.jugadores = [
            Jugador("Jugador 1", COLOR_JUGADOR_1),
            Jugador("Jugador 2", COLOR_JUGADOR_2)
        ]
        self.turno_actual_idx = 0
        self.puntos = []
        self.lineas_dibujadas = set()
        self.triangulos_posibles = []
        self.triangulos_completados = []
        self.puntos_seleccionados = []
        self.dado_valor = 0
        self.tiros_restantes = 0
        self.juego_terminado = False

        self._inicializar_tablero()
        self._generar_triangulos_posibles()
        self.lanzar_dado()

    @property
    def jugador_actual(self):
        return self.jugadores[self.turno_actual_idx]

    def _inicializar_tablero(self):
        espacio_x = (ANCHO - 2 * MARGEN_X) / (COLUMNAS - 1)
        espacio_y = (ALTO - 2 * MARGEN_Y) / (FILAS - 1)

        for i in range(FILAS):
            for j in range(COLUMNAS):
                x = MARGEN_X + j * espacio_x
                y = MARGEN_Y + i * espacio_y
                self.puntos.append(Punto(int(x), int(y), i, j))

    def _generar_triangulos_posibles(self):
        for p1, p2, p3 in itertools.combinations(self.puntos, 3):
            if not Triangulo.es_colineal(p1, p2, p3):
                self.triangulos_posibles.append(Triangulo(p1, p2, p3))
        print(f"Generados {len(self.triangulos_posibles)} triángulos posibles.")

    def lanzar_dado(self):
        self.dado_valor = random.randint(1, 3)
        self.tiros_restantes = self.dado_valor

    def procesar_clic(self, pos_raton):
        if self.juego_terminado:
            return

        for punto in self.puntos:
            if punto.colisiona_con_coordenadas(pos_raton):
                if punto not in self.puntos_seleccionados:
                    self.puntos_seleccionados.append(punto)

                if len(self.puntos_seleccionados) == 2:
                    p1, p2 = self.puntos_seleccionados
                    nueva_linea = Linea(p1, p2, self.jugador_actual)

                    if nueva_linea not in self.lineas_dibujadas:
                        self.lineas_dibujadas.add(nueva_linea)
                        self.jugador_actual.lineas.append(nueva_linea)
                        self.tiros_restantes -= 1
                        era_ultimo_tiro = self.tiros_restantes == 0
                        
                        puntos_ganados = self._comprobar_nuevos_triangulos()
                        if puntos_ganados > 0:
                            self.jugador_actual.puntuacion += puntos_ganados
                            self.tiros_restantes += puntos_ganados
                        
                        if self.tiros_restantes == 0:
                            self._cambiar_turno()
                    
                    self.puntos_seleccionados = []
                break

    def _comprobar_nuevos_triangulos(self):
        puntos_ganados_en_turno = 0
        for triangulo in self.triangulos_posibles:
            if triangulo.comprobar_completado(self.lineas_dibujadas):
                triangulo.jugador_propietario = self.jugador_actual
                self.triangulos_completados.append(triangulo)
                puntos_ganados_en_turno += 1
        
        self.triangulos_posibles = [t for t in self.triangulos_posibles if not t.jugador_propietario]
        
        if not self.triangulos_posibles:
            self.juego_terminado = True

        return puntos_ganados_en_turno

    def _cambiar_turno(self):
        if self.juego_terminado:
            return
        self.turno_actual_idx = (self.turno_actual_idx + 1) % len(self.jugadores)
        self.lanzar_dado()