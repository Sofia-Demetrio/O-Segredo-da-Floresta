# config/utils.py

import pygame
from config.settings import FATOR_ESCALA_X, FATOR_ESCALA_Y


def redimensionar_fonte(tamanho_base):

    return int(tamanho_base * min(FATOR_ESCALA_X, FATOR_ESCALA_Y))


def redimensionar_posicao(x_base, y_base):

    return (int(x_base * FATOR_ESCALA_X), int(y_base * FATOR_ESCALA_Y))


def redimensionar_rect(rect_base):

    return pygame.Rect(
        int(rect_base.x * FATOR_ESCALA_X),
        int(rect_base.y * FATOR_ESCALA_Y),
        int(rect_base.width * FATOR_ESCALA_X),
        int(rect_base.height * FATOR_ESCALA_Y)
    )


def redimensionar_imagem(imagem, largura_base, altura_base):
 
    if imagem:
        return pygame.transform.scale(
            imagem,
            (int(largura_base * FATOR_ESCALA_X), 
             int(altura_base * FATOR_ESCALA_Y))
        )
    return None