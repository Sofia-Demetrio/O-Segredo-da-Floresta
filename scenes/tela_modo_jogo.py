# scenes/tela_modo_jogo.py


import os
import pygame
from config.settings import (
    TELA_LARGURA_PADRAO, TELA_ALTURA_PADRAO, 
    BRANCO, VERDE, PRETO, AMARELO_HISTORIA, VERDE_CLARO,
    atualizar_tamanhos_globais
)
from config.utils import redimensionar_fonte, redimensionar_posicao, redimensionar_imagem
from scenes.base_scene import BaseScene


class TelaModoJogo(BaseScene):
    def __init__(self, tela, clock):
        super().__init__(tela, clock)
        pygame.display.set_caption("Marciano vs Caçador - Escolha o Modo de Jogo")
        
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
        
        self.modo_escolhido = None
        self.opcao_selecionada = None
    
    def carregar_fontes(self):
        caminho_fontes = os.path.join(self.pasta_do_script, "..", "assets", "fonts")
        caminho_fontes = os.path.normpath(caminho_fontes)
        
        tamanho_titulo = redimensionar_fonte(72)
        tamanho_menu = redimensionar_fonte(48)
        tamanho_regras = redimensionar_fonte(28)
        
        fonte_carregada = False
        for extensao in [".ttf", ".otf", ""]:
            caminho_fonte = os.path.join(caminho_fontes, f"Roman_New_Times{extensao}")
            try:
                self.fonte_titulo = pygame.font.Font(caminho_fonte, tamanho_titulo)
                self.fonte_menu = pygame.font.Font(caminho_fonte, tamanho_menu)
                self.fonte_regras = pygame.font.Font(caminho_fonte, tamanho_regras)
                fonte_carregada = True
                break
            except:
                continue
        
        if not fonte_carregada:
            print("AVISO: Fonte 'Roman_New_Times' não encontrada. Usando padrão.")
            self.fonte_titulo = pygame.font.Font(None, tamanho_titulo)
            self.fonte_menu = pygame.font.Font(None, tamanho_menu)
            self.fonte_regras = pygame.font.Font(None, tamanho_regras)
        
        self.atualizar_textos_menu()
    
    def atualizar_textos_menu(self):
        from config.settings import TELA_LARGURA, TELA_ALTURA
        
        titulo_renderizado = self.fonte_titulo.render("ESCOLHA O MODO DE JOGO", True, BRANCO)
        titulo_x = (TELA_LARGURA - titulo_renderizado.get_width()) // 2
        self.titulo_posicao = (titulo_x, redimensionar_posicao(0, 280)[1])
        self.titulo_renderizado = titulo_renderizado
        
        texto_single = self.fonte_menu.render("1 JOGADOR", True, BRANCO)
        texto_multi = self.fonte_menu.render("2 JOGADORES", True, BRANCO)
        
        single_x = (TELA_LARGURA - texto_single.get_width()) // 2
        multi_x = (TELA_LARGURA - texto_multi.get_width()) // 2
        
        self.itens_menu = [
            {
                "texto": "1 JOGADOR", 
                "texto_renderizado": texto_single, 
                "rect": pygame.Rect(single_x, redimensionar_posicao(0, 380)[1], 
                                   texto_single.get_width(), texto_single.get_height()), 
                "modo": "single",
                "regras": [
                    "- VOCÊ CONTROLARÁ O CAÇADOR",
                    "- O MARCIANO SERÁ CONTROLADO PELO COMPUTADOR",
                    "- O PC ESCOLHERÁ ALEATORIAMENTE UMA DAS FLORESTAS",
                    "- VOCÊ PRECISA ENCONTRAR O MARCIANO ANTES QUE ELE ESCAPE!"
                ]
            },
            {
                "texto": "2 JOGADORES", 
                "texto_renderizado": texto_multi, 
                "rect": pygame.Rect(multi_x, redimensionar_posicao(0, 460)[1], 
                                   texto_multi.get_width(), texto_multi.get_height()), 
                "modo": "multi",
                "regras": [
                    "- JOGADOR 1 CONTROLARÁ O CAÇADOR",
                    "- JOGADOR 2 CONTROLARÁ O MARCIANO",
                    "- O MARCIANO ESCOLHE UMA FLORESTA PARA SE ESCONDER",
                    "- O CAÇADOR PRECISA ENCONTRÁ-LO!",
                    "- CADA JOGADOR TEM HABILIDADES ESPECIAIS!"
                ]
            }
        ]
    
    def handle_events(self):
        from config.settings import TELA_LARGURA, TELA_ALTURA
        
        mouse_pos = pygame.mouse.get_pos()
        self.opcao_selecionada = None
        
        for item in self.itens_menu:
            if item["rect"].collidepoint(mouse_pos):
                self.opcao_selecionada = item
                break
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.rodando = False
                self.modo_escolhido = "sair"
            
            if event.type == pygame.VIDEORESIZE:
                self.handle_resize(event)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for item in self.itens_menu:
                        if item["rect"].collidepoint(mouse_pos):
                            self.modo_escolhido = item["modo"]
                            self.rodando = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.rodando = False
                    self.modo_escolhido = "voltar"
        
        return None
    
    def draw_caixa_regras_lado(self, regras):
        from config.settings import TELA_LARGURA, TELA_ALTURA, FATOR_ESCALA_X, FATOR_ESCALA_Y
        
        largura_maxima = int(550 * FATOR_ESCALA_X)
        altura_linha = int(50 * FATOR_ESCALA_Y)
        margem = int(20 * min(FATOR_ESCALA_X, FATOR_ESCALA_Y))
        
        linhas = []
        for regra in regras:
            if self.fonte_regras.size(regra)[0] > largura_maxima - 60:
                palavras = regra.split(' ')
                linha_atual = ""
                for palavra in palavras:
                    teste = linha_atual + palavra + " "
                    if self.fonte_regras.size(teste)[0] < largura_maxima - 60:
                        linha_atual = teste
                    else:
                        if linha_atual:
                            linhas.append(linha_atual.strip())
                        linha_atual = palavra + " "
                if linha_atual:
                    linhas.append(linha_atual.strip())
            else:
                linhas.append(regra)
        
        altura_caixa = len(linhas) * altura_linha + margem * 2
        caixa_x = TELA_LARGURA - largura_maxima - int(50 * FATOR_ESCALA_X)
        caixa_y = int(360 * FATOR_ESCALA_Y)
        
        caixa_surface = pygame.Surface((int(largura_maxima), int(altura_caixa)), pygame.SRCALPHA)
        caixa_surface.fill((0, 0, 0, 220))
        self.tela.blit(caixa_surface, (caixa_x, caixa_y))
        pygame.draw.rect(self.tela, AMARELO_HISTORIA, (caixa_x, caixa_y, largura_maxima, altura_caixa), 3, border_radius=10)
        
        titulo_regras = self.fonte_regras.render("REGRAS DO MODO", True, VERDE_CLARO)
        titulo_x = caixa_x + (largura_maxima - titulo_regras.get_width()) // 2
        titulo_y = caixa_y + 10
        self.tela.blit(titulo_regras, (titulo_x, titulo_y))
        
        # Linhas de regras
        for i, linha in enumerate(linhas):
            texto_render = self.fonte_regras.render(linha, True, AMARELO_HISTORIA)
            texto_x = caixa_x + 25
            texto_y = caixa_y + margem + 40 + (i * altura_linha)
            self.tela.blit(texto_render, (texto_x, texto_y))
    
    def reload_fonts(self):
        """Recarrega fontes após redimensionamento"""
        self.carregar_fontes()
    
    def draw(self):
        """Desenha a tela de seleção de modo"""
        from config.settings import TELA_LARGURA, TELA_ALTURA, FATOR_ESCALA_X, FATOR_ESCALA_Y
        
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
        
        if self.opcao_selecionada:
            self.draw_caixa_regras_lado(self.opcao_selecionada["regras"])
        
        fonte_pequena = pygame.font.Font(None, redimensionar_fonte(24))
        instrucao_render = fonte_pequena.render("Clique em uma opção para selecionar | ESC para voltar", True, BRANCO)
        instrucao_x = (TELA_LARGURA - instrucao_render.get_width()) // 2
        instrucao_y = TELA_ALTURA - int(50 * FATOR_ESCALA_Y)
        self.tela.blit(instrucao_render, (instrucao_x, instrucao_y))
        
        pygame.display.flip()
    
    def run(self):
        while self.rodando:
            self.handle_events()
            self.update_vagalumes()
            self.draw()
            self.clock.tick(60)
        return self.modo_escolhido