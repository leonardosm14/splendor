import random
from typing import List, Optional
from .carta import Carta
from .enums.niveisEnum import NiveisEnum
from .enums.pedrasEnum import PedrasEnum

class Baralho:
    def __init__(self, nivel: NiveisEnum, seed: int = None):
        self.nivel = nivel
        self.cartas: List[Carta] = []
        self.seed = seed
        # Removido a inicialização automática do baralho
        # O baralho será preenchido apenas pelas cartas dos arquivos de imagem

    def verificaSeTemCartaDoMesmoNivelNoBaralho(self) -> bool:
        return len(self.cartas) > 0

    def temCartas(self) -> bool:
        """Verifica se o baralho tem cartas"""
        return len(self.cartas) > 0

    def pegarCartaDoBaralho(self) -> Optional[Carta]:
        """Retorna uma carta do baralho"""
        if self.cartas:
            carta = self.cartas.pop(0)  # Use pop(0) para garantir ordem igual para ambos jogadores
            return carta
        return None  # Não lança erro, apenas retorna None

    def adicionarCarta(self, carta: Carta):
        """Adiciona uma carta ao baralho"""
        self.cartas.append(carta)