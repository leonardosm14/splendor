from typing import Dict, List
from .enums.pedrasEnum import PedrasEnum
from .carta import Carta
from .pedra import Pedra

class Jogador:
    def __init__(
            self,
            nome: str,
            pontuacao: int,
            jogadorEmTurno: bool,
            jogadorVenceu: bool,
            jogadorEmpatou: bool,
            cartasEmMao: List[Carta],
            pedrasEmMao: Dict[Pedra, int],
            cartasReservdas: List[Carta]):
        self.nome = nome
        self.pontuacao = pontuacao
        self.jogadorEmTurno = jogadorEmTurno
        self.jogadorVenceu = jogadorVenceu
        self.jogadorEmpatou = jogadorEmpatou
        self.cartasEmMao = cartasEmMao
        self.pedrasEmMao = pedrasEmMao
        self.cartasReservadas = cartasReservdas
    
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