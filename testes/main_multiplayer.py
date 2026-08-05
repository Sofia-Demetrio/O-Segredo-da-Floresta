# main_multiplayer_debug.py
import pygame
import sys
import random
from config.settings import TELA_LARGURA_PADRAO, TELA_ALTURA_PADRAO, atualizar_tamanhos_globais
from scenes.tela_multiplayer import TelaMultiplayer

class TelaMultiplayerDebug(TelaMultiplayer):
    
    def gerar_novo_numero(self):
        # Chama o método original
        super().gerar_novo_numero()
    
        print(f"Número sorteado (para teste): {self.arvore_escondida}")

def main():
    pygame.init()
    pygame.mixer.init()
    janela = pygame.display.set_mode((TELA_LARGURA_PADRAO, TELA_ALTURA_PADRAO), pygame.RESIZABLE)
    relogio = pygame.time.Clock()
    atualizar_tamanhos_globais(TELA_LARGURA_PADRAO, TELA_ALTURA_PADRAO)

    jogo = TelaMultiplayerDebug(janela, relogio)
    jogo.run()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()