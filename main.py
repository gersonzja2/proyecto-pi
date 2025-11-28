import pygame
import sys
from src.Constantes import *
from src.Logica.Logica import ModeloJuego
from src.Interfaz.Interfaz import VistaJuego

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
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                # Pasa las coordenadas del clic al modelo para que procese la lógica.
                self.modelo.procesar_clic(evento.pos)

    def ejecutar(self):
        """Bucle principal del juego."""
        while not self.terminado:
            self.reloj.tick(FPS)
            self._manejar_eventos()
            self.vista.dibujar(self.modelo)
        
        pygame.quit()
        sys.exit()

# --- Punto de Entrada Principal ---
if __name__ == '__main__':
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Unir Puntos y Crear Triángulos")
    controlador = ControladorJuego(pantalla)
    controlador.ejecutar()
