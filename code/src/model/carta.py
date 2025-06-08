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