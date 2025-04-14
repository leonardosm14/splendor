from random import shuffle
from .carta import Carta
import os
from .enums.niveisEnum import NiveisEnum


class Baralho:
    def __init__(self, nivel: NiveisEnum):
        self.nivel = nivel
        self.cartas = []
        self.cartas_visiveis = []
        self.carregar_cartas()

    def carregar_cartas(self):
        pasta = f"resources/cartas/"
        for arquivo in os.listdir(pasta):
            if arquivo.endswith(".png"):
                self.cartas.append(Carta.from_filename(
                    cartaId=len(self.cartas),
                    nivel=self.nivel,
                    filename=arquivo
                ))
        shuffle(self.cartas)

    def revelar_cartas(self):
        while len(self.cartas_visiveis) < 4 and self.cartas:
            carta = self.cartas.pop()
            carta.visivel = True
            self.cartas_visiveis.append(carta)

    def getNivel(self) -> NiveisEnum:
        return self.nivel

    def adicionarCarta(self, carta: Carta) -> None:
        self.cartas.append(carta)
        self.quantidadeCartas = len(self.cartas)

    def removerCarta(self, carta: Carta) -> None:
        if carta in self.cartas:
            self.cartas.remove(carta)
            self.quantidadeCartas = len(self.cartas)
        else:
            raise ValueError("A carta não está no baralho.")

    def quantidadeDeCartas(self) -> int:
        return len(self.cartas)
