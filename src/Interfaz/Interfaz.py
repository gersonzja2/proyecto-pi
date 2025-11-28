import pygame
from utilities.Constantes import *

class VistaJuego:
    """(VISTA) Se encarga de dibujar el estado del juego en la pantalla."""
    def __init__(self, pantalla):
        self.pantalla = pantalla
        self.fuente = pygame.font.Font(None, 36)
        self.fuente_grande = pygame.font.Font(None, 50)
        self.rect_boton_terminar = pygame.Rect(ANCHO / 2 - 100, 20, 200, 40)

    def dibujar(self, modelo):
        """Dibuja todos los elementos del juego basándose en el modelo."""
        self._dibujar_fondo()
        self._dibujar_triangulos_relleno(modelo)
        self._dibujar_lineas(modelo)
        self._dibujar_puntos(modelo)
        self._dibujar_ui(modelo)

        pygame.display.flip()

    def _dibujar_fondo(self):
        self.pantalla.fill(COLOR_FONDO)

    def _dibujar_triangulos_relleno(self, modelo):
        for triangulo in modelo.triangulos_completados:
            if triangulo.jugador_propietario:
                color_relleno = triangulo.jugador_propietario.color[:3] + (100,)
                superficie_triangulo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
                pygame.draw.polygon(superficie_triangulo, color_relleno, [(p.x, p.y) for p in triangulo.puntos])
                self.pantalla.blit(superficie_triangulo, (0, 0))

    def _dibujar_lineas(self, modelo):
        for linea in modelo.lineas_dibujadas:
            pygame.draw.line(self.pantalla, linea.jugador.color, (linea.puntos[0].x, linea.puntos[0].y), (linea.puntos[1].x, linea.puntos[1].y), 4)

    def _dibujar_puntos(self, modelo):
        for punto in modelo.puntos:
            pygame.draw.circle(self.pantalla, COLOR_PUNTO, (punto.x, punto.y), punto.radio)
            pygame.draw.circle(self.pantalla, (0, 0, 0), (punto.x, punto.y), punto.radio, 2)
            if punto in modelo.puntos_seleccionados:
                pygame.draw.circle(self.pantalla, (255, 255, 0), (punto.x, punto.y), punto.radio + 2, 3)

    def _dibujar_ui(self, modelo):
        # Puntuación Jugador 1
        texto_j1 = self.fuente.render(f"{modelo.jugadores[0].nombre}: {modelo.jugadores[0].puntuacion}", True, modelo.jugadores[0].color)
        self.pantalla.blit(texto_j1, (20, 20))

        # Puntuación Jugador 2
        texto_j2 = self.fuente.render(f"{modelo.jugadores[1].nombre}: {modelo.jugadores[1].puntuacion}", True, modelo.jugadores[1].color)
        rect_j2 = texto_j2.get_rect(topright=(ANCHO - 20, 20))
        self.pantalla.blit(texto_j2, rect_j2)

        # Indicador de turno
        jugador_actual = modelo.jugador_actual
        texto_turno = self.fuente.render(f"Turno de {jugador_actual.nombre}", True, COLOR_TEXTO)
        rect_turno = texto_turno.get_rect(midbottom=(ANCHO / 2, ALTO - 20))
        self.pantalla.blit(texto_turno, rect_turno)

        # Indicador del dado y tiros restantes
        texto_dado = self.fuente.render(f"Dado: {modelo.dado_valor} | Tiros restantes: {modelo.tiros_restantes}", True, jugador_actual.color)
        rect_dado = texto_dado.get_rect(midbottom=(ANCHO / 2, ALTO - 50))
        self.pantalla.blit(texto_dado, rect_dado)
        
        # Botón de terminar partida
        pygame.draw.rect(self.pantalla, (200, 50, 50), self.rect_boton_terminar)
        pygame.draw.rect(self.pantalla, (255, 255, 255), self.rect_boton_terminar, 2)
        texto_boton = self.fuente.render("Terminar Partida", True, (255, 255, 255))
        rect_texto_boton = texto_boton.get_rect(center=self.rect_boton_terminar.center)
        self.pantalla.blit(texto_boton, rect_texto_boton)

    def dibujar_fin_juego(self, ganador):
        """Dibuja la pantalla de fin de juego."""
        self.pantalla.fill((0, 0, 0)) # NEGRO
        if ganador:
            msg = f"¡Gana {ganador.nombre}!"
            color = ganador.color
        else:
            msg = "¡Es un empate!"
            color = COLOR_TEXTO
        texto_fin = self.fuente_grande.render("Juego Terminado", True, (255, 255, 255)) # BLANCO
        rect_fin = texto_fin.get_rect(center=(ANCHO / 2, ALTO / 2 - 50))
        texto_resultado = self.fuente.render(msg, True, color)
        rect_resultado = texto_resultado.get_rect(center=(ANCHO / 2, ALTO / 2 + 20))
        self.pantalla.blit(texto_fin, rect_fin)
        self.pantalla.blit(texto_resultado, rect_resultado)