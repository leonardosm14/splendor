from tkinter import *
from PIL import Image, ImageTk
from view.tela_regras import TelaRegras

class TelaInicial:
    def __init__(self, root: Tk, show_screen):
        self.root = root
        self.show_screen = show_screen  # Função para mudar de tela
        self.root.title("Splendor")
        self.root.geometry("1080x720")
        self.root.resizable(False, False)

        # Frame principal
        self.frame = Frame(self.root)
        self.frame.pack(expand=True, fill='both')

        # Canvas para todas as imagens
        self.canvas = Canvas(
            self.frame,
            width=1080,
            height=720,
            highlightthickness=0
        )
        self.canvas.pack()

        # Fundo
        bg = Image.open("resources/background-inicio.png").resize((1080, 720))
        self.bg_photo = ImageTk.PhotoImage(bg)
        self.canvas.create_image(
            540,  # x = width/2
            360,  # y = height/2
            image=self.bg_photo
        )

        # Logo com transparência
        logo = Image.open("resources/logo.png")
        logo = logo.resize((int(logo.width * 0.75), int(logo.height * 0.75)))
        self.logo_photo = ImageTk.PhotoImage(logo)
        self.canvas.create_image(
            540,  # x = width/2
            150,  # y position for logo
            image=self.logo_photo
        )

        # Cartas no canto esquerdo
        cartas = Image.open("resources/cartas-inicio.png")
        # Reduzir para 40% do tamanho original
        new_width = int(cartas.width * 0.60)
        new_height = int(cartas.height * 0.60)
        cartas = cartas.resize((new_width, new_height))
        self.cartas_photo = ImageTk.PhotoImage(cartas)
        self.canvas.create_image(
            180,
            360,
            image=self.cartas_photo
        )

        # Joias no canto direito
        joias = Image.open("resources/joias-inicio.png")
        # Reduzir para 40% do tamanho original
        new_width = int(joias.width * 0.65)
        new_height = int(joias.height * 0.65)
        joias = joias.resize((new_width, new_height))
        self.joias_photo = ImageTk.PhotoImage(joias)
        self.canvas.create_image(
            900,
            360,
            image=self.joias_photo
        )

        # Box dimensions (reduced sizes)
        BOX_WIDTH = 267  # Reduced by half (534/2)
        BOX_HEIGHT = 272  # Reduced by half (545/2)
        BUTTON_WIDTH = 207  # Reduced by half (414/2)
        BUTTON_HEIGHT = 65  # New button height
        BUTTON_SPACING = 15  # Reduced by half (30/2)

        # Calculate vertical center of the screen (excluding logo area)
        LOGO_BOTTOM = 150 + 50  # Approximate bottom of logo (logo y + half height)
        SCREEN_HEIGHT = 720
        available_space = SCREEN_HEIGHT - LOGO_BOTTOM
        
         # Centralizar a sombra no meio da tela
        box_center_y = 720 // 2

        # Redimensiona a sombra e posiciona centralizada
        sombra = Image.open("resources/botões/Sombra.png")
        sombra = sombra.resize((BOX_WIDTH, BOX_HEIGHT))
        self.sombra_photo = ImageTk.PhotoImage(sombra)
        self.canvas.create_image(
            540,
            box_center_y,
            image=self.sombra_photo
        )

        # Calcular posições dos botões com base no centro da sombra
        total_buttons_height = (3 * BUTTON_HEIGHT) + (2 * BUTTON_SPACING)
        buttons_start_y = box_center_y - (total_buttons_height // 2)
        y_positions = [
            280 + i * (BUTTON_HEIGHT + BUTTON_SPACING)
            for i in range(3)
        ]

        # Carregar e redimensionar imagens dos botões para o tamanho correto
        jogar = Image.open("resources/botões/jogar.png")
        regras = Image.open("resources/botões/regras.png")
        creditos = Image.open("resources/botões/creditos.png")

        # Redimensionar para o tamanho correto
        jogar = jogar.resize((BUTTON_WIDTH, BUTTON_HEIGHT))
        regras = regras.resize((BUTTON_WIDTH, BUTTON_HEIGHT))
        creditos = creditos.resize((BUTTON_WIDTH, BUTTON_HEIGHT))

        # Converter imagens para PhotoImage
        self.jogar_photo = ImageTk.PhotoImage(jogar)
        self.regras_photo = ImageTk.PhotoImage(regras)
        self.creditos_photo = ImageTk.PhotoImage(creditos)

        # Place buttons at calculated positions
        self.jogar_button = self.canvas.create_image(
            540,  # x = width/2
            y_positions[0],
            image=self.jogar_photo,
            tags="jogar"
        )
        
        self.regras_button = self.canvas.create_image(
            540,
            y_positions[1],
            image=self.regras_photo,
            tags="regras"
        )
        
        self.creditos_button = self.canvas.create_image(
            540,
            y_positions[2],
            image=self.creditos_photo,
            tags="creditos"
        )

        # Adicionar eventos de clique
        self.canvas.tag_bind("jogar", "<Button-1>", self.iniciarJogo)
        self.canvas.tag_bind("regras", "<Button-1>", self.mostrarRegras)
        self.canvas.tag_bind("creditos", "<Button-1>", self.mostrarCreditos)

        # Adicionar eventos hover (opcional)
        for tag in ["jogar", "regras", "creditos"]:
            self.canvas.tag_bind(tag, "<Enter>", lambda e, t=tag: self.on_enter(t))
            self.canvas.tag_bind(tag, "<Leave>", lambda e, t=tag: self.on_leave(t))

    def on_enter(self, tag: str) -> None:
        self.canvas.config(cursor="hand2")

    def on_leave(self, tag: str) -> None:
        self.canvas.config(cursor="")

    def button_click_animation(self, tag: str) -> None:
        self.canvas.move(tag, 0, 5)
        self.root.after(100, lambda: self.canvas.move(tag, 0, -5))

    def iniciarJogo(self, event=None) -> None:
        self.show_screen("jogo")

    def mostrarRegras(self, event=None) -> None:
        print("Showing rules screen...")  # Debug print
        self.show_screen("regras")  # Use the screen management system

    def mostrarCreditos(self, event=None) -> None:
        self.show_screen("creditos")

    def sair(self) -> None:
        print("Saindo do jogo...")
        self.root.quit()