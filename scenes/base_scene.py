# scenes/base_scene.py

import pygame
from config.settings import FPS, atualizar_tamanhos_globais
from config.utils import redimensionar_imagem
from entities.vagalume import Vagalume


class BaseScene:
    #Classe base para todas as cenas/telas do jogo
    
    def __init__(self, tela, clock):
        self.tela = tela
        self.clock = clock
        self.rodando = True
        
        # Sistema de vagalumes
        self.lista_vagalumes = []
        self.quantidade_vagalumes = 30
        
        # Imagem de fundo
        self.imagem_fundo_original = None
        self.imagem_fundo = None
        
    def init_vagalumes(self, quantidade=30):
        self.quantidade_vagalumes = quantidade
        self.lista_vagalumes = []
        for _ in range(quantidade):
            self.lista_vagalumes.append(Vagalume())
    
    def update_vagalumes(self):
        tempo_segundos = pygame.time.get_ticks() / 1000.0
        for vagalume in self.lista_vagalumes:
            vagalume.update(tempo_segundos)
    
    def draw_background(self):
        if self.imagem_fundo:
            self.tela.blit(self.imagem_fundo, (0, 0))
        else:
            from config.settings import PRETO
            self.tela.fill(PRETO)
    
    def draw_vagalumes(self):

        for vagalume in self.lista_vagalumes:
            vagalume.draw(self.tela)
    
    def handle_events(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.rodando = False
                return "sair"
            
            if event.type == pygame.VIDEORESIZE:
                self.handle_resize(event)
        
        return None
    
    def handle_resize(self, event):
        nova_largura = max(event.w, 800)
        nova_altura = max(event.h, 600)
        self.tela = pygame.display.set_mode((nova_largura, nova_altura), pygame.RESIZABLE)
        atualizar_tamanhos_globais(nova_largura, nova_altura)
        self.resize_resources()
    
    def resize_resources(self):
        if self.imagem_fundo_original:
            from config.settings import TELA_LARGURA_PADRAO, TELA_ALTURA_PADRAO
            self.imagem_fundo = redimensionar_imagem(
                self.imagem_fundo_original, 
                TELA_LARGURA_PADRAO, 
                TELA_ALTURA_PADRAO
            )
        
        for vagalume in self.lista_vagalumes:
            vagalume.redimensionar()
        
        self.reload_fonts()
    
    def reload_fonts(self):
        #Recarrega fontes - sobrescrever nas subclasses
        pass
    
    def run(self):
        #Loop principal - implementar na subclasse
        raise NotImplementedError("Subclasse deve implementar run()")