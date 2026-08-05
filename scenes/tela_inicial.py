# scenes/tela_inicial.py

import os
import pygame
from config.settings import (
    TELA_LARGURA_PADRAO, TELA_ALTURA_PADRAO, 
    BRANCO, VERDE, PRETO, atualizar_tamanhos_globais
)
from config.utils import redimensionar_fonte, redimensionar_posicao, redimensionar_imagem
from scenes.base_scene import BaseScene


class TelaInicial(BaseScene):
    def __init__(self, tela, clock):
        super().__init__(tela, clock)
        pygame.display.set_caption("Marciano vs Caçador")
        
        self.pasta_do_script = os.path.dirname(os.path.abspath(__file__))
        self.acao_selecionada = None
        
        
        caminho_imagem = os.path.join(self.pasta_do_script, "..", "assets", "images", "cenario_1.jpg")
        caminho_imagem = os.path.normpath(caminho_imagem)
        try:
            self.imagem_fundo_original = pygame.image.load(caminho_imagem)
        except:
            print("AVISO: Imagem cenario_1.jpg não encontrada.")
            self.imagem_fundo_original = None
        
        self.imagem_fundo = redimensionar_imagem(
            self.imagem_fundo_original, 
            TELA_LARGURA_PADRAO, 
            TELA_ALTURA_PADRAO
        )
        
        self.init_vagalumes(30)
        
        caminho_musica = os.path.join(self.pasta_do_script, "..", "assets", "sounds", 
                                      "2019-05-01_-_Undercover_Spy_Agent_-_David_Fesliyan.mp3")
        caminho_musica = os.path.normpath(caminho_musica)
        if not pygame.mixer.music.get_busy():
            try:
                pygame.mixer.music.load(caminho_musica)
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(0.5)
            except:
                print("AVISO: Arquivo de áudio não encontrado.")
        
        self.carregar_fontes()
    
    def carregar_fontes(self):
        caminho_fontes = os.path.join(self.pasta_do_script, "..", "assets", "fonts")
        caminho_fontes = os.path.normpath(caminho_fontes)
        
        tamanho_titulo = redimensionar_fonte(72)
        tamanho_menu = redimensionar_fonte(48)
        
        fonte_carregada = False
        for extensao in [".ttf", ".otf", ""]:
            caminho_fonte = os.path.join(caminho_fontes, f"Roman_New_Times{extensao}")
            try:
                self.fonte_titulo = pygame.font.Font(caminho_fonte, tamanho_titulo)
                self.fonte_menu = pygame.font.Font(caminho_fonte, tamanho_menu)
                fonte_carregada = True
                break
            except:
                continue
        
        if not fonte_carregada:
            print("AVISO: Fonte 'Roman_New_Times' não encontrada. Usando padrão.")
            self.fonte_titulo = pygame.font.Font(None, tamanho_titulo)
            self.fonte_menu = pygame.font.Font(None, tamanho_menu)
        
        self.atualizar_textos_menu()
    
    def atualizar_textos_menu(self):
        
        from config.settings import TELA_LARGURA, TELA_ALTURA
        
        titulo_renderizado = self.fonte_titulo.render("MARCIANO VS CAÇADOR", True, BRANCO)
        titulo_x = (TELA_LARGURA - titulo_renderizado.get_width()) // 2
        self.titulo_posicao = (titulo_x, redimensionar_posicao(0, 280)[1])
        self.titulo_renderizado = titulo_renderizado
        
        texto_iniciar = self.fonte_menu.render("INICIAR", True, BRANCO)
        texto_creditos = self.fonte_menu.render("CRÉDITOS", True, BRANCO)
        
        iniciar_x = (TELA_LARGURA - texto_iniciar.get_width()) // 2
        creditos_x = (TELA_LARGURA - texto_creditos.get_width()) // 2
        
        self.itens_menu = [
            {"texto": "INICIAR", "texto_renderizado": texto_iniciar, 
             "rect": pygame.Rect(iniciar_x, redimensionar_posicao(0, 400)[1], 
                                texto_iniciar.get_width(), texto_iniciar.get_height()), 
             "acao": "iniciar"},
            {"texto": "CRÉDITOS", "texto_renderizado": texto_creditos, 
             "rect": pygame.Rect(creditos_x, redimensionar_posicao(0, 480)[1], 
                                texto_creditos.get_width(), texto_creditos.get_height()), 
             "acao": "creditos"}
        ]
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.rodando = False
                self.acao_selecionada = "sair"
                return
            if event.type == pygame.VIDEORESIZE:
                self.handle_resize(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    for item in self.itens_menu:
                        if item["rect"].collidepoint(mouse_pos):
                            self.acao_selecionada = item["acao"]
                            self.rodando = False
                            return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.rodando = False
                    self.acao_selecionada = "sair"
                    return
    
    def reload_fonts(self):
        self.carregar_fontes()
    
    def draw(self):
        from config.settings import TELA_LARGURA, TELA_ALTURA
        self.draw_background()
        self.draw_vagalumes()
        overlay = pygame.Surface((TELA_LARGURA, TELA_ALTURA))
        overlay.set_alpha(160)
        overlay.fill(PRETO)
        self.tela.blit(overlay, (0, 0))
        self.tela.blit(self.titulo_renderizado, self.titulo_posicao)
        mouse_pos = pygame.mouse.get_pos()
        for item in self.itens_menu:
            if item["rect"].collidepoint(mouse_pos):
                texto_temp = self.fonte_menu.render(item["texto"], True, VERDE)
            else:
                texto_temp = item["texto_renderizado"]
            self.tela.blit(texto_temp, (item["rect"].x, item["rect"].y))
        pygame.display.flip()
    
    def run(self):
        while self.rodando:
            self.handle_events()
            self.update_vagalumes()
            self.draw()
            self.clock.tick(60)
        return self.acao_selecionada