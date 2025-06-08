from model.enums.pedrasEnum import PedrasEnum

class Pedra:
    def __init__(self, tipo: PedrasEnum, habilitada: bool):
        self.tipo = tipo
        self.habilitada = habilitada
    
    """ Verifica se duas pedras são iguais, comparando o tipo."""
    def verificarIgualdadePedras(self, other: "Pedra") -> bool:
        return self.tipo == other.tipo
    
    def habilitarPedra(self):
        self.habilitada = True
    
    def desabilitarPedra(self):
        self.habilitada = False