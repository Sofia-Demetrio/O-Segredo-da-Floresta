# scenes/tela_transicao_floresta.py

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


class TelaTransicaoFloresta(BaseScene):
    def __init__(self, tela, clock):
        super().__init__(tela, clock)
        pygame.display.set_caption("Investigação - Entrada na Floresta")

        self.pasta_do_script = os.path.dirname(os.path.abspath(__file__))

       
        caminho_fundo = os.path.join(self.pasta_do_script, "..", "assets", "images", "cenario_1.jpg")
        caminho_fundo = os.path.normpath(caminho_fundo)
        try:
            self.imagem_fundo_original = pygame.image.load(caminho_fundo)
        except:
            print("AVISO: Imagem 'cenario_1.jpg' não encontrada.")
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

        
        self.som_digitacao = None
        self.som_tocando = False
        caminho_som = os.path.join(self.pasta_do_script, "..", "assets", "sounds", "magiaz-teclado-371741.mp3")
        caminho_som = os.path.normpath(caminho_som)
        try:
            self.som_digitacao = pygame.mixer.Sound(caminho_som)
            self.som_digitacao.set_volume(0.25)
        except:
            print("AVISO: Som de digitação não encontrado.")

        self.init_vagalumes(20)
        self.carregar_fontes()

        
        self.espaco_imagem_base = 170
        self.atualizar_balao()

        self.texto_completo = (
            "A entrada na floresta é mais silenciosa do que eu imaginava. "
            "Cada passo parece ser observado, como se algo já soubesse que eu estou aqui. "
            "Ainda assim, não vou voltar atrás."
        )

        self.texto_atual = ""
        self.indice_caractere = 0
        self.tempo_ultimo_caractere = 0
        self.texto_completo_gerado = False
        self.linhas_para_desenhar = []
        self.botao_seguir_rect = None
        self.botao_seguir_hover = False

    def carregar_fontes(self):
        caminho_fontes = os.path.join(self.pasta_do_script, "..", "assets", "fonts")
        caminho_fontes = os.path.normpath(caminho_fontes)

        tamanho_balao = redimensionar_fonte(32)
        tamanho_botao = redimensionar_fonte(36)

        try:
            caminho_fonte = os.path.join(caminho_fontes, "Aquifer.ttf")
            self.fonte_balao = pygame.font.Font(caminho_fonte, tamanho_balao)
            self.fonte_botao = pygame.font.Font(caminho_fonte, tamanho_botao)
        except:
            try:
                caminho_fonte = os.path.join(caminho_fontes, "Aquifer.otf")
                self.fonte_balao = pygame.font.Font(caminho_fonte, tamanho_balao)
                self.fonte_botao = pygame.font.Font(caminho_fonte, tamanho_botao)
            except:
                print("AVISO: Fonte 'Aquifer' não encontrada. Usando padrão.")
                self.fonte_balao = pygame.font.Font(None, tamanho_balao)
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

    def atualizar_maquina_escrever(self):
        if self.texto_completo_gerado:
            return
        tempo_atual = pygame.time.get_ticks()
        if tempo_atual - self.tempo_ultimo_caractere > 35:
            if self.indice_caractere < len(self.texto_completo):
                self.indice_caractere += 1
                self.tempo_ultimo_caractere = tempo_atual
                self.texto_atual = self.texto_completo[:self.indice_caractere]
            else:
                self.texto_completo_gerado = True
                self.parar_som()

    def quebrar_texto(self, texto, largura_maxima):
        palavras = texto.split(' ')
        linhas = []
        linha_atual = ""
        for palavra in palavras:
            testar_linha = linha_atual + palavra + " "
            if self.fonte_balao.size(testar_linha)[0] < largura_maxima:
                linha_atual = testar_linha
            else:
                if linha_atual:
                    linhas.append(linha_atual)
                linha_atual = palavra + " "
        if linha_atual:
            linhas.append(linha_atual)
        return linhas

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.botao_seguir_rect:
            self.botao_seguir_hover = self.botao_seguir_rect.collidepoint(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.rodando = False
                return "sair"
            if event.type == pygame.VIDEORESIZE:
                self.handle_resize(event)

            if self.texto_completo_gerado:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.botao_seguir_rect and self.botao_seguir_hover:
                        self.rodando = False
                        return "proximo"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.rodando = False
                        return "proximo"
            else:
                # Pular digitação com clique ou espaço
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.pular_digitacao()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.pular_digitacao()
        return None

    def pular_digitacao(self):
        if not self.texto_completo_gerado:
            self.parar_som()
            self.indice_caractere = len(self.texto_completo)
            self.texto_atual = self.texto_completo
            self.texto_completo_gerado = True
            self.linhas_para_desenhar = []

    def desenhar(self):
        from config.settings import TELA_LARGURA, TELA_ALTURA, FATOR_ESCALA_X, FATOR_ESCALA_Y

        self.draw_background()
        self.draw_vagalumes()

        overlay = pygame.Surface((TELA_LARGURA, TELA_ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.tela.blit(overlay, (0, 0))

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

        texto_para_desenhar = self.texto_atual if not self.texto_completo_gerado else self.texto_completo
        linhas = self.quebrar_texto(texto_para_desenhar, self.balao_largura - 60)

        espacamento_linha = redimensionar_fonte(38)
        inicio_texto_y = self.balao_y + redimensionar_fonte(40)
        for i, linha in enumerate(linhas):
            texto_render = self.fonte_balao.render(linha.strip(), True, BRANCO)
            self.tela.blit(texto_render, (self.balao_x + redimensionar_fonte(35), inicio_texto_y + i * espacamento_linha))

        if self.texto_completo_gerado:
            texto_seguir = self.fonte_botao.render("SEGUIR", True, BRANCO)
            seguir_rect = texto_seguir.get_rect()
            seguir_rect.bottomright = (self.balao_rect.right - 40, self.balao_rect.bottom - 20)
            self.botao_seguir_rect = seguir_rect

            cor_seguir = VERDE if self.botao_seguir_hover else BRANCO
            texto_seguir_render = self.fonte_botao.render("SEGUIR", True, cor_seguir)
            self.tela.blit(texto_seguir_render, self.botao_seguir_rect)
        else:
            self.botao_seguir_rect = None

        pygame.display.flip()

    def resize_resources(self):
        super().resize_resources()
        self.atualizar_balao()
        self.carregar_fontes()

    def reload_fonts(self):
        self.carregar_fontes()

    def run(self):
        self.atualizar_balao()
        self.iniciar_digitacao()
        while self.rodando:
            acao = self.handle_events()
            if acao == "proximo":
                self.parar_som()
                return "proximo"
            if acao == "sair":
                return "sair"
            self.atualizar_maquina_escrever()
            self.update_vagalumes()
            self.desenhar()
            self.clock.tick(60)
        self.parar_som()
        return "proximo"