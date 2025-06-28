from typing import Dict, List
from .enums.pedrasEnum import PedrasEnum
from .carta import Carta
from .pedra import Pedra

class Jogador:
    def __init__(
            self,
            nome: str,
            jogadorEmTurno: bool):
        self.nome = nome
        self.pontuacao = 0
        self.jogadorEmTurno = jogadorEmTurno
        self.jogadorVenceu = False
        self.jogadorEmpatou = False
        self.cartasEmMao = list()
        self.pedrasEmMao = {pedra: 0 for pedra in PedrasEnum}
        self.cartasReservadas = list()
    
    def pegarPedras(self) -> Dict[Pedra, int]:
        return self.pedrasEmMao
    
    def pegarPontuacaoJogador(self) -> int:
        return self.pontuacao

    def adicionarCartaNaMao(self, carta: Carta):
        self.cartasEmMao.append(carta)
    
    def pegarCartas(self) -> List[Carta]:
        return self.cartasEmMao

    def atualizarPontuacaoJogador(self, pontosCarta: int):
        self.pontuacao += pontosCarta
    
    def removerPedraDaMao(self, pedra: Pedra):
        self.pedrasEmMao[pedra] -= 1
    
    def adicionarPedraNaMao(self, pedra: Pedra):
        self.pedrasEmMao[pedra] += 1
    
    def habilitarJogador(self):
        self.jogadorEmTurno = True
    
    def desabilitarJogador(self):
        self.jogadorEmTurno = False
    
    def adicionarCartaNaReserva(self, carta: Carta):
        self.cartasReservadas.append(carta)
    
    def pegarNome(self) -> str:
        return self.nome

    def verificarSeTemCartaRoubo(self) -> bool:
        for carta in self.cartasEmMao:
            if carta.verificarSeCartaDeRoubo():
                return True
        return False
    
    def possuiPedra(self, pedra: Pedra) -> bool:
        return (self.pedrasEmMao[pedra] != 0)
    
    def verificaSeEstaReservada(self, carta: Carta) -> bool:
        return (carta in self.cartasReservadas)

    def jogadorVenceu(self):
        self.jogadorVenceu = True
    
    def jogadorEmpatou(self):
        self.jogadorEmpatou = True
    
    def to_dict(self):
        return {
            "nome": self.nome,
            "pontuacao": self.pontuacao,
            "jogadorEmTurno": self.jogadorEmTurno,
            "cartasEmMao": [carta.to_dict() for carta in self.cartasEmMao],
            "pedrasEmMao": {pedra.name: qtd for pedra, qtd in self.pedrasEmMao.items()},
            "cartasReservadas": [carta.to_dict() for carta in self.cartasReservadas],
        }

    @classmethod
    def from_dict(cls, data):
        from .enums.pedrasEnum import PedrasEnum
        from .carta import Carta
        jogador = cls(data["nome"], data["jogadorEmTurno"])
        jogador.pontuacao = data["pontuacao"]
        jogador.cartasEmMao = [Carta.from_dict(c) for c in data["cartasEmMao"]]
        jogador.pedrasEmMao = {PedrasEnum[k]: v for k, v in data["pedrasEmMao"].items()}
        jogador.cartasReservadas = [Carta.from_dict(c) for c in data["cartasReservadas"]]
        return jogador