# scenes/tela_pasta_fechada.py


import os
import pygame
from config.settings import TELA_LARGURA_PADRAO, TELA_ALTURA_PADRAO
from config.utils import redimensionar_fonte, redimensionar_imagem
from scenes.base_scene import BaseScene

BRANCO = (245, 230, 163)          
PRETO = (17, 36, 41)              
VERDE = (112, 163, 162)           
AMARELO_HISTORIA = (245, 230, 163)
FUNDO_BALAO = (17, 36, 41, 230)   


class TelaPastaFechada(BaseScene):
    def __init__(self, tela, clock):
        super().__init__(tela, clock)
        pygame.display.set_caption("Investigação - Pasta Fechada")

        self.pasta_do_script = os.path.dirname(os.path.abspath(__file__))

        # Carrega fundo
        caminho_fundo = os.path.join(self.pasta_do_script, "..", "assets", "images", "pasta_fechada.png")
        caminho_fundo = os.path.normpath(caminho_fundo)
        try:
            self.imagem_fundo_original = pygame.image.load(caminho_fundo)
        except:
            print("AVISO: Imagem 'pasta_fechada.png' não encontrada.")
            self.imagem_fundo_original = None
        self.imagem_fundo = redimensionar_imagem(
            self.imagem_fundo_original,
            TELA_LARGURA_PADRAO,
            TELA_ALTURA_PADRAO
        )

        self.som_digitacao = None
        self.som_tocando = False
        caminho_som = os.path.join(self.pasta_do_script, "..", "assets", "sounds", "magiaz-teclado-371741.mp3")
        caminho_som = os.path.normpath(caminho_som)
        try:
            self.som_digitacao = pygame.mixer.Sound(caminho_som)
            self.som_digitacao.set_volume(0.25)
        except:
            print("AVISO: Som de digitação não encontrado.")

        self.init_vagalumes(15)
        self.carregar_fontes()

        self.margem_esquerda = 60
        self.margem_superior = 80
        self.margem_inferior = 80
        self.largura_bal = 420
        self.altura_bal = TELA_ALTURA_PADRAO - self.margem_superior - self.margem_inferior
        self.balao_rect = pygame.Rect(
            self.margem_esquerda,
            self.margem_superior,
            self.largura_bal,
            self.altura_bal
        )

        self.texto_completo = (
            "Antes de se aventurar pela floresta, leia os trechos do diário de Helena. "
            "As anotações podem revelar pistas importantes sobre os perigos que o aguardam "
            "e ajudar a entender o que realmente aconteceu durante a expedição."
        )
        self.texto_atual = ""
        self.indice_caractere = 0
        self.tempo_ultimo_caractere = 0
        self.texto_completo_gerado = False
        self.linhas_para_desenhar = []

        self.botao_continuar_rect = None
        self.botao_continuar_hover = False

        self.iniciar_digitacao()

    def carregar_fontes(self):
        caminho_fontes = os.path.join(self.pasta_do_script, "..", "assets", "fonts")
        caminho_fontes = os.path.normpath(caminho_fontes)
        tamanho_bal = redimensionar_fonte(28)
        tamanho_botao = redimensionar_fonte(32)

        try:
            fonte = os.path.join(caminho_fontes, "Aquifer.ttf")
            self.fonte_bal = pygame.font.Font(fonte, tamanho_bal)
            self.fonte_botao = pygame.font.Font(fonte, tamanho_botao)
        except:
            try:
                fonte = os.path.join(caminho_fontes, "Aquifer.otf")
                self.fonte_bal = pygame.font.Font(fonte, tamanho_bal)
                self.fonte_botao = pygame.font.Font(fonte, tamanho_botao)
            except:
                print("AVISO: Fonte Aquifer não encontrada. Usando padrão.")
                self.fonte_bal = pygame.font.Font(None, tamanho_bal)
                self.fonte_botao = pygame.font.Font(None, tamanho_botao)

    def iniciar_digitacao(self):
        self.texto_atual = ""
        self.indice_caractere = 0
        self.texto_completo_gerado = False
        self.linhas_para_desenhar = []
        self.tempo_ultimo_caractere = pygame.time.get_ticks()
        if self.som_digitacao and not self.som_tocando:
            self.som_digitacao.play(-1)
            self.som_tocando = True

    def parar_som(self):
        if self.som_digitacao and self.som_tocando:
            self.som_digitacao.stop()
            self.som_tocando = False

    def atualizar_digitacao(self):
        if self.texto_completo_gerado:
            return
        agora = pygame.time.get_ticks()
        if agora - self.tempo_ultimo_caractere > 35:
            if self.indice_caractere < len(self.texto_completo):
                self.indice_caractere += 1
                self.tempo_ultimo_caractere = agora
                self.texto_atual = self.texto_completo[:self.indice_caractere]
            else:
                self.texto_completo_gerado = True
                self.parar_som()

    def quebrar_texto(self, texto, largura_max):
        palavras = texto.split(' ')
        linhas = []
        linha_atual = ""
        for palavra in palavras:
            teste = linha_atual + palavra + " "
            if self.fonte_bal.size(teste)[0] < largura_max:
                linha_atual = teste
            else:
                if linha_atual:
                    linhas.append(linha_atual)
                linha_atual = palavra + " "
        if linha_atual:
            linhas.append(linha_atual)
        return linhas

    def desenhar_balao(self):
  
        surface = pygame.Surface((self.largura_bal, self.altura_bal), pygame.SRCALPHA)
        surface.fill(FUNDO_BALAO)
        self.tela.blit(surface, (self.balao_rect.x, self.balao_rect.y))
        # Borda
        pygame.draw.rect(self.tela, AMARELO_HISTORIA, self.balao_rect, 4)

    
        margem_interna = 30
        largura_texto = self.largura_bal - 2 * margem_interna
        texto_para_mostrar = self.texto_atual if not self.texto_completo_gerado else self.texto_completo
        linhas = self.quebrar_texto(texto_para_mostrar, largura_texto)

        espacamento = redimensionar_fonte(34)
        inicio_y = self.balao_rect.y + margem_interna + 10

        for i, linha in enumerate(linhas):
            surf = self.fonte_bal.render(linha.strip(), True, AMARELO_HISTORIA)
            self.tela.blit(surf, (self.balao_rect.x + margem_interna, inicio_y + i * espacamento))

       
        if self.texto_completo_gerado:
            texto_botao = self.fonte_botao.render("CONTINUAR", True, BRANCO)
            rect_botao = texto_botao.get_rect()
            rect_botao.bottomright = (self.balao_rect.right - 30, self.balao_rect.bottom - 30)
            self.botao_continuar_rect = rect_botao

           
            pygame.draw.rect(self.tela, PRETO, rect_botao.inflate(20, 10), border_radius=5)
            pygame.draw.rect(self.tela, AMARELO_HISTORIA, rect_botao.inflate(20, 10), 2, border_radius=5)

            cor = VERDE if self.botao_continuar_hover else BRANCO
            render = self.fonte_botao.render("CONTINUAR", True, cor)
            self.tela.blit(render, rect_botao)
        else:
            self.botao_continuar_rect = None

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.botao_continuar_rect:
            self.botao_continuar_hover = self.botao_continuar_rect.collidepoint(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.rodando = False
                return "sair"
            if event.type == pygame.VIDEORESIZE:
                self.handle_resize(event)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.texto_completo_gerado and self.botao_continuar_rect and self.botao_continuar_hover:
                    self.parar_som()
                    self.rodando = False
                    return "proximo"
                else:
                
                    self.parar_som()
                    self.indice_caractere = len(self.texto_completo)
                    self.texto_completo_gerado = True
                    self.texto_atual = self.texto_completo
                    self.linhas_para_desenhar = []
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.rodando = False
                    return "voltar"
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    if self.texto_completo_gerado:
                        self.parar_som()
                        self.rodando = False
                        return "proximo"
                    else:
                        self.parar_som()
                        self.indice_caractere = len(self.texto_completo)
                        self.texto_completo_gerado = True
                        self.texto_atual = self.texto_completo
                        self.linhas_para_desenhar = []
        return None

    def draw(self):
        from config.settings import TELA_LARGURA, TELA_ALTURA, FATOR_ESCALA_X, FATOR_ESCALA_Y

        self.draw_background()
        self.draw_vagalumes()

      
        overlay = pygame.Surface((TELA_LARGURA, TELA_ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.tela.blit(overlay, (0, 0))

        
        self.desenhar_balao()

        pygame.display.flip()

    def resize_resources(self):
        super().resize_resources()
        
        self.altura_bal = TELA_ALTURA_PADRAO - self.margem_superior - self.margem_inferior
        self.balao_rect = pygame.Rect(
            self.margem_esquerda,
            self.margem_superior,
            self.largura_bal,
            self.altura_bal
        )

    def run(self):
        while self.rodando:
            acao = self.handle_events()
            if acao:
                return acao
            self.atualizar_digitacao()
            self.update_vagalumes()
            self.draw()
            self.clock.tick(60)
        return "proximo"