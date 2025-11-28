import pygame

# --- Configuración y Constantes ---
pygame.init()
pygame.mixer.init()
    
pygame.mixer.music.load('assets/megalovia.mp3')
pygame.mixer.music.play(-1) # -1 para reproducir en bucle infinito