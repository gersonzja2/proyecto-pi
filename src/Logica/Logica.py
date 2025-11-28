import itertools
import random
from utilities.Constantes import *

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

    @property
    def ganador(self):
        """Determina el ganador del juego basado en la puntuación."""
        if not self.juego_terminado:
            return None
        
        p1_score = self.jugadores[0].puntuacion
        p2_score = self.jugadores[1].puntuacion

        if p1_score > p2_score:
            return self.jugadores[0]
        elif p2_score > p1_score:
            return self.jugadores[1]
        else:
            return None # Empate

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
                    
                    if self._es_linea_valida(p1, p2):
                        self.lineas_dibujadas.add(nueva_linea)
                        self.jugador_actual.lineas.append(nueva_linea)
                        self.tiros_restantes -= 1
                        
                        se_formo_triangulo = self._comprobar_nuevos_triangulos()
                        if se_formo_triangulo:
                            self.tiros_restantes += 1
                        
                        if self.tiros_restantes == 0:
                            self._cambiar_turno()
                    
                    self.puntos_seleccionados = []
                break

    def _hay_movimientos_posibles(self):
        """Comprueba si queda alguna línea válida por trazar en el tablero."""
        for p1, p2 in itertools.combinations(self.puntos, 2):
            if self._es_linea_valida(p1, p2):
                # Encontró al menos un movimiento posible
                return True
        return False

    def _es_linea_valida(self, p1, p2):
        """Verifica si una línea entre p1 y p2 es válida para ser dibujada."""
        # 1. La línea no debe existir previamente.
        if Linea(p1, p2, self.jugador_actual) in self.lineas_dibujadas:
            return False

        # 2. Los puntos deben ser adyacentes (horizontal, vertical o diagonal de 1 paso).
        es_adyacente = abs(p1.fila - p2.fila) <= 1 and abs(p1.col - p2.col) <= 1
        if not es_adyacente or (p1.fila == p2.fila and p1.col == p2.col):
            return False

        # 3. Si es una línea diagonal, la diagonal opuesta no debe existir.
        es_diagonal = abs(p1.fila - p2.fila) == 1 and abs(p1.col - p2.col) == 1
        if es_diagonal:
            # Encontrar los otros dos puntos del cuadrado 2x2.
            p3 = next((p for p in self.puntos if p.fila == p1.fila and p.col == p2.col), None)
            p4 = next((p for p in self.puntos if p.fila == p2.fila and p.col == p1.col), None)

            if p3 and p4:
                # Crear la línea diagonal opuesta y verificar si existe.
                linea_opuesta = Linea(p3, p4, None) # El jugador no importa para la comprobación.
                if linea_opuesta in self.lineas_dibujadas:
                    return False

        return True

    def _comprobar_nuevos_triangulos(self):
        """Comprueba si se han formado nuevos triángulos, actualiza la puntuación y devuelve si se formó alguno."""
        puntos_ganados_en_turno = 0
        for triangulo in self.triangulos_posibles:
            if triangulo.comprobar_completado(self.lineas_dibujadas):
                triangulo.jugador_propietario = self.jugador_actual
                self.triangulos_completados.append(triangulo)
                puntos_ganados_en_turno += 1

        if puntos_ganados_en_turno > 0:
            self.jugador_actual.puntuacion += puntos_ganados_en_turno
            self.triangulos_posibles = [t for t in self.triangulos_posibles if not t.jugador_propietario]
            return True
        return False

    def _cambiar_turno(self):
        if self.juego_terminado:
            return
            
        self.turno_actual_idx = (self.turno_actual_idx + 1) % len(self.jugadores)
        self.lanzar_dado()

    def reiniciar(self):
        """Reinicia el estado del juego a su configuración inicial."""
        self.jugadores = [
            Jugador("Jugador 1", COLOR_JUGADOR_1),
            Jugador("Jugador 2", COLOR_JUGADOR_2)
        ]
        self.turno_actual_idx = 0
        self.lineas_dibujadas = set()
        self.triangulos_posibles = []
        self.triangulos_completados = []
        self.puntos_seleccionados = []
        self.juego_terminado = False
        self._generar_triangulos_posibles()
        self.lanzar_dado()