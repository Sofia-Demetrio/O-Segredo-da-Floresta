# main.py
import pygame
import sys
from config.settings import TELA_LARGURA_PADRAO, TELA_ALTURA_PADRAO, atualizar_tamanhos_globais
from scenes.tela_inicial import TelaInicial
from scenes.tela_creditos import TelaCreditos
from scenes.tela_historia import TelaHistoria
from scenes.tela_pasta_fechada import TelaPastaFechada
from scenes.tela_escritorio import TelaEscritorio
from scenes.tela_transicao_floresta import TelaTransicaoFloresta
from scenes.tela_multiplayer import TelaMultiplayer
from scenes.minigame_curupira import MinigameCurupira
from scenes.minigame_iara import MinigameIara
from scenes.minigame_boitata import MinigameBoitata

class TelaMultiplayerDebug(TelaMultiplayer):
    
    def gerar_novo_numero(self):
        super().gerar_novo_numero()
        print(f"Número sorteado: {self.arvore_escondida}")#pra testar a tela de vitória 


def main():
    pygame.init()
    pygame.mixer.init()
    
    janela = pygame.display.set_mode((TELA_LARGURA_PADRAO, TELA_ALTURA_PADRAO), pygame.RESIZABLE)
    relogio = pygame.time.Clock()
    atualizar_tamanhos_globais(TELA_LARGURA_PADRAO, TELA_ALTURA_PADRAO)
    
    print("INICIANDO JOGO")
    
    while True:
        menu = TelaInicial(janela, relogio)
        acao = menu.run()
        
        if acao == "sair":
            break
        elif acao == "creditos":
            creditos = TelaCreditos(janela, relogio)
            creditos.run()
            continue
        elif acao == "iniciar":
        
            print("Iniciando história...")
            historia = TelaHistoria(janela, relogio)
            historia.run()
            
            print("Abrindo pasta fechada...")
            pasta = TelaPastaFechada(janela, relogio)
            retorno_pasta = pasta.run()
            if retorno_pasta == "sair":
                break
            elif retorno_pasta == "voltar":
                continue
            
            print("Abrindo escritório de investigação...")
            escritorio = TelaEscritorio(janela, relogio)
            retorno_escritorio = escritorio.run()
            if retorno_escritorio == "sair":
                break
            elif retorno_escritorio == "voltar":
                continue
            
            print("Entrando na floresta...")
            transicao = TelaTransicaoFloresta(janela, relogio)
            transicao.run()
            
            print("Iniciando Minigame Curupira...")
            jogo_curupira = MinigameCurupira(janela, relogio)
            resultado_curupira = jogo_curupira.run()
            if resultado_curupira == "sair":
                break
            elif resultado_curupira == "voltar":
                continue
            
            print("Iniciando Minigame Iara...")
            jogo_iara = MinigameIara(janela, relogio)
            resultado_iara = jogo_iara.run()
            if resultado_iara == "sair":
                break
            elif resultado_iara == "voltar":
                continue
            
            print("Iniciando Minigame Boitatá...")
            jogo_boitata = MinigameBoitata(janela, relogio)
            resultado_boitata = jogo_boitata.run()
            if resultado_boitata == "sair":
                break
            elif resultado_boitata == "voltar":
                continue
            
            print("Iniciando desafio final (adivinhe o número)...")
            jogo_multi = TelaMultiplayerDebug(janela, relogio)
            jogo_multi.run()
            
            print("Fim da partida.\n")
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()