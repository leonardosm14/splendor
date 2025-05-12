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
            cartasEmMao: List[Carta],
            pedrasEmMao: Dict[Pedra, int]):
        self.nome = nome
        self.pontuacao = pontuacao
        self.jogadorEmTurno = jogadorEmTurno
        self.jogadorVenceu = jogadorVenceu
        self.cartasEmMao = cartasEmMao
        self.pedrasEmMao = pedrasEmMao
    
    # getters
    def getNome(self) -> str:
        return self.nome
    
    def getPontuacao(self) -> int:
        return self.pontuacao
    
    def getJogadorEmTurno(self) -> bool:
        return self.jogadorEmTurno
    
    def getJogadorVenceu(self) -> bool:
        return self.jogadorVenceu
    
    def getCartasEmMao(self) -> List[Carta]:
        return self.cartasEmMao
    
    def getPedrasEmMao(self) -> Dict[Pedra, int]:
        return self.pedrasEmMao
    
    # setters
    def setNome(self, nome: str) -> None:
        self.nome = nome

    def setPontuacao(self, pontuacao: int) -> None:
        self.pontuacao = pontuacao

    def setJogadorEmTurno(self, jogadorEmTurno: bool) -> None:
        self.jogadorEmTurno = jogadorEmTurno

    def setJogadorVenceu(self, jogadorVenceu: bool) -> None:
        self.jogadorVenceu = jogadorVenceu

    def setCartasEmMao(self, cartasEmMao: List[Carta]) -> None:
        self.cartasEmMao = cartasEmMao

    def setPedrasEmMao(self, pedrasEmMao: Dict[Pedra, int]) -> None:
        self.pedrasEmMao = pedrasEmMao
    
    # Operações com cartas

    # adicionar cartas
    def adicionarCarta(self, carta: Carta) -> None:
        self.cartasEmMao.append(carta)
        self.pontuacao += carta.pontos
        pedrasDaCarta: List[Pedra] = carta.getPedras()
        for pedra in pedrasDaCarta:
            self.adicionarPedra(pedra=pedra)
        
    # remover cartas
    def removerCarta(self, carta: Carta) -> None:
        if carta in self.cartasEmMao:
            self.cartasEmMao.remove(carta)
        else:
            raise Exception("Carta não encontrada na mão do jogador")
    
    def getQuantidadeCartas(self) -> int:
        return len(self.cartasEmMao)
    
    # Operações com pedras

    # adicionar pedras
    def adicionarPedra(self, pedra: Pedra) -> None:
        if pedra in self.pedrasEmMao:
            self.pedrasEmMao[pedra] += 1
        else:
            self.pedrasEmMao[pedra] = 1
    
    # remover pedras
    def removerPedra(self, pedra: Pedra) -> None:
        if pedra in self.pedrasEmMao:
            if self.pedrasEmMao[pedra] > 1:
                self.pedrasEmMao[pedra] -= 1
            else:
                self.pedrasEmMao[pedra] = 0
        else:
            raise Exception("Pedra não encontrada na mão do jogador")
    
    def getQuantidadeDeEsmeraldas(self) -> int:
        return self.pedrasEmMao.get(PedrasEnum.ESMERALDA, 0)
    
    def getQuantidadeDeDiamantes(self) -> int:
        return self.pedrasEmMao.get(PedrasEnum.DIAMANTE, 0)
    
    def getQuantidadeDeRubis(self) -> int:
        return self.pedrasEmMao.get(PedrasEnum.RUBI, 0)
    
    def getQuantidadeDeSafiras(self) -> int:
        return self.pedrasEmMao.get(PedrasEnum.SAFIRA, 0)
    
    def getQuantidadeDeOnix(self) -> int:
        return self.pedrasEmMao.get(PedrasEnum.ONIX, 0)
    
    def getQuantidadeDeOuro(self) -> int:
        return self.pedrasEmMao.get(PedrasEnum.OURO, 0)

    def getQuantidadeDePedras(self) -> int:
        return sum(self.pedrasEmMao.values())