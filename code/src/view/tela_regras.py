from tkinter import *
from PIL import Image, ImageTk

class TelaRegras:
    def __init__(self, root: Tk, show_screen, destino_voltar="inicial"):
        self.show_screen = show_screen
        self.destino_voltar = destino_voltar  # Novo atributo

        # Frame principal
        self.frame = Frame(root)
        self.frame.pack(expand=True, fill='both')

        # Canvas para todas as imagens
        self.canvas = Canvas(
            self.frame,
            width=1080,
            height=720,
            highlightthickness=0,
            bg='#352314'
        )
        self.canvas.pack()

        # Título
        self.canvas.create_text(
            540, 100,
            text="Regras do Jogo",
            fill="white",
            font=('Aclonica', 36, 'bold')
        )

        # Texto das regras
        texto_regras = (
            "Quem inicia a partida é sorteado de forma aleatória. A cada turno, cada jogador pode escolher apenas uma das seguintes ações:\n\n"
            "• Comprar três pedras diferentes\n"
            "• Comprar duas pedras iguais\n"
            "• Reservar 1 das cartas da mesa e, se ainda houver ouro disponível, comprar um\n"
            "• Comprar uma das cartas dispostas na mesa se tiver pedras o suficiente e retirar outra do baralho para pôr no lugar.\n"
            "  Se for uma carta de roubo, o jogador fica com ela pra si e retira outra carta\n"
            "• Fazer uma oferta de troca de pedras ao outro jogador. Se ele recusar, escolher outra ação (pode ser outra oferta)\n"
            "• Usar uma carta de roubo, se tiver, para roubar as pedras descritas na carta do outro jogador.\n"
            "  Se o jogador roubado não tiver todas as pedras, apenas as que ele tiver serão roubadas.\n"
            "  Se ele não tiver nenhuma, o roubo não pode ser feito.\n\n"
            "Encerramento da Partida:\n"
            "A partida é encerrada quando um dos jogadores atingir 15 ou mais pontos.\n"
            "O adversário daquele que alcançou os 15 pontos ainda tem direito a mais uma jogada final\n"
            "de compra de carta na tentativa de ultrapassá-lo. Ganha aquele que tiver mais pontos."
        )

        self.canvas.create_text(
            540, 400,
            text=texto_regras,
            fill="white",
            font=('Aclonica', 14),
            justify="center",
            width=800
        )

        # Imagem do botão "Voltar"
        self.botao_voltar_img = Image.open("resources/botoes/botao-voltar.png")
        self.botao_voltar_img = self.botao_voltar_img.resize((150, 70))
        self.botao_voltar_tk = ImageTk.PhotoImage(self.botao_voltar_img)

        # Colocar imagem no canvas como botão
        self.botao_voltar = self.canvas.create_image(
            100, 50,
            image=self.botao_voltar_tk,
            anchor="center",
            tags="voltar"
        )

        # Bind eventos para o botão
        self.canvas.tag_bind("voltar", "<Button-1>", lambda e: self.voltar())
        self.canvas.tag_bind("voltar", "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind("voltar", "<Leave>", lambda e: self.canvas.config(cursor=""))

    def voltar(self):
        print(f"Returning to screen: {self.destino_voltar}")
        if self.show_screen:
            self.show_screen(self.destino_voltar)
        else:
            print("Error: show_screen not properly initialized")
