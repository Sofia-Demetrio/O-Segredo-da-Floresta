# scenes/minigame_iara.py

import os
import pygame
from config.settings import TELA_LARGURA_PADRAO, TELA_ALTURA_PADRAO
from config.utils import redimensionar_fonte
from scenes.base_scene import BaseScene

BRANCO = (245, 230, 163)
PRETO = (17, 36, 41)
VERDE = (112, 163, 162)
AMARELO_HISTORIA = (245, 230, 163)
MARROM = (139, 69, 19)
AZUL_AGUA = (50, 100, 150)

PERSONAGEM_LARGURA_BASE = 240
PERSONAGEM_ALTURA_BASE = 240
PLATAFORMA_LARGURA_BASE = 280
PLATAFORMA_ALTURA_BASE = 40
COR_PLATAFORMA = VERDE
COR_BORDA_PLATAFORMA = (80, 130, 130)


class PlataformaRetangular:
    def __init__(self, x_mundo, y_mundo, largura, altura):
        self.rect = pygame.Rect(x_mundo, y_mundo, largura, altura)

    def desenhar(self, surface, offset_x):
        rect_tela = self.rect.move(-offset_x, 0)
        pygame.draw.rect(surface, COR_PLATAFORMA, rect_tela)
        pygame.draw.rect(surface, COR_BORDA_PLATAFORMA, rect_tela, 2)

    def checar_colisao(self, player_rect, vel_y):
 
        if vel_y < 0:
            return False  
        if player_rect.centerx < self.rect.left or player_rect.centerx > self.rect.right:
            return False
        if player_rect.bottom >= self.rect.top and player_rect.top <= self.rect.bottom:
            return True
        return False


class MinigameIara(BaseScene):
    def __init__(self, tela, clock):
        super().__init__(tela, clock)
        pygame.display.set_caption("Minigame - Iara: Travessia do Rio")
        self.pasta_do_script = os.path.dirname(os.path.abspath(__file__))

        from config.settings import FATOR_ESCALA_X, FATOR_ESCALA_Y
        self.escala = min(FATOR_ESCALA_X, FATOR_ESCALA_Y)

        self.personagem_largura = int(PERSONAGEM_LARGURA_BASE * self.escala)
        self.personagem_altura = int(PERSONAGEM_ALTURA_BASE * self.escala)

        self.sprite_correndo = self.carregar_sprite("correndo.png", 
                                                    (self.personagem_largura, self.personagem_altura))
        self.sprite_pulando = self.carregar_sprite("pulando.png", 
                                                   (self.personagem_largura, self.personagem_altura))

        self.fundo_img = None
        caminho_fundo = os.path.join(self.pasta_do_script, "..", "assets", "images", "iara.jpg")
        caminho_fundo = os.path.normpath(caminho_fundo)
        try:
            self.fundo_img = pygame.image.load(caminho_fundo)
            escala_fundo = TELA_ALTURA_PADRAO / self.fundo_img.get_height()
            nova_largura = int(self.fundo_img.get_width() * escala_fundo)
            self.fundo_img = pygame.transform.scale(self.fundo_img, (nova_largura, TELA_ALTURA_PADRAO))
            self.fundo_largura = nova_largura
        except:
            print("AVISO: iara.jpg não encontrado. Usando fundo azul água.")
            self.fundo_img = None
            self.fundo_largura = TELA_LARGURA_PADRAO

        self.carregar_fontes()
        self.init_vagalumes(10)

        self.som_iara = None
        caminho_som = os.path.join(self.pasta_do_script, "..", "assets", "sounds",
                                   "alesiadavina-a-sirenx27s-song-207057.mp3")
        caminho_som = os.path.normpath(caminho_som)
        try:
            self.som_iara = pygame.mixer.Sound(caminho_som)
            self.som_iara.set_volume(0.5) 
            print("Música da Iara carregada como som sobreposto.")
        except Exception as e:
            print(f"AVISO: Não foi possível carregar o som da Iara: {e}")

        self.som_digitacao = None
        caminho_tecla = os.path.join(self.pasta_do_script, "..", "assets", "sounds", "magiaz-teclado-371741.mp3")
        caminho_tecla = os.path.normpath(caminho_tecla)
        try:
            self.som_digitacao = pygame.mixer.Sound(caminho_tecla)
            self.som_digitacao.set_volume(0.2)
        except:
            pass

        self.dialogo_vencedor = False
        self.texto_dialogo = ("Você é mais teimoso do que eu imaginava. Esta floresta guarda segredos que jamais deveriam ser descobertos, e ainda assim você continua avançando.\n\nMas diga-me... quando a verdade finalmente se revelar, será que conseguirá aceitá-la?\n\nOu será consumido pelas ilusões do Boitatá antes mesmo de encontrar as respostas que procura?")
        self.dialogo_texto_atual = ""
        self.dialogo_indice = 0
        self.dialogo_tempo_ultimo = 0
        self.dialogo_completo = False
        self.dialogo_linhas = []
        self.botao_continuar_rect = None
        self.botao_continuar_hover = False

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
            surf.fill(MARROM)
            return surf

    def carregar_fontes(self):
        caminho_fontes = os.path.join(self.pasta_do_script, "..", "assets", "fonts")
        tamanho = redimensionar_fonte(48)
        try:
            fonte = os.path.join(caminho_fontes, "Aquifer.ttf")
            self.fonte = pygame.font.Font(fonte, tamanho)
        except:
            self.fonte = pygame.font.Font(None, tamanho)

    def criar_plataformas(self):
        self.plataformas = []
        largura_plat = int(PLATAFORMA_LARGURA_BASE * self.escala)
        altura_plat = int(PLATAFORMA_ALTURA_BASE * self.escala)

        num_plataformas = max(8, int(self.fundo_largura / (largura_plat * 1.8)))
        y_mundo = TELA_ALTURA_PADRAO - int(160 * self.escala)
        espacamento = (self.fundo_largura - largura_plat) / (num_plataformas - 1) if num_plataformas > 1 else 0

        for i in range(num_plataformas):
            x_mundo = i * espacamento
            plat = PlataformaRetangular(x_mundo, y_mundo, largura_plat, altura_plat)
            self.plataformas.append(plat)

    def resetar_jogo(self):
        self.criar_plataformas()
        primeira_plat = self.plataformas[0]
        self.pos_inv_x_mundo = primeira_plat.rect.x + (primeira_plat.rect.width // 2) - (self.personagem_largura // 2)
        self.pos_inv_y_mundo = primeira_plat.rect.y - self.personagem_altura

        self.personagem_rect_mundo = pygame.Rect(
            self.pos_inv_x_mundo,
            self.pos_inv_y_mundo,
            self.personagem_largura,
            self.personagem_altura
        )

        self.vel_y = 0
        self.gravidade = 0.8
        self.forca_pulo = -22
        self.no_chao = True

        self.camera_offset = 0
        self.venceu = False
        self.jogando = True

        self.investigador_img_atual = self.sprite_correndo
        self.atualizar_rect_personagem()

        self.tempo_vitoria = 0
        self.proximo = False

        self.dialogo_vencedor = False
        self.dialogo_texto_atual = ""
        self.dialogo_indice = 0
        self.dialogo_completo = False
        self.dialogo_linhas = []

    def atualizar_rect_personagem(self):
        self.personagem_rect_mundo.x = self.pos_inv_x_mundo
        self.personagem_rect_mundo.y = self.pos_inv_y_mundo

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
                if self.venceu and self.dialogo_completo:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.rodando = False
                        self.proximo = True
                        return "proximo"
                if self.jogando and not self.venceu:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        if self.no_chao:
                            self.vel_y = self.forca_pulo
                            self.no_chao = False
                    if event.key == pygame.K_r:
                        self.resetar_jogo()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.venceu and self.dialogo_completo and self.botao_continuar_rect and self.botao_continuar_hover:
                    self.rodando = False
                    self.proximo = True
                    return "proximo"
                if self.venceu and not self.dialogo_completo:
                    self.pular_digitacao_dialogo()
        return None

    def pular_digitacao_dialogo(self):
        if not self.dialogo_completo:
            self.dialogo_indice = len(self.texto_dialogo)
            self.dialogo_texto_atual = self.texto_dialogo
            self.dialogo_completo = True
            if self.som_digitacao:
                self.som_digitacao.stop()
            self.dialogo_linhas = self.quebrar_texto_dialogo(self.texto_dialogo)

    def quebrar_texto_dialogo(self, texto):
        palavras = texto.split(' ')
        linhas = []
        linha_atual = ""
        fonte_dialogo = self.fonte  
        largura_max = int(TELA_LARGURA_PADRAO * 0.8) 
        for palavra in palavras:
            teste = linha_atual + palavra + " "
            if fonte_dialogo.size(teste)[0] < largura_max:
                linha_atual = teste
            else:
                if linha_atual:
                    linhas.append(linha_atual)
                linha_atual = palavra + " "
        if linha_atual:
            linhas.append(linha_atual)
        return linhas

    def atualizar_dialogo(self):
        if not self.venceu or self.dialogo_completo:
            return
        agora = pygame.time.get_ticks()
        if agora - self.dialogo_tempo_ultimo > 35:
            if self.dialogo_indice < len(self.texto_dialogo):
                self.dialogo_indice += 1
                self.dialogo_tempo_ultimo = agora
                self.dialogo_texto_atual = self.texto_dialogo[:self.dialogo_indice]
                # Toca o som de digitação
                if self.som_digitacao and not self.som_digitacao.get_num_channels():
                    self.som_digitacao.play()
            else:
                self.dialogo_completo = True
                if self.som_digitacao:
                    self.som_digitacao.stop()
                self.dialogo_linhas = self.quebrar_texto_dialogo(self.texto_dialogo)

    def update(self):
        if self.venceu:
            self.atualizar_dialogo()
            return

        if not self.jogando:
            return

        keys = pygame.key.get_pressed()
        velocidade_h = 6
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.pos_inv_x_mundo += velocidade_h
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.pos_inv_x_mundo -= velocidade_h * 0.6

        self.pos_inv_x_mundo = max(0, min(self.pos_inv_x_mundo, 
                                          self.fundo_largura - self.personagem_largura))
        self.atualizar_rect_personagem()

        self.vel_y += self.gravidade
        self.pos_inv_y_mundo += self.vel_y
        self.atualizar_rect_personagem()

        self.no_chao = False
        for plat in self.plataformas:
            if plat.checar_colisao(self.personagem_rect_mundo, self.vel_y):
                self.pos_inv_y_mundo = plat.rect.top - self.personagem_altura
                self.vel_y = 0
                self.no_chao = True
                self.atualizar_rect_personagem()

                if self.pos_inv_x_mundo >= (self.fundo_largura - self.personagem_largura * 1.2):
                    self.venceu = True
                    self.tempo_vitoria = pygame.time.get_ticks()
                    self.jogando = False
                    self.dialogo_vencedor = True
                    self.dialogo_indice = 0
                    self.dialogo_tempo_ultimo = pygame.time.get_ticks()
                    self.dialogo_completo = False
                    self.dialogo_texto_atual = ""
                    
                    if self.som_digitacao:
                        self.som_digitacao.play(-1)  
                break 

        if self.pos_inv_y_mundo > TELA_ALTURA_PADRAO + 50:
            self.resetar_jogo()
            return

        self.investigador_img_atual = self.sprite_pulando if not self.no_chao else self.sprite_correndo

        self.camera_offset = self.pos_inv_x_mundo - (TELA_LARGURA_PADRAO // 2 - self.personagem_largura // 2)
        self.camera_offset = max(0, min(self.camera_offset, self.fundo_largura - TELA_LARGURA_PADRAO))

        self.update_vagalumes()

    def draw(self):
        if self.fundo_img:
            self.tela.blit(self.fundo_img, (-self.camera_offset, 0))
            if self.fundo_largura - self.camera_offset < TELA_LARGURA_PADRAO:
                self.tela.blit(self.fundo_img, (self.fundo_largura - self.camera_offset, 0))
        else:
            self.tela.fill(AZUL_AGUA)

        self.draw_vagalumes()
        for plat in self.plataformas:
            plat.desenhar(self.tela, self.camera_offset)

        rect_tela = pygame.Rect(
            self.personagem_rect_mundo.x - self.camera_offset,
            self.personagem_rect_mundo.y,
            self.personagem_rect_mundo.width,
            self.personagem_rect_mundo.height
        )
        self.tela.blit(self.investigador_img_atual, rect_tela)

        if self.jogando and not self.venceu:
            texto = self.fonte.render("Como jogar: Setas: Mover Segurar espaço: Pular R: Reiniciar jogo", True, BRANCO)
            self.tela.blit(texto, (5, TELA_ALTURA_PADRAO - 80))

        if self.venceu:
            overlay = pygame.Surface((TELA_LARGURA_PADRAO, TELA_ALTURA_PADRAO), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.tela.blit(overlay, (0, 0))

            if self.dialogo_linhas:
                
                y_offset = int(TELA_ALTURA_PADRAO * 0.2)
                for i, linha in enumerate(self.dialogo_linhas):
                    if i >= 15:  
                        break
                    texto_surf = self.fonte.render(linha.strip(), True, AMARELO_HISTORIA)
                    x_center = (TELA_LARGURA_PADRAO - texto_surf.get_width()) // 2
                    self.tela.blit(texto_surf, (x_center, y_offset + i * 45))
            else:
            
                texto_parcial = self.dialogo_texto_atual
                
                linhas_temp = self.quebrar_texto_dialogo(texto_parcial)
                y_offset = int(TELA_ALTURA_PADRAO * 0.2)
                for i, linha in enumerate(linhas_temp):
                    if i >= 15:
                        break
                    texto_surf = self.fonte.render(linha.strip(), True, AMARELO_HISTORIA)
                    x_center = (TELA_LARGURA_PADRAO - texto_surf.get_width()) // 2
                    self.tela.blit(texto_surf, (x_center, y_offset + i * 45))

            
            if self.dialogo_completo:
                texto_continuar = self.fonte.render("CONTINUAR", True, BRANCO)
                if self.botao_continuar_hover:
                    texto_continuar = self.fonte.render("CONTINUAR", True, VERDE)
                rect_cont = texto_continuar.get_rect()
            
                rect_cont.bottomright = (TELA_LARGURA_PADRAO - 30, TELA_ALTURA_PADRAO - 30)
                self.botao_continuar_rect = rect_cont
                self.tela.blit(texto_continuar, rect_cont)
            else:
                self.botao_continuar_rect = None

        pygame.display.flip()

    def resize_resources(self):
        super().resize_resources()
        self.resetar_jogo()

    def run(self):
        
        canal_iara = None
        if self.som_iara:
            try:
                canal_iara = self.som_iara.play(-1)
                if canal_iara:
                    canal_iara.set_volume(0.6)
            except Exception as e:
                print(f"Erro ao tocar som da Iara: {e}")

        self.proximo = False
        while self.rodando:
            acao = self.handle_events()
            if acao:
                if canal_iara:
                    canal_iara.stop()
                if self.som_digitacao:
                    self.som_digitacao.stop()
                return acao
            self.update()
            self.draw()
            self.clock.tick(60)

        if canal_iara:
            canal_iara.stop()
        if self.som_digitacao:
            self.som_digitacao.stop()
        return "proximo" if self.proximo else "voltar"