# scenes/tela_multiplayer.py

import os
import random
import pygame
from config.settings import (
    TELA_LARGURA_PADRAO, TELA_ALTURA_PADRAO,
    BRANCO, PRETO, VERDE, VERMELHO, CINZA_ESCURO, AMARELO_HISTORIA
)
from config.utils import redimensionar_fonte, redimensionar_imagem
from scenes.base_scene import BaseScene


class TelaMultiplayer(BaseScene):
    def __init__(self, tela, clock):
        super().__init__(tela, clock)
        pygame.display.set_caption("Marciano vs Caçador - Desafio Final")
        self.pasta_do_script = os.path.dirname(os.path.abspath(__file__))

        caminho_fundo = os.path.join(self.pasta_do_script, "..", "assets", "images", "cenario_1.jpg")
        try:
            self.imagem_fundo_original = pygame.image.load(caminho_fundo)
        except:
            self.imagem_fundo_original = None
        self.imagem_fundo = redimensionar_imagem(
            self.imagem_fundo_original, TELA_LARGURA_PADRAO, TELA_ALTURA_PADRAO
        )

        self.desaparecimento_img = None
        self.desaparecimento_fundo = None
        caminho_desaparecimento = os.path.join(self.pasta_do_script, "..", "assets", "images", "desaparecimento.png")
        try:
            self.desaparecimento_img = pygame.image.load(caminho_desaparecimento).convert()
            self.desaparecimento_fundo = pygame.transform.scale(
                self.desaparecimento_img, (TELA_LARGURA_PADRAO, TELA_ALTURA_PADRAO)
            )
        except:
            print("AVISO: desaparecimento.png não encontrado. Usando fundo preto.")
            self.desaparecimento_img = None
            self.desaparecimento_fundo = None

        self.despedida_img = None
        self.despedida_fundo = None
        caminho_despedida = os.path.join(self.pasta_do_script, "..", "assets", "images", "despedida.png")
        try:
            self.despedida_img = pygame.image.load(caminho_despedida).convert()
            self.despedida_fundo = pygame.transform.scale(
                self.despedida_img, (TELA_LARGURA_PADRAO, TELA_ALTURA_PADRAO)
            )
        except:
            print("AVISO: despedida.png não encontrado. Usando fundo preto.")
            self.despedida_img = None
            self.despedida_fundo = None

        self.init_vagalumes(30)

        self.carregar_fontes()

        self.coracao_img = None
        caminho_coracao = os.path.join(self.pasta_do_script, "..", "assets", "images", "coracao.png")
        try:
            self.coracao_img = pygame.image.load(caminho_coracao).convert_alpha()
        except:
            print("AVISO: coracao.png não encontrado. Usando círculo.")

        self.som_digitacao = None
        self.som_tocando = False
        caminho_som = os.path.join(self.pasta_do_script, "..", "assets", "sounds", "magiaz-teclado-371741.mp3")
        try:
            self.som_digitacao = pygame.mixer.Sound(caminho_som)
            self.som_digitacao.set_volume(0.25)
        except:
            pass

        self.estado = "dialogo_inicial"  
                                         
        self.arvore_escondida = 0
        self.tentativas = 0
        self.max_tentativas = 5
        self.mensagem = ""
        self.mensagem_cor = AMARELO_HISTORIA
        self.game_over_tipo = None
        self.input_texto = ""
        self.input_ativo = True

        
        self.dialogo_texto_completo = (
            "Quando percebeu que você não desistiria, o ser que os guardiões protegiam se escondeu "
            "entre as árvores da floresta. Agora, oculto em meio a centenas de possibilidades, ele aguarda.\n\n"
            "Você terá apenas 5 chances para encontrá-lo.\n\n"
            "Talvez, ao encontrá-lo, descubra finalmente as respostas que tanto procurou."
        )
        self.dialogo_texto_atual = ""
        self.dialogo_indice = 0
        self.dialogo_tempo_ultimo = 0
        self.dialogo_completo_gerado = False
        self.dialogo_linhas = []
        self.botao_continuar_rect = None
        self.botao_continuar_hover = False

        
        self.botao_voltar_rect = None
        self.botao_voltar_hover = False
        self.botao_voltar_inicio_rect = None
        self.botao_voltar_inicio_hover = False
        self.botao_voltar_menu_rect = None   
        self.botao_voltar_menu_hover = False

        
        self.tempo_derrota = 0
        self.derrota_texto_exibido = False
        self.tempo_vitoria_mensagem = 0
        self.vitoria_mensagem_exibida = False

        self.iniciar_digitacao()

    def carregar_fontes(self):
        
        caminho_fontes = os.path.join(self.pasta_do_script, "..", "assets", "fonts")
        tamanhos = {
            "titulo": 48,
            "texto": 32,
            "pequena": 24,
            "dialogo": 30,
            "botao": 36
        }
        tamanhos = {k: redimensionar_fonte(v) for k, v in tamanhos.items()}

        
        fonte_path = None
        for ext in [".ttf", ".otf"]:
            tentativa = os.path.join(caminho_fontes, f"Aquifer{ext}")
            if os.path.exists(tentativa):
                fonte_path = tentativa
                break

        if fonte_path:
            self.fonte_titulo = pygame.font.Font(fonte_path, tamanhos["titulo"])
            self.fonte_texto = pygame.font.Font(fonte_path, tamanhos["texto"])
            self.fonte_pequena = pygame.font.Font(fonte_path, tamanhos["pequena"])
            self.fonte_dialogo = pygame.font.Font(fonte_path, tamanhos["dialogo"])
            self.fonte_botao = pygame.font.Font(fonte_path, tamanhos["botao"])
        else:
            self.fonte_titulo = pygame.font.Font(None, tamanhos["titulo"])
            self.fonte_texto = pygame.font.Font(None, tamanhos["texto"])
            self.fonte_pequena = pygame.font.Font(None, tamanhos["pequena"])
            self.fonte_dialogo = pygame.font.Font(None, tamanhos["dialogo"])
            self.fonte_botao = pygame.font.Font(None, tamanhos["botao"])

    
    def iniciar_digitacao(self):
        self.dialogo_texto_atual = ""
        self.dialogo_indice = 0
        self.dialogo_completo_gerado = False
        self.dialogo_linhas = []
        self.dialogo_tempo_ultimo = pygame.time.get_ticks()
        if self.som_digitacao and not self.som_tocando:
            self.som_digitacao.play(-1)
            self.som_tocando = True

    def parar_som(self):
        if self.som_digitacao and self.som_tocando:
            self.som_digitacao.stop()
            self.som_tocando = False

    def atualizar_digitacao(self):
        if self.dialogo_completo_gerado or self.estado != "dialogo_inicial":
            return
        agora = pygame.time.get_ticks()
        if agora - self.dialogo_tempo_ultimo > 30:
            if self.dialogo_indice < len(self.dialogo_texto_completo):
                self.dialogo_indice += 1
                self.dialogo_tempo_ultimo = agora
                self.dialogo_texto_atual = self.dialogo_texto_completo[:self.dialogo_indice]
            else:
                self.dialogo_completo_gerado = True
                self.parar_som()

    def pular_digitacao(self):
        if not self.dialogo_completo_gerado:
            self.parar_som()
            self.dialogo_indice = len(self.dialogo_texto_completo)
            self.dialogo_texto_atual = self.dialogo_texto_completo
            self.dialogo_completo_gerado = True

    def quebrar_texto(self, texto, largura_max, fonte):
        palavras = texto.split(' ')
        linhas = []
        linha_atual = ""
        for palavra in palavras:
            teste = linha_atual + palavra + " "
            if fonte.size(teste)[0] < largura_max:
                linha_atual = teste
            else:
                if linha_atual:
                    linhas.append(linha_atual)
                linha_atual = palavra + " "
        if linha_atual:
            linhas.append(linha_atual)
        return linhas

    def gerar_novo_numero(self):
        self.arvore_escondida = random.randint(1, 100)
        self.tentativas = 0
        self.estado = "jogando"
        self.mensagem = "Tente adivinhar!"
        self.mensagem_cor = AMARELO_HISTORIA
        self.input_texto = ""
        self.game_over_tipo = None
        self.tempo_derrota = 0
        self.derrota_texto_exibido = False
        self.tempo_vitoria_mensagem = 0
        self.vitoria_mensagem_exibida = False

    def reiniciar_jogo(self):
        self.estado = "dialogo_inicial"
        self.tentativas = 0
        self.input_texto = ""
        self.game_over_tipo = None
        self.dialogo_texto_atual = ""
        self.dialogo_indice = 0
        self.dialogo_completo_gerado = False
        self.botao_continuar_rect = None
        self.parar_som()
        self.iniciar_digitacao()
        self.tempo_derrota = 0
        self.derrota_texto_exibido = False
        self.tempo_vitoria_mensagem = 0
        self.vitoria_mensagem_exibida = False

    def processar_chute(self, valor):
        self.tentativas += 1
        vidas_restantes = self.max_tentativas - self.tentativas

        if valor == self.arvore_escondida:
            self.estado = "vitoria_mensagem"
            self.game_over_tipo = "vitoria"
            self.mensagem = (
                "Você encontrou o marciano.\n\nFinalmente, a verdade será revelada.\n\n"
                "Helena deixou uma carta para você."
            )
            self.mensagem_cor = AMARELO_HISTORIA
            self.tempo_vitoria_mensagem = pygame.time.get_ticks()
            self.vitoria_mensagem_exibida = True
            return True
        else:
            if vidas_restantes == 0:
                self.estado = "game_over"
                self.game_over_tipo = "derrota"
                self.mensagem = (
                    f"Você falhou em encontrá-lo. Ele estava escondido na árvore número {self.arvore_escondida}.\n\n"
                    "Você mexeu com algo maior do que você."
                )
                self.mensagem_cor = VERMELHO
                self.tempo_derrota = pygame.time.get_ticks()
                self.derrota_texto_exibido = True
                return False
            else:
                dica = "menor" if valor > self.arvore_escondida else "maior"
                self.mensagem = f"ERROU! Tente um número {dica}."
                self.mensagem_cor = AMARELO_HISTORIA
                self.input_texto = ""
                return False

    def desenhar_dialogo(self):
        from config.settings import TELA_LARGURA, TELA_ALTURA

        overlay = pygame.Surface((TELA_LARGURA, TELA_ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.tela.blit(overlay, (0, 0))

        margem = 80
        largura_bal = TELA_LARGURA - 2 * margem
        altura_bal = TELA_ALTURA - 2 * margem
        balao_rect = pygame.Rect(margem, margem, largura_bal, altura_bal)

        surface_balao = pygame.Surface((largura_bal, altura_bal), pygame.SRCALPHA)
        surface_balao.fill((17, 36, 41, 230))
        self.tela.blit(surface_balao, (margem, margem))
        pygame.draw.rect(self.tela, AMARELO_HISTORIA, balao_rect, 4)

        texto_para_mostrar = self.dialogo_texto_atual if not self.dialogo_completo_gerado else self.dialogo_texto_completo
        linhas = self.quebrar_texto(texto_para_mostrar, largura_bal - 80, self.fonte_dialogo)
        espacamento = redimensionar_fonte(38)
        inicio_y = margem + 50
        for i, linha in enumerate(linhas):
            texto_render = self.fonte_dialogo.render(linha.strip(), True, BRANCO)
            self.tela.blit(texto_render, (margem + 40, inicio_y + i * espacamento))

        if self.dialogo_completo_gerado:
            texto_botao = self.fonte_botao.render("CONTINUAR", True, BRANCO)
            rect_botao = texto_botao.get_rect()
            rect_botao.bottomright = (balao_rect.right - 40, balao_rect.bottom - 30)
            self.botao_continuar_rect = rect_botao
            cor = VERDE if self.botao_continuar_hover else BRANCO
            render = self.fonte_botao.render("CONTINUAR", True, cor)
            self.tela.blit(render, rect_botao)
        else:
            self.botao_continuar_rect = None

        pygame.display.flip()

    def draw_game_over(self):
        from config.settings import TELA_LARGURA, TELA_ALTURA

        overlay = pygame.Surface((TELA_LARGURA, TELA_ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        self.tela.blit(overlay, (0, 0))

        if self.game_over_tipo == "vitoria":
            pass
        else:
            linhas = self.mensagem.split('\n')
            y_offset = TELA_ALTURA // 2 - (len(linhas) * 40) // 2
            for linha in linhas:
                msg = self.fonte_texto.render(linha, True, VERMELHO)
                self.tela.blit(msg, (TELA_LARGURA // 2 - msg.get_width() // 2, y_offset))
                y_offset += 45

        pygame.display.flip()

    def draw_vitoria_mensagem(self):
        from config.settings import TELA_LARGURA, TELA_ALTURA

        overlay = pygame.Surface((TELA_LARGURA, TELA_ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.tela.blit(overlay, (0, 0))

        linhas = self.mensagem.split('\n')
        y_offset = TELA_ALTURA // 2 - (len(linhas) * 45) // 2
        for linha in linhas:
            if linha.strip() == "":
                y_offset += 20
                continue
            msg = self.fonte_titulo.render(linha, True, AMARELO_HISTORIA)
            self.tela.blit(msg, (TELA_LARGURA // 2 - msg.get_width() // 2, y_offset))
            y_offset += 50

        pygame.display.flip()

    def draw_vitoria_imagem(self):
        from config.settings import TELA_LARGURA, TELA_ALTURA

        if self.despedida_fundo:
            self.tela.blit(self.despedida_fundo, (0, 0))
        else:
            self.tela.fill(PRETO)

        self.draw_vagalumes()

        texto_botao = self.fonte_botao.render("Voltar ao menu", True, BRANCO)
        rect_botao = texto_botao.get_rect()
        rect_botao.bottomright = (TELA_LARGURA - 50, TELA_ALTURA - 50)
        self.botao_voltar_menu_rect = rect_botao
        cor = VERDE if self.botao_voltar_menu_hover else BRANCO
        render = self.fonte_botao.render("Voltar ao menu", True, cor)
        self.tela.blit(render, rect_botao)

        pygame.display.flip()

    def draw_imagem_derrota(self):
        from config.settings import TELA_LARGURA, TELA_ALTURA

        if self.desaparecimento_fundo:
            self.tela.blit(self.desaparecimento_fundo, (0, 0))
        else:
            self.tela.fill(PRETO)

        self.draw_vagalumes()

        texto_botao = self.fonte_botao.render("Voltar ao início do jogo", True, BRANCO)
        rect_botao = texto_botao.get_rect()
        rect_botao.bottomright = (TELA_LARGURA - 50, TELA_ALTURA - 50)
        self.botao_voltar_inicio_rect = rect_botao
        cor = VERDE if self.botao_voltar_inicio_hover else BRANCO
        render = self.fonte_botao.render("Voltar ao início do jogo", True, cor)
        self.tela.blit(render, rect_botao)

        pygame.display.flip()

    def draw_jogo(self):
        from config.settings import TELA_LARGURA, TELA_ALTURA, FATOR_ESCALA_X, FATOR_ESCALA_Y

        titulo = "ENCONTRE O MARCIANO"
        titulo_render = self.fonte_titulo.render(titulo, True, BRANCO)
        titulo_x = (TELA_LARGURA - titulo_render.get_width()) // 2
        titulo_y = 80
        self.tela.blit(titulo_render, (titulo_x, titulo_y))

        linha_y = titulo_y + titulo_render.get_height() + 15
        pygame.draw.line(self.tela, BRANCO, (TELA_LARGURA // 4, linha_y), (TELA_LARGURA * 3 // 4, linha_y), 3)

        instr = self.fonte_texto.render("Digite um número de 1 a 100 para procurar o marciano.", True, BRANCO)
        instr_x = (TELA_LARGURA - instr.get_width()) // 2
        instr_y = linha_y + 20
        self.tela.blit(instr, (instr_x, instr_y))

        for i, linha in enumerate(self.mensagem.split('\n')):
            msg = self.fonte_texto.render(linha, True, self.mensagem_cor)
            msg_x = (TELA_LARGURA - msg.get_width()) // 2
            msg_y = instr_y + 40 + i * 40
            self.tela.blit(msg, (msg_x, msg_y))

        input_y = msg_y + 60
        input_largura = 200
        input_altura = 50
        input_x = (TELA_LARGURA - input_largura) // 2
        pygame.draw.rect(self.tela, CINZA_ESCURO, (input_x, input_y, input_largura, input_altura))
        pygame.draw.rect(self.tela, self.mensagem_cor, (input_x, input_y, input_largura, input_altura), 3)
        texto_input = self.fonte_texto.render(self.input_texto + ("_" if self.input_ativo else ""), True, BRANCO)
        self.tela.blit(texto_input, (input_x + (input_largura - texto_input.get_width()) // 2,
                                    input_y + (input_altura - texto_input.get_height()) // 2))

        instr2 = self.fonte_pequena.render("Digite um número e pressione ENTER", True, BRANCO)
        self.tela.blit(instr2, (TELA_LARGURA // 2 - instr2.get_width() // 2, input_y + input_altura + 15))

        vidas_restantes = self.max_tentativas - self.tentativas
        coracao_tamanho = int(40 * min(FATOR_ESCALA_X, FATOR_ESCALA_Y))
        espacamento = int(50 * min(FATOR_ESCALA_X, FATOR_ESCALA_Y))
        inicio_x = (TELA_LARGURA - (self.max_tentativas * espacamento)) // 2
        coracao_y = input_y + input_altura + 60

        for i in range(self.max_tentativas):
            x = inicio_x + i * espacamento
            if i < vidas_restantes:
                if self.coracao_img:
                    img = pygame.transform.scale(self.coracao_img, (coracao_tamanho, coracao_tamanho))
                    self.tela.blit(img, (x, coracao_y))
                else:
                    pygame.draw.circle(self.tela, VERMELHO, (x + coracao_tamanho//2, coracao_y + coracao_tamanho//2), coracao_tamanho//2)
            else:
                if self.coracao_img:
                    img = pygame.transform.scale(self.coracao_img, (coracao_tamanho, coracao_tamanho))
                    img.set_alpha(100)
                    self.tela.blit(img, (x, coracao_y))
                else:
                    pygame.draw.circle(self.tela, CINZA_ESCURO, (x + coracao_tamanho//2, coracao_y + coracao_tamanho//2), coracao_tamanho//2, 2)

        texto_voltar = self.fonte_pequena.render("VOLTAR", True, VERDE if self.botao_voltar_hover else BRANCO)
        voltar_rect = texto_voltar.get_rect()
        voltar_rect.bottomright = (TELA_LARGURA - 40, TELA_ALTURA - 50)
        self.botao_voltar_rect = voltar_rect
        if self.botao_voltar_hover:
            pygame.draw.rect(self.tela, (0, 80, 0), voltar_rect.inflate(20, 10), border_radius=5)
        self.tela.blit(texto_voltar, voltar_rect)

        esc_texto = self.fonte_pequena.render("ESC para voltar", True, BRANCO)
        self.tela.blit(esc_texto, (TELA_LARGURA - esc_texto.get_width() - 40, TELA_ALTURA - 25))

        pygame.display.flip()

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.botao_voltar_rect:
            self.botao_voltar_hover = self.botao_voltar_rect.collidepoint(mouse_pos)
        if self.botao_continuar_rect:
            self.botao_continuar_hover = self.botao_continuar_rect.collidepoint(mouse_pos)
        if self.botao_voltar_inicio_rect:
            self.botao_voltar_inicio_hover = self.botao_voltar_inicio_rect.collidepoint(mouse_pos)
        if self.botao_voltar_menu_rect:
            self.botao_voltar_menu_hover = self.botao_voltar_menu_rect.collidepoint(mouse_pos)

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

                if self.estado == "dialogo_inicial":
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        if self.dialogo_completo_gerado:
                            self.parar_som()
                            self.gerar_novo_numero()
                        else:
                            self.pular_digitacao()
                    continue

                if self.estado == "jogando" and self.input_ativo:
                    if event.key == pygame.K_RETURN:
                        if self.input_texto:
                            try:
                                valor = int(self.input_texto)
                                self.processar_chute(valor)
                            except ValueError:
                                self.mensagem = "Digite um NÚMERO válido!"
                                self.mensagem_cor = VERMELHO
                            self.input_texto = ""
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_texto = self.input_texto[:-1]
                    else:
                        if event.unicode.isdigit() and len(self.input_texto) < 3:
                            self.input_texto += event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.estado == "dialogo_inicial":
                    if self.botao_continuar_rect and self.botao_continuar_hover:
                        self.parar_som()
                        self.gerar_novo_numero()
                    elif not self.dialogo_completo_gerado:
                        self.pular_digitacao()
                    continue

                if self.estado == "imagem_derrota":
                    if self.botao_voltar_inicio_rect and self.botao_voltar_inicio_hover:
                        self.rodando = False
                        return "menu"
                    continue

                if self.estado == "vitoria_imagem":
                    if self.botao_voltar_menu_rect and self.botao_voltar_menu_hover:
                        self.rodando = False
                        return "menu"
                    continue

                if self.botao_voltar_rect and self.botao_voltar_hover:
                    self.rodando = False
                    return "voltar"

        return None

    def update(self):
        if self.estado == "dialogo_inicial":
            self.atualizar_digitacao()
        elif self.estado == "game_over" and self.game_over_tipo == "derrota" and self.derrota_texto_exibido:
            agora = pygame.time.get_ticks()
            if agora - self.tempo_derrota > 5000:
                self.estado = "imagem_derrota"
        elif self.estado == "vitoria_mensagem" and self.vitoria_mensagem_exibida:
            agora = pygame.time.get_ticks()
            if agora - self.tempo_vitoria_mensagem > 3000:
                self.estado = "vitoria_imagem"
        self.update_vagalumes()

    def draw(self):
        if self.estado == "imagem_derrota":
            self.draw_imagem_derrota()
        elif self.estado == "vitoria_imagem":
            self.draw_vitoria_imagem()
        elif self.estado == "vitoria_mensagem":
            self.draw_background()
            self.draw_vagalumes()
            self.draw_vitoria_mensagem()
        else:
            self.draw_background()
            self.draw_vagalumes()
            from config.settings import TELA_LARGURA, TELA_ALTURA
            overlay = pygame.Surface((TELA_LARGURA, TELA_ALTURA), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 170))
            self.tela.blit(overlay, (0, 0))

            if self.estado == "dialogo_inicial":
                self.desenhar_dialogo()
            elif self.estado == "game_over":
                self.draw_game_over()
            else:
                self.draw_jogo()

    def resize_resources(self):
        super().resize_resources()
        if self.desaparecimento_img:
            from config.settings import TELA_LARGURA, TELA_ALTURA
            self.desaparecimento_fundo = pygame.transform.scale(
                self.desaparecimento_img, (TELA_LARGURA, TELA_ALTURA)
            )
        if self.despedida_img:
            from config.settings import TELA_LARGURA, TELA_ALTURA
            self.despedida_fundo = pygame.transform.scale(
                self.despedida_img, (TELA_LARGURA, TELA_ALTURA)
            )

    def run(self):
        self.iniciar_digitacao()
        while self.rodando:
            acao = self.handle_events()
            if acao:
                self.parar_som()
                return acao
            self.update()
            self.draw()
            self.clock.tick(60)
        return "voltar"