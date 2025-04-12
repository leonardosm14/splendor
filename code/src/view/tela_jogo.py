from tkinter import *
from PIL import Image, ImageTk
from model.tabuleiro import Tabuleiro
from model.jogador import Jogador
from model.enums.niveisEnum import NiveisEnum
from model.enums.pedrasEnum import PedrasEnum
from model.pedra import Pedra
from model.carta import Carta
import os

class TelaJogo:
    def __init__(self, root: Tk, show_screen):
        self.root = root
        self.show_screen = show_screen
        self.images = {}

        # Initialize players
        self.jogadorLocal = Jogador(
            nome="Jogador 1",
            pontuacao=0,
            jogadorEmTurno=True,
            jogadorVenceu=False,
            cartasEmMao=[],
            pedrasEmMao={}
        )
        
        self.jogadorRemoto = Jogador(
            nome="Jogador 2",
            pontuacao=0,
            jogadorEmTurno=False,
            jogadorVenceu=False,
            cartasEmMao=[],
            pedrasEmMao={}
        )

        self.tabuleiro = Tabuleiro(jogadorLocal=self.jogadorLocal, jogadorRemoto=self.jogadorRemoto)

        # Window dimensions
        self.WINDOW_WIDTH = 1742
        self.WINDOW_HEIGHT = 926

        # Card and spacing dimensions
        self.CARD_WIDTH = 100
        self.CARD_HEIGHT = 150
        self.HORIZONTAL_GAP = 15  # Gap between cards
        self.DECK_TO_CARDS_GAP = 20  # Gap between deck and first card
        self.VERTICAL_GAP = 50  # Gap between rows

        # Calculate center position for the game grid
        total_cards_width = (self.CARD_WIDTH * 4) + (self.HORIZONTAL_GAP * 3)
        total_width_with_deck = total_cards_width + self.CARD_WIDTH + self.DECK_TO_CARDS_GAP
        
        # Center everything
        self.START_X = 230
        self.START_Y = 100
        
        # Position gems and buttons closer together
        self.GEMS_X = self.START_X + total_width_with_deck + 30  # Closer to cards
        self.BUTTONS_X = self.GEMS_X + 100  # Closer to gems
        
        # Player info constants
        self.PLAYER_INFO_WIDTH = 200
        self.PLAYER_INFO_X = 50

        # Create the main canvas
        self.canvas = Canvas(
            self.root,
            width=self.WINDOW_WIDTH,
            height=self.WINDOW_HEIGHT,
            bg='#352314',
            highlightthickness=0
        )
        self.canvas.pack(expand=True, fill='both')

        # Load and display all elements
        self.load_all_images()
        self.display_player_info()
        self.create_decks_and_cards()
        self.create_gem_piles()
        self.create_action_buttons()

    def load_all_images(self):
        """Load all game images"""
        self.images = {}
        
        # Load deck back images
        for nivel in range(1, 4):
            try:
                deck_img = Image.open(f"resources/cartas/cartasNiveis/nivel{nivel}.png").resize((self.CARD_WIDTH, self.CARD_HEIGHT))
                self.images[f"nivel{nivel}"] = ImageTk.PhotoImage(deck_img)
            except FileNotFoundError as e:
                print(f"Deck image not found: {e}")

        # Load button images with increased height
        try:
            BUTTON_WIDTH = 150
            BUTTON_HEIGHT = 100
            BUTTON_SPACING = 15  # Define spacing between buttons

            self.botao_reservar = Image.open("resources/botões/reservar-carta.png").resize((BUTTON_WIDTH, BUTTON_HEIGHT))
            self.botao_reservar = ImageTk.PhotoImage(self.botao_reservar)
            self.botao_comprar_pedras = Image.open("resources/botões/comprar-pedras.png").resize((BUTTON_WIDTH, BUTTON_HEIGHT))
            self.botao_comprar_pedras = ImageTk.PhotoImage(self.botao_comprar_pedras)
            self.botao_comprar_carta = Image.open("resources/botões/comprar-carta.png").resize((BUTTON_WIDTH, BUTTON_HEIGHT))
            self.botao_comprar_carta = ImageTk.PhotoImage(self.botao_comprar_carta)
            self.botao_trocar_carta = Image.open("resources/botões/trocar-carta.png").resize((BUTTON_WIDTH, BUTTON_HEIGHT))
            self.botao_trocar_carta = ImageTk.PhotoImage(self.botao_trocar_carta)
            
        except FileNotFoundError as e:
            print(f"Button image not found: {e}")

    def create_decks_and_cards(self):
        """Create decks and their visible cards"""
        for i, nivel in enumerate(NiveisEnum):
            y_pos = self.START_Y + (i * (self.CARD_HEIGHT + self.VERTICAL_GAP))
            
            # Mover os baralhos um pouco mais para a direita
            deck_x = self.START_X + 15  # Adiciona 20px para mover os baralhos à direita
            
            # Draw deck
            self.canvas.create_image(
                deck_x, 
                y_pos,
                image=self.images[f"nivel{nivel.value}"],
                anchor='nw'
            )

            # Draw visible cards with adjusted spacing
            for j in range(4):
                x_card = (deck_x + self.CARD_WIDTH + self.DECK_TO_CARDS_GAP + 
                         (j * (self.CARD_WIDTH + self.HORIZONTAL_GAP)))
                self.display_card(x_card, y_pos, nivel, j + 1 + i*4)

    def display_card(self, x, y, nivel, card_id):
        """Display a single card"""
        filename = "diamante-5-rubi-3-esmeralda-2.png"
        try:
            imagem_carta = Image.open(f"resources/cartas/{filename}").resize((self.CARD_WIDTH, self.CARD_HEIGHT))
            self.images[f"card_{card_id}"] = ImageTk.PhotoImage(imagem_carta)
            self.canvas.create_image(x, y, image=self.images[f"card_{card_id}"], anchor='nw')
        except FileNotFoundError:
            print(f"Card image not found: {filename}")

    def create_gem_piles(self, start_x=None):
        """Create vertically aligned gem piles"""
        GEM_SIZE = 50  # Increased gem size
        GEM_VERTICAL_GAP = 60  # Increased vertical gap for larger gems
        
        # Use provided start_x or default to self.GEMS_X
        start_x = 830
        
        # Calculate total height of all gems
        total_gems_height = len(PedrasEnum) * (GEM_SIZE + GEM_VERTICAL_GAP)
        gems_start_y = 170  # Center vertically

        for i, tipo_pedra in enumerate(PedrasEnum):
            y_pos = gems_start_y + (i * GEM_VERTICAL_GAP)
            pedra = Pedra(tipo_pedra, self.tabuleiro.get_quantidade_pedras(tipo_pedra))
            self.create_gem_pile(start_x, y_pos, pedra, GEM_SIZE)

    def create_gem_pile(self, x, y, pedra: Pedra, gem_size: int):
        """Create a single gem pile with stack effect"""
        nome_arquivo = pedra.get_nome_arquivo()
        try:
            imagem = Image.open(f"resources/pedras/{nome_arquivo}.png").resize((gem_size, gem_size))
            self.images[f"pedra_{nome_arquivo}"] = ImageTk.PhotoImage(imagem)

            # Create stack effect
            for i in range(min(3, pedra.quantidade)):
                self.canvas.create_image(
                    x + (i * 3),  # Slightly larger offset for stack effect
                    y + (i * 3),
                    image=self.images[f"pedra_{nome_arquivo}"],
                    anchor='nw'
                )

            # Show quantity
            self.canvas.create_text(
                x + gem_size + 10,
                y + gem_size//2,
                text=str(pedra.quantidade),
                fill='white',
                font=('Aclonica', 14)  # Slightly larger font
            )
        except FileNotFoundError:
            print(f"Gem image not found: {nome_arquivo}")

    def create_action_buttons(self):
        """Create action buttons vertically aligned"""
        buttons = [
            (self.botao_reservar, self.reservar_carta),
            (self.botao_comprar_pedras, self.comprar_pedras),
            (self.botao_comprar_carta, self.comprar_carta),
            (self.botao_trocar_carta, self.trocar_carta)
        ]

        BUTTON_WIDTH = 150
        BUTTON_HEIGHT = 100
        BUTTON_SPACING = 5  # Reduced spacing between buttons
        
        # Calculate total height of all buttons including spacing
        total_buttons_height = (len(buttons) * BUTTON_HEIGHT) + ((len(buttons) - 1) * BUTTON_SPACING)
        
        # Center buttons vertically in the window
        button_start_y = 150
        
        # Position buttons on the right side of the window
        button_x = 900  # 50px margin from right edge

        for i, (image, command) in enumerate(buttons):
            y_pos = button_start_y + (i * (BUTTON_HEIGHT + BUTTON_SPACING))
            self.canvas.create_image(
                button_x,
                y_pos,
                image=image,
                anchor='nw',
                tags=f"button_{i}"
            )
            self.canvas.tag_bind(f"button_{i}", '<Button-1>', lambda e, cmd=command: cmd())

    def display_player_info(self):
        """Display player information with shadows and turn indicators"""
        fonte_nome = ("Aclonica-Regular", 16, "bold")
        fonte_pontos = ("Aclonica-Regular", 12)
        GEM_SIZE = 25
        GEM_GAP = 8

        # Shadow dimensions
        SHADOW_WIDTH = 250  # Unified width for all shadows
        SHADOW_HEIGHT = 150  # Unified height for all shadows

        # Load and resize shadow images
        try:
            # Resize all shadows to the same dimensions
            sombra_sup = Image.open("resources/sombra_superior_esquerda.png").resize((SHADOW_WIDTH, SHADOW_HEIGHT))
            self.sombra_superior = ImageTk.PhotoImage(sombra_sup)

            sombra_inf = Image.open("resources/sombra_inferior_esquerda.png").resize((SHADOW_WIDTH, SHADOW_HEIGHT))
            self.sombra_inferior = ImageTk.PhotoImage(sombra_inf)

            sombra_central = Image.open("resources/sombra_canto_central.png").resize((SHADOW_WIDTH, SHADOW_HEIGHT+50))
            self.sombra_central = ImageTk.PhotoImage(sombra_central)

            # Load "É sua vez" and "Finalizar rodada" buttons with the same dimensions as other buttons
            BUTTON_WIDTH = 150
            BUTTON_HEIGHT = 80
            self.img_eh_sua_vez = ImageTk.PhotoImage(
                Image.open("resources/eh_a_sua_vez.png").resize((BUTTON_WIDTH, BUTTON_HEIGHT))
            )
            self.img_finalizar = ImageTk.PhotoImage(
                Image.open("resources/finalizar_jogada.png").resize((BUTTON_WIDTH, BUTTON_HEIGHT))
            )
        except FileNotFoundError as e:
            print(f"Error loading UI images: {e}")
            return

        # Draw shadows aligned to the left edges
        # Top-left shadow
        self.canvas.create_image(-6, -5, image=self.sombra_superior, anchor='nw')

        # Bottom-left shadow
        self.canvas.create_image(-6, 560, image=self.sombra_inferior, anchor='nw')

        # Center-left shadow
        self.canvas.create_image(-6, 250, image=self.sombra_central, anchor='nw')

        # Adjust player info positions to align with shadows
        # Player 2 (top) info
        player2_start_y = 20
        self.canvas.create_text(
            SHADOW_WIDTH // 2, player2_start_y,
            text=self.jogadorRemoto.getNome(),
            fill="white",
            font=fonte_nome,
            anchor='center'
        )

        # Player 2 gems
        x = 20
        y = player2_start_y + 30
        for tipo_pedra in PedrasEnum:
            nome_arquivo = Pedra(tipo_pedra).get_nome_arquivo()
            try:
                if f"small_pedra_{nome_arquivo}" not in self.images:
                    imagem = Image.open(f"resources/pedras/{nome_arquivo}.png").resize((GEM_SIZE, GEM_SIZE))
                    self.images[f"small_pedra_{nome_arquivo}"] = ImageTk.PhotoImage(imagem)

                self.canvas.create_image(x, y, image=self.images[f"small_pedra_{nome_arquivo}"], anchor='nw')
                self.canvas.create_text(
                    x + GEM_SIZE // 2, y + GEM_SIZE + 5,
                    text=str(self.jogadorRemoto.pedrasEmMao.get(tipo_pedra, 0)),
                    fill="white",
                    font=("Arial", 10)
                )
                x += GEM_SIZE + GEM_GAP
            except FileNotFoundError:
                print(f"Gem image not found: {nome_arquivo}")

        # Player 2 points
        self.canvas.create_text(
            SHADOW_WIDTH // 2, player2_start_y + 80,
            text=f"Pontos: {self.jogadorRemoto.getPontuacao()} / 15",
            fill="white",
            font=fonte_pontos,
            anchor='center'
        )

        # Player 1 infos
        player1_start_y = 590
        self.canvas.create_text(
            SHADOW_WIDTH // 2, player1_start_y,
            text=self.jogadorLocal.getNome(),
            fill="white",
            font=fonte_nome,
            anchor='center'
        )

        # Player 1 pedras
        x = 20
        y = 620
        for tipo_pedra in PedrasEnum:
            nome_arquivo = Pedra(tipo_pedra).get_nome_arquivo()
            if f"small_pedra_{nome_arquivo}" in self.images:
                self.canvas.create_image(x, y, image=self.images[f"small_pedra_{nome_arquivo}"], anchor='nw')
                self.canvas.create_text(
                    x + GEM_SIZE // 2, y + GEM_SIZE + 5,
                    text=str(self.jogadorLocal.pedrasEmMao.get(tipo_pedra, 0)),
                    fill="white",
                    font=("Arial", 10)
                )
                x += GEM_SIZE + GEM_GAP

        # Player 1 pontos
        self.canvas.create_text(
            SHADOW_WIDTH // 2, player1_start_y + 80,
            text=f"Pontos: {self.jogadorLocal.getPontuacao()} / 15",
            fill="white",
            font=fonte_pontos,
            anchor='center'
        )


        # Turn indicator and buttons in center-left
        center_x = SHADOW_WIDTH // 2  # Alinhado com a sombra central
        center_y = self.WINDOW_HEIGHT // 2

        # Texto da rodada
        rodada_atual = self.tabuleiro.get_rodada()  # Obtém a rodada atual da classe Tabuleiro
        self.canvas.create_text(
            center_x ,
            center_y - 190,  # Posicionado logo abaixo do indicador "É sua vez"
            text=f"Rodada {rodada_atual}",
            fill="white",
            font="Aclonica-Regular",
            anchor='center'
        )

        # "É sua vez" indicador
        self.canvas.create_image(
            center_x - BUTTON_WIDTH // 2 - 5,
            center_y - BUTTON_HEIGHT - 100,
            image=self.img_eh_sua_vez,
            anchor='nw'
        )

        # Finalizar jogada button
        self.canvas.create_image(
            center_x - BUTTON_WIDTH // 2 - 5,
            center_y - BUTTON_HEIGHT - 30,
            image=self.img_finalizar,
            anchor='nw',
            tags="finalizar_jogada"
        )
        self.canvas.tag_bind("finalizar_jogada", '<Button-1>', lambda e: self.finalizar_rodada())

    def reservar_carta(self):
        print("Reservar carta clicado")

    def comprar_pedras(self):
        print("Comprar pedras clicado")

    def comprar_carta(self):
        print("Comprar carta clicado")

    def trocar_carta(self):
        print("Trocar carta clicado")

    def finalizar_rodada(self):
        print("Finalizando rodada...")