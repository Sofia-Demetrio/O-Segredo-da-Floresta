# teste_boitata.py

import pygame
import sys
from config.settings import TELA_LARGURA_PADRAO, TELA_ALTURA_PADRAO, atualizar_tamanhos_globais
from scenes.minigame_boitata import MinigameBoitata

def main():                          
    pygame.init()
    pygame.mixer.init()

    janela = pygame.display.set_mode((TELA_LARGURA_PADRAO, TELA_ALTURA_PADRAO), pygame.RESIZABLE)
    relogio = pygame.time.Clock()
    atualizar_tamanhos_globais(TELA_LARGURA_PADRAO, TELA_ALTURA_PADRAO)

    print("TESTE MINIGAME BOITATÁ")
    jogo = MinigameBoitata(janela, relogio)
    jogo.run()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()