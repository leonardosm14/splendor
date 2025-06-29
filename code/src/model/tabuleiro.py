from typing import Dict, List, Optional, Tuple
import random
from .jogador import Jogador
from .pedra import Pedra
from .baralho import Baralho
from .carta import Carta
from .enums.pedrasEnum import PedrasEnum
from .enums.niveisEnum import NiveisEnum

class Tabuleiro:
    def __init__(self, jogadorLocal: Jogador, jogadorRemoto: Jogador, seed: int = 0, inicializar_cartas=True):
        self.jogadorLocal = jogadorLocal
        self.jogadorRemoto = jogadorRemoto
        self.baralhos = [
            Baralho(nivel=NiveisEnum.NIVEL1, seed=seed),
            Baralho(nivel=NiveisEnum.NIVEL2, seed=seed),
            Baralho(nivel=NiveisEnum.NIVEL3, seed=seed)
        ]
        self.pedrasNoTabuleiro = {pedra: 7 for pedra in PedrasEnum}
        self.cartasNoTabuleiro = []
        self.rodada = 0
        self.partidaEmAndamento = False
        self.ultimaPartida = False
        self.todasCartas = list()
        self.oferta_pendente = None
        if inicializar_cartas:
            for i in range(3):  # Níveis 1, 2 e 3
                for _ in range(4):  # 4 cartas por nível
                    carta = self.baralhos[i].pegarCartaDoBaralho()
                    if carta:
                        self.cartasNoTabuleiro.append(carta)
    
    def jogadorLocal(self):
        return self.jogadorLocal
    
    def jogadorRemoto(self):
        return self.jogadorRemoto
    
    def inicializar_cartas_tabuleiro(self):
        """Inicializa as cartas visíveis no tabuleiro"""
        self.cartasNoTabuleiro = []
        for nivel in [0, 1, 2]:  # Níveis enumerados como 0, 1, 2
            for _ in range(4):  # 4 cartas por nível
                try:
                    carta = self.baralhos[nivel].pegarCartaDoBaralho()
                    # Se for carta de roubo, pega outra carta
                    while carta and carta.cartaDeRoubo:
                        carta = self.baralhos[nivel].pegarCartaDoBaralho()
                    self.cartasNoTabuleiro.append(carta)
                except (ValueError, IndexError) as e:
                    print(f"Erro ao pegar carta do baralho nível {nivel}: {e}")
                    self.cartasNoTabuleiro.append(None)
                    
    
    def verificarPedrasSuficientes(self, carta: Carta) -> bool:
        """Verifica se o jogador local tem pedras suficientes para comprar uma carta, considerando ouro como coringa"""
        pedrasJogador = self.jogadorLocal.pegarPedras()
        pedrasCarta = carta.pegarPedrasDaCarta()

        print(f"Verificando pedras: Jogador {pedrasJogador}, Carta {pedrasCarta}")
        
        # Calcula quantas pedras de ouro o jogador tem
        ouro_disponivel = pedrasJogador.get(PedrasEnum.OURO, 0)
        
        # Verifica se tem pedras suficientes para cada tipo, usando ouro como coringa se necessário
        for pedra, quantidade_necessaria in pedrasCarta.items():
            pedras_disponiveis = pedrasJogador.get(pedra, 0)
            
            # Se não tem pedras suficientes do tipo específico
            if pedras_disponiveis < quantidade_necessaria:
                # Calcula quantas pedras de ouro precisaria usar
                ouro_necessario = quantidade_necessaria - pedras_disponiveis
                
                # Se não tem ouro suficiente, não pode comprar
                if ouro_disponivel < ouro_necessario:
                    return False
                
                # Usa ouro como coringa
                ouro_disponivel -= ouro_necessario
        
        return True
    
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
        self.todasCartas.append(carta)
        # Adicione ao baralho correto
        self.baralhos[nivel.value - 1].adicionarCarta(carta)

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
        """Reposiciona cartas no tabuleiro se necessário"""
        # Remove cartas None do tabuleiro e repõe com novas cartas
        for i, carta in enumerate(self.cartasNoTabuleiro):
            if carta is None:
                # Determina o nível baseado no índice
                nivel_idx = i // 4
                if nivel_idx < len(self.baralhos) and self.baralhos[nivel_idx].temCartas():
                    nova_carta = self.baralhos[nivel_idx].pegarCartaDoBaralho()
                    if nova_carta:
                        self.cartasNoTabuleiro[i] = nova_carta
    
    def pegarCartaDoTabuleiro(self, indiceCarta: int) -> Tuple[Optional[Carta], bool]:
        if 0 <= indiceCarta < len(self.cartasNoTabuleiro):
            carta = self.cartasNoTabuleiro[indiceCarta]
            if carta and self.verificarPedrasSuficientes(carta):
                self.cartasNoTabuleiro[indiceCarta] = None
                
                # Repõe carta do mesmo nível
                nivel = carta.nivel
                try:
                    nova_carta = self.baralhos[nivel.value - 1].pegarCartaDoBaralho()
                    self.cartasNoTabuleiro[indiceCarta] = nova_carta
                except (ValueError, IndexError):
                    pass
                    
                return carta, True
        return None, False
    
    def pegarPedrasDoTabuleiro(self, pedras: Dict[PedrasEnum, int]) -> bool:
        if all(self.pedrasNoTabuleiro[pedra] >= quantidade for pedra, quantidade in pedras.items()):
            if len(pedras) <= 3:
                for pedra, quantidade in pedras.items():
                    self.pedrasNoTabuleiro[pedra] -= quantidade
                    self.jogadorLocal.adicionarPedraNaMao(pedra, quantidade)
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
    
    def pegarNomeJogador(self) -> str:
        return self.jogadorLocal.pegarNome()
    
    def pegarPontuacaoJogador(self) -> int:
        return self.jogadorLocal.pegarPontuacaoJogador()
    
    def pegarPedrasJogador(self) -> Dict[PedrasEnum, int]:
        return self.jogadorLocal.pegarPedras()
    
    def pegarCartasRoubo(self) -> List[Carta]:
        """Retorna todas as cartas de roubo dos jogadores"""
        cartas_roubo = []
        for carta in self.jogadorLocal.pegarCartas():
            if carta.verificarSeCartaDeRoubo():
                cartas_roubo.append(carta)
        for carta in self.jogadorRemoto.pegarCartas():
            if carta.verificarSeCartaDeRoubo():
                cartas_roubo.append(carta)
        return cartas_roubo
    
    def pegarPedrasCarta(self, carta: Carta) -> Dict[PedrasEnum, int]:
        """Retorna as pedras necessárias para comprar uma carta"""
        return carta.pegarPedrasDaCarta()
    
    def verificarIgualdadePedras(self, pedraA: Pedra, pedraB: Pedra) -> bool:
        return pedraA.pegarTipo() == pedraB.pegarTipo()
    
    def verificarOuroDisponivel(self) -> bool:
        return self.pedrasNoTabuleiro[PedrasEnum.OURO] > 0
    
    def verificaSeJogadorTemPedra(self, pedra: PedrasEnum) -> bool:
        return self.jogadorLocal.pegarPedras().get(pedra, 0) > 0
    
    def verificarSeEstaReservada(self, carta: Carta) -> bool:
        return carta in self.jogadorLocal.cartasReservadas()
    
    def verificarSeTemCartaDoMesmoNivelNoBaralho(self, nivelCarta: int) -> bool:
        return self.baralhos[nivelCarta-1].verificaSeTemCartaDoMesmoNivelNoBaralho()
    
    def verificaSeTemCartaRoubo(self) -> bool:
        return self.jogadorLocal.verificarSeTemCartaRoubo()
    
    def verificaSeTemCartaDeRoubo(self) -> bool:
        """Verifica se há cartas de roubo no jogo"""
        for carta in self.jogadorLocal.pegarCartas():
            if carta.verificarSeCartaDeRoubo():
                return True
        for carta in self.jogadorRemoto.pegarCartas():
            if carta.verificarSeCartaDeRoubo():
                return True
        return False
    
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
    
    def habilitarPedrasTabuleiro(self):
        for pedra in self.pedrasNoTabuleiro:
            pedra.habilitarPedra()
    

    def to_dict(self):
        return {
            "jogadorLocal": self.jogadorLocal.to_dict(),
            "jogadorRemoto": self.jogadorRemoto.to_dict(),
            "pedrasNoTabuleiro": {pedra.name: qtd for pedra, qtd in self.pedrasNoTabuleiro.items()},
            "cartasNoTabuleiro": [carta.to_dict() if carta else None for carta in self.cartasNoTabuleiro],
            "rodada": self.rodada,
            "partidaEmAndamento": self.partidaEmAndamento,
            "ultimaPartida": self.ultimaPartida,
            "oferta_pendente": self._serializar_oferta_pendente() if hasattr(self, 'oferta_pendente') and self.oferta_pendente else None,
        }
    
    def _serializar_oferta_pendente(self):
        """Serializa a oferta pendente convertendo PedrasEnum para strings"""
        if not self.oferta_pendente:
            return None
        
        try:
            return {
                'pedra_local': self.oferta_pendente['pedra_local'].name if self.oferta_pendente['pedra_local'] else None,
                'pedra_remoto': self.oferta_pendente['pedra_remoto'].name if self.oferta_pendente['pedra_remoto'] else None,
                'jogador_origem': self.oferta_pendente['jogador_origem']
            }
        except Exception as e:
            print(f"Erro ao serializar oferta pendente: {e}")
            print(f"Oferta pendente: {self.oferta_pendente}")
            return None

    @classmethod
    def from_dict(cls, data):
        jogador_local = Jogador.from_dict(data["jogadorLocal"])
        jogador_remoto = Jogador.from_dict(data["jogadorRemoto"])
        tabuleiro = cls(jogador_local, jogador_remoto, inicializar_cartas=False)
        tabuleiro.pedrasNoTabuleiro = {PedrasEnum[p]: v for p, v in data["pedrasNoTabuleiro"].items()}
        tabuleiro.cartasNoTabuleiro = [Carta.from_dict(c) if c else None for c in data["cartasNoTabuleiro"]]
        tabuleiro.rodada = data.get("rodada", 0)
        tabuleiro.partidaEmAndamento = data.get("partidaEmAndamento", False)
        tabuleiro.ultimaPartida = data.get("ultimaPartida", False)
        tabuleiro.oferta_pendente = cls._deserializar_oferta_pendente(data.get("oferta_pendente"))
        return tabuleiro
    
    @classmethod
    def _deserializar_oferta_pendente(cls, oferta_data):
        """Deserializa a oferta pendente convertendo strings para PedrasEnum"""
        if not oferta_data:
            return None
        
        try:
            return {
                'pedra_local': PedrasEnum[oferta_data['pedra_local']] if oferta_data['pedra_local'] else None,
                'pedra_remoto': PedrasEnum[oferta_data['pedra_remoto']] if oferta_data['pedra_remoto'] else None,
                'jogador_origem': oferta_data['jogador_origem']
            }
        except Exception as e:
            print(f"Erro ao deserializar oferta pendente: {e}")
            print(f"Dados da oferta: {oferta_data}")
            return None