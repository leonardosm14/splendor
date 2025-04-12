from typing import Dict, List

from .jogador import Jogador
from .pedra import Pedra
from .baralho import Baralho
from .carta import Carta
from .enums.pedrasEnum import PedrasEnum
from .enums.niveisEnum import NiveisEnum

class Tabuleiro:
    def __init__(self, jogadorLocal: Jogador, jogadorRemoto: Jogador):
        self.baralhos: Dict[NiveisEnum, Baralho] = {
            NiveisEnum.NIVEL1: Baralho(NiveisEnum.NIVEL1),
            NiveisEnum.NIVEL2: Baralho(NiveisEnum.NIVEL2),
            NiveisEnum.NIVEL3: Baralho(NiveisEnum.NIVEL3),
        }

        self.cartas_visiveis: Dict[NiveisEnum, List[Carta]] = {
            NiveisEnum.NIVEL1: [],
            NiveisEnum.NIVEL2: [],
            NiveisEnum.NIVEL3: [],
        }

        self.pedras = self.gerar_pedras_iniciais()
        self.jogadorLocal = jogadorLocal
        self.jogadorRemoto = jogadorRemoto
        self.rodada = 1
    
    def gerar_pedras_iniciais(self) -> list[Pedra]:
        pedras = {}
        for tipo in PedrasEnum:
            if tipo == PedrasEnum.OURO:
                quantidade = 5
            else:
                quantidade = 7
            pedras[tipo] = quantidade
        return pedras

    def get_quantidade_pedras(self, tipo: PedrasEnum) -> Dict[str, int]:
        return self.pedras[tipo]

    def get_rodada(self) -> int:
        return self.rodada

    def avancar_rodada(self) -> None:
        self.rodada += 1

    def revelar_cartas(self, nivel: NiveisEnum) -> None:
        baralho = self.baralhos[nivel]
        cartas_visiveis = self.cartas_visiveis[nivel]

        while len(cartas_visiveis) < 4 and len(baralho.cartas) > 0:
            carta = baralho.pop()
            carta.cartaVisivel = True
            cartas_visiveis.append(carta)
