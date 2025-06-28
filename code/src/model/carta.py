from typing import Dict, Union
from .enums.niveisEnum import NiveisEnum
from .enums.pedrasEnum import PedrasEnum
from .pedra import Pedra


class Carta:
    def __init__(self, 
                 id: int,
                 pontos: int, 
                 nivel: NiveisEnum, 
                 pedras: Dict[PedrasEnum, int],
                 cartaDeRoubo: bool,
                 bonus: Union[PedrasEnum, None],
                 habilitada: bool):
        
        self.id = id
        self.pontos = pontos
        self.nivel = nivel
        self.pedras = pedras
        self.cartaDeRoubo = cartaDeRoubo
        self.bonus = bonus
        self.habilitada = habilitada
    
    def pegarPontosDaCarta(self) -> int:
        return self.pontos
    
    def pegarPedrasDaCarta(self) -> Dict[PedrasEnum, int]:
        return self.pedras
    
    def verificarSeTemBonus(self) -> bool:
        return self.bonus is not None
    
    def pegarPedraDeBonus(self) -> PedrasEnum:
        return self.bonus

    def pegarNivelCarta(self):
        return self.nivel

    def verificarSeCartaDeRoubo(self):
        return self.cartaDeRoubo

    def desabilitarCarta(self):
        self.habilitada = False

    def habilitarCarta(self):
        self.habilitada = True        
    
    def to_dict(self):
        return {
            "id": self.id,
            "pontos": self.pontos,
            "nivel": self.nivel.name,
            "pedras": {pedra.name: qtd for pedra, qtd in self.pedras.items()},
            "cartaDeRoubo": self.cartaDeRoubo,
            "bonus": self.bonus.name if self.bonus else None,
            "habilitada": self.habilitada,
        }

    @classmethod
    def from_dict(cls, data):
        nivel = NiveisEnum[data["nivel"]]
        pedras = {PedrasEnum[k]: v for k, v in data["pedras"].items()}
        bonus = PedrasEnum[data["bonus"]] if data["bonus"] else None
        return cls(
            id=data["id"],
            pontos=data["pontos"],
            nivel=nivel,
            pedras=pedras,
            cartaDeRoubo=data["cartaDeRoubo"],
            bonus=bonus,
            habilitada=data["habilitada"]
        )