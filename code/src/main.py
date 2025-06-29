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

class PlayerInterface(DogPlayerInterface):
    def __init__(self):
        self.root = Tk()
        self.root.title("Splendor")
        self.root.geometry("1742x926")
        self.root.resizable(False, False)
        self.background_image = PhotoImage(file="resources/extra/background-inicio.png")

        TkFont.Font(root=self.root, name="Aclonica", family="Aclonica")
        self.default_font = ('Aclonica', 14)
        self.title_font = ('Aclonica', 36, 'bold')

        self.current_screen = None
        self.partida_em_andamento = False
        self.jogador_local = None
        self.jogador_remoto = None
        self.dog_server_interface = None
        self.aguardando_jogadores = False

        self.show_screen("inicial")

    def finalizar_jogada(self, tabuleiro):
        self.send_move(tabuleiro)

    def send_move(self, tabuleiro):
        try:
            move_dict = {
                "tabuleiro_atualizado": tabuleiro.to_dict(),
                "match_status": "next"  # ou "finished" se for o fim da partida
            }
            self.dog_server_interface.send_move(move_dict)
            # Atualiza o tabuleiro localmente para o jogador que enviou a jogada
            messagebox.showinfo("Turno", "Aguardando jogada do oponente...")
        except Exception as e:
            print(f"Erro ao enviar estado do tabuleiro: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", f"Erro ao enviar jogada: {e}")

    def show_screen(self, screen_name: str):
        print(f"Changing to screen: {screen_name}")
        self.clear_screen()

        if screen_name == "inicial":
            self.partida_em_andamento = False
            self.current_screen = TelaInicial(self.root, self.show_screen)

        elif screen_name == "jogo":
            if not self.partida_em_andamento:
                self.aguardando_jogadores = True
                self.start_match(2)

        elif screen_name == "regras":
            destino_voltar = "jogo" if self.partida_em_andamento else "inicial"
            self.current_screen = TelaRegras(self.root, self.show_screen, destino_voltar)

        elif screen_name == "creditos":
            destino_voltar = "jogo" if self.partida_em_andamento else "inicial"
            self.current_screen = TelaCreditos(self.root, self.show_screen, destino_voltar)

    def start_match(self, num_players):
        """Inicia o processo de partida"""
        if not self.dog_server_interface:
            messagebox.showerror("Erro", "Não conectado ao servidor")
            return

        start_status = self.dog_server_interface.start_match(num_players)
        message = start_status.get_message()
        players = start_status.get_players()

        if len(players) < 2:
            self.aguardando_jogadores = True
            self.janela_espera = Toplevel(self.root)
            self.janela_espera.title("Aguardando")
            Label(self.janela_espera, text="Aguardando outro jogador...").pack(pady=20)
            Button(self.janela_espera, text="Cancelar", command=self.cancelar_espera).pack(pady=10)
        else:
            self.tratar_inicio_partida(start_status)

    def cancelar_espera(self):
        """Cancela a espera por outros jogadores"""
        if hasattr(self, 'janela_espera'):
            self.janela_espera.destroy()
        self.dog_server_interface.end_match()
        self.show_screen("inicial")

    def receive_start(self, start_status):
        """Chamado quando a partida realmente inicia"""
        if hasattr(self, 'janela_espera'):
            self.janela_espera.destroy()
        
        self.aguardando_jogadores = False
        self.partida_em_andamento = True
        
        if not self.current_screen or not isinstance(self.current_screen, TelaJogo):
            self.tratar_inicio_partida(start_status)

    def tratar_inicio_partida(self, start_status):
        """Lógica comum para iniciar a partida"""
        players = start_status.get_players()
        if len(players) < 2:
            print("Ainda não há jogadores suficientes. Ignorando início da partida.")
            return

        self.create_players_instances(start_status)
        self.partida_em_andamento = True

        # Usa sempre o seed fixo 12345
        self.seed_partida = 12345
        print(f"Seed fixo usado para a partida: {self.seed_partida}")

        self.current_screen = TelaJogo(
            self.root,
            self.show_screen,
            self.jogador_local,
            self.jogador_remoto,
            self.finalizar_jogada,
            self.seed_partida  # Passa o seed para a TelaJogo
        )

        if self.jogador_local.jogadorEmTurno:
            messagebox.showinfo("Seu turno", "Você começa jogando!")
        else:
            messagebox.showinfo("Turno do oponente", "Aguardando jogada do oponente...")

    def create_players_instances(self, start_status):
        players = start_status.get_players()
        local_id = start_status.get_local_id()

        if len(players) < 2:
            raise ValueError("Jogadores insuficientes para iniciar a partida")

        self.jogador_local = None
        self.jogador_remoto = None

        for name, player_id, order in players:
            print(f"Jogador: {name}, ID: {player_id}, Ordem: {order}")
            if player_id == local_id:
                # Jogador local: habilitado apenas se order == 1
                self.jogador_local = Jogador(nome=name, jogadorEmTurno=(int(order) == 1))
                print(f"Jogador local criado: {name}, em turno: {int(order) == 1}")
            else:
                # Jogador remoto: habilitado apenas se order == 1
                self.jogador_remoto = Jogador(nome=name, jogadorEmTurno=(int(order) == 1))
                print(f"Jogador remoto criado: {name}, em turno: {int(order) == 1}")

        if not self.jogador_local or not self.jogador_remoto:
            raise ValueError("Falha ao criar jogadores")

    def receive_move(self, a_move):
        if self.partida_em_andamento:
            tabuleiro_atualizado = a_move.get("tabuleiro_atualizado")
            print("Recebendo tabuleiro:", tabuleiro_atualizado)  # DEBUG
            if tabuleiro_atualizado:
                try:
                    tabuleiro_obj = Tabuleiro.from_dict(tabuleiro_atualizado)
                    # Inverte jogador local e remoto
                    tabuleiro_obj.jogadorLocal, tabuleiro_obj.jogadorRemoto = tabuleiro_obj.jogadorRemoto, tabuleiro_obj.jogadorLocal
                    
                    # Atualiza o tabuleiro (que agora recarrega as imagens automaticamente)
                    self.current_screen.atualizarTabuleiro(tabuleiro_obj)
                    messagebox.showinfo("Turno", "Agora é seu turno!")
                except Exception as e:
                    print(f"Erro ao processar movimento: {e}")

    def receive_withdrawal_notification(self):
        """Chamado quando um jogador desiste da partida"""
        if self.partida_em_andamento:
            self.partida_em_andamento = False
            if hasattr(self, 'current_screen') and hasattr(self.current_screen, 'notificarDesistencia'):
                self.current_screen.notificarDesistencia()
            else:
                messagebox.showinfo("Desistência", "O jogador adversário desistiu da partida.")
                self.show_screen("inicial")

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def run(self):
        player_name = simpledialog.askstring("Nome", "Digite seu nome:") or "Jogador"
        self.dog_server_interface = DogActor()
        message = self.dog_server_interface.initialize(player_name, self)

        if message == "Você está sem conexão":
            messagebox.showerror("Erro", message)
            self.root.destroy()
        else:
            self.root.mainloop()

if __name__ == "__main__":
    app = PlayerInterface()
    app.run()
