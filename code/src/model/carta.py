from typing import Dict
from .enums.niveisEnum import NiveisEnum
from .enums.pedrasEnum import PedrasEnum
from .pedra import Pedra


class Carta:
    def __init__(self, 
                 cartaId: int, 
                 pontos: int, 
                 nivel: NiveisEnum,
                 pedras: Dict[PedrasEnum, int], 
                 cartaVisivel: bool,
                 cartaDeRoubo: bool,
                 imagem_path: str, 
                 premio: Pedra):
        self.cartaId = cartaId
        self.pontos = pontos
        self.nivel = nivel
        self.pedras = pedras  # dicionário com custos {tipo_joia: quantidade}
        self.cartaVisivel = cartaVisivel
        self.cartaDeRoubo = cartaDeRoubo
        self.imagem_path = imagem_path
        self.visivel = False
        self.premio = premio  # tipo de joia que a carta dá como prêmio

    # Getters
    def getcartaId(self) -> int:
        return self.cartaId

    def getPontos(self) -> int:
        return self.pontos

    def getNivel(self) -> NiveisEnum:
        return self.nivel

    def getPedras(self) -> Dict[PedrasEnum, int]:
        return self.pedras

    def getCartaVisivel(self) -> bool:
        return self.cartaVisivel

    def getCartaDeRoubo(self) -> bool:
        return self.cartaDeRoubo

    # Setters
    def setId(self, id: int) -> None:
        self.cartaId = id

    def setPontos(self, pontos: int) -> None:
        self.pontos = pontos

    def setPedras(self, pedras: Dict[PedrasEnum, int]) -> None:
        self.pedras = pedras
    
    def setCartaDeRoubo(self, cartaDeRoubo: bool) -> None:
        self.cartaDeRoubo = cartaDeRoubo

    # Utility Methods
    def adicionarPedras(self, tipo: PedrasEnum, quantidade: int) -> None:
        if tipo in self.pedras:
            self.pedras[tipo] += quantidade
        else:
            self.pedras[tipo] = quantidade

    def verificarCusto(self, pedrasJogador: Dict[PedrasEnum, int]) -> bool:
        for tipo, quantidade in self.pedras.items():
            if pedrasJogador.get(tipo, 0) < quantidade:
                return False
        return True

    @staticmethod
    def from_filename(cartaId: int, nivel: NiveisEnum, filename: str) -> "Carta":
        """
        Cria uma instância de Carta a partir do nome do arquivo.
        Exemplo de nome: "diamante-5-rubi-3-esmeralda-2.png"
        """
        base_name = filename.replace(".png", "")
        parts = base_name.split("-")

        premio = Pedra(PedrasEnum[parts[0].upper()])
        pontos = int(parts[1])

        pedras = {}
        for i in range(2, len(parts), 2):
            tipo_pedra = PedrasEnum[parts[i].upper()]
            quantidade = int(parts[i + 1])
            pedras[tipo_pedra] = quantidade

        imagem_path = f"resources/cartas/{nivel.name.lower()}/{filename}"

        return Carta(
            cartaId=cartaId,
            pontos=pontos,
            nivel=nivel,
            pedras=pedras,
            cartaVisivel=True,
            cartaDeRoubo=False,
            imagem_path=imagem_path,
            premio=premio
        )
