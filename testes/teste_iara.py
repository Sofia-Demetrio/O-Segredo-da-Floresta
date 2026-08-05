# teste_iara.py

import pygame
import sys
from config.settings import TELA_LARGURA_PADRAO, TELA_ALTURA_PADRAO, atualizar_tamanhos_globais
from scenes.minigame_iara import MinigameIara

def main():
    pygame.init()
    pygame.mixer.init()

    janela = pygame.display.set_mode((TELA_LARGURA_PADRAO, TELA_ALTURA_PADRAO), pygame.RESIZABLE)
    relogio = pygame.time.Clock()
    atualizar_tamanhos_globais(TELA_LARGURA_PADRAO, TELA_ALTURA_PADRAO)

    print("TESTE MINIGAME IARA")
    jogo = MinigameIara(janela, relogio)
    jogo.run()  

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()