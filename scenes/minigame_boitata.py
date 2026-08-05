# scenes/minigame_boitata.py

import os
import pygame
import random
import math
from config.settings import TELA_LARGURA_PADRAO, TELA_ALTURA_PADRAO
from config.utils import redimensionar_fonte
from scenes.base_scene import BaseScene

# Cores
BRANCO = (245, 230, 163)
PRETO = (17, 36, 41)
VERMELHO = (200, 50, 50)
VERDE = (112, 163, 162)
AMARELO_HISTORIA = (245, 230, 163)
CINZA = (100, 100, 100)
VERMELHO_TRANSP = (200, 50, 50, 100)

TOLERANCIA_X = 40 
TOLERANCIA_Y = 15 

# Coordenadas das plataformas 
PLATAFORMAS = [

    ["Superior 1", 150, 240, 455, 395, 302, 317],
    ["Superior 2", 465, 240, 770, 395, 617, 317],
    ["Superior 3", 780, 240, 1085, 395, 932, 317],
    ["Superior 4", 1095, 240, 1400, 395, 1247, 317],
    ["Inferior 1", 150, 405, 455, 560, 302, 482],
    ["Inferior 2", 465, 405, 770, 560, 617, 482],
    ["Inferior 3", 780, 405, 1085, 560, 932, 482],
    ["Inferior 4", 1095, 405, 1400, 560, 1247, 482]
]

# Tamanho base do personagem 
PERSONAGEM_LARGURA_BASE = 240
PERSONAGEM_ALTURA_BASE = 240

TEMPO_MEMORIZACAO = 5  
DURACAO_PULO = 600     


class PlataformaPonte:
    def __init__(self, x1, y1, x2, y2, centro_x, centro_y, perigosa=False):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.centro_x = centro_x
        self.centro_y = centro_y
        self.perigosa = perigosa
        self.rect = pygame.Rect(x1, y1, x2-x1, y2-y1)

    def desenhar_indicador(self, surface):
        fonte = pygame.font.Font(None, 60)
        texto = fonte.render("X", True, VERMELHO)
        
        if self.rect.x == 150:
            novo_centro_x = self.rect.x + (self.rect.width * 0.75)
            texto_rect = texto.get_rect(center=(novo_centro_x, self.centro_y))
        else:
            texto_rect = texto.get_rect(center=(self.centro_x, self.centro_y))
            
        surface.blit(texto, texto_rect)

    def desenhar_perigo(self, surface):
    
        largura_ajustada = self.rect.width - (TOLERANCIA_X * 2)
        altura_ajustada = self.rect.height - (TOLERANCIA_Y * 2)
        x_pos = self.rect.x + TOLERANCIA_X

        # Se for a primeira coluna, corta a largura na metade se não o personagem morre direto
        if self.rect.x == 150:
            largura_ajustada = largura_ajustada // 2
            x_pos = self.rect.x + (self.rect.width // 2) + (TOLERANCIA_X // 2)
        
        if largura_ajustada > 0 and altura_ajustada > 0:
            s = pygame.Surface((largura_ajustada, altura_ajustada), pygame.SRCALPHA)
            s.fill((255, 0, 0, 100))
            surface.blit(s, (x_pos, self.rect.y + TOLERANCIA_Y))


class MinigameBoitata(BaseScene):
    def __init__(self, tela, clock):
        super().__init__(tela, clock)
        pygame.display.set_caption("Minigame - Boitatá: Ponte da Memória")
        self.pasta_do_script = os.path.dirname(os.path.abspath(__file__))

        from config.settings import FATOR_ESCALA_X, FATOR_ESCALA_Y
        self.escala = min(FATOR_ESCALA_X, FATOR_ESCALA_Y)

        # Tamanho do personagem
        self.personagem_largura = int(PERSONAGEM_LARGURA_BASE * self.escala)
        self.personagem_altura = int(PERSONAGEM_ALTURA_BASE * self.escala)

        # Carrega sprites
        self.sprite_parado = self.carregar_sprite("parado.png",
                                                  (self.personagem_largura, self.personagem_altura))
        self.sprite_correndo = self.carregar_sprite("correndo.png",
                                                    (self.personagem_largura, self.personagem_altura))
        self.sprite_pulando = self.carregar_sprite("pulando.png",
                                                   (self.personagem_largura, self.personagem_altura))

        self.fundo_img = None
        caminho_fundo = os.path.join(self.pasta_do_script, "..", "assets", "images", "ponte.png")
        caminho_fundo = os.path.normpath(caminho_fundo)
        try:
            self.fundo_img = pygame.image.load(caminho_fundo)
            self.fundo_img = pygame.transform.scale(self.fundo_img, (TELA_LARGURA_PADRAO, TELA_ALTURA_PADRAO))
        except:
            print("AVISO: ponte.png não encontrado. Usando fundo preto.")
            self.fundo_img = None

        self.carregar_fontes()
        self.init_vagalumes(15)

        self.texto_final_completo = (
            "Tentamos avisá-lo. Tentamos afastá-lo do caminho antes que fosse tarde demais. "
            "O Curupira guiou seus passos para longe, a Iara tentou fazê-lo desistir, e até o Boitatá "
            "colocou ilusões diante de seus olhos.\n\n"
            "Mas você insistiu.\n\n"
            "Entenda, não queremos guerra. Nunca quisemos. Tudo o que fazemos é proteger esta floresta "
            "e os segredos que ela guarda. Há coisas aqui que não pertencem ao mundo dos homens.\n\n"
            "Ainda há tempo para voltar. Mas se decidir continuar, terá que enfrentar as consequências "
            "de suas escolhas."
        )
        self.texto_final_atual = ""
        self.indice_texto_final = 0
        self.tempo_ultimo_caractere = 0
        self.texto_final_completo_gerado = False
        self.linhas_texto_final = []
        self.mostrando_texto_final = False
        self.botao_continuar_rect = None
        self.botao_continuar_hover = False
        self.som_digitacao = None
        self.som_tocando = False
        caminho_som = os.path.join(self.pasta_do_script, "..", "assets", "sounds", "magiaz-teclado-371741.mp3")
        caminho_som = os.path.normpath(caminho_som)
        try:
            self.som_digitacao = pygame.mixer.Sound(caminho_som)
            self.som_digitacao.set_volume(0.25)
        except:
            print("AVISO: Som de digitação não encontrado.")

        self.resetar_jogo()

    def carregar_sprite(self, nome_arquivo, tamanho):
        caminho = os.path.join(self.pasta_do_script, "..", "assets", "images", nome_arquivo)
        caminho = os.path.normpath(caminho)
        try:
            img = pygame.image.load(caminho).convert_alpha()
            return pygame.transform.scale(img, tamanho)
        except:
            print(f"AVISO: {nome_arquivo} não encontrado.")
            surf = pygame.Surface(tamanho, pygame.SRCALPHA)
            surf.fill((139, 69, 19))
            return surf

    def carregar_fontes(self):
        caminho_fontes = os.path.join(self.pasta_do_script, "..", "assets", "fonts")
        tamanho = redimensionar_fonte(48)
        tamanho_instrucoes = redimensionar_fonte(24)
        tamanho_texto_final = redimensionar_fonte(30)
        try:
            fonte = os.path.join(caminho_fontes, "Aquifer.ttf")
            self.fonte = pygame.font.Font(fonte, tamanho)
            self.fonte_instrucoes = pygame.font.Font(fonte, tamanho_instrucoes)
            self.fonte_texto_final = pygame.font.Font(fonte, tamanho_texto_final)
        except:
            self.fonte = pygame.font.Font(None, tamanho)
            self.fonte_instrucoes = pygame.font.Font(None, tamanho_instrucoes)
            self.fonte_texto_final = pygame.font.Font(None, tamanho_texto_final)

    def resetar_jogo(self):
        """Garante a existência de EXATAMENTE 3 zonas de perigo sem travar o jogador."""
        self.plataformas = []
        
        caminho_linha = []  # Guarda 0 para cima, 1 para baixo para cada coluna
        atual = random.choice([0, 1])
        caminho_linha.append(atual)
        
        for col in range(1, 4):
            proximo = random.choice([0, 1])
            caminho_linha.append(proximo)
            atual = proximo

        # escolhe exatamente 3 colunas distintas para colocar perigo
        colunas_com_perigo = random.sample([0, 1, 2, 3], 3)
        
        indices_perigo = set()
        for col in colunas_com_perigo:
            linha_segura = caminho_linha[col]
            linha_perigo = 1 if linha_segura == 0 else 0
            idx_perigo = col + (4 if linha_perigo == 1 else 0)
            indices_perigo.add(idx_perigo)

        # Monta a estrutura final das plataformas
        for idx, (nome, x1, y1, x2, y2, cx, cy) in enumerate(PLATAFORMAS):
            perigosa = idx in indices_perigo
            plat = PlataformaPonte(x1, y1, x2, y2, cx, cy, perigosa)
            self.plataformas.append(plat)

        # Posição inicial
        self.pos_inv_x = 5
        self.pos_inv_y = (TELA_ALTURA_PADRAO // 2) - (self.personagem_altura // 2)

        self.investigador_rect = pygame.Rect(self.pos_inv_x, self.pos_inv_y,
                                             self.personagem_largura, self.personagem_altura)

        self.fase = "memorizacao"
        self.venceu = False
        self.jogando = True
        self.proximo = False
        self.tempo_vitoria = 0

        self.tempo_inicio_memorizacao = pygame.time.get_ticks()
        self.tempo_memorizacao = TEMPO_MEMORIZACAO * 1000

        self.investigador_img_atual = self.sprite_parado

        # Controle de Pulo
        self.pulando = False
        self.tempo_inicio_pulo = 0
        self.offset_y_pulo = 0

        self.mostrando_texto_final = False
        self.texto_final_atual = ""
        self.indice_texto_final = 0
        self.texto_final_completo_gerado = False
        self.linhas_texto_final = []
        self.botao_continuar_rect = None
        self.botao_continuar_hover = False
        if self.som_tocando:
            self.som_digitacao.stop()
            self.som_tocando = False

    def iniciar_texto_final(self):
        self.mostrando_texto_final = True
        self.texto_final_atual = ""
        self.indice_texto_final = 0
        self.texto_final_completo_gerado = False
        self.linhas_texto_final = []
        self.tempo_ultimo_caractere = pygame.time.get_ticks()
        if self.som_digitacao and not self.som_tocando:
            self.som_digitacao.play(-1)
            self.som_tocando = True

    def parar_som(self):
        if self.som_digitacao and self.som_tocando:
            self.som_digitacao.stop()
            self.som_tocando = False

    def pular_digitacao(self):
        if not self.texto_final_completo_gerado:
            self.parar_som()
            self.indice_texto_final = len(self.texto_final_completo)
            self.texto_final_atual = self.texto_final_completo
            self.texto_final_completo_gerado = True
            self.linhas_texto_final = []  # força recálculo

    def atualizar_texto_final(self):
        if not self.mostrando_texto_final or self.texto_final_completo_gerado:
            return
        agora = pygame.time.get_ticks()
        if agora - self.tempo_ultimo_caractere > 30:
            if self.indice_texto_final < len(self.texto_final_completo):
                self.indice_texto_final += 1
                self.tempo_ultimo_caractere = agora
                self.texto_final_atual = self.texto_final_completo[:self.indice_texto_final]
            else:
                self.texto_final_completo_gerado = True
                self.parar_som()

    def quebrar_texto_final(self, texto, largura_max):
        palavras = texto.split(' ')
        linhas = []
        linha_atual = ""
        for palavra in palavras:
            teste = linha_atual + palavra + " "
            if self.fonte_texto_final.size(teste)[0] < largura_max:
                linha_atual = teste
            else:
                if linha_atual:
                    linhas.append(linha_atual)
                linha_atual = palavra + " "
        if linha_atual:
            linhas.append(linha_atual)
        return linhas

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.rodando = False
                return "sair"
            if event.type == pygame.VIDEORESIZE:
                self.handle_resize(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.rodando = False
                    return "voltar"
                if self.mostrando_texto_final:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        if self.texto_final_completo_gerado:
                            self.parar_som()
                            self.rodando = False
                            self.proximo = True
                            return "proximo"
                        else:
                            self.pular_digitacao()
                    continue
                if self.venceu or self.fase == "vitoria":
                    continue
                if event.key == pygame.K_r:
                    self.resetar_jogo()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.mostrando_texto_final:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.botao_continuar_rect and self.botao_continuar_rect.collidepoint(mouse_pos):
                        self.parar_som()
                        self.rodando = False
                        self.proximo = True
                        return "proximo"
                    else:
                        if not self.texto_final_completo_gerado:
                            self.pular_digitacao()
        return None

    def update(self):
        if self.venceu and not self.mostrando_texto_final:
            self.iniciar_texto_final()
            return

        if self.mostrando_texto_final:
            self.atualizar_texto_final()
            self.update_vagalumes()
            return

        if self.fase == "vitoria":
            return

        if self.fase == "memorizacao":
            agora = pygame.time.get_ticks()
            if agora - self.tempo_inicio_memorizacao > self.tempo_memorizacao:
                self.fase = "jogando"
            return

        agora = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        if self.pulando:
            tempo_decorrido = agora - self.tempo_inicio_pulo
            if tempo_decorrido >= DURACAO_PULO:
                if keys[pygame.K_SPACE]:
                    self.tempo_inicio_pulo = agora
                    progresso = 0
                    self.offset_y_pulo = int(math.sin(progresso * math.pi) * 50)
                else:
                    self.pulando = False
                    self.offset_y_pulo = 0
            else:
                progresso = tempo_decorrido / DURACAO_PULO
                self.offset_y_pulo = int(math.sin(progresso * math.pi) * 50)
        elif keys[pygame.K_SPACE]:
            self.pulando = True
            self.tempo_inicio_pulo = agora
            self.offset_y_pulo = 0

        velocidade = 6
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -velocidade
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = velocidade
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -velocidade
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = velocidade

        if self.pulando:
            self.investigador_img_atual = self.sprite_pulando
        elif dx != 0 or dy != 0:
            self.investigador_img_atual = self.sprite_correndo
        else:
            self.investigador_img_atual = self.sprite_parado

        # limitação de movimento dentro da tela e dentro da ponte
        proxima_pos_x = self.pos_inv_x + dx
        proxima_pos_y = self.pos_inv_y + dy

        centro_y_futuro = proxima_pos_y + (self.personagem_altura // 2)

        Y_MINIMO_PERMITIDO = 230  
        Y_MAXIMO_PERMITIDO = 540  

        self.pos_inv_x = max(0, min(proxima_pos_x, TELA_LARGURA_PADRAO - self.personagem_largura))
        
        if Y_MINIMO_PERMITIDO <= centro_y_futuro <= Y_MAXIMO_PERMITIDO:
            self.pos_inv_y = proxima_pos_y

        self.investigador_rect.x = self.pos_inv_x
        self.investigador_rect.y = self.pos_inv_y
        # ------------------------------

        # verifica se morreu
        if not self.pulando:
            hitbox_jogador_interna = pygame.Rect(
                self.investigador_rect.x + 40,
                self.investigador_rect.y + 10,
                self.investigador_rect.width - 80,
                self.investigador_rect.height - 20
            )

            for plat in self.plataformas:
                if plat.perigosa:
                    largura_ajustada = plat.rect.width - (TOLERANCIA_X * 2)
                    x_pos = plat.rect.x + TOLERANCIA_X

                    if plat.rect.x == 150:
                        largura_ajustada = largura_ajustada // 2
                        x_pos = plat.rect.x + (plat.rect.width // 2) + (TOLERANCIA_X // 2)

                    rect_perigo_ajustado = pygame.Rect(
                        x_pos,
                        plat.rect.y + TOLERANCIA_Y,
                        largura_ajustada,
                        plat.rect.height - (TOLERANCIA_Y * 2)
                    )
                    
                    if hitbox_jogador_interna.colliderect(rect_perigo_ajustado):
                        self.resetar_jogo()
                        return

        # Verifica vitória
        if self.pos_inv_x >= 1400 - (self.personagem_largura // 2):
            self.venceu = True
            self.fase = "vitoria"
            self.tempo_vitoria = pygame.time.get_ticks()

        self.update_vagalumes()

    def desenhar_painel_instrucoes(self):
        from config.settings import FATOR_ESCALA_X, FATOR_ESCALA_Y, TELA_LARGURA, TELA_ALTURA
        
        # Dimensões base do balão
        largura = int(340 * FATOR_ESCALA_X)
        altura = int(140 * FATOR_ESCALA_Y)
        
        # Posicionamento no canto inferior direito
        x = TELA_LARGURA - largura - int(20 * FATOR_ESCALA_X)
        y = TELA_ALTURA - altura - int(20 * FATOR_ESCALA_Y)
        
        # Fundo do balão (fundo escuro com Alpha)
        surface_balao = pygame.Surface((largura, altura), pygame.SRCALPHA)
        surface_balao.fill((17, 36, 41, 210))  
        self.tela.blit(surface_balao, (x, y))
        
        # Borda do balão
        rect_balao = pygame.Rect(x, y, largura, altura)
        pygame.draw.rect(self.tela, AMARELO_HISTORIA, rect_balao, 3)
        
        # Texto das Instruções 
        linhas = [
            "Como jogar:",
            "• Setas / WASD: Mover",
            "• Segurar espaço: Pular",
            "• R: Reiniciar jogo"
        ]
        
        espacamento_linha = redimensionar_fonte(26)
        inicio_texto_y = y + redimensionar_fonte(15)
        
        for i, linha in enumerate(linhas):
            cor = AMARELO_HISTORIA if i == 0 else BRANCO
            texto_renderizado = self.fonte_instrucoes.render(linha, True, cor)
            self.tela.blit(texto_renderizado, (x + redimensionar_fonte(15), inicio_texto_y + (i * espacamento_linha)))

    def draw(self):
        if self.fundo_img:
            self.tela.blit(self.fundo_img, (0, 0))
        else:
            self.tela.fill(PRETO)

        self.draw_vagalumes()

        if self.fase == "memorizacao":
            for plat in self.plataformas:
                if plat.perigosa:
                    plat.desenhar_perigo(self.tela)  
                    plat.desenhar_indicador(self.tela)  

        pos_desenho_y = self.investigador_rect.y - self.offset_y_pulo
        self.tela.blit(self.investigador_img_atual, (self.investigador_rect.x, pos_desenho_y))

        self.desenhar_painel_instrucoes()

        if self.fase == "memorizacao":
            tempo_restante = max(0, (self.tempo_memorizacao -
                                     (pygame.time.get_ticks() - self.tempo_inicio_memorizacao)) // 1000)
            texto = self.fonte.render(f"Memorize o caminho seguro! {tempo_restante+1}s", True, AMARELO_HISTORIA)
            self.tela.blit(texto, (TELA_LARGURA_PADRAO//2 - texto.get_width()//2, 30))
        elif self.fase == "jogando":
            texto = self.fonte.render("Chegue ao outro lado da ponte!", True, BRANCO)
            self.tela.blit(texto, (TELA_LARGURA_PADRAO//2 - texto.get_width()//2, 30))

        if self.mostrando_texto_final:
            overlay = pygame.Surface((TELA_LARGURA_PADRAO, TELA_ALTURA_PADRAO), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.tela.blit(overlay, (0, 0))

            margem_x = 100
            margem_y = 80
            largura_bal = TELA_LARGURA_PADRAO - 2 * margem_x
            altura_bal = TELA_ALTURA_PADRAO - 2 * margem_y
            balao_rect = pygame.Rect(margem_x, margem_y, largura_bal, altura_bal)

            surface_balao = pygame.Surface((largura_bal, altura_bal), pygame.SRCALPHA)
            surface_balao.fill((17, 36, 41, 230))
            self.tela.blit(surface_balao, (margem_x, margem_y))
            pygame.draw.rect(self.tela, AMARELO_HISTORIA, balao_rect, 4)

            texto_para_mostrar = self.texto_final_atual if not self.texto_final_completo_gerado else self.texto_final_completo
            linhas = self.quebrar_texto_final(texto_para_mostrar, largura_bal - 80)

            espacamento_linha = redimensionar_fonte(38)
            inicio_texto_y = margem_y + 50
            for i, linha in enumerate(linhas):
                texto_render = self.fonte_texto_final.render(linha.strip(), True, BRANCO)
                self.tela.blit(texto_render, (margem_x + 40, inicio_texto_y + i * espacamento_linha))

            if self.texto_final_completo_gerado:
                botao_texto = "CONTINUAR"
                cor_botao = VERDE if self.botao_continuar_hover else BRANCO
                texto_botao = self.fonte.render(botao_texto, True, cor_botao)
                rect_botao = texto_botao.get_rect()
                rect_botao.bottomright = (balao_rect.right - 40, balao_rect.bottom - 30)
                self.botao_continuar_rect = rect_botao
                self.tela.blit(texto_botao, rect_botao)
            else:
                self.botao_continuar_rect = None

        pygame.display.flip()

    def resize_resources(self):
        super().resize_resources()
        self.resetar_jogo()

    def run(self):
        self.proximo = False
        while self.rodando:
            acao = self.handle_events()
            if acao:
                self.parar_som()
                return acao
            self.update()
            self.draw()
            self.clock.tick(60)
        self.parar_som()
        return "proximo" if self.proximo else "voltar"