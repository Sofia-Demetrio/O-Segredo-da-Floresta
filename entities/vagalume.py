# entities/vagalume.py

import random
import math
import pygame
from config.settings import TELA_LARGURA, TELA_ALTURA, FATOR_ESCALA_X, FATOR_ESCALA_Y


class Vagalume:
    def __init__(self):
        self.x = random.randint(0, TELA_LARGURA)
        self.y = random.randint(0, TELA_ALTURA)
        
        self.raio_base = random.randint(2, 4)
        self.raio = int(self.raio_base * min(FATOR_ESCALA_X, FATOR_ESCALA_Y))
        
        self.cor_base = (200, 255, 100)
        
        self.alfa = 0
        self.velocidade_piscar = random.uniform(2.0, 5.0)
        self.fase = random.uniform(0, 6.28)
        
    def update(self, tempo_total):

        oscilacao = math.sin(tempo_total * self.velocidade_piscar + self.fase)
        self.alfa = int(max(0, oscilacao * 150 + 105))
        
        if self.alfa < 5 and random.random() < 0.05:
            self.x = random.randint(0, TELA_LARGURA)
            self.y = random.randint(0, TELA_ALTURA)
            
    def draw(self, surface):

        if self.alfa > 10:
            surf_vagalume = pygame.Surface((self.raio * 3, self.raio * 3), pygame.SRCALPHA)
            cor_com_alfa = self.cor_base + (self.alfa,)
            pygame.draw.circle(surf_vagalume, cor_com_alfa, (self.raio, self.raio), self.raio)
            glow_com_alfa = (255, 255, 150) + (int(self.alfa * 0.3),)
            pygame.draw.circle(surf_vagalume, glow_com_alfa, (self.raio, self.raio), self.raio * 2)
            surface.blit(surf_vagalume, (self.x - self.raio, self.y - self.raio))
    
    def redimensionar(self):

        self.raio = int(self.raio_base * min(FATOR_ESCALA_X, FATOR_ESCALA_Y))