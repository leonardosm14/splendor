from tkinter import *
from tkinter import font as TkFont
from view.tela_inicial import TelaInicial
from view.tela_jogo import TelaJogo
from view.tela_regras import TelaRegras
from view.tela_creditos import TelaCreditos

from dog.dog_interface import DogPlayerInterface

class PlayerInterface(DogPlayerInterface):  # herda da DogPlayerInterface
    def __init__(self):
        super().__init__()
        
        self.root = Tk()
        self.root.title("Splendor")
        self.root.geometry("1742x926")
        self.root.resizable(False, False)

        # Fonte personalizada
        TkFont.Font(root=self.root, name="Aclonica", family="Aclonica")
        self.default_font = ('Aclonica', 14)
        self.title_font = ('Aclonica', 36, 'bold')

        self.current_screen = None
        self.partida_em_andamento = False  # novo atributo

        self.show_screen("inicial")

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_screen(self, screen_name: str):
        print(f"Changing to screen: {screen_name}")
        self.clear_screen()
        
        if screen_name == "inicial":
            self.partida_em_andamento = False
            self.current_screen = TelaInicial(self.root, self.show_screen)
        elif screen_name == "jogo":
            self.partida_em_andamento = True
            self.current_screen = TelaJogo(self.root, self.show_screen)
        elif screen_name == "regras":
            destino_voltar = "jogo" if self.partida_em_andamento else "inicial"
            self.current_screen = TelaRegras(self.root, self.show_screen, destino_voltar)
        elif screen_name == "creditos":
            destino_voltar = "jogo" if self.partida_em_andamento else "inicial"
            self.current_screen = TelaCreditos(self.root, self.show_screen, destino_voltar)

    def run(self):
        self.root.mainloop()

    # Métodos obrigatórios da DogPlayerInterface
    def receive_start(self, start_status):
        print("receive_start chamado com:", start_status)

    def receive_move(self, a_move):
        print("receive_move chamado com:", a_move)

    def receive_withdrawal_notification(self):
        print("receive_withdrawal_notification chamado")


if __name__ == "__main__":
    app = PlayerInterface()
    app.run()
