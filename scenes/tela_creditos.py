# scenes/tela_creditos.py

import os
import pygame
from config.settings import (
    TELA_LARGURA_PADRAO, TELA_ALTURA_PADRAO, 
    BRANCO, PRETO, atualizar_tamanhos_globais
)
from config.utils import redimensionar_fonte, redimensionar_imagem
from scenes.base_scene import BaseScene


class TelaCreditos(BaseScene):
    def __init__(self, tela, clock):
        super().__init__(tela, clock)
        pygame.display.set_caption("Marciano vs Caçador - Créditos")
        
        self.pasta_do_script = os.path.dirname(os.path.abspath(__file__))
    
        caminho_fundo = os.path.join(self.pasta_do_script, "..", "assets", "images", "cenario_1.jpg")
        caminho_fundo = os.path.normpath(caminho_fundo)
        try:
            self.imagem_fundo_original = pygame.image.load(caminho_fundo)
        except:
            print("AVISO: Imagem de fundo não encontrada.")
            self.imagem_fundo_original = None
        
        self.imagem_fundo = redimensionar_imagem(
            self.imagem_fundo_original, 
            TELA_LARGURA_PADRAO, 
            TELA_ALTURA_PADRAO
        )
        
        self.init_vagalumes(30)
        
        self.carregar_fontes()
        
        self.informacoes = [
            ("Disciplina:", "Computação Gráfica"),
            ("Professora:", "Priscila Marques Kai"),
            ("Aluna:", "Sofia Monteiro dos Santos Demetrio Gomes")
        ]
    
    def carregar_fontes(self):
   
        caminho_fontes = os.path.join(self.pasta_do_script, "..", "assets", "fonts")
        caminho_fontes = os.path.normpath(caminho_fontes)
        
        tamanho_titulo = redimensionar_fonte(64)
        tamanho_label = redimensionar_fonte(48)
        tamanho_valor = redimensionar_fonte(36)
        
        try:
            caminho_fonte = os.path.join(caminho_fontes, "Aquifer.ttf")
            self.fonte_titulo = pygame.font.Font(caminho_fonte, tamanho_titulo)
            self.fonte_label = pygame.font.Font(caminho_fonte, tamanho_label)
            self.fonte_valor = pygame.font.Font(caminho_fonte, tamanho_valor)
        except:
            try:
                caminho_fonte = os.path.join(caminho_fontes, "Aquifer.otf")
                self.fonte_titulo = pygame.font.Font(caminho_fonte, tamanho_titulo)
                self.fonte_label = pygame.font.Font(caminho_fonte, tamanho_label)
                self.fonte_valor = pygame.font.Font(caminho_fonte, tamanho_valor)
            except:
                print("AVISO: Fonte 'Aquifer' não encontrada. Usando padrão.")
                self.fonte_titulo = pygame.font.Font(None, tamanho_titulo)
                self.fonte_label = pygame.font.Font(None, tamanho_label)
                self.fonte_valor = pygame.font.Font(None, tamanho_valor)
    
    def reload_fonts(self):
        self.carregar_fontes()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.rodando = False
                return "sair"
            
            if event.type == pygame.VIDEORESIZE:
                self.handle_resize(event)
            
            if event.type == pygame.KEYDOWN:
                self.rodando = False
                return "voltar"
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.rodando = False
                return "voltar"
        
        return None
    
    def draw(self):
        from config.settings import TELA_LARGURA, TELA_ALTURA
        
        self.draw_background()
        self.draw_vagalumes()
        
        overlay = pygame.Surface((TELA_LARGURA, TELA_ALTURA))
        overlay.set_alpha(200)
        overlay.fill(PRETO)
        self.tela.blit(overlay, (0, 0))
        
        titulo_texto = self.fonte_titulo.render("CRÉDITOS", True, BRANCO)
        titulo_x = (TELA_LARGURA - titulo_texto.get_width()) // 2
        titulo_y = int(100 * (TELA_ALTURA / 800))
        self.tela.blit(titulo_texto, (titulo_x, titulo_y))
        
        linha_y = titulo_y + titulo_texto.get_height() + 15
        pygame.draw.line(self.tela, BRANCO, (TELA_LARGURA // 4, linha_y), (TELA_LARGURA * 3 // 4, linha_y), 3)
        
        espacamento_inicial = linha_y + int(100 * (TELA_ALTURA / 800))
        espacamento_entre_itens = int(120 * (TELA_ALTURA / 800))
        
        for i, (label, valor) in enumerate(self.informacoes):
            label_render = self.fonte_label.render(label, True, BRANCO)
            label_x = (TELA_LARGURA - label_render.get_width()) // 2
            label_y = espacamento_inicial + (i * espacamento_entre_itens)
            self.tela.blit(label_render, (label_x, label_y))
            
            valor_render = self.fonte_valor.render(valor, True, BRANCO)
            valor_x = (TELA_LARGURA - valor_render.get_width()) // 2
            valor_y = label_y + label_render.get_height() + 20
            self.tela.blit(valor_render, (valor_x, valor_y))
        
        linha_final_y = TELA_ALTURA - int(100 * (TELA_ALTURA / 800))
        pygame.draw.line(self.tela, BRANCO, (TELA_LARGURA // 4, linha_final_y), (TELA_LARGURA * 3 // 4, linha_final_y), 3)
        
        fonte_instrucao = pygame.font.Font(None, redimensionar_fonte(24))
        instrucao_render = fonte_instrucao.render("Clique ou pressione qualquer tecla para voltar", True, BRANCO)
        instrucao_x = (TELA_LARGURA - instrucao_render.get_width()) // 2
        instrucao_y = TELA_ALTURA - int(50 * (TELA_ALTURA / 800))
        self.tela.blit(instrucao_render, (instrucao_x, instrucao_y))
        
        pygame.display.flip()
    
    def run(self):
        """Loop principal da tela de créditos"""
        while self.rodando:
            acao = self.handle_events()
            if acao:
                return acao
            self.update_vagalumes()
            self.draw()
            self.clock.tick(60)
        return "voltar"