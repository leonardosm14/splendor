from tkinter import *
import random
from tkinter import messagebox
from PIL import Image, ImageTk
from pathlib import Path
from typing import Dict, List

from dog.dog_actor import DogActor
from model.tabuleiro import Tabuleiro
from model.jogador import Jogador
from model.enums.niveisEnum import NiveisEnum
from model.enums.pedrasEnum import PedrasEnum
from model.pedra import Pedra
from model.carta import Carta

class TelaJogo:
    def __init__(self, root: Tk, show_screen, jogador_local: Jogador, jogador_remoto: Jogador, finalizar_jogada_callback):
        self.root = root
        self.show_screen = show_screen
        
        # Window dimensions
        self.WINDOW_WIDTH = 1280
        self.WINDOW_HEIGHT = 720

        # Card and spacing dimensions
        self.CARD_WIDTH = 10
        self.CARD_HEIGHT = 15
        self.HORIZONTAL_GAP = 100
        self.DECK_TO_CARDS_GAP = 30
        self.VERTICAL_GAP = 150

        # Calculate positions
        total_cards_width = (self.CARD_WIDTH * 4) + (self.HORIZONTAL_GAP * 3)
        total_width_with_deck = total_cards_width + self.CARD_WIDTH + self.DECK_TO_CARDS_GAP
        
        self.START_X = 450
        self.START_Y = 110
        
        self.GEMS_X = self.START_X + total_width_with_deck + 130
        self.GEM_SIZE = 60
        self.BUTTONS_X = self.GEMS_X
        
        # Player info
        self.PLAYER_INFO_WIDTH = 200
        self.PLAYER_INFO_X = 50

        # Create single canvas
        self.canvas = Canvas(
            root,
            width=self.WINDOW_WIDTH,
            height=self.WINDOW_HEIGHT,
            bg='#352314',
            highlightthickness=0
        )
        self.canvas.pack(expand=True, fill='both')

        self.tabuleiro = Tabuleiro(jogadorLocal=jogador_local, jogadorRemoto=jogador_remoto)  # Inicializa com jogadores
        self.tabuleiro_inicio_partida = self.tabuleiro  # Utilizado para restaurar o estado inicial do tabuleiro naquela partida
        self.finalizar_jogada_callback = finalizar_jogada_callback  # Callback para finalizar jogada

        # Estruturas de dados
        self.cartas: Dict[ImageTk.PhotoImage, dict] = dict()
        self.pedras: List[ImageTk.PhotoImage] = list()
        self.botoes: Dict[str, ImageTk.PhotoImage] = dict()
        self.pedrasSelecionadas: List[PedrasEnum] = list()
        self.cartaSelecionada = None
        self.ofertaDePedras = {"local": None, "remoto": None}

        # Carrega os recursos
        self.carregarCartas()
        self.carregarPedras()
        self.carregarBotoes()
        self.desenharInfosJogadores()
        
        # Garantir que as dimensões sejam corretas
        self.root.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.canvas.configure(width=self.WINDOW_WIDTH, height=self.WINDOW_HEIGHT)

        self.capas_baralho = {}
        for nivel in [1, 2, 3]:
            try:
                img = Image.open(f"./resources/cartas/baralho/{nivel}.png").resize((self.CARD_WIDTH*10, self.CARD_HEIGHT*10), Image.Resampling.LANCZOS)
                self.capas_baralho[nivel] = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Erro ao carregar capa do baralho nível {nivel}: {e}")
                self.capas_baralho[nivel] = None

        
        # Configurar layout imediatamente
        self.configurarTela()
        
        # Forçar atualização do canvas
        self.canvas.update()

        self.habilitarJogadas()
    
    def habilitarJogadas(self):
        if self.tabuleiro.jogadorLocal.jogadorEmTurno:
            """Habilita as jogadas possíveis na tela"""
            self.habilitarBotaoComprarPedras()
            self.habilitarBotaoComprarCarta()
            self.habilitarReservarCarta()
            self.habilitarBotaoOfertaDeTroca()
        else:
            self.desabilitarBotaoComprarCarta()
            self.desabilitarBotaoComprarPedras()
            self.desabilitarReservarCarta()
            self.desabilitarBotaoOfertaDeTroca()
            

    def pegarTabuleiro(self) -> Tabuleiro:
        return self.tabuleiro

    def atualizarTabuleiro(self, tabuleiro: Tabuleiro):
        self.tabuleiro = tabuleiro
        self.tabuleiro_inicio_partida = tabuleiro
        self.desenharTabuleiro()
        self.desenharPedras()
        self.desenharBotoes()
        self.desenharInfosJogadores()
        self.habilitarJogadas()
    
    def desenharInfosJogadores(self):
        """Atualiza as informações dos jogadores na interface"""
        infos_jogador_local = {
            "nome": self.tabuleiro.jogadorLocal.pegarNome(),
            "pontos": self.tabuleiro.jogadorLocal.pegarPontuacaoJogador(),
            "pedras": self.tabuleiro.jogadorLocal.pegarPedras(),
            "cartas": self.tabuleiro.jogadorLocal.pegarCartas()
        }

        infos_jogador_remoto = {
            "nome": self.tabuleiro.jogadorRemoto.pegarNome(),
            "pontos": self.tabuleiro.jogadorRemoto.pegarPontuacaoJogador(),
            "pedras": self.tabuleiro.jogadorRemoto.pegarPedras(),
            "cartas": self.tabuleiro.jogadorRemoto.pegarCartas()
        }

    
    def notificarDesistencia(self):
        self.tabuleiro.partidaEmAndamento = False  # Marca que a partida não está mais em andamento
        # Cria uma nova janela para notificar a desistência
        desistencia_window = Toplevel(self.root)
        desistencia_window.title("Desistência")
        desistencia_window.geometry("300x150")
        desistencia_window.resizable(False, False)
        
        # Configura o layout
        frame = Frame(desistencia_window, bg="white")
        frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        Label(frame, text="O jogador adversário desistiu da partida.", 
              font=("Arial", 12), bg="white", fg="red", wraplength=280).pack(pady=20)
        
        Button(frame, text="OK", command=lambda: [desistencia_window.destroy(), self.restaurarEstadoInicial()], 
               font=("Arial", 10), bg="lightgray").pack(pady=10)

    def restaurarEstadoInicial(self):
        """Restaura o estado inicial do jogo"""
        self.frame.destroy()  # Destroi a instância atual da tela
        self.show_screen("inicial")  # Retorna para a tela inicial
    
    def desabilitarJogador(self):
        self.tabuleiro.jogadorLocal.desabilitarJogador()

    def carregarCartas(self):
        """Carrega as imagens das cartas normais e de roubo"""
        def carregarCartasDeDiretorio(diretorio: Path, nivel: NiveisEnum = None):
            """Carrega cartas de um diretório específico"""
            for carta_img in diretorio.glob("*.png"):
                try:
                    img = Image.open(carta_img)
                    img = img.resize((self.CARD_WIDTH * 10, self.CARD_HEIGHT * 10), Image.Resampling.LANCZOS)  # Redimensiona a imagem
                    img_tk = ImageTk.PhotoImage(img)
                    self.cartas[img_tk] = {"nivel": nivel}  # Adiciona informações da carta
                except Exception as e:
                    print(f"Erro ao carregar carta {carta_img}: {e}")

        # Diretórios das cartas
        diretorios_cartas = {
            NiveisEnum.NIVEL1: Path("./resources/cartas/cartas-tabuleiro/cartas-nivel-1"),
            NiveisEnum.NIVEL2: Path("./resources/cartas/cartas-tabuleiro/cartas-nivel-2"),
            NiveisEnum.NIVEL3: Path("./resources/cartas/cartas-tabuleiro/cartas-nivel-3"),
        }
        cartas_roubo_dir = Path("./resources/cartas/cartas-de-roubo")

        # Carregar cartas normais
        for nivel, diretorio in diretorios_cartas.items():
            carregarCartasDeDiretorio(diretorio, nivel)

        # Carregar cartas de roubo
        carregarCartasDeDiretorio(cartas_roubo_dir)
        

    def carregarBotoes(self):
        """Carrega e redimensiona as imagens dos botões"""
        botoes_dir = Path("./resources/botoes")
        tamanho_botoes = (150, 100)  # largura x altura desejada

        for botao_img in botoes_dir.glob("*.png"):
            try:
                img = Image.open(botao_img)
                img = img.resize(tamanho_botoes, Image.Resampling.LANCZOS)
                img_tk = ImageTk.PhotoImage(img)
                self.botoes[botao_img.stem] = img_tk
            except Exception as e:
                print(f"Erro ao carregar botão {botao_img}: {e}")

    def carregarPedras(self):
        """Carrega as imagens das pedras"""
        pedras_dir = Path("./resources/pedras")
        for pedra_img in pedras_dir.glob("*.png"):
            try:
                img = Image.open(pedra_img)
                img = img.resize((self.GEM_SIZE, self.GEM_SIZE), Image.Resampling.LANCZOS)  # Redimensiona a imagem
                img_tk = ImageTk.PhotoImage(img)
                self.pedras.append(img_tk)
            except Exception as e:
                print(f"Erro ao carregar pedra {pedra_img}: {e}")

    def configurarTela(self):
        self.canvas.delete("all")
        self.desenharTabuleiro()
        self.desenharPedras()
        self.desenharInfosJogadores()
        self.desenharBotoes()


    def clickComprarPedras(self):
        """Ação ao clicar no botão 'Comprar Pedras'"""
        messagebox.showinfo("Comprar Pedras", "Selecione as pedras que deseja comprar clicando no tabuleiro.")
        
        # Desativa os demais botões de compra
        self.desabilitarBotaoComprarCarta()
        self.desabilitarReservarCarta()
        self.desabilitarBotaoOfertaDeTroca()
        self.desabilitarCartas()

        self.habilitarPedras()
        self.habilitarDesfazerJogada()

    def clickDesfazerJogada(self):
        """Ação ao clicar no botão 'Desfazer Jogada'"""
        if not self.movimentos_realizados:
            messagebox.showinfo("Desfazer Jogada", "Nenhuma jogada foi realizada para desfazer.")
            return

        # Restaura o estado inicial do tabuleiro
        self.tabuleiro = self.tabuleiro_inicio_partida
        self.desenharTabuleiro()  # Redesenha o tabuleiro com o estado inicial
        messagebox.showinfo("Jogada Desfeita", "O tabuleiro foi restaurado ao estado inicial da partida.")

    def clickComprarCarta(self):
        """Ação ao clicar no botão 'Comprar Carta'"""
        messagebox.showinfo("Comprar Carta", "Selecione a carta que deseja comprar clicando no tabuleiro.")

        self.desabilitarBotaoComprarPedras()
        self.desabilitarReservarCarta()
        self.desabilitarBotaoOfertaDeTroca()
        self.desabilitarPedras()

        self.habilitarCartas()
        self.habilitarDesfazerJogada()
    

    def selecionarPedra(self, pedra, jogador):
        """Guarda a pedra selecionada no dict de oferta de pedras"""
        self.ofertaDePedras[jogador] = pedra
        messagebox.showinfo("Troca de Pedras", f"Você selecionou a pedra {pedra} para troca.")
    
    
    def exibirPopupTroca(self):
        """Exibe um popup para troca de pedras"""
        popup = Toplevel(self.root)
        popup.title("Troca de Pedras")
        popup.geometry("300x200")
        
        Label(popup, text="Selecione as pedras que deseja trocar:").pack(pady=10)

        pedras_jogador_local = self.tabuleiro.jogadorLocal.pegarPedras()
        for pedra, qtd in pedras_jogador_local.items():
            if qtd > 0:
                pedra_button = Button(popup, text=f"{pedra.name} ({qtd})", 
                                      command=lambda p=pedra: self.selecionarPedra(p, "local"))
                pedra_button.pack(pady=5)

        pedras_jogador_remoto = self.tabuleiro.jogadorRemoto.pegarPedras()
        for pedra, qtd in pedras_jogador_remoto.items():
            if qtd > 0:
                pedra_button = Button(popup, text=f"{pedra.name} ({qtd})", 
                                      command=lambda p=pedra: self.selecionarPedra(p, "remoto"))
                pedra_button.pack(pady=5)
        
        Button(popup, text="Finalizar Troca", command=lambda: [popup.destroy(), self.clickFinalizarJogada()]).pack(pady=10)

    def clickOfertaDeTroca(self):
        """Ação ao clicar no botão 'Oferta de Troca'"""
        messagebox.showinfo("Oferta de Troca", "Selecione as pedras que deseja trocar.")
        self.desabilitarBotaoComprarPedras()
        self.desabilitarReservarCarta()
        self.desabilitarBotaoComprarPedras()
        self.desabilitarPedras()
        self.habilitarCartas()
        self.habilitarDesfazerJogada()

        self.exibirPopupTroca()

    def clickPedra(self, pedra: PedrasEnum):
        """Ação ao clicar em uma pedra no tabuleiro"""
        self.pedrasSelecionadas.append(pedra)

        if len(self.pedrasSelecionadas) == 2:
            # Duas pedras selecionadas: verifica se são iguais
            if self.pedrasSelecionadas[0] == self.pedrasSelecionadas[1]:
                sucesso = self.tabuleiro.pegarPedrasDoTabuleiro({pedra: 2})
                if sucesso:
                    messagebox.showinfo(
                        "Pedras Selecionadas",
                        f"Você selecionou 2 pedras do tipo {pedra.name}."
                    )
                    self.habilitarBotaoFinalizarJogada()
                    self.desabilitarPedras()  # Desabilita as pedras após seleção válida
            else:
                messagebox.showinfo(
                    "Pedras Selecionadas",
                    f"Você selecionou 2 pedras diferentes: {self.pedrasSelecionadas[0].name} e {self.pedrasSelecionadas[1].name}. Agora selecione uma terceira pedra diferente."
                )
        elif len(self.pedrasSelecionadas) == 3:
            p1, p2, p3 = self.pedrasSelecionadas
            # Se alguma pedra for igual, não é permitido
            if p1 == p2 or p1 == p3 or p2 == p3:
                messagebox.showerror(
                    "Erro",
                    "A terceira pedra selecionada não pode ser igual às anteriores. Tente novamente."
                )
                self.pedrasSelecionadas.pop()  # Remove a última pedra selecionada
            else:
                sucesso = self.tabuleiro.pegarPedrasDoTabuleiro({p1: 1, p2: 1, p3: 1})
                if sucesso:
                    messagebox.showinfo(
                        "Pedras Selecionadas",
                        f"Você selecionou 3 pedras diferentes: {p1.name}, {p2.name}, e {p3.name}."
                    )
                    self.habilitarBotaoFinalizarJogada()
                    self.desabilitarPedras()  # Desabilita as pedras após seleção válida
        

    def clickCarta(self, indiceCarta: int):
        """Ação ao clicar em uma carta no tabuleiro"""
        self.cartaSelecionada = self.tabuleiro.pegarCartaDoTabuleiro(indiceCarta)
        pedras_suficientes = self.tabuleiro.verificarPedrasSuficientes(self.cartaSelecionada)
        if not pedras_suficientes:
            self.notificarJogadaInvalida()
            self.cartaSelecionada = None
        else:
            self.habilitarBotaoFinalizarJogada()
    
    def reporTabuleiro(self, nivel: NiveisEnum):
        tem_mesmo_nivel = self.tabuleiro.verificaSeTemCartaComMesmoNivel(nivel)
        if tem_mesmo_nivel:
            nova_carta = self.tabuleiro.adicionarCartaTabuleiro(nivel)
            carta_roubo = self.tabuleiro.verificaSeCartaDeRoubo(nova_carta)
            if carta_roubo:
                self.tabuleiro.adicionarCartaNaMao(nova_carta)
                self.reporTabuleiro(nivel) 
            self.atualizarTabuleiro()

    def realizarCompraCarta(self):
        self.tabuleiro.adicionarCartaNaMao(self.cartaSelecionada)
        pontos_carta = self.tabuleiro.pegarPontosCarta(self.cartaSelecionada)
        pedras_carta = self.tabuleiro.pegarPedrasCarta(self.cartaSelecionada)
        tem_bonus = self.tabuleiro.verificarBonusCarta(self.cartaSelecionada)
        
        if tem_bonus:
            pedra_bonus = self.tabuleiro.pegarPedraDeBonus(self.cartaSelecionada)
            self.tabuleiro.jogadorLocal.adicionarPedra(pedra_bonus)
        
        self.tabuleiro.jogadorLocal.adicionarPontos(pontos_carta)
        self.tabuleiro.jogadorLocal.removerPedras(pedras_carta)
        self.tabuleiro.jogadorLocal.adicionarPedra(pedra_bonus)
        
        self.desenharInfosJogadores()
        
        reservada = self.tabuleiro.verificaSeEstaReservada(self.cartaSelecionada)

        if not reservada:
            self.tabuleiro.removerCartaDoTabuleiro(self.cartaSelecionada)
            nivel_carta = self.tabuleiro.pegarNivelCarta(self.cartaSelecionada)
            self.reporTabuleiro(nivel_carta)

    def realizarCompraPedras(self):
        self.tabuleiro.adicionarPedrasNaMao(self.pedrasSelecionadas)
        self.desenharInfosJogadores()

    def clickFinalizarJogada(self):
        if len(self.pedrasSelecionadas) >= 2:
            self.realizarCompraPedras()

        if self.cartaSelecionada and len(self.pedrasSelecionadas == 0):
            self.realizarCompraCarta()
            ultima_partida = self.tabuleiro.ehUltimaPartida()
            if ultima_partida:
                self.avaliarVencedor()

        self.atualizarTabuleiro()
        self.tabuleiro.desabilitarJogador()
        self.finalizar_jogada_callback(self.tabuleiro)


    def desenharBotoes(self):
        """Desenha os botões na tela"""
        h = 1080
        off = 200
        botoes_pos = {
            "comprar_pedras": (h, 100),
            "comprar_carta": (h, 200),
            "reservar_carta": (h, 300),
            "oferta_de_troca": (h, 400),
            "finalizar_jogada": (100, 50+off)  # Botão para finalizar jogada
        }
        
        for nome, img in self.botoes.items():
            if nome in botoes_pos:
                x, y = botoes_pos[nome]
                self.canvas.create_image(x, y, image=img, anchor=NW, tags=f"botao_{nome}")
                if nome == "comprar_pedras":
                    self.canvas.tag_bind(f"botao_{nome}", "<Button-1>", lambda event: self.clickComprarPedras())
                elif nome == "comprar_carta":
                    self.canvas.tag_bind(f"botao_{nome}", "<Button-1>", lambda event: self.clickComprarCarta())
                elif nome == "reservar_carta":
                    self.canvas.tag_bind(f"botao_{nome}", "<Button-1>", lambda event: self.clickReservarCarta())
                elif nome == "oferta_de_troca":
                    self.canvas.tag_bind(f"botao_{nome}", "<Button-1>", lambda event: self.clickOfertaDeTroca())
                elif nome == "finalizar_jogada":
                    self.canvas.tag_bind(f"botao_{nome}", "<Button-1>", lambda event: self.finalizar_jogada_callback(self.tabuleiro))

    def desenharTabuleiro(self):
        self.canvas.delete("all")
        niveis = [NiveisEnum.NIVEL1, NiveisEnum.NIVEL2, NiveisEnum.NIVEL3]
        for nivel_idx, nivel in enumerate(niveis):
            y_pos = self.START_Y + (nivel_idx * (self.CARD_HEIGHT + self.VERTICAL_GAP))
            deck_x = self.START_X

            # Desenhar capa do baralho alinhada com as cartas
            capa_img = self.capas_baralho.get(nivel.value)
            if capa_img:
                self.canvas.create_image(deck_x-80, y_pos, image=capa_img, anchor=NW, tags=f"capa_nivel{nivel.value}")

            # Desenhar cartas do nível
            cartas_nivel = [carta_img for carta_img, carta_info in self.cartas.items() if carta_info["nivel"] == nivel]
            for i, carta_img in enumerate(cartas_nivel[:4]):
                x = deck_x + self.CARD_WIDTH + self.DECK_TO_CARDS_GAP + i * (self.CARD_WIDTH + self.HORIZONTAL_GAP)
                self.canvas.create_image(x, y_pos, image=carta_img, anchor=NW, tags=f"carta_{nivel.name}_{i}")
                self.canvas.tag_bind(f"carta_{nivel.name}_{i}", "<Button-1>", lambda event, idx=i, nivel=nivel: self.clickCarta(idx, nivel))

    def habilitarBotaoComprarCarta(self):
        """Habilita o botão 'Comprar Carta'"""
        if "comprar_carta" in self.botoes:
            img = self.botoes["comprar_carta"]
            self.canvas.itemconfig("botao_comprar_carta", image=img)
            self.canvas.tag_bind("botao_comprar_carta", "<Button-1>", lambda event: self.clickComprarCarta())

    def desabilitarBotaoComprarCarta(self):
        """Desabilita o botão 'Comprar Carta'"""
        if "comprar_carta" in self.botoes:
            pil_img = Image.open("./resources/botoes/comprar_carta.png").resize((150, 100), Image.Resampling.LANCZOS).convert("RGBA")
            alpha = pil_img.split()[3]
            alpha = alpha.point(lambda p: int(p * 0.5))
            pil_img.putalpha(alpha)
            img = ImageTk.PhotoImage(pil_img)
            self.canvas.itemconfig("botao_comprar_carta", image=img)
            self.canvas.tag_unbind("botao_comprar_carta", "<Button-1>")
            self.botoes["comprar_carta_disabled"] = img

    def habilitarBotaoComprarPedras(self):
        """Habilita o botão 'Comprar Pedras'"""
        if "comprar_pedras" in self.botoes:
            img = self.botoes["comprar_pedras"]
            self.canvas.itemconfig("botao_comprar_pedras", image=img)
            self.canvas.tag_bind("botao_comprar_pedras", "<Button-1>", lambda event: self.clickComprarPedras())

    def desabilitarBotaoComprarPedras(self):
        """Desabilita o botão 'Comprar Pedras'"""
        if "comprar_pedras" in self.botoes:
            
            pil_img = Image.open("./resources/botoes/comprar_pedras.png").resize((150, 100), Image.Resampling.LANCZOS).convert("RGBA")
            alpha = pil_img.split()[3]
            alpha = alpha.point(lambda p: int(p * 0.5))
            pil_img.putalpha(alpha)
            img = ImageTk.PhotoImage(pil_img)
            self.canvas.itemconfig("botao_comprar_pedras", image=img)
            self.canvas.tag_unbind("botao_comprar_pedras", "<Button-1>")
            self.botoes["comprar_pedras_disabled"] = img

    def habilitarBotaoOfertaDeTroca(self):
        """Habilita o botão 'Oferta de Troca'"""
        if "oferta_de_troca" in self.botoes:
            img = self.botoes["oferta_de_troca"]
            self.canvas.itemconfig("botao_oferta_de_troca", image=img)
            self.canvas.tag_bind("botao_oferta_de_troca", "<Button-1>", lambda event: self.clickOfertaDeTroca())

    def desabilitarBotaoOfertaDeTroca(self):
        """Desabilita o botão 'Oferta de Troca'"""
        if "oferta_de_troca" in self.botoes:
            
            pil_img = Image.open("./resources/botoes/oferta_de_troca.png").resize((150, 100), Image.Resampling.LANCZOS).convert("RGBA")
            alpha = pil_img.split()[3]
            alpha = alpha.point(lambda p: int(p * 0.5))
            pil_img.putalpha(alpha)
            img = ImageTk.PhotoImage(pil_img)
            self.canvas.itemconfig("botao_oferta_de_troca", image=img)
            self.canvas.tag_unbind("botao_oferta_de_troca", "<Button-1>")
            self.botoes["oferta_de_troca_disabled"] = img

    def habilitarReservarCarta(self):
        """Habilita o botão 'Reservar Carta'"""
        if "reservar_carta" in self.botoes:
            img = self.botoes["reservar_carta"]
            self.canvas.itemconfig("botao_reservar_carta", image=img)
            self.canvas.tag_bind("botao_reservar_carta", "<Button-1>", lambda event: self.clickComprarCarta())
    
    def desabilitarReservarCarta(self):
        """Desabilita o botão 'Reservar Carta'"""
        if "reservar_carta" in self.botoes:
            
            pil_img = Image.open("./resources/botoes/reservar_carta.png").resize((150, 100), Image.Resampling.LANCZOS).convert("RGBA")
            alpha = pil_img.split()[3]
            alpha = alpha.point(lambda p: int(p * 0.5))
            pil_img.putalpha(alpha)
            img = ImageTk.PhotoImage(pil_img)
            self.canvas.itemconfig("botao_reservar_carta", image=img)
            self.canvas.tag_unbind("botao_reservar_carta", "<Button-1>")
            self.botoes["reservar_carta_disabled"] = img

    def habilitarDesfazerJogada(self):
        """Habilita o botão 'Desfazer Jogada'"""
        if "desfazer_jogada" in self.botoes:
            img = self.botoes["desfazer_jogada"]
            self.canvas.itemconfig("botao_desfazer_jogada", image=img)
            self.canvas.tag_bind("botao_desfazer_jogada", "<Button-1>", lambda event: self.clickDesfazerJogada())
    
    def desabilitarDesfazerJogada(self):
        """Desabilita o botão 'Desfazer Jogada'"""
        if "desfazer_jogada" in self.botoes:
            
            pil_img = Image.open("./resources/botoes/desfazer-jogada.png").resize((150, 100), Image.Resampling.LANCZOS).convert("RGBA")
            alpha = pil_img.split()[3]
            alpha = alpha.point(lambda p: int(p * 0.5))
            pil_img.putalpha(alpha)
            img = ImageTk.PhotoImage(pil_img)
            self.canvas.itemconfig("botao_desfazer_jogada", image=img)
            self.canvas.tag_unbind("botao_desfazer_jogada", "<Button-1>")
            self.botoes["desfazer_jogada_disabled"] = img

    def habilitarBotaoFinalizarJogada(self):
        """Habilita o botão 'Finalizar Jogada'"""
        if "finalizar_jogada" in self.botoes:
            img = self.botoes["finalizar_jogada"]
            self.canvas.itemconfig("botao_finalizar_jogada", image=img)
            self.canvas.tag_bind("botao_finalizar_jogada", "<Button-1>", lambda event: self.finalizar_jogada_callback(self.tabuleiro))

    def desabilitarBotaoFinalizarJogada(self):
        """Desabilita o botão 'Finalizar Jogada'"""
        if "finalizar_jogada" in self.botoes:
            
            pil_img = Image.open("./resources/botoes/finalizar-jogada.png").resize((150, 100), Image.Resampling.LANCZOS).convert("RGBA")
            alpha = pil_img.split()[3]
            alpha = alpha.point(lambda p: int(p * 0.5))
            pil_img.putalpha(alpha)
            img = ImageTk.PhotoImage(pil_img)
            self.canvas.itemconfig("botao_finalizar_jogada", image=img)
            self.canvas.tag_unbind("botao_finalizar_jogada", "<Button-1>")
            self.botoes["finalizar_jogada_disabled"] = img

    # Métodos para habilitar/desabilitar cartas
    def habilitarCartas(self):
        """Habilita todas as cartas no tabuleiro"""
        for i in range(len(self.cartas)):
            self.canvas.tag_bind(f"carta_{i}", "<Button-1>", lambda event, idx=i: self.clickCarta(idx))

    def desabilitarCartas(self):
        """Desabilita todas as cartas no tabuleiro e aplica transparência"""
        for i, (img_tk, carta_info) in enumerate(self.cartas.items()):
            self.canvas.tag_unbind(f"carta_{i}", "<Button-1>")
            # Reabra a imagem original do arquivo
            if "caminho" in carta_info:
                pil_img = Image.open(carta_info["caminho"]).resize((self.CARD_WIDTH * 10, self.CARD_HEIGHT * 10), Image.Resampling.LANCZOS).convert("RGBA")
                alpha = pil_img.split()[3]
                alpha = alpha.point(lambda p: int(p * 0.5))
                pil_img.putalpha(alpha)
                img_transp = ImageTk.PhotoImage(pil_img)
                self.canvas.itemconfig(f"carta_{i}", image=img_transp)
                self.cartas[img_transp] = carta_info


    # Métodos para habilitar/desabilitar pedras
    def habilitarPedras(self):
        """Habilita todas as pedras no tabuleiro"""
        for pedra in self.tabuleiro.pedrasNoTabuleiro.keys():
            self.canvas.tag_bind(f"pedra_{pedra.name}", "<Button-1>", lambda event, pedra=pedra: self.clickPedra(pedra))

    def desabilitarPedras(self):
        """Desabilita todas as pedras no tabuleiro e aplica transparência"""
        for i, pedra in enumerate(self.tabuleiro.pedrasNoTabuleiro.keys()):
            self.canvas.tag_unbind(f"pedra_{pedra.name}", "<Button-1>")
            # Aplica transparência na imagem da pedra
            if i < len(self.pedras):
                pil_img = self.pedras[i]._PhotoImage__photo.zoom(1).copy().convert("RGBA")
                alpha = pil_img.split()[3]
                alpha = alpha.point(lambda p: int(p * 0.5))
                pil_img.putalpha(alpha)
                img_transp = ImageTk.PhotoImage(pil_img)
                self.canvas.itemconfig(f"pedra_{pedra.name}", image=img_transp)
                # Mantém referência para não ser coletado
                self.pedras[i] = img_transp

    def avaliarVencedor(self):
        pontos1 = self.tabuleiro.jogadorLocal.pegarPontuacaoJogador()
        pontos2 = self.tabuleiro.jogadorRemoto.pegarPontuacaoJogador()

        if pontos1 > pontos2:
            vencedor = self.tabuleiro.jogadorLocal.pegarNome()
            self.tabuleiro.jogadorLocal.jogadorVenceu()
            self.notificarVencedor(vencedor)
        elif pontos2 > pontos1:
            vencedor = self.tabuleiro.jogadorRemoto.pegarNome()
            self.tabuleiro.jogadorRemoto.jogadorVenceu()
            self.notificarVencedor(vencedor)
        else:
            self.tabuleiro.jogadorLocal.jogadorEmpatou()
            self.tabuleiro.jogadorRemoto.jogadorEmpatou()
            self.notificarEmpate()
        
        self.restaurarEstadoInicial()
    
    def identificarPossivelComprarCartas(self) -> bool:
        """Identifica se o jogador pode comprar cartas e habilita o botão de compra"""
        for carta in self.tabuleiro.cartasNoTabuleiro:
            if carta and self.tabuleiro.verificarPedrasSuficientes(carta):
                return True
        return False
    
    def habilitarTabuleiro(self):
        pontos = self.tabuleiro.jogadorRemoto.pegarPontuacaoJogador()
        if pontos >= 15:
            self.tabuleiro.habilitarUltimaPartida()
        
        jogada_final = self.tabuleiro.ehUltimaPartida()
        possivel_comprar_cartas = self.identificarPossivelComprarCartas()

        if jogada_final and not possivel_comprar_cartas:
            self.avaliarVencedor()
        
        elif not jogada_final and not possivel_comprar_cartas:
            self.habilitarBotaoComprarPedras()
            self.habilitarBotaoOfertaDeTroca()
            self.habilitarBotaoReservarCarta()
        
        elif possivel_comprar_cartas and not jogada_final:
            tem_carta_roubo = self.tabuleiro.verificaSeTemCartaDeRoubo()
            if tem_carta_roubo:
                cartas_de_roubo = self.tabuleiro.pegarCartasDeRoubo()
                tem_pedras = False
                for carta in cartas_de_roubo:
                    pedras = self.tabuleiro.pegarPedrasCarta(carta)
                    for pedra in pedras:
                        if pedra in self.tabuleiro.pegarPedrasJogador():
                            tem_pedras = True
                            break
                if tem_pedras:
                    carta.habilitar()
            
            self.habilitarBotaoComprarCarta()
            self.habilitarBotaoComprarPedras()
            self.habilitarBotaoOfertaDeTroca()
            self.habilitarBotaoReservarCarta()
    
    def desenharPedras(self):
        GEM_SIZE = 50
        GEM_VERTICAL_GAP = 60
        
        gems_start_y = 100
        
        for i, (pedra, qtd) in enumerate(self.tabuleiro.pedrasNoTabuleiro.items()):
            if qtd > 0 and i < len(self.pedras):
                y_pos = gems_start_y + (i * GEM_VERTICAL_GAP)
                
                # Stack effect
                for j in range(min(3, qtd)):
                    self.canvas.create_image(
                        self.GEMS_X + (j * 3),
                        y_pos + (j * 3),
                        image=self.pedras[i],
                        anchor='nw',
                        tags=f"pedra_{pedra.name}"
                    )
                
                # Quantity text
                self.canvas.create_text(
                    self.GEMS_X + GEM_SIZE + 20,
                    y_pos + GEM_SIZE//2,
                    text=str(qtd),
                    fill='white',
                    font=('Aclonica', 14)
                )
    
    def desenharInfosJogadores(self):
        # Player 1 (local)
        self.canvas.create_rectangle(
            self.PLAYER_INFO_X, 
            self.WINDOW_HEIGHT - 200,
            self.PLAYER_INFO_X + self.PLAYER_INFO_WIDTH,
            self.WINDOW_HEIGHT - 50,
            fill="#352314",
            outline="white"
        )
        jogador_local = self.tabuleiro.jogadorLocal
        self.canvas.create_text(
            self.PLAYER_INFO_X + 10,
            self.WINDOW_HEIGHT - 180,
            text=f"Nome: {jogador_local.pegarNome()}",
            fill="white",
            anchor="nw",
            font=("Arial", 12)
        )
        self.canvas.create_text(
            self.PLAYER_INFO_X + 10,
            self.WINDOW_HEIGHT - 150,
            text=f"Pontos: {jogador_local.pegarPontuacaoJogador()}",
            fill="white",
            anchor="nw",
            font=("Arial", 12)
        )
        self.canvas.create_text(
            self.PLAYER_INFO_X + 10,
            self.WINDOW_HEIGHT - 120,
            text=f"Pedras: {', '.join([f'{pedra.name} ({qtd})' for pedra, qtd in jogador_local.pegarPedras().items()])}",
            fill="white",
            anchor="nw",
            font=("Arial", 12)
        )

        # Player 2 (remoto)
        self.canvas.create_rectangle(
            self.PLAYER_INFO_X,
            50,
            self.PLAYER_INFO_X + self.PLAYER_INFO_WIDTH,
            200,
            fill="#352314",
            outline="white"
        )
        jogador_remoto = self.tabuleiro.jogadorRemoto
        self.canvas.create_text(
            self.PLAYER_INFO_X + 10,
            70,
            text=f"Nome: {jogador_remoto.pegarNome()}",
            fill="white",
            anchor="nw",
            font=("Arial", 12)
        )
        self.canvas.create_text(
            self.PLAYER_INFO_X + 10,
            100,
            text=f"Pontos: {jogador_remoto.pegarPontuacaoJogador()}",
            fill="white",
            anchor="nw",
            font=("Arial", 12)
        )
        self.canvas.create_text(
            self.PLAYER_INFO_X + 10,
            130,
            text=f"Pedras: {', '.join([f'{pedra.name} ({qtd})' for pedra, qtd in jogador_remoto.pegarPedras().items()])}",
            fill="white",
            anchor="nw",
            font=("Arial", 12)
        )
