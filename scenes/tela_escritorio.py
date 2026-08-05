# scenes/tela_escritorio.py

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


class TelaEscritorio(BaseScene):
    def __init__(self, tela, clock):
        super().__init__(tela, clock)
        pygame.display.set_caption("Investigação - Arquivos de Arandu")

        self.pasta_do_script = os.path.dirname(os.path.abspath(__file__))

       
        caminho_fundo = os.path.join(self.pasta_do_script, "..", "assets", "images", "pasta.png")
        caminho_fundo = os.path.normpath(caminho_fundo)
        try:
            self.imagem_fundo_original = pygame.image.load(caminho_fundo)
        except:
            print("AVISO: Imagem 'pasta.png' não encontrada.")
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

        
        self.som_pagina = None
        caminho_pagina = os.path.join(self.pasta_do_script, "..", "assets", "sounds", "freesound_community-pageturn-102978.mp3")
        caminho_pagina = os.path.normpath(caminho_pagina)
        try:
            self.som_pagina = pygame.mixer.Sound(caminho_pagina)
            self.som_pagina.set_volume(0.4)
        except:
            print("AVISO: Som de página não encontrado.")

        self.init_vagalumes(20)
        self.carregar_fontes()

        
        self.area_papel_base = pygame.Rect(806, 172, 380, 485)
        self.angulo_rotacao = -0.8

        self.menu_botoes_base = [
            {"texto": "Diário da Expedição",   "arquivo": "diario.txt",    "pos": (40, 80)},
            {"texto": "Lendas e Figuras",      "arquivo": "lendas.txt",    "pos": (40, 160)},
            {"texto": "Notícias da Época",     "arquivo": "noticias.txt",  "pos": (40, 240)},
        ]
        self.botoes_menu = []
        self.botao_continuar = {"texto": "CONTINUAR", "rect": None}
        self.texto_atual = ""

        self.opcao_selecionada = "diario.txt"

        
        self.mostrando_balao = False
        self.texto_balao_completo = (
            "Com todas as informações que reuni ao longo desses últimos cinco anos, "
            "estou pronto para entrar na mata e trazer minha irmã de volta para casa."
        )
        self.balao_texto_atual = ""
        self.balao_indice = 0
        self.balao_tempo_ultimo = 0
        self.balao_texto_completo_gerado = False
        self.balao_linhas = []
        self.botao_seguir_rect = None
        self.botao_seguir_hover = False
        self.espaco_imagem_base = 170
        self.atualizar_balao()

        
        self.carregar_arquivo("diario.txt")
        self.atualizar_botoes()

    def carregar_fontes(self):
        caminho_fontes = os.path.join(self.pasta_do_script, "..", "assets", "fonts")
        caminho_fontes = os.path.normpath(caminho_fontes)

        tamanho_menu = redimensionar_fonte(36)
        tamanho_texto = redimensionar_fonte(18)
        tamanho_balao = redimensionar_fonte(32)
        tamanho_botao_balao = redimensionar_fonte(36)

        
        try:
            caminho_fonte_aquifer = os.path.join(caminho_fontes, "Aquifer.ttf")
            self.fonte_menu = pygame.font.Font(caminho_fonte_aquifer, tamanho_menu)
            self.fonte_texto = pygame.font.Font(caminho_fonte_aquifer, tamanho_texto)
            self.fonte_balao = pygame.font.Font(caminho_fonte_aquifer, tamanho_balao)
            self.fonte_botao_balao = pygame.font.Font(caminho_fonte_aquifer, tamanho_botao_balao)
        except:
            try:
                caminho_fonte_aquifer_otf = os.path.join(caminho_fontes, "Aquifer.otf")
                self.fonte_menu = pygame.font.Font(caminho_fonte_aquifer_otf, tamanho_menu)
                self.fonte_texto = pygame.font.Font(caminho_fonte_aquifer_otf, tamanho_texto)
                self.fonte_balao = pygame.font.Font(caminho_fonte_aquifer_otf, tamanho_balao)
                self.fonte_botao_balao = pygame.font.Font(caminho_fonte_aquifer_otf, tamanho_botao_balao)
            except:
                
                try:
                    fonte_path = os.path.join(caminho_fontes, "Roman_New_Times.otf")
                    self.fonte_menu = pygame.font.Font(fonte_path, tamanho_menu)
                    self.fonte_texto = pygame.font.Font(fonte_path, tamanho_texto)
                    self.fonte_balao = pygame.font.Font(fonte_path, tamanho_balao)
                    self.fonte_botao_balao = pygame.font.Font(fonte_path, tamanho_botao_balao)
                except:
                    
                    self.fonte_menu = pygame.font.Font(None, tamanho_menu)
                    self.fonte_texto = pygame.font.Font(None, tamanho_texto)
                    self.fonte_balao = pygame.font.Font(None, tamanho_balao)
                    self.fonte_botao_balao = pygame.font.Font(None, tamanho_botao_balao)

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

    def atualizar_botoes(self):
        from config.settings import FATOR_ESCALA_X, FATOR_ESCALA_Y, TELA_LARGURA, TELA_ALTURA

       
        self.botoes_menu = []
        for btn in self.menu_botoes_base:
            x = int(btn["pos"][0] * FATOR_ESCALA_X)
            y = int(btn["pos"][1] * FATOR_ESCALA_Y)
            texto_render = self.fonte_menu.render(btn["texto"], True, BRANCO)
            rect = texto_render.get_rect(topleft=(x, y))
            self.botoes_menu.append({
                "texto": btn["texto"],
                "arquivo": btn["arquivo"],
                "rect": rect,
                "texto_renderizado": texto_render
            })

        texto_continuar = self.fonte_menu.render("CONTINUAR", True, BRANCO)
        continuar_x = TELA_LARGURA - texto_continuar.get_width() - int(40 * FATOR_ESCALA_X)
        continuar_y = TELA_ALTURA - int(50 * FATOR_ESCALA_Y)
        self.botao_continuar["texto"] = texto_continuar
        self.botao_continuar["rect"] = texto_continuar.get_rect(topleft=(continuar_x, continuar_y))

    def carregar_arquivo(self, nome_arquivo):
        self.opcao_selecionada = nome_arquivo
        caminho_base = os.path.join(self.pasta_do_script, "..", "data")
        caminho_arquivo = os.path.join(caminho_base, nome_arquivo)
        caminho_arquivo = os.path.normpath(caminho_arquivo)
        try:
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                self.texto_atual = f.read()
        except FileNotFoundError:
            self.texto_atual = f"[Arquivo não encontrado: {nome_arquivo}]\n\nCrie o arquivo em:\n{caminho_arquivo}"
        except Exception as e:
            self.texto_atual = f"Erro ao ler arquivo: {str(e)}"

    def iniciar_balao(self):
        self.mostrando_balao = True
        self.balao_texto_atual = ""
        self.balao_indice = 0
        self.balao_texto_completo_gerado = False
        self.balao_linhas = []
        self.balao_tempo_ultimo = pygame.time.get_ticks()
        self.som_tocando = False
        if self.som_digitacao:
            self.som_digitacao.play(-1)
            self.som_tocando = True

    def parar_som_balao(self):
        if self.som_digitacao and self.som_tocando:
            self.som_digitacao.stop()
            self.som_tocando = False

    def atualizar_balao_escrita(self):
        if not self.mostrando_balao or self.balao_texto_completo_gerado:
            return
        tempo_atual = pygame.time.get_ticks()
        if tempo_atual - self.balao_tempo_ultimo > 35:
            if self.balao_indice < len(self.texto_balao_completo):
                self.balao_indice += 1
                self.balao_tempo_ultimo = tempo_atual
                self.balao_texto_atual = self.texto_balao_completo[:self.balao_indice]
            else:
                self.balao_texto_completo_gerado = True
                self.parar_som_balao()

    def quebrar_texto_balao(self, texto, largura_maxima):
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

    def pular_digitacao_balao(self):
        if not self.balao_texto_completo_gerado:
            self.parar_som_balao()
            self.balao_indice = len(self.texto_balao_completo)
            self.balao_texto_completo_gerado = True
            self.balao_texto_atual = self.texto_balao_completo
            self.balao_linhas = []  
    def desenhar_balao(self):
        from config.settings import TELA_LARGURA, TELA_ALTURA, FATOR_ESCALA_X, FATOR_ESCALA_Y

        
        overlay = pygame.Surface((TELA_LARGURA, TELA_ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
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

        
        texto_para_quebrar = self.balao_texto_atual if not self.balao_texto_completo_gerado else self.texto_balao_completo
        largura_max_texto = self.balao_largura - 60
        linhas = self.quebrar_texto_balao(texto_para_quebrar, largura_max_texto)

        espacamento_linha = redimensionar_fonte(38)
        inicio_texto_y = self.balao_y + redimensionar_fonte(40)
        for i, linha in enumerate(linhas):
            texto_renderizado = self.fonte_balao.render(linha.strip(), True, BRANCO)
            self.tela.blit(texto_renderizado, (self.balao_x + redimensionar_fonte(35), inicio_texto_y + i * espacamento_linha))

        
        if self.balao_texto_completo_gerado:
            texto_seguir = self.fonte_botao_balao.render("SEGUIR", True, BRANCO)
            seguir_rect = texto_seguir.get_rect()
            seguir_rect.bottomright = (self.balao_rect.right - 40, self.balao_rect.bottom - 20)
            self.botao_seguir_rect = seguir_rect

            mouse_pos = pygame.mouse.get_pos()
            cor_seguir = VERDE if self.botao_seguir_rect.collidepoint(mouse_pos) else BRANCO
            texto_seguir_render = self.fonte_botao_balao.render("SEGUIR", True, cor_seguir)
            self.tela.blit(texto_seguir_render, self.botao_seguir_rect)
        else:
            self.botao_seguir_rect = None

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.rodando = False
                return "sair"
            if event.type == pygame.VIDEORESIZE:
                self.handle_resize(event)

            if self.mostrando_balao:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.botao_seguir_rect and self.botao_seguir_rect.collidepoint(event.pos):
                        self.parar_som_balao()
                        self.mostrando_balao = False
                        return "proximo"
                    else:
                        if not self.balao_texto_completo_gerado:
                            self.pular_digitacao_balao()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        if self.balao_texto_completo_gerado:
                            self.parar_som_balao()
                            self.mostrando_balao = False
                            return "proximo"
                        else:
                            self.pular_digitacao_balao()
                continue

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for btn in self.botoes_menu:
                    if btn["rect"].collidepoint(mouse_pos):
                        if self.som_pagina:
                            self.som_pagina.play()
                        self.carregar_arquivo(btn["arquivo"])

                if self.botao_continuar["rect"] and self.botao_continuar["rect"].collidepoint(mouse_pos):
                    self.iniciar_balao()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.rodando = False
                    return "voltar"
        return None

    def resize_resources(self):
        super().resize_resources()
        self.atualizar_balao()
        self.atualizar_botoes()
        self.carregar_fontes()

    def reload_fonts(self):
        self.carregar_fontes()
        self.atualizar_botoes()

    def renderizar_texto_rotacionado(self, texto, rect_area):
        
        surf = pygame.Surface((rect_area.width, rect_area.height), pygame.SRCALPHA)
        margem_x = int(rect_area.width * 0.08)
        margem_y = int(rect_area.height * 0.08)
        largura_texto = rect_area.width - margem_x * 2
        altura_linha = self.fonte_texto.get_height() + 6

        
        palavras = texto.split(' ')
        linhas = []
        linha_atual = ""
        for palavra in palavras:
            teste = linha_atual + palavra + " "
            if self.fonte_texto.size(teste)[0] < largura_texto:
                linha_atual = teste
            else:
                if linha_atual:
                    linhas.append(linha_atual)
                linha_atual = palavra + " "
        if linha_atual:
            linhas.append(linha_atual)

        y_offset = margem_y
        for linha in linhas:
            if y_offset + altura_linha > rect_area.height - margem_y:
                break
            
            texto_surf = self.fonte_texto.render(linha, True, (0, 0, 0))
            surf.blit(texto_surf, (margem_x, y_offset))
            y_offset += altura_linha

        texto_rotacionado = pygame.transform.rotate(surf, self.angulo_rotacao)
        novo_rect = texto_rotacionado.get_rect(center=rect_area.center)
        return texto_rotacionado, novo_rect

    def draw(self):
        from config.settings import TELA_LARGURA, TELA_ALTURA, FATOR_ESCALA_X, FATOR_ESCALA_Y

        self.draw_background()
        self.draw_vagalumes()

        overlay = pygame.Surface((TELA_LARGURA, TELA_ALTURA))
        overlay.set_alpha(160)
        overlay.fill(PRETO)
        self.tela.blit(overlay, (0, 0))

        rect_papel_atual = pygame.Rect(
            int(self.area_papel_base.x * FATOR_ESCALA_X),
            int(self.area_papel_base.y * FATOR_ESCALA_Y),
            int(self.area_papel_base.width * FATOR_ESCALA_X),
            int(self.area_papel_base.height * FATOR_ESCALA_Y)
        )
        texto_img, texto_rect = self.renderizar_texto_rotacionado(self.texto_atual, rect_papel_atual)
        self.tela.blit(texto_img, texto_rect)

        mouse_pos = pygame.mouse.get_pos()
        for btn in self.botoes_menu:
            if btn["arquivo"] == self.opcao_selecionada:
                cor = VERDE
            else:
                cor = VERDE if btn["rect"].collidepoint(mouse_pos) else BRANCO
            texto_render = self.fonte_menu.render(btn["texto"], True, cor)
            self.tela.blit(texto_render, btn["rect"].topleft)

        if self.botao_continuar["rect"]:
            cor_cont = VERDE if self.botao_continuar["rect"].collidepoint(mouse_pos) else BRANCO
            self.tela.blit(self.botao_continuar["texto"], self.botao_continuar["rect"].topleft)

        if self.mostrando_balao:
            self.desenhar_balao()

        pygame.display.flip()

    def run(self):
        self.atualizar_botoes()
        while self.rodando:
            acao = self.handle_events()
            if acao == "proximo":
                return "proximo"
            if acao == "sair":
                return "sair"
            if acao == "voltar":
                return "voltar"

            self.update_vagalumes()
            if self.mostrando_balao:
                self.atualizar_balao_escrita()
            self.draw()
            self.clock.tick(60)
        return "voltar"