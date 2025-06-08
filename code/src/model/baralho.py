import random
from typing import List
from .carta import Carta
import os
from .enums.niveisEnum import NiveisEnum


class Baralho:
    def __init__(self, nivel: NiveisEnum):
        self.nivel = nivel
        self.cartas = list()
        self.cartasViseis = list()
    
    def adicionarCarta(self, carta: Carta):
        self.cartas.append(carta)
        if (carta.habilitada):
            self.cartasViseis.append(carta)
    
    def verificaSeTemCartaDoMesmoNivelNoBaralho(self, cartaNivel: NiveisEnum) -> bool:
        return len(self.cartas)!=0
    
    def pegarCartaDoBaralho(self) -> Carta:
        carta = random.choice(self.cartas)
        self.cartas.remove(carta)
        carta.habilitar()
        return carta