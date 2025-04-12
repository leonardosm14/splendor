from tkinter import *
from view.tela_inicial import TelaInicial
from view.tela_jogo import TelaJogo
from view.tela_regras import TelaRegras
from view.tela_creditos import TelaCreditos
import pyglet

from dog.dog_interface import DogPlayerInterface

class PlayerInterface(DogPlayerInterface):  # herda da DogPlayerInterface
    def __init__(self):
        super().__init__()

        # Load Aclonica font
        pyglet.font.add_file('resources/fonts/Aclonica-Regular.ttf')
        
        self.root = Tk()
        self.root.title("Splendor")
        self.root.geometry("1742x926")
        self.root.resizable(False, False)
        
        self.default_font = ('Aclonica-Regular', 14)
        self.title_font = ('Aclonica-Regular', 36, 'bold')
        
        self.current_screen = None
        self.show_screen = self.show_screen
        self.show_screen("inicial")

    def clear_screen(self):
        if self.current_screen and self.current_screen.frame:
            self.current_screen.frame.destroy()

    def show_screen(self, screen_name: str):
        print(f"Changing to screen: {screen_name}")
        self.clear_screen()
        
        if screen_name == "inicial":
            self.current_screen = TelaInicial(self.root, self.show_screen)
        elif screen_name == "jogo":
            self.current_screen = TelaJogo(self.root, self.show_screen)
        elif screen_name == "regras":
            self.current_screen = TelaRegras(self.root, self.show_screen)
        elif screen_name == "creditos":
            self.current_screen = TelaCreditos(self.root, self.show_screen)

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
