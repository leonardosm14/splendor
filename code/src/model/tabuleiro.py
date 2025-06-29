from typing import Dict, List, Optional, Tuple
import random
from .jogador import Jogador
from .baralho import Baralho
from .carta import Carta
from .enums.pedrasEnum import PedrasEnum
from .enums.niveisEnum import NiveisEnum

# Variável global para o valor mínimo de pontos para vitória
PONTOS_MINIMOS_VITORIA = 4

class Tabuleiro:
    def __init__(self, jogadorLocal: Jogador, jogadorRemoto: Jogador, seed: int = 0, inicializar_cartas=True):
        self.jogadorLocal = jogadorLocal
        self.jogadorRemoto = jogadorRemoto
        self.seed_partida = seed  # Armazena o seed da partida
        
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
    
    def jogadorLocal(self):
        return self.jogadorLocal
    
    def jogadorRemoto(self):
        return self.jogadorRemoto
    
    def inicializar_cartas_tabuleiro(self):
        """Inicializa as cartas visíveis no tabuleiro"""
        self.cartasNoTabuleiro = []
        
        # Usa o seed para determinar qual jogador recebe as cartas de roubo
        # Isso garante que ambos os jogadores tenham o mesmo resultado
        rng = random.Random(self.seed_partida)
        
        for nivel in [0, 1, 2]:  # Níveis enumerados como 0, 1, 2
            for _ in range(4):  # 4 cartas por nível
                try:
                    carta = self.baralhos[nivel].pegarCartaDoBaralho()
                    
                    # Se for carta de roubo, pega outra carta até encontrar uma normal
                    tentativas = 0
                    max_tentativas = min(20, len(self.baralhos[nivel].cartas))  # Não tenta mais que cartas disponíveis
                    
                    while carta and carta.cartaDeRoubo and tentativas < max_tentativas:
                        # Distribui a carta de roubo de forma determinística baseada no seed
                        # Se o número aleatório for par, vai para jogadorLocal, senão para jogadorRemoto
                        if rng.randint(0, 1) == 0:
                            self.jogadorLocal.adicionarCartaDeRoubo(carta)
                            print(f"Carta de roubo adicionada ao jogador local: {carta.id}")
                        else:
                            self.jogadorRemoto.adicionarCartaDeRoubo(carta)
                            print(f"Carta de roubo adicionada ao jogador remoto: {carta.id}")
                        
                        # Pega outra carta
                        carta = self.baralhos[nivel].pegarCartaDoBaralho()
                        tentativas += 1
                    
                    # Se ainda é carta de roubo após todas as tentativas, distribui de forma determinística
                    if carta and carta.cartaDeRoubo:
                        if rng.randint(0, 1) == 0:
                            self.jogadorLocal.adicionarCartaDeRoubo(carta)
                            print(f"Carta de roubo final adicionada ao jogador local: {carta.id}")
                        else:
                            self.jogadorRemoto.adicionarCartaDeRoubo(carta)
                            print(f"Carta de roubo final adicionada ao jogador remoto: {carta.id}")
                        self.cartasNoTabuleiro.append(None)
                    else:
                        # Carta normal encontrada
                        self.cartasNoTabuleiro.append(carta)
                        
                except (ValueError, IndexError) as e:
                    print(f"Erro ao pegar carta do baralho nível {nivel}: {e}")
                    self.cartasNoTabuleiro.append(None)
        
        print(f"Inicialização concluída. Cartas no tabuleiro: {len(self.cartasNoTabuleiro)}")
        print(f"Cartas de roubo do jogador local: {len([c for c in self.jogadorLocal.pegarCartas() if c.cartaDeRoubo])}")
        print(f"Cartas de roubo do jogador remoto: {len([c for c in self.jogadorRemoto.pegarCartas() if c.cartaDeRoubo])}")
    
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
        baralho_idx = nivel.value - 1
        if 0 <= baralho_idx < len(self.baralhos):
            self.baralhos[baralho_idx].adicionarCarta(carta)
            print(f"Carta {id} adicionada ao baralho {nivel.name} (índice {baralho_idx})")
        else:
            print(f"ERRO: Índice de baralho inválido {baralho_idx} para nível {nivel.name}")

    def ehUltimaPartida(self) -> bool:
        return self.ultimaPartida
    
    def atualizarPedrasNoTabuleiro(self):
        """Atualiza a contagem de pedras disponíveis no tabuleiro"""
        pedrasJogadorLocal = self.jogadorLocal.pegarPedras()
        pedrasJogadorRemoto = self.jogadorRemoto.pegarPedras()
        
        self.pedrasNoTabuleiro = {
            pedra: max(0, 7 - (pedrasJogadorLocal[pedra] + pedrasJogadorRemoto[pedra]))
            for pedra in PedrasEnum
        }
    
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
    
    def verificarIgualdadePedras(self, pedraA: PedrasEnum, pedraB: PedrasEnum) -> bool:
        return pedraA == pedraB
    
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
        # Como não há mais classe Pedra, este método não faz mais sentido
        # As pedras são habilitadas/desabilitadas através da interface gráfica
        pass
    

    def to_dict(self):
        # Versão compactada para reduzir o tamanho dos dados enviados
        return {
            "jL": self.jogadorLocal.to_dict_compact(),  # Jogador Local
            "jR": self.jogadorRemoto.to_dict_compact(),  # Jogador Remoto
            "p": {pedra.name: qtd for pedra, qtd in self.pedrasNoTabuleiro.items()},  # Pedras
            "c": [carta.to_dict_compact() if carta else None for carta in self.cartasNoTabuleiro],  # Cartas
            "r": self.rodada,  # Rodada
            "pA": self.partidaEmAndamento,  # Partida em Andamento
            "uP": self.ultimaPartida,  # Última Partida
            "o": self._serializar_oferta_pendente_compact() if hasattr(self, 'oferta_pendente') and self.oferta_pendente else None,  # Oferta
            "s": getattr(self, 'seed_partida', 0),  # Seed da partida
        }
    
    def _serializar_oferta_pendente_compact(self):
        """Serializa a oferta pendente de forma compacta"""
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
            return None

    @classmethod
    def from_dict(cls, data):
        # Versão compactada para deserialização
        jogador_local = Jogador.from_dict_compact(data["jL"])
        jogador_remoto = Jogador.from_dict_compact(data["jR"])
        tabuleiro = cls(jogador_local, jogador_remoto, inicializar_cartas=False)
        tabuleiro.pedrasNoTabuleiro = {PedrasEnum[p]: v for p, v in data["p"].items()}
        tabuleiro.cartasNoTabuleiro = [Carta.from_dict_compact(c) if c else None for c in data["c"]]
        tabuleiro.rodada = data.get("r", 0)
        tabuleiro.partidaEmAndamento = data.get("pA", False)
        tabuleiro.ultimaPartida = data.get("uP", False)
        tabuleiro.oferta_pendente = cls._deserializar_oferta_pendente_compact(data.get("o"))
        tabuleiro.seed_partida = data.get("s", 0)
        print(f"Tabuleiro deserializado com seed: {tabuleiro.seed_partida}")
        
        # Recria os baralhos com o seed correto para garantir consistência
        if tabuleiro.seed_partida > 0:
            print(f"Recriando baralhos com seed: {tabuleiro.seed_partida}")
            tabuleiro.baralhos = [
                Baralho(nivel=NiveisEnum.NIVEL1, seed=tabuleiro.seed_partida),
                Baralho(nivel=NiveisEnum.NIVEL2, seed=tabuleiro.seed_partida),
                Baralho(nivel=NiveisEnum.NIVEL3, seed=tabuleiro.seed_partida)
            ]
        
        return tabuleiro
    
    @classmethod
    def _deserializar_oferta_pendente_compact(cls, oferta_data):
        """Deserializa a oferta pendente de forma compacta"""
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
            return None