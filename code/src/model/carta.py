from typing import Dict, Union
from .enums.niveisEnum import NiveisEnum
from .enums.pedrasEnum import PedrasEnum


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
    
    
    def pegarPontos(self) -> int:
        return self.pontos
    
    def pegarPedrasDaCarta(self) -> Dict[PedrasEnum, int]:
        return self.pedras
    
    def temBonus(self) -> bool:
        return self.bonus is not None
    
    def pegarBonus(self) -> PedrasEnum:
        return self.bonus
    
    def pegarPedraDeBonus(self) -> PedrasEnum:
        return self.bonus

    def pegarNivel(self):
        return self.nivel

    def verificarSeCartaDeRoubo(self):
        return self.cartaDeRoubo

    def desabilitarCarta(self):
        self.habilitada = False

    def habilitarCarta(self):
        self.habilitada = True        
    
    def habilitar(self):
        self.habilitada = True
    
    def to_dict(self):
        return {
            "id": self.id,
            "pontos": self.pontos,
            "nivel": self.nivel.name,
            "pedras": {k.name: v for k, v in self.pedras.items()},
            "cartaDeRoubo": self.cartaDeRoubo,
            "bonus": self.bonus.name if self.bonus else None,
            "habilitada": self.habilitada
        }
    
    def to_dict_compact(self):
        """Versão compacta para reduzir o tamanho dos dados enviados"""
        return {
            "i": self.id,  # ID
            "p": self.pontos,  # Pontos
            "n": self.nivel.name,  # Nível
            "pd": {k.name: v for k, v in self.pedras.items()},  # Pedras
            "cR": self.cartaDeRoubo,  # Carta de Roubo
            "b": self.bonus.name if self.bonus else None,  # Bônus
            "h": self.habilitada  # Habilitada
        }

    # @classmethod
    # def from_dict(cls, data):
    #     return cls(
    #         id=data["id"],
    #         pontos=data["pontos"],
    #         nivel=NiveisEnum[data["nivel"]],
    #         pedras={PedrasEnum[k]: v for k, v in data["pedras"].items()},
    #         cartaDeRoubo=data["cartaDeRoubo"],
    #         bonus=PedrasEnum[data["bonus"]] if data["bonus"] else None,
    #         habilitada=data.get("habilitada", True)
    #     )
    
    @classmethod
    def from_dict_compact(cls, data):
        """Versão compacta para deserialização"""
        return cls(
            id=data["i"],
            pontos=data["p"],
            nivel=NiveisEnum[data["n"]],
            pedras={PedrasEnum[k]: v for k, v in data["pd"].items()},
            cartaDeRoubo=data["cR"],
            bonus=PedrasEnum[data["b"]] if data["b"] else None,
            habilitada=data.get("h", True)
        )