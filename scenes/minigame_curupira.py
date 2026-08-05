# scenes/minigame_curupira.py

import os
import pygame
import random
from config.settings import TELA_LARGURA_PADRAO, TELA_ALTURA_PADRAO
from config.utils import redimensionar_fonte
from scenes.base_scene import BaseScene

# Cores
BRANCO = (245, 230, 163)
PRETO = (17, 36, 41)
VERMELHO = (200, 50, 50)
VERDE = (112, 163, 162)
AMARELO_HISTORIA = (245, 230, 163)
LARANJA = (255, 140, 0)

# Constantes de Tamanho
PERSONAGEM_BASE = 300
FOGO_BASE = 100

class Fogo:
    def __init__(self, x, y, imagem, velocidade_y, escala):
        largura = int(FOGO_BASE * escala)
        altura = int(FOGO_BASE * escala)
        if imagem:
            self.imagem = pygame.transform.scale(imagem, (largura, altura))
        else:
            self.imagem = None
        self.rect = pygame.Rect(x, y, largura, altura)
        self.velocidade_y = velocidade_y

    def update(self):
        self.rect.y += self.velocidade_y

    def draw(self, surface):
        if self.imagem:
            surface.blit(self.imagem, self.rect)
        else:
            pygame.draw.rect(surface, LARANJA, self.rect)

class MinigameCurupira(BaseScene):
    def __init__(self, tela, clock):
        super().__init__(tela, clock)
        pygame.display.set_caption("Minigame - Curupira: Desvie do Fogo!")
        self.pasta_do_script = os.path.dirname(os.path.abspath(__file__))
        
        from config.settings import FATOR_ESCALA_X, FATOR_ESCALA_Y
        self.escala = min(FATOR_ESCALA_X, FATOR_ESCALA_Y)

        self.personagem_largura = int(PERSONAGEM_BASE * self.escala)
        self.personagem_altura = int(PERSONAGEM_BASE * self.escala)

        # Sprites
        self.sprite_parado = self.carregar_sprite("parado.png", (self.personagem_largura, self.personagem_altura))
        self.sprite_correndo = self.carregar_sprite("correndo.png", (self.personagem_largura, self.personagem_altura))
        self.sprite_pulando = self.carregar_sprite("pulando.png", (self.personagem_largura, self.personagem_altura))

        # Fogo
        self.fogo_img = None
        caminho_fogo = os.path.join(self.pasta_do_script, "..", "assets", "images", "fogo.png")
        try:
            self.fogo_img = pygame.image.load(caminho_fogo).convert_alpha()
        except:
            pass

        # Fundo Curupira (com fallback)
        self.fundo_img = None
        self.fundo_largura = TELA_LARGURA_PADRAO
        caminho_fundo = os.path.join(self.pasta_do_script, "..", "assets", "images", "curupira.jpg")
        try:
            self.fundo_img = pygame.image.load(caminho_fundo)
            escala_fundo = TELA_ALTURA_PADRAO / self.fundo_img.get_height()
            nova_largura = int(self.fundo_img.get_width() * escala_fundo)
            self.fundo_img = pygame.transform.scale(self.fundo_img, (nova_largura, TELA_ALTURA_PADRAO))
            self.fundo_largura = nova_largura
        except:
            self.fundo_img = pygame.Surface((TELA_LARGURA_PADRAO, TELA_ALTURA_PADRAO))
            self.fundo_img.fill(PRETO)
            self.fundo_largura = TELA_LARGURA_PADRAO

        self.carregar_fontes()
        self.init_vagalumes(10)
        self.resetar_jogo()

        # Controle do botão CONTINUAR
        self.mostrar_botao_continuar = False
        self.botao_continuar_rect = None
        self.botao_continuar_hover = False

    def carregar_sprite(self, nome_arquivo, tamanho):
        caminho = os.path.join(self.pasta_do_script, "..", "assets", "images", nome_arquivo)
        try:
            img = pygame.image.load(caminho).convert_alpha()
            return pygame.transform.scale(img, tamanho)
        except:
            surf = pygame.Surface(tamanho, pygame.SRCALPHA)
            surf.fill(VERDE)
            return surf

    def carregar_fontes(self):
        caminho_fontes = os.path.join(self.pasta_do_script, "..", "assets", "fonts")
        tamanho = redimensionar_fonte(48)
        tamanho_inst = redimensionar_fonte(24)
        try:
            fonte_caminho = os.path.join(caminho_fontes, "Aquifer.ttf")
            self.fonte = pygame.font.Font(fonte_caminho, tamanho)
            self.fonte_instrucoes = pygame.font.Font(fonte_caminho, tamanho_inst)
            self.fonte_botao = pygame.font.Font(fonte_caminho, tamanho)  # mesma fonte para o botão
        except:
            self.fonte = pygame.font.Font(None, tamanho)
            self.fonte_instrucoes = pygame.font.Font(None, tamanho_inst)
            self.fonte_botao = pygame.font.Font(None, tamanho)

    def resetar_jogo(self):
        self.investigador_img_atual = self.sprite_parado
        self.investigador_rect = pygame.Rect(0, 0, self.personagem_largura, self.personagem_altura)

        self.pos_inv_x = 50
        self.pos_inv_y_chao = TELA_ALTURA_PADRAO - self.personagem_altura
        self.pos_inv_y = self.pos_inv_y_chao
        
        self.vel_y = 0
        self.gravidade = 1.2
        self.forca_pulo = -25
        self.no_chao = True

        self.fundo_x1 = 0
        self.fundo_x2 = self.fundo_largura
        self.velocidade_fundo = 5

        self.fogos = []
        self.tempo_ultimo_fogo = 0
        self.intervalo_fogos = 450
        self.velocidade_fogo_y = 8

        self.jogando = True
        self.vitoria = False
        self.proximo = False
        self.mostrar_botao_continuar = False
        self.botao_continuar_rect = None
        self.botao_continuar_hover = False

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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.rodando = False
                    return "voltar"
                # Pulo (apenas se não estiver na vitória)
                if not self.vitoria:
                    if (event.key == pygame.K_SPACE or event.key == pygame.K_UP or event.key == pygame.K_w) and self.no_chao:
                        self.vel_y = self.forca_pulo
                        self.no_chao = False
                # Avançar com tecla se estiver na vitória e botão visível
                if self.vitoria and self.mostrar_botao_continuar:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.rodando = False
                        self.proximo = True
                        return "proximo"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.vitoria and self.mostrar_botao_continuar and self.botao_continuar_rect and self.botao_continuar_rect.collidepoint(mouse_pos):
                    self.rodando = False
                    self.proximo = True
                    return "proximo"
        return None

    def update(self):
        if self.vitoria:
            return

        # Movimento horizontal
        keys = pygame.key.get_pressed()
        velocidade_h = 10
        movendo = False
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.pos_inv_x -= velocidade_h
            movendo = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.pos_inv_x += velocidade_h
            movendo = True

        self.vel_y += self.gravidade
        self.pos_inv_y += self.vel_y

        if self.pos_inv_y >= self.pos_inv_y_chao:
            self.pos_inv_y = self.pos_inv_y_chao
            self.vel_y = 0
            self.no_chao = True

        from config.settings import TELA_LARGURA
        limite_dir = TELA_LARGURA - self.investigador_rect.width
        self.pos_inv_x = max(0, min(self.pos_inv_x, limite_dir))
        
        self.investigador_rect.x = self.pos_inv_x
        self.investigador_rect.y = self.pos_inv_y

        # Vitória (chegou ao final)
        if self.pos_inv_x >= limite_dir - 10:
            self.vitoria = True
            self.mostrar_botao_continuar = True
            return

        # Sprite atual
        if not self.no_chao:
            self.investigador_img_atual = self.sprite_pulando
        elif movendo:
            self.investigador_img_atual = self.sprite_correndo
        else:
            self.investigador_img_atual = self.sprite_parado

        # Rolagem do fundo
        self.fundo_x1 -= self.velocidade_fundo
        self.fundo_x2 -= self.velocidade_fundo
        if self.fundo_x1 <= -self.fundo_largura:
            self.fundo_x1 = self.fundo_largura
        if self.fundo_x2 <= -self.fundo_largura:
            self.fundo_x2 = self.fundo_largura

        # Spawn de fogos
        agora = pygame.time.get_ticks()
        if agora - self.tempo_ultimo_fogo > self.intervalo_fogos:
            x_fogo = random.randint(0, TELA_LARGURA)
            self.fogos.append(Fogo(x_fogo, -100, self.fogo_img, self.velocidade_fogo_y, self.escala))
            self.tempo_ultimo_fogo = agora

        # Update e Colisão
        for fogo in self.fogos[:]:
            fogo.update()
            hitbox_inv = self.investigador_rect.inflate(-self.personagem_largura//2, -self.personagem_altura//3)
            if hitbox_inv.colliderect(fogo.rect):
                self.resetar_jogo()
                return
            if fogo.rect.y > TELA_ALTURA_PADRAO:
                self.fogos.remove(fogo)

        self.update_vagalumes()

    def draw(self):
        from config.settings import TELA_LARGURA, TELA_ALTURA
        if self.fundo_img:
            self.tela.blit(self.fundo_img, (self.fundo_x1, 0))
            self.tela.blit(self.fundo_img, (self.fundo_x2, 0))
        else:
            self.tela.fill(PRETO)

        self.draw_vagalumes()
        for fogo in self.fogos:
            fogo.draw(self.tela)

        self.tela.blit(self.investigador_img_atual, self.investigador_rect)

        # Instruções
        if self.jogando and not self.vitoria:
            texto = self.fonte_instrucoes.render("Setas: Mover Espaço: Pular", True, BRANCO)
            self.tela.blit(texto, (20, TELA_ALTURA - 40))

        # Tela de vitória
        if self.vitoria:
            overlay = pygame.Surface((TELA_LARGURA, TELA_ALTURA), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.tela.blit(overlay, (0, 0))
            
            linhas = [
                "O Curupira tentou afastá-lo da floresta,",
                "mas você foi insistente e seguiu em frente.",
                "Agora, um novo desafio o aguarda.",
                "Será que você conseguirá resistir aos encantos da Iara?"
            ]
            
            y_offset = TELA_ALTURA//2 - 100
            for linha in linhas:
                surf = self.fonte.render(linha, True, AMARELO_HISTORIA)
                self.tela.blit(surf, (TELA_LARGURA//2 - surf.get_width()//2, y_offset))
                y_offset += 50

            # Botão CONTINUAR (sem bordas) no canto inferior direito
            if self.mostrar_botao_continuar:
                cor_botao = VERDE if self.botao_continuar_hover else BRANCO
                texto_botao = self.fonte_botao.render("CONTINUAR", True, cor_botao)
                botao_rect = texto_botao.get_rect()
                botao_rect.bottomright = (TELA_LARGURA - 50, TELA_ALTURA - 50)
                self.botao_continuar_rect = botao_rect
                self.tela.blit(texto_botao, botao_rect)
            else:
                self.botao_continuar_rect = None

        pygame.display.flip()

    def run(self):
        self.proximo = False
        while self.rodando:
            acao = self.handle_events()
            if acao:
                return acao
            self.update()
            self.draw()
            self.clock.tick(60)
        return "proximo" if self.proximo else "voltar"