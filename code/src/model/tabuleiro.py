from typing import Dict, List, Optional, Tuple
import random
from .jogador import Jogador
from .pedra import Pedra
from .baralho import Baralho
from .carta import Carta
from .enums.pedrasEnum import PedrasEnum
from .enums.niveisEnum import NiveisEnum

class Tabuleiro:
    def __init__(self, jogadorLocal: Jogador, jogadorRemoto: Jogador):
        self.jogadorLocal = jogadorLocal
        self.jogadorRemoto = jogadorRemoto
        self.baralhos = [Baralho() for _ in range(3)]  # Baralhos para níveis 1, 2 e 3
        self.pedrasNoTabuleiro = {pedra: 7 for pedra in PedrasEnum}
        self.cartasNoTabuleiro = [self.baralhos[i].pegarCartaDoBaralho() for i in range(3) for _ in range(4)]  # 4 cartas por nível
        self.rodada = 0
        self.partidaEmAndamento = False
        self.ultimaPartida = False

        #Novos
        self.todasCartas = list()
    
    def verificarPedrasSuficientes(self, carta: Carta) -> bool:
        """Verifica se o jogador local tem pedras suficientes para comprar uma carta"""
        pedrasJogador = self.jogadorLocal.pegarPedras()
        pedrasCarta = carta.pegarPedrasDaCarta()
        
        return all(
            pedrasJogador[pedra] >= pedrasCarta[pedra]
            for pedra in pedrasCarta
        )
    
    def instanciarCartas(self,
                         id: int,
                        pontos: int,
                        nivel: NiveisEnum,
                        pedras: Dict[PedrasEnum, int],
                        cartaDeRoubo: bool,
                        bonus: PedrasEnum | None,
                        habilitada: bool ):
        
        carta = Carta(id = id,
                      pontos = pontos,
                      nivel=nivel,
                      pedras=pedras,
                      cartaDeRoubo=cartaDeRoubo,
                      bonus=bonus,
                      habilitada=habilitada)
        
        self.todasCarta.append(carta)

    def ehUltimaPartida(self) -> bool:
        return self.ultimaPartida
    
    def atualizarEstadoTabuleiro(self):
        """Atualiza o estado geral do tabuleiro após uma jogada"""
        self.atualizarPedrasNoTabuleiro()
        self.reposicionarCartasSeNecessario()
        self.verificarFimDeJogo()
    
    def atualizarPedrasNoTabuleiro(self):
        """Atualiza a contagem de pedras disponíveis no tabuleiro"""
        pedrasJogadorLocal = self.jogadorLocal.pegarPedras()
        pedrasJogadorRemoto = self.jogadorRemoto.pegarPedras()
        
        self.pedrasNoTabuleiro = {
            pedra: max(0, 7 - (pedrasJogadorLocal[pedra] + pedrasJogadorRemoto[pedra]))
            for pedra in PedrasEnum
        }
    
    def reposicionarCartasSeNecessario(self):
        """Repõe cartas visíveis se necessário após uma compra"""
        for i, carta in enumerate(self.cartasNoTabuleiro):
            if carta is None:
                nivel = i // 4 + 1  # Determina o nível baseado na posição
                self.cartasNoTabuleiro[i] = self.baralhos[nivel-1].pegarCartaDoBaralho()
    
    def pegarCartaDoTabuleiro(self, indiceCarta: int) -> Tuple[Optional[Carta], bool]:
        """
        Tenta pegar uma carta do tabuleiro.
        Retorna:
        - A carta (ou None se falhar)
        - Boolean indicando sucesso
        """
        if 0 <= indiceCarta < len(self.cartasNoTabuleiro):
            carta = self.cartasNoTabuleiro[indiceCarta]
            if carta and self.verificarPedrasSuficientes(carta):
                self.cartasNoTabuleiro[indiceCarta] = None
                return carta, True
        return None, False
    
    def pegarPedrasDoTabuleiro(self, pedras: Dict[PedrasEnum, int]) -> bool:
        """
        Tenta pegar pedras do tabuleiro, respeitando as regras do jogo.
        Retorna True se bem sucedido.
        """
        # Verifica se há pedras suficientes no tabuleiro
        if all(self.pedrasNoTabuleiro[pedra] >= quantidade for pedra, quantidade in pedras.items()):
            # Verifica regra de não pegar mais de 3 pedras diferentes
            if len(pedras) <= 3:
                for pedra, quantidade in pedras.items():
                    self.pedrasNoTabuleiro[pedra] -= quantidade
                    self.jogadorLocal.adicionarPedra(pedra, quantidade)
                return True
        return False
    
    def reservarCarta(self, indiceCarta: int) -> bool:
        """
        Reserva uma carta do tabuleiro para o jogador local.
        Retorna True se bem sucedido.
        """
        if 0 <= indiceCarta < len(self.cartasNoTabuleiro) and self.cartasNoTabuleiro[indiceCarta]:
            carta = self.cartasNoTabuleiro[indiceCarta]
            if self.jogadorLocal.reservarCarta(carta):
                self.cartasNoTabuleiro[indiceCarta] = None
                return True
        return False
    
    def verificarFimDeJogo(self):
        """Verifica se as condições de fim de jogo foram atingidas"""
        if (self.jogadorLocal.pegarPontuacaoJogador() >= 15 or 
            self.jogadorRemoto.pegarPontuacaoJogador() >= 15):
            self.habilitarUltimaPartida()
    
    def avaliarVencedor(self) -> Optional[Jogador]:
        """
        Avalia o vencedor do jogo.
        Retorna:
        - Jogador vencedor
        - None em caso de empate
        """
        pontosLocal = self.jogadorLocal.pegarPontuacaoJogador()
        pontosRemoto = self.jogadorRemoto.pegarPontuacaoJogador()
        
        if pontosLocal > pontosRemoto:
            self.jogadorLocal.jogadorVenceu()
            return self.jogadorLocal
        elif pontosRemoto > pontosLocal:
            self.jogadorRemoto.jogadorVenceu()
            return self.jogadorRemoto
        return None
    
    def habilitarInteracoes(self, habilitar: bool):
        """Habilita ou desabilita interações com o tabuleiro"""
        if habilitar:
            self.jogadorLocal.habilitarJogador()
        else:
            self.jogadorLocal.desabilitarJogador()
    
    def reiniciarParaNovaPartida(self):
        """Prepara o tabuleiro para uma nova partida"""
        self.pedrasNoTabuleiro = {pedra: 7 for pedra in PedrasEnum}
        self.cartasNoTabuleiro = [self.baralhos[i].pegarCartaDoBaralho() for i in range(3) for _ in range(4)]
        self.rodada = 0
        self.partidaEmAndamento = True
        self.ultimaPartida = False
    
    # Mantendo os métodos originais com melhorias internas
    def pegarNomeJogador(self) -> str:
        return self.jogadorLocal.pegarNome()
    
    def pegarPontuacaoJogador(self) -> int:
        return self.jogadorLocal.pegarPontuacaoJogador()
    
    def pegarPedrasJogador(self) -> Dict[PedrasEnum, int]:
        return self.jogadorLocal.pegarPedras()
    
    def pegarCartasRoubo(self) -> List[Carta]:
        return [carta for carta in self.jogadorLocal.pegarCartas() if carta.verificarSeCartaDeRoubo()]
    
    def verificarIgualdadePedras(self, pedraA: Pedra, pedraB: Pedra) -> bool:
        return pedraA.tipo == pedraB.tipo
    
    def verificarOuroDisponivel(self) -> bool:
        return self.pedrasNoTabuleiro[PedrasEnum.OURO] > 0
    
    def verificaSeJogadorTemPedra(self, pedra: Pedra) -> bool:
        return self.jogadorLocal.pegarPedras().get(pedra.tipo, 0) > 0
    
    def verificarSeEstaReservada(self, carta: Carta) -> bool:
        return carta in self.jogadorLocal.cartasReservadas()
    
    def verificarSeTemCartaDoMesmoNivelNoBaralho(self, nivelCarta: int) -> bool:
        return self.baralhos[nivelCarta-1].verificaSeTemCartaDoMesmoNivelNoBaralho()
    
    def verificaSeTemCartaRoubo(self) -> bool:
        return self.jogadorLocal.verificarSeTemCartaRoubo()
    
    def habilitarUltimaPartida(self):
        self.ultimaPartida = True
    
    def habilitarCartasTabuleiro(self):
        for carta in self.cartasNoTabuleiro:
            if carta:
                carta.habilitarCarta()
    
    def desabilitarCartasTabuleiro(self):
        for carta in self.cartasNoTabuleiro:
            if carta:
                carta.desabilitarCarta()