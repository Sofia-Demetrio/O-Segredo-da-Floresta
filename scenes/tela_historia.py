# scenes/tela_historia.py

import os
import pygame
from config.settings import (
    TELA_LARGURA_PADRAO, TELA_ALTURA_PADRAO, 
    atualizar_tamanhos_globais
)
from config.utils import redimensionar_fonte, redimensionar_imagem
from scenes.base_scene import BaseScene


BRANCO = (245, 230, 163)      
PRETO = (17, 36, 41)          
VERDE = (112, 163, 162)       
AMARELO_HISTORIA = (245, 230, 163) 


class TelaHistoria(BaseScene):
    def __init__(self, tela, clock):
        super().__init__(tela, clock)
        pygame.display.set_caption("Marciano vs Caçador - História")
        
        self.pasta_do_script = os.path.dirname(os.path.abspath(__file__))
        
        self.som_digitacao = None
        self.som_tocando = False
        caminho_som = os.path.join(self.pasta_do_script, "..", "assets", "sounds", "magiaz-teclado-371741.mp3")
        caminho_som = os.path.normpath(caminho_som)
        try:
            self.som_digitacao = pygame.mixer.Sound(caminho_som)
            self.som_digitacao.set_volume(0.25)
        except:
            print("AVISO: Arquivo de som não encontrado.")
        
        caminho_fundo = os.path.join(self.pasta_do_script, "..", "assets", "images", "investigacao.png")
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
        
        self.imagem_xerife_original = None
        self.imagem_xerife = None
        self.xerife_rect = None
        caminho_xerife = os.path.join(self.pasta_do_script, "..", "assets", "images", "Sheriff.png")
        caminho_xerife = os.path.normpath(caminho_xerife)
        try:
            self.imagem_xerife_original = pygame.image.load(caminho_xerife)
        except:
            print("AVISO: Imagem do investigador não encontrada.")
        
        
        self.carregar_fontes()
        
        self.espaco_imagem_base = 170
        self.atualizar_balao()
        
        self.cenas = [
            "Em 2004, as autoridades confirmaram o desaparecimento de um grupo de pesquisadores "
            "nas proximidades da Reserva Florestal de Arandu. Entre eles havia historiadores, "
            "antropólogos e arqueólogos que investigavam a origem das lendas folclóricas da região "
            "e a forma como essas figuras influenciavam a vida da população local.",
            
            "Helena liderava a expedição. Antropóloga respeitada, ela foi vista pela última vez "
            "entrando na mata durante a madrugada. Nenhum vestígio de seu paradeiro foi encontrado, "
            "e nenhuma testemunha conseguiu esclarecer o que aconteceu. Após quinze dias de buscas "
            "sem resultados, as autoridades encerraram oficialmente as operações.",
            
            "Hoje fazem cinco anos desde aquele dia...Cinco anos desde que Helena desapareceu...\n\n"
            "Cinco anos desde que perdi minha irmã...",
            
            "Com o tempo, as buscas acabaram, as pessoas seguiram em frente e as esperanças "
            "desapareceram. Eu também estava prestes a desistir...\n\n"
            "Até encontrar os diários que ela deixou para trás."
        ]
        
        self.cena_atual = 0
        self.total_cenas = len(self.cenas)
        self.texto_atual = self.cenas[self.cena_atual]
        self.indice_caractere = 0
        self.velocidade_caractere = 35
        self.tempo_ultimo_caractere = pygame.time.get_ticks()
        self.texto_completo_gerado = False
        self.linhas_para_desenhar = []
        
        self.texto_pular = "PULAR"
        self.botao_pular_rect = None
        self.botao_pular_hover = False
    
    def carregar_fontes(self):
        caminho_fontes = os.path.join(self.pasta_do_script, "..", "assets", "fonts")
        caminho_fontes = os.path.normpath(caminho_fontes)
        
        tamanho_historia = redimensionar_fonte(32)
        tamanho_botao = redimensionar_fonte(36)
        
        try:
            caminho_fonte = os.path.join(caminho_fontes, "Aquifer.ttf")
            self.fonte_historia = pygame.font.Font(caminho_fonte, tamanho_historia)
            self.fonte_botao = pygame.font.Font(caminho_fonte, tamanho_botao)
        except:
            try:
                caminho_fonte = os.path.join(caminho_fontes, "Aquifer.otf")
                self.fonte_historia = pygame.font.Font(caminho_fonte, tamanho_historia)
                self.fonte_botao = pygame.font.Font(caminho_fonte, tamanho_botao)
            except:
                print("AVISO: Fonte 'Aquifer' não encontrada. Usando padrão.")
                self.fonte_historia = pygame.font.Font(None, tamanho_historia)
                self.fonte_botao = pygame.font.Font(None, tamanho_botao)
    
    def atualizar_balao(self):
        from config.settings import TELA_LARGURA, TELA_ALTURA, FATOR_ESCALA_X, FATOR_ESCALA_Y
        
        self.espaco_imagem = int(self.espaco_imagem_base * min(FATOR_ESCALA_X, FATOR_ESCALA_Y))
        self.balao_largura = int((TELA_LARGURA_PADRAO - 100 - self.espaco_imagem_base) * FATOR_ESCALA_X)
        self.balao_altura = int(240 * FATOR_ESCALA_Y)
        self.balao_x = int(50 * FATOR_ESCALA_X) + self.espaco_imagem
        self.balao_y = TELA_ALTURA - self.balao_altura - int(40 * FATOR_ESCALA_Y)
        self.balao_rect = pygame.Rect(self.balao_x, self.balao_y, self.balao_largura, self.balao_altura)
        
        
        if self.imagem_xerife_original:
            tamanho_xerife = int(150 * min(FATOR_ESCALA_X, FATOR_ESCALA_Y))
            self.imagem_xerife = pygame.transform.scale(self.imagem_xerife_original, (tamanho_xerife, tamanho_xerife))
            self.xerife_rect = self.imagem_xerife.get_rect()
            self.xerife_rect.x = self.balao_x - self.espaco_imagem + int(10 * FATOR_ESCALA_X)
            self.xerife_rect.centery = self.balao_y + self.balao_altura // 2
    
    def iniciar_som_digitacao(self):
        if self.som_digitacao and not self.som_tocando:
            try:
                self.som_digitacao.play(-1)
                self.som_tocando = True
            except:
                pass
    
    def parar_som_digitacao(self):
        if self.som_digitacao and self.som_tocando:
            try:
                self.som_digitacao.stop()
                self.som_tocando = False
            except:
                pass
    
    def quebrar_texto(self, texto):
        palavras = texto.split(' ')
        linhas = []
        linha_atual = ""
        largura_maxima = self.balao_largura - 60
        
        for palavra in palavras:
            testar_linha = linha_atual + palavra + " "
            if self.fonte_historia.size(testar_linha)[0] < largura_maxima:
                linha_atual = testar_linha
            else:
                if linha_atual:
                    linhas.append(linha_atual)
                linha_atual = palavra + " "
        if linha_atual:
            linhas.append(linha_atual)
        return linhas
    
    def avancar_cena(self):
        self.parar_som_digitacao()
        self.cena_atual += 1
        if self.cena_atual >= self.total_cenas:
            self.rodando = False
            return
        self.texto_atual = self.cenas[self.cena_atual]
        self.indice_caractere = 0
        self.texto_completo_gerado = False
        self.tempo_ultimo_caractere = pygame.time.get_ticks()
        self.linhas_para_desenhar = []
    
    def pular_digitacao_cena_atual(self):
        if not self.texto_completo_gerado:
            self.parar_som_digitacao()
            self.indice_caractere = len(self.texto_atual)
            self.texto_completo_gerado = True
            texto_parcial = self.texto_atual[:self.indice_caractere]
            self.linhas_para_desenhar = self.quebrar_texto(texto_parcial)
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        
        if self.botao_pular_rect:
            self.botao_pular_hover = self.botao_pular_rect.collidepoint(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.rodando = False
                pygame.quit()
                exit()
            
            if event.type == pygame.VIDEORESIZE:
                self.handle_resize(event)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.botao_pular_rect and self.botao_pular_hover:
                        self.rodando = False
                        return
                    if not self.texto_completo_gerado:
                        self.pular_digitacao_cena_atual()
                    else:
                        self.avancar_cena()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.rodando = False
                elif event.key == pygame.K_SPACE:
                    if not self.texto_completo_gerado:
                        self.pular_digitacao_cena_atual()
                    else:
                        self.avancar_cena()
        
        return None
    
    def update_maquina_escrever(self):
        if not self.texto_completo_gerado and self.rodando:
            if self.indice_caractere == 0 and not self.som_tocando:
                self.iniciar_som_digitacao()
            
            tempo_atual = pygame.time.get_ticks()
            if tempo_atual - self.tempo_ultimo_caractere > self.velocidade_caractere:
                self.indice_caractere += 1
                self.tempo_ultimo_caractere = tempo_atual
                if self.indice_caractere >= len(self.texto_atual):
                    self.parar_som_digitacao()
                    self.texto_completo_gerado = True
        
        if not self.texto_completo_gerado:
            texto_parcial = self.texto_atual[:self.indice_caractere]
            self.linhas_para_desenhar = self.quebrar_texto(texto_parcial)
        else:
            if not self.linhas_para_desenhar:
                self.linhas_para_desenhar = self.quebrar_texto(self.texto_atual)
        
        self.update_vagalumes()
    
    def resize_resources(self):
        super().resize_resources()
        self.atualizar_balao()
        self.carregar_fontes()
    
    def reload_fonts(self):
        self.carregar_fontes()
    
    def draw(self):
        from config.settings import TELA_LARGURA, TELA_ALTURA, FATOR_ESCALA_X, FATOR_ESCALA_Y
        
        self.draw_background()
        self.draw_vagalumes()
        
        if self.imagem_xerife and self.xerife_rect:
            fundo_imagem = pygame.Surface((self.xerife_rect.width + 10, self.xerife_rect.height + 10), pygame.SRCALPHA)
            fundo_imagem.fill((0, 0, 0, 150))
            self.tela.blit(fundo_imagem, (self.xerife_rect.x - 5, self.xerife_rect.y - 5))
            self.tela.blit(self.imagem_xerife, self.xerife_rect)
            pygame.draw.rect(self.tela, AMARELO_HISTORIA, self.xerife_rect, 3)
        
        surface_balao = pygame.Surface((self.balao_largura, self.balao_altura), pygame.SRCALPHA)
        surface_balao.fill((17, 36, 41, 230))  
        self.tela.blit(surface_balao, (self.balao_x, self.balao_y))
        pygame.draw.rect(self.tela, AMARELO_HISTORIA, self.balao_rect, 4)
        
        if self.imagem_xerife:
            triangulo_pontos = [
                (self.balao_x - 15, self.balao_y + self.balao_altura // 2 - 10),
                (self.balao_x, self.balao_y + self.balao_altura // 2),
                (self.balao_x - 15, self.balao_y + self.balao_altura // 2 + 10)
            ]
            pygame.draw.polygon(self.tela, (17, 36, 41), triangulo_pontos)
            pygame.draw.polygon(self.tela, AMARELO_HISTORIA, triangulo_pontos, 2)
        
        espacamento_linha = redimensionar_fonte(38)
        inicio_texto_y = self.balao_y + redimensionar_fonte(40)
        
        for i, linha in enumerate(self.linhas_para_desenhar):
            texto_renderizado = self.fonte_historia.render(linha.strip(), True, AMARELO_HISTORIA)
            self.tela.blit(texto_renderizado, (self.balao_x + redimensionar_fonte(35), inicio_texto_y + (i * espacamento_linha)))
        
        cor_botao = VERDE if self.botao_pular_hover else BRANCO
        texto_pular_render = self.fonte_botao.render(self.texto_pular, True, cor_botao)
        texto_x = TELA_LARGURA - texto_pular_render.get_width() - redimensionar_fonte(40)
        texto_y = redimensionar_fonte(25)
        
        self.botao_pular_rect = pygame.Rect(texto_x - 10, texto_y - 5, 
                                           texto_pular_render.get_width() + 20, 
                                           texto_pular_render.get_height() + 10)
        
        self.tela.blit(texto_pular_render, (texto_x, texto_y))
        pygame.display.flip()
    
    def run(self):
        while self.rodando:
            self.handle_events()
            self.update_maquina_escrever()
            self.draw()
            self.clock.tick(60)
        
        self.parar_som_digitacao()
        return "proximo"