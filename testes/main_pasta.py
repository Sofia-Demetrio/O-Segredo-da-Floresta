# main_pasta.py

import pygame
import sys
from config.settings import TELA_LARGURA_PADRAO, TELA_ALTURA_PADRAO, atualizar_tamanhos_globais
from scenes.tela_pasta_fechada import TelaPastaFechada

def main():
    pygame.init()
    pygame.mixer.init()

    janela = pygame.display.set_mode((TELA_LARGURA_PADRAO, TELA_ALTURA_PADRAO), pygame.RESIZABLE)
    relogio = pygame.time.Clock()
    atualizar_tamanhos_globais(TELA_LARGURA_PADRAO, TELA_ALTURA_PADRAO)

    print("=== TESTE TELA PASTA FECHADA ===")
    tela = TelaPastaFechada(janela, relogio)
    tela.run()  

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()