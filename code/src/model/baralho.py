import random
from typing import List, Optional
from .carta import Carta
from .enums.niveisEnum import NiveisEnum
from .enums.pedrasEnum import PedrasEnum

class Baralho:
    def __init__(self, nivel: NiveisEnum):
        self.nivel = nivel
        self.cartas: List[Carta] = []
        self.inicializar_baralho()

    def inicializar_baralho(self):
        """Inicializa o baralho com cartas do nível especificado"""
        cores_pedras = [p for p in PedrasEnum if p != PedrasEnum.OURO]
        
        for i in range(10):  # Exemplo: 10 cartas por nível
            bonus = random.choice(cores_pedras)
            self.cartas.append(
                Carta(
                    id=i,
                    pontos=random.randint(1, 3),
                    nivel=self.nivel,
                    pedras={p: random.randint(0, 2) for p in cores_pedras},
                    cartaDeRoubo=False,
                    bonus=bonus,
                    habilitada=True
                )
            )

    def verificaSeTemCartaDoMesmoNivelNoBaralho(self) -> bool:
        return len(self.cartas) > 0

    def pegarCartaDoBaralho(self) -> Optional[Carta]:
        """Retorna uma carta aleatória do baralho"""
        if self.cartas:
            carta = random.choice(self.cartas)
            self.cartas.remove(carta)  # Remove a carta do baralho após selecioná-la
            return carta
        raise ValueError("Baralho vazio! Não há cartas disponíveis.")

    def adicionarCarta(self, carta: Carta):
        self.cartas.append(carta)
        if carta.habilitada:
            self.cartasVisiveis.append(carta)