import pygame
import sys
from utilities.Constantes import *
from src.Logica.Logica import ModeloJuego, Jugador
from src.Interfaz.Interfaz import VistaJuego
from utilities.SongBank import *

class ControladorJuego:
    """(CONTROLADOR) Gestiona el bucle principal y los eventos de usuario."""
    def __init__(self, pantalla):
        self.pantalla = pantalla
        self.reloj = pygame.time.Clock()
        self.modelo = ModeloJuego()
        self.vista = VistaJuego(pantalla)
        self.terminado = False

    def _manejar_eventos(self):
        """Gestiona las entradas del usuario."""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.terminado = True
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                # Comprobar si se hizo clic en el botón de terminar
                if self.vista.rect_boton_terminar.collidepoint(evento.pos):
                    self.modelo.juego_terminado = True
                else:
                    # Si no, procesar clic en el tablero
                    self.modelo.procesar_clic(evento.pos)
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    self.modelo.reiniciar()

    def _mostrar_pantalla_final(self):
        """Muestra la pantalla de fin de juego y espera a que el usuario cierre."""
        ganador = self.modelo.ganador
        self.vista.dibujar_fin_juego(ganador)
        pygame.display.flip()

        esperando_salida = True
        while esperando_salida:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    esperando_salida = False
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_r: # Reiniciar la partida
                        self.modelo.reiniciar()
                        esperando_salida = False
                        return # Salir del método para evitar que se marque como terminado
                    elif evento.key == pygame.K_ESCAPE:
                        esperando_salida = False
            self.reloj.tick(FPS)
        
        self.terminado = True

    def ejecutar(self):
        """Bucle principal del juego."""
        while not self.terminado:
            self.reloj.tick(FPS)

            if self.modelo.juego_terminado:
                self._mostrar_pantalla_final()
            else:
                self._manejar_eventos()
                self.vista.dibujar(self.modelo)
            
            if self.terminado:
                break
        
        pygame.quit()
        sys.exit()

# --- Punto de Entrada Principal ---
if __name__ == '__main__':
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Unir Puntos y Crear Triángulos")
    controlador = ControladorJuego(pantalla)
    controlador.ejecutar()
