from model.enums.pedrasEnum import PedrasEnum

class Pedra:
    def __init__(self, tipo, quantidade=0):
        self.tipo = tipo
        self.quantidade = quantidade

    def getTipo(self) -> PedrasEnum:
        return self.tipo

    def getIlustracao(self) -> str:
        return self.ilustracao

    def mesmoTipo(self, other: 'Pedra') -> bool:
        if isinstance(other, Pedra):
            return self.tipo == other.tipo
        return False

    def get_nome_arquivo(self) -> str:
        """Returns the filename for the gem image."""
        return f"{self.tipo.value.capitalize()} - joia"