from tkinter import *
from tkinter import font as TkFont
from tkinter import simpledialog
from tkinter import messagebox
from model.jogador import Jogador
from model.tabuleiro import Tabuleiro
from view.tela_inicial import TelaInicial
from view.tela_jogo import TelaJogo
from view.tela_regras import TelaRegras
from view.tela_creditos import TelaCreditos

from dog.dog_interface import DogPlayerInterface
from dog.dog_actor import DogActor
from tkinter import PhotoImage

class PlayerInterface(DogPlayerInterface):  # herda da DogPlayerInterface
    def __init__(self):

        self.root = Tk()
        self.root.title("Splendor")
        self.root.geometry("1742x926")
        self.root.resizable(False, False)
        self.background_image = PhotoImage(file="resources/background-inicio.png")

        TkFont.Font(root=self.root, name="Aclonica", family="Aclonica")
        self.default_font = ('Aclonica', 14)
        self.title_font = ('Aclonica', 36, 'bold')

        self.current_screen = None
        self.partida_em_andamento = False
        self.jogador_local = None
        self.jogador_remoto = None

        self.show_screen("inicial")

    def clear_screen(self):
        # Em vez de destruir os widgets, apenas os escondemos
        for widget in self.root.winfo_children():
            widget.pack_forget()  

    def show_screen(self, screen_name: str):
        print(f"Changing to screen: {screen_name}")
        self.clear_screen()
        
        if screen_name == "inicial":
            self.partida_em_andamento = False
            self.current_screen = TelaInicial(self.root, self.show_screen)
        elif screen_name == "jogo":
            if not self.partida_em_andamento:
                self.partida_em_andamento = True
                jogadores = self.start_match(num_players=2)  # Inicia a lógica de sincronização
            self.current_screen = TelaJogo(self.root, self.show_screen, self.local_player, self.remote_player)
        elif screen_name == "regras":
            destino_voltar = "jogo" if self.partida_em_andamento else "inicial"
            self.current_screen = TelaRegras(self.root, self.show_screen, destino_voltar)
        elif screen_name == "creditos":
            destino_voltar = "jogo" if self.partida_em_andamento else "inicial"
            self.current_screen = TelaCreditos(self.root, self.show_screen, destino_voltar)

    def run(self):
        self.player_name = simpledialog.askstring("Nome do Jogador", "Digite seu nome:")
        self.dog_server_interface = DogActor()
        message = self.dog_server_interface.initialize(self.player_name, self)
        
        if message == "Você está sem conexão":
            messagebox.showerror("Erro", message)
            self.root.destroy()  # Fecha o jogo
        else:
            messagebox.showinfo(message=message, title="Dog Server")
            self.root.mainloop()

    # Métodos obrigatórios da DogPlayerInterface
    def receive_start(self, start_status):
        # Este método será chamado quando o servidor confirmar que todos os jogadores estão prontos
        message = start_status.get_message()
        messagebox.showinfo(message="Todos os jogadores estão prontos! Iniciando o jogo...")
        self.show_screen("jogo")  # Transfere para a tela do jogo

    def receive_move(self, a_move):
        print("receive_move chamado com:", a_move)

    def receive_withdrawal_notification(self):
        print("receive_withdrawal_notification chamado")

    def create_players_instances(self, start_status):
        players = start_status.get_players()
        local_id = start_status.get_local_id()
        for player in players:
            name, id, order = player[0], player[1], player[2]
            if id == local_id:
                self.jogador_local = Jogador(nome=name, order=order)
            else:
                self.jogador_remoto = Jogador(nome=name, order=order)

    
    def start_match(self, num_players):
        # Solicita ao servidor para verificar o estado dos jogadores
        start_status = self.dog_server_interface.start_match(num_players)
        message = start_status.get_message()
        players = start_status.get_players()  # Obtém a lista de jogadores conectados

        if len(players) == num_players:  # Verifica se o número de jogadores conectados é suficiente
            messagebox.showinfo(message="Todos os jogadores estão prontos! Iniciando o jogo...")
            self.create_players_instances(start_status=start_status)
            self.show_screen("jogo")  # Transfere para a tela do jogo
        else:
            messagebox.showinfo(message=f"Aguardando outros jogadores... (1/{num_players})")

if __name__ == "__main__":
    app = PlayerInterface()
    app.run()
