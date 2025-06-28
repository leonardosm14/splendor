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
        self.PLAYER_INFO_WIDTH = 250
        self.PLAYER_INFO_X = 0

        # Create single canvas
        self.canvas = Canvas(
            root,
            width=self.WINDOW_WIDTH,
            height=self.WINDOW_HEIGHT,
            bg='#352314',
            highlightthickness=0
        )
        self.canvas.pack(expand=True, fill='both')

        self.tabuleiro = Tabuleiro(jogadorLocal=jogador_local, jogadorRemoto=jogador_remoto, seed=12345)  # Inicializa com jogadores
        self.tabuleiro_inicio_partida = self.tabuleiro  # Utilizado para restaurar o estado inicial do tabuleiro naquela partida
        self.finalizar_jogada_callback = finalizar_jogada_callback  # Callback para finalizar jogada
    

        # Estruturas de dados
        self.cartas: Dict[ImageTk.PhotoImage, dict] = dict()
        self.pedras: List[PedrasEnum, ImageTk.PhotoImage] = dict()
        self.botoes: Dict[str, ImageTk.PhotoImage] = dict()
        self.pedrasSelecionadas: List[PedrasEnum] = list()
        self.cartaSelecionada = None
        self.ofertaDePedras = {"local": None, "remoto": None}
        self.modo_reserva = False  # Inicializa o modo de reserva

        # Carrega os recursos
        self.carregarCartas()
        self.carregarPedras()
        self.carregarBotoes()
        
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

        # Verifica se é o turno do jogador local para habilitar jogadas
        if self.tabuleiro.jogadorLocal.jogadorEmTurno:
            self.habilitarJogadas()
        else:
            self.desabilitarJogadas()
    
    def habilitarJogadas(self):
        self.habilitarBotaoComprarPedras()
        self.habilitarBotaoComprarCarta()
        self.habilitarReservarCarta()
        self.habilitarBotaoOfertaDeTroca()
        self.habilitarPedras()
        self.desabilitarCartas()
    
    def desabilitarJogadas(self):
        self.desabilitarBotaoComprarCarta()
        self.desabilitarBotaoComprarPedras()
        self.desabilitarReservarCarta()
        self.desabilitarBotaoOfertaDeTroca()
        self.desabilitarCartas()
        self.desabilitarPedras()
            

    def pegarTabuleiro(self) -> Tabuleiro:
        return self.tabuleiro

    def atualizarTabuleiro(self, tabuleiro: Tabuleiro):
        # Salva o estado recebido como o estado inicial para desfazer jogada
        self.tabuleiro_inicio_partida = tabuleiro
        
        # Atualiza o tabuleiro atual
        self.tabuleiro = tabuleiro
        
        # Recarrega as imagens das cartas para garantir que todas as cartas no tabuleiro
        # tenham suas imagens carregadas corretamente
        self.recarregarImagensCartas()
        
        self.desenharTabuleiro()
        
        # Verifica se é o turno do jogador local
        if self.tabuleiro.jogadorLocal.jogadorEmTurno:
            self.tabuleiro.jogadorLocal.habilitarJogador()
            self.habilitarJogadas()
        else:
            self.tabuleiro.jogadorLocal.desabilitarJogador()
            self.desabilitarJogadas()

    def recarregarImagensCartas(self):
        """Recarrega as imagens das cartas para todas as cartas no tabuleiro"""
        # Limpa o cache de imagens das cartas
        self.carta_imgs = {}
        
        # Recarrega todas as cartas do tabuleiro
        for carta in self.tabuleiro.cartasNoTabuleiro:
            if carta is not None:
                self.get_carta_img(carta)
        
        # Recarrega cartas dos jogadores também
        for carta in self.tabuleiro.jogadorLocal.pegarCartas():
            self.get_carta_img(carta)
        
        for carta in self.tabuleiro.jogadorRemoto.pegarCartas():
            self.get_carta_img(carta)
        
        # Recarrega cartas de roubo dos jogadores
        for carta in self.tabuleiro.pegarCartasRoubo():
            self.get_carta_img(carta)

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
    
    def extrair_dados_carta(self, carta_img_path: Path, nivel: NiveisEnum, roubo=False):
        nome = carta_img_path.stem
        pontos = 0
        bonus = None
        pedras = {}
        cartaDeRoubo = roubo
        habilitada = True

        partes = nome.split('-')
        for parte in partes:
            if parte.startswith("pontos:"):
                pontos = int(parte.split(":")[1])
            elif parte.startswith("bonus:"):
                bonus_nome = parte.split(":")[1]
                bonus = PedrasEnum[bonus_nome.upper()]
            elif parte.startswith("roubo"):
                pedras_roubo = parte.split('-')[1:]
                for pedra_nome in pedras_roubo:
                    pedra_enum = PedrasEnum[pedra_nome.upper()]
                    pedras[pedra_enum] = 1
            elif ':' in parte:
                pedra_nome, qtd = parte.split(':')
                # Só adiciona se não for bonus
                if pedra_nome.lower() not in [p.name.lower() for p in PedrasEnum]:
                    continue
                pedra_enum = PedrasEnum[pedra_nome.upper()]
                pedras[pedra_enum] = int(qtd)
        
        # Usa o nome do arquivo como ID para garantir consistência
        id_carta = hash(nome)
        return id_carta, pontos, pedras, cartaDeRoubo, bonus, habilitada

    def get_carta_img(self, carta):
        """Retorna a imagem ImageTk.PhotoImage para uma carta específica"""
        if carta is None:
            return None
        
        # Verifica se a imagem já está em cache
        if carta.id in self.carta_imgs:
            return self.carta_imgs[carta.id]
        
        # Se não está em cache, tenta carregar do arquivo baseado nas características da carta
        try:
            # Procura o arquivo da carta baseado nas características
            diretorios_cartas = [
                (Path("./resources/cartas/cartas-tabuleiro/cartas-nivel-1"), False),
                (Path("./resources/cartas/cartas-tabuleiro/cartas-nivel-2"), False),
                (Path("./resources/cartas/cartas-tabuleiro/cartas-nivel-3"), False),
                (Path("./resources/cartas/cartas-tabuleiro/cartas-de-roubo"), True),
            ]
            
            for diretorio, is_roubo in diretorios_cartas:
                for carta_img in diretorio.glob("*.png"):
                    nome = carta_img.stem
                    id_carta, pontos, pedras, cartaDeRoubo, bonus, habilitada = self.extrair_dados_carta(carta_img, None, is_roubo)
                    
                    # Compara as características da carta com o arquivo
                    if (carta.pontos == pontos and 
                        carta.pedras == pedras and 
                        carta.cartaDeRoubo == cartaDeRoubo and 
                        carta.bonus == bonus):
                        
                        img = Image.open(carta_img)
                        img = img.resize((self.CARD_WIDTH * 10, self.CARD_HEIGHT * 10), Image.Resampling.LANCZOS)
                        img_tk = ImageTk.PhotoImage(img)
                        self.carta_imgs[carta.id] = img_tk
                        return img_tk
            
            # Se não encontrou, retorna None
            print(f"Imagem não encontrada para carta - Pontos: {carta.pontos}, Pedras: {carta.pedras}, Bonus: {carta.bonus}, Roubo: {carta.cartaDeRoubo}")
            return None
            
        except Exception as e:
            print(f"Erro ao carregar imagem da carta {carta.id}: {e}")
            return None

    def carregarCartas(self):
        self.carta_imgs = {}
        seed = 12345  # Use um valor compartilhado entre os jogadores

        def carregarCartasDeDiretorio(diretorio: Path, nivel: NiveisEnum = None, roubo=False):
            for carta_img in diretorio.glob("*.png"):
                try:
                    img = Image.open(carta_img)
                    img = img.resize((self.CARD_WIDTH * 10, self.CARD_HEIGHT * 10), Image.Resampling.LANCZOS)
                    img_tk = ImageTk.PhotoImage(img)
                    id_base, pontos, pedras, cartaDeRoubo, bonus, habilitada = self.extrair_dados_carta(carta_img, nivel, roubo)
                    nivel_destino = NiveisEnum.NIVEL3 if roubo else nivel

                    if not roubo:
                        # Para cartas normais, cria 3 cópias com IDs únicos
                        for i in range(3):
                            id_carta = hash(f"{id_base}_{i}")
                            self.tabuleiro.instanciarCartas(
                                id=id_carta,
                                pontos=pontos,
                                nivel=nivel_destino,
                                pedras=pedras.copy(),
                                cartaDeRoubo=False,
                                bonus=bonus,
                                habilitada=habilitada
                            )
                            self.carta_imgs[id_carta] = img_tk
                    else:
                        # Para cartas de roubo, cria apenas uma cópia e adiciona ao baralho
                        # mas não ao tabuleiro inicial
                        if len([c for c in self.tabuleiro.todasCartas if c.cartaDeRoubo]) < 3:
                            id_carta = hash(f"{id_base}_roubo")
                            self.tabuleiro.instanciarCartas(
                                id=id_carta,
                                pontos=pontos,
                                nivel=nivel_destino,
                                pedras=pedras.copy(),
                                cartaDeRoubo=True,
                                bonus=bonus,
                                habilitada=habilitada
                            )
                            self.carta_imgs[id_carta] = img_tk
                except Exception as e:
                    print(f"Erro ao carregar carta {carta_img}: {e}")

        diretorios_cartas = {
            NiveisEnum.NIVEL1: Path("./resources/cartas/cartas-tabuleiro/cartas-nivel-1"),
            NiveisEnum.NIVEL2: Path("./resources/cartas/cartas-tabuleiro/cartas-nivel-2"),
            NiveisEnum.NIVEL3: Path("./resources/cartas/cartas-tabuleiro/cartas-nivel-3"),
        }
        cartas_roubo_dir = Path("./resources/cartas/cartas-tabuleiro/cartas-de-roubo")

        for nivel, diretorio in diretorios_cartas.items():
            carregarCartasDeDiretorio(diretorio, nivel)
        carregarCartasDeDiretorio(cartas_roubo_dir, NiveisEnum.NIVEL3, roubo=True)

        # Embaralhe cada baralho com a mesma seed
        for baralho in self.tabuleiro.baralhos:
            random.Random(seed + baralho.nivel.value).shuffle(baralho.cartas)

        self.tabuleiro.inicializar_cartas_tabuleiro()
        

    def carregarBotoes(self):
        """Carrega e redimensiona as imagens dos botões"""
        botoes_dir = Path("./resources/botoes")

        for botao_img in botoes_dir.glob("*.png"):
            try:
                img = Image.open(botao_img)
                if botao_img.stem in ["desfazer_jogada", "finalizar_jogada"]:
                    tamanho_botoes = (150, 80)
                else:
                    tamanho_botoes = (150, 100)
                img = img.resize(tamanho_botoes, Image.Resampling.LANCZOS)
                img_tk = ImageTk.PhotoImage(img)
                self.botoes[botao_img.stem] = img_tk
            except Exception as e:
                print(f"Erro ao carregar botão {botao_img}: {e}")

    def carregarPedras(self):
        """Carrega as imagens das pedras e cria um dict {PedrasEnum: ImageTk.PhotoImage}"""
        from model.enums.pedrasEnum import PedrasEnum
        pedras_dir = Path("./resources/pedras")
        self.pedras = {}  # Agora é um dict: {PedrasEnum: ImageTk.PhotoImage}
        for pedra_img in pedras_dir.glob("*.png"):
            try:
                nome_pedra = pedra_img.stem.lower()  # ex: 'diamante'
                # Procura o enum correspondente pelo nome em lower
                enum_pedra = next((p for p in PedrasEnum if p.name.lower() == nome_pedra), None)
                if enum_pedra:
                    img = Image.open(pedra_img)
                    img = img.resize((self.GEM_SIZE, self.GEM_SIZE), Image.Resampling.LANCZOS)
                    img_tk = ImageTk.PhotoImage(img)
                    self.pedras[enum_pedra] = img_tk
                else:
                    print(f"Arquivo de pedra '{pedra_img}' não corresponde a nenhum PedrasEnum.")
            except Exception as e:
                print(f"Erro ao carregar pedra {pedra_img}: {e}")

    def configurarTela(self):
        self.canvas.delete("all")
        self.desenharTabuleiro()

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
        # Restaura o tabuleiro ao estado que foi recebido pelo DOG
        self.tabuleiro = self.tabuleiro_inicio_partida
        self.pedrasSelecionadas = list()
        self.cartaSelecionada = None
        self.modo_reserva = False
        
        # Redesenha o tabuleiro com o estado inicial
        self.desenharTabuleiro()
        
        # Habilita/desabilita jogadas baseado no turno atual
        if self.tabuleiro.jogadorLocal.jogadorEmTurno:
            self.habilitarJogadas()
        else:
            self.desabilitarJogadas()
            
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
        self.modo_reserva = False  # Define o modo de compra

    def clickReservarCarta(self):
        """Ação ao clicar no botão 'Reservar Carta'"""
        messagebox.showinfo("Reservar Carta", "Selecione a carta que deseja reservar clicando no tabuleiro.")

        self.desabilitarBotaoComprarPedras()
        self.desabilitarBotaoComprarCarta()
        self.desabilitarBotaoOfertaDeTroca()
        self.desabilitarPedras()

        self.habilitarCartas()
        self.habilitarDesfazerJogada()
        self.modo_reserva = True  # Define o modo de reserva

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
        self.pedrasSelecionadas.append(pedra)

        if len(self.pedrasSelecionadas) == 2:
            if self.pedrasSelecionadas[0] == self.pedrasSelecionadas[1]:
                messagebox.showinfo(
                    "Pedras Selecionadas",
                    f"Você selecionou 2 pedras do tipo {pedra.name}."
                )
                self.habilitarBotaoFinalizarJogada()
                self.desabilitarPedras()
            else:
                messagebox.showinfo(
                    "Pedras Selecionadas",
                    f"Você selecionou 2 pedras diferentes: {self.pedrasSelecionadas[0].name} e {self.pedrasSelecionadas[1].name}. Agora selecione uma terceira pedra diferente."
                )
        elif len(self.pedrasSelecionadas) == 3:
            p1, p2, p3 = self.pedrasSelecionadas
            if p1 == p2 or p1 == p3 or p2 == p3:
                messagebox.showerror(
                    "Erro",
                    "A terceira pedra selecionada não pode ser igual às anteriores. Tente novamente."
                )
                self.pedrasSelecionadas.pop()
            else:
                messagebox.showinfo(
                    "Pedras Selecionadas",
                    f"Você selecionou 3 pedras diferentes: {p1.name}, {p2.name}, e {p3.name}."
                )
                self.habilitarBotaoFinalizarJogada()
                self.desabilitarPedras()
        
    def notificarJogadaInvalida(self, mensagem: str):
        """Exibe uma mensagem de erro quando uma jogada inválida é realizada"""
        messagebox.showerror(
            title="Jogada inválida",
            message=mensagem,
            parent=self.root
        )

    def clickCarta(self, indiceCarta: int):
        """Método chamado quando uma carta é clicada no tabuleiro"""
        # Verifica se há uma carta no índice selecionado
        if indiceCarta >= len(self.tabuleiro.cartasNoTabuleiro) or self.tabuleiro.cartasNoTabuleiro[indiceCarta] is None:
            self.notificarJogadaInvalida("Não há carta nesta posição!")
            return

        carta = self.tabuleiro.cartasNoTabuleiro[indiceCarta]
        self.cartaSelecionada = carta

        # Verifica se o jogador tem pedras suficientes
        if not self.tabuleiro.verificarPedrasSuficientes(carta):
            self.notificarJogadaInvalida("Você não tem pedras suficientes para comprar esta carta!")
            self.cartaSelecionada = None
            return

        self.habilitarBotaoFinalizarJogada()
        
    def reporTabuleiro(self, nivel: NiveisEnum):
        try:
            if not self.tabuleiro.baralhos[nivel.value - 1].temCartas():
                return
            inicio_nivel = (nivel.value - 1) * 4
            for i in range(inicio_nivel, inicio_nivel + 4):
                if self.tabuleiro.cartasNoTabuleiro[i] is None:
                    nova_carta = self.tabuleiro.baralhos[nivel.value - 1].pegarCartaDoBaralho()
                    if nova_carta is None:
                        break
                    # Se for carta de roubo, vai para a área do jogador
                    if nova_carta.cartaDeRoubo:
                        self.tabuleiro.jogadorLocal.adicionarCartaDeRoubo(nova_carta)
                        # Não coloca no tabuleiro, tenta repor outra carta
                        continue
                    self.tabuleiro.cartasNoTabuleiro[i] = nova_carta
                    break
        except Exception as e:
            print(f"Erro ao repor tabuleiro: {e}")
        
    def desenharCartasJogadores(self):
        """Desenha as cartas dos jogadores nas áreas específicas"""
        # Jogador local (embaixo, centralizado) - mostra apenas pontos
        cartas_local = self.tabuleiro.jogadorLocal.pegarCartas()
        if cartas_local:
            # Remove cartas de roubo da lista (elas são tratadas separadamente)
            cartas_normais = [c for c in cartas_local if not c.cartaDeRoubo]
            if cartas_normais:
                # Organiza em 3 colunas
                colunas = 3
                
                for i, carta in enumerate(cartas_normais):
                    coluna = i % colunas
                    linha = i // colunas
                    
                    # Posição centralizada na parte inferior
                    x_base = self.WINDOW_WIDTH // 2
                    y_base = self.WINDOW_HEIGHT - 20
                    
                    # Espaçamento entre colunas
                    x = x_base + (coluna - 1) * 80
                    y = y_base - linha * 30
                    
                    # Desenha apenas o texto dos pontos
                    self.canvas.create_text(
                        x, y, 
                        text=str(carta.pontos), 
                        fill="white", 
                        font=("Arial", 16, "bold"),
                        tags=f"carta_jogador_local_{i}"
                    )

        # Jogador remoto (em cima, centralizado, invertido) - mostra apenas pontos
        cartas_remoto = self.tabuleiro.jogadorRemoto.pegarCartas()
        if cartas_remoto:
            # Remove cartas de roubo da lista
            cartas_normais = [c for c in cartas_remoto if not c.cartaDeRoubo]
            if cartas_normais:
                # Organiza em 3 colunas
                colunas = 3
                
                for i, carta in enumerate(cartas_normais):
                    coluna = i % colunas
                    linha = i // colunas
                    
                    # Posição centralizada na parte superior
                    x_base = self.WINDOW_WIDTH // 2
                    y_base = 20
                    
                    # Espaçamento entre colunas
                    x = x_base + (coluna - 1) * 80
                    y = y_base + linha * 30
                    
                    # Desenha apenas o texto dos pontos
                    self.canvas.create_text(
                        x, y, 
                        text=str(carta.pontos), 
                        fill="white", 
                        font=("Arial", 16, "bold"),
                        tags=f"carta_jogador_remoto_{i}"
                    )

    def desenharCartasRouboJogador(self):
        """Desenha as cartas de roubo dos jogadores"""
        # Jogador local (embaixo)
        cartas_roubo_local = self.tabuleiro.jogadorLocal.pegarCartas()
        cartas_roubo_local = [c for c in cartas_roubo_local if c.cartaDeRoubo]
        if cartas_roubo_local:
            for i, carta in enumerate(cartas_roubo_local):
                img_tk = self.get_carta_img(carta)
                if img_tk:
                    # Centralizado e cortado (exemplo: só metade da carta)
                    x = self.WINDOW_WIDTH // 2 + (i - len(cartas_roubo_local)//2) * (self.CARD_WIDTH*5)
                    y = self.WINDOW_HEIGHT - self.CARD_HEIGHT*5
                    self.canvas.create_image(x, y, image=img_tk, anchor='s', tags=f"roubo_local_{i}")

        # Jogador remoto (em cima, invertido)
        cartas_roubo_remoto = self.tabuleiro.jogadorRemoto.pegarCartas()
        cartas_roubo_remoto = [c for c in cartas_roubo_remoto if c.cartaDeRoubo]
        if cartas_roubo_remoto:
            for i, carta in enumerate(cartas_roubo_remoto):
                img_tk = self.get_carta_img(carta)
                if img_tk:
                    # Inverter imagem 180 graus
                    try:
                        from PIL import Image
                        # Encontra o arquivo da carta
                        diretorios_cartas = [
                            Path("./resources/cartas/cartas-tabuleiro/cartas-de-roubo"),
                        ]
                        
                        for diretorio in diretorios_cartas:
                            for carta_img in diretorio.glob("*.png"):
                                nome = carta_img.stem
                                id_carta = hash(nome)
                                if carta.id == id_carta or str(carta.id).startswith(str(id_carta)):
                                    pil_img = Image.open(carta_img).resize((self.CARD_WIDTH * 10, self.CARD_HEIGHT * 10), Image.Resampling.LANCZOS)
                                    pil_img = pil_img.transpose(Image.ROTATE_180)
                                    img_tk_invertida = ImageTk.PhotoImage(pil_img)
                                    x = self.WINDOW_WIDTH // 2 + (i - len(cartas_roubo_remoto)//2) * (self.CARD_WIDTH*5)
                                    y = self.CARD_HEIGHT*2
                                    self.canvas.create_image(x, y, image=img_tk_invertida, anchor='n', tags=f"roubo_remoto_{i}")
                                    break
                            else:
                                continue
                            break
                        else:
                            # Se não encontrou a imagem, usa a original
                            x = self.WINDOW_WIDTH // 2 + (i - len(cartas_roubo_remoto)//2) * (self.CARD_WIDTH*5)
                            y = self.CARD_HEIGHT*2
                            self.canvas.create_image(x, y, image=img_tk, anchor='n', tags=f"roubo_remoto_{i}")
                    except Exception as e:
                        # Se houver erro, usa a imagem original
                        x = self.WINDOW_WIDTH // 2 + (i - len(cartas_roubo_remoto)//2) * (self.CARD_WIDTH*5)
                        y = self.CARD_HEIGHT*2
                        self.canvas.create_image(x, y, image=img_tk, anchor='n', tags=f"roubo_remoto_{i}")

    def desenharTabuleiro(self):
        self.canvas.delete("all")
        niveis = [NiveisEnum.NIVEL1, NiveisEnum.NIVEL2, NiveisEnum.NIVEL3]
        for nivel_idx, nivel in enumerate(niveis):
            y_pos = self.START_Y + (nivel_idx * (self.CARD_HEIGHT + self.VERTICAL_GAP))
            deck_x = self.START_X

            capa_img = self.capas_baralho.get(nivel.value)
            if capa_img:
                self.canvas.create_image(deck_x-80, y_pos, image=capa_img, anchor=NW, tags=f"capa_nivel{nivel.value}")

            for i in range(4):
                idx = nivel_idx * 4 + i
                carta = self.tabuleiro.cartasNoTabuleiro[idx]
                if carta is not None:
                    img_tk = self.get_carta_img(carta)
                    if img_tk:
                        x = deck_x + self.CARD_WIDTH + self.DECK_TO_CARDS_GAP + i * (self.CARD_WIDTH + self.HORIZONTAL_GAP)
                        self.canvas.create_image(x, y_pos, image=img_tk, anchor=NW, tags=f"carta_{nivel.name}_{idx}")
                        # Só habilita clique se for o turno do jogador
                        if self.tabuleiro.jogadorLocal.jogadorEmTurno:
                            self.canvas.tag_bind(f"carta_{nivel.name}_{idx}", "<Button-1>", lambda event, idx=idx: self.clickCarta(idx))

        self.tabuleiro.atualizarPedrasNoTabuleiro()
        self.desenharBotoes()
        self.desenharPedras()
        self.desenharInfosJogadores()
        self.desenharCartasJogadores()  # Adiciona o desenho das cartas dos jogadores
        self.desenharCartasRouboJogador()  # Adiciona o desenho das cartas de roubo dos jogadores
        self.desabilitarBotaoFinalizarJogada()
        self.desabilitarDesfazerJogada()

    def desenharBotoes(self):
        """Desenha os botões na tela"""
        h = 1080
        off = 200
        botoes_pos = {
            "comprar_pedras": (h, 100),
            "comprar_carta": (h, 200),
            "reservar_carta": (h, 300),
            "oferta_de_troca": (h, 400),
            "desfazer_jogada": (h, 500),  # Botão para desfazer jogada - abaixo dos outros
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
                elif nome == "desfazer_jogada":
                    self.canvas.tag_bind(f"botao_{nome}", "<Button-1>", lambda event: self.clickDesfazerJogada())
                elif nome == "finalizar_jogada":
                    self.canvas.tag_bind(f"botao_{nome}", "<Button-1>", lambda event: self.clickFinalizarJogada())

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
            self.canvas.tag_bind("botao_reservar_carta", "<Button-1>", lambda event: self.clickReservarCarta())
    
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
            
            pil_img = Image.open("./resources/botoes/desfazer_jogada.png").resize((150, 80), Image.Resampling.LANCZOS).convert("RGBA")
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
            self.canvas.tag_bind("botao_finalizar_jogada", "<Button-1>", lambda event: self.clickFinalizarJogada())

    def desabilitarBotaoFinalizarJogada(self):
        """Desabilita o botão 'Finalizar Jogada'"""
        if "finalizar_jogada" in self.botoes:
            
            pil_img = Image.open("./resources/botoes/finalizar_jogada.png").resize((150, 80), Image.Resampling.LANCZOS).convert("RGBA")
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
        niveis = [NiveisEnum.NIVEL1, NiveisEnum.NIVEL2, NiveisEnum.NIVEL3]
        for nivel_idx, nivel in enumerate(niveis):
            for i in range(4):
                idx = nivel_idx * 4 + i
                carta = self.tabuleiro.cartasNoTabuleiro[idx]
                if carta is not None:
                    self.canvas.tag_bind(f"carta_{nivel.name}_{idx}", "<Button-1>", lambda event, idx=idx: self.clickCarta(idx))
                    # Restaura a imagem normal da carta
                    img_tk = self.get_carta_img(carta)
                    if img_tk:
                        self.canvas.itemconfig(f"carta_{nivel.name}_{idx}", image=img_tk)

    def desabilitarCartas(self):
        """Desabilita todas as cartas no tabuleiro e aplica transparência apenas quando necessário, sem nunca removê-las do canvas"""
        if not hasattr(self, 'carta_imgs_transparentes'):
            self.carta_imgs_transparentes = {}
        niveis = [NiveisEnum.NIVEL1, NiveisEnum.NIVEL2, NiveisEnum.NIVEL3]
        for nivel_idx, nivel in enumerate(niveis):
            for i in range(4):
                idx = nivel_idx * 4 + i
                carta = self.tabuleiro.cartasNoTabuleiro[idx]
                if carta is not None:
                    self.canvas.tag_unbind(f"carta_{nivel.name}_{idx}", "<Button-1>")
                    # Aplica transparência apenas se não for o turno do jogador
                    if not self.tabuleiro.jogadorLocal.jogadorEmTurno:
                        # Aplica transparência à carta
                        try:
                            # Recarrega a imagem e aplica transparência
                            diretorios_cartas = [
                                (Path("./resources/cartas/cartas-tabuleiro/cartas-nivel-1"), False),
                                (Path("./resources/cartas/cartas-tabuleiro/cartas-nivel-2"), False),
                                (Path("./resources/cartas/cartas-tabuleiro/cartas-nivel-3"), False),
                                (Path("./resources/cartas/cartas-tabuleiro/cartas-de-roubo"), True),
                            ]
                            for diretorio, is_roubo in diretorios_cartas:
                                for carta_img in diretorio.glob("*.png"):
                                    nome = carta_img.stem
                                    id_carta, pontos, pedras, cartaDeRoubo, bonus, habilitada = self.extrair_dados_carta(carta_img, None, is_roubo)
                                    if (carta.pontos == pontos and 
                                        carta.pedras == pedras and 
                                        carta.cartaDeRoubo == cartaDeRoubo and 
                                        carta.bonus == bonus):
                                        pil_img = Image.open(carta_img).resize((self.CARD_WIDTH * 10, self.CARD_HEIGHT * 10), Image.Resampling.LANCZOS).convert("RGBA")
                                        alpha = pil_img.split()[3]
                                        alpha = alpha.point(lambda p: int(p * 0.5))
                                        pil_img.putalpha(alpha)
                                        img_transp = ImageTk.PhotoImage(pil_img)
                                        # GUARDA REFERÊNCIA
                                        self.carta_imgs_transparentes[carta.id] = img_transp
                                        self.canvas.itemconfig(f"carta_{nivel.name}_{idx}", image=img_transp)
                                        break
                                else:
                                    continue
                                break
                        except Exception as e:
                            print(f"Erro ao aplicar transparência na carta: {e}")
                    else:
                        # Se for o turno do jogador, garante que a imagem normal está sendo usada
                        img_tk = self.get_carta_img(carta)
                        if img_tk:
                            self.canvas.itemconfig(f"carta_{nivel.name}_{idx}", image=img_tk)

    # Métodos para habilitar/desabilitar pedras
    def habilitarPedras(self):
        """Habilita todas as pedras no tabuleiro"""
        for pedra in self.tabuleiro.pedrasNoTabuleiro.keys():
            self.canvas.tag_bind(f"pedra_{pedra.name}", "<Button-1>", lambda event, pedra=pedra: self.clickPedra(pedra))
            # Restaura a imagem normal da pedra
            if pedra in self.pedras:
                self.canvas.itemconfig(f"pedra_{pedra.name}", image=self.pedras[pedra])

    def desabilitarPedras(self):
        """Desabilita todas as pedras no tabuleiro e aplica transparência"""
        from model.enums.pedrasEnum import PedrasEnum
        for pedra in self.tabuleiro.pedrasNoTabuleiro.keys():
            self.canvas.tag_unbind(f"pedra_{pedra.name}", "<Button-1>")
            # Aplica transparência apenas se não for o turno do jogador
            if not self.tabuleiro.jogadorLocal.jogadorEmTurno:
                caminho = f"./resources/pedras/{pedra.name.lower()}.png"
                try:
                    pil_img = Image.open(caminho).resize((self.GEM_SIZE, self.GEM_SIZE), Image.Resampling.LANCZOS).convert("RGBA")
                    alpha = pil_img.split()[3]
                    alpha = alpha.point(lambda p: int(p * 0.5))
                    pil_img.putalpha(alpha)
                    img_transp = ImageTk.PhotoImage(pil_img)
                    self.canvas.itemconfig(f"pedra_{pedra.name}", image=img_transp)
                    # Mantém referência para não ser coletado
                    self.pedras[pedra] = img_transp
                except Exception as e:
                    print(f"Erro ao aplicar transparência na pedra {pedra.name}: {e}")

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
    
    def notificarVencedor(self, vencedor: str):
        """Exibe uma mensagem de vitória"""
        messagebox.showinfo("Fim de Jogo", f"Parabéns! {vencedor} venceu a partida!")
    
    def notificarEmpate(self):
        """Exibe uma mensagem de empate"""
        messagebox.showinfo("Fim de Jogo", "A partida terminou em empate!")
    
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
                
                # Desenha apenas uma pedra (sem efeito de pilha)
                self.canvas.create_image(
                    self.GEMS_X,
                    y_pos,
                    image=self.pedras[pedra],  # Access the ImageTk.PhotoImage using PedraEnum as key
                    anchor='nw',
                    tags=f"pedra_{pedra.name}"  # Use PedraEnum name for the tag
                )
                
                # Só habilita clique se for o turno do jogador
                if self.tabuleiro.jogadorLocal.jogadorEmTurno:
                    self.canvas.tag_bind(f"pedra_{pedra.name}", "<Button-1>", lambda event, pedra=pedra: self.clickPedra(pedra))
                
                # Quantity text
                self.canvas.create_text(
                    self.GEMS_X + GEM_SIZE + 20,
                    y_pos + GEM_SIZE//2,
                    text=str(qtd),
                    fill='white',
                    font=('Aclonica', 14)
                )
    
    def desenharInfosJogadores(self):
        # Carregue as imagens de fundo (só uma vez)
        if not hasattr(self, "bg_jogador_local"):
            img_local = Image.open("./resources/extra/sombra_inferior_esquerda.png").resize((self.PLAYER_INFO_WIDTH, 120), Image.Resampling.LANCZOS)
            self.bg_jogador_local = ImageTk.PhotoImage(img_local)
            img_remoto = Image.open("./resources/extra/sombra_superior_esquerda.png").resize((self.PLAYER_INFO_WIDTH, 120), Image.Resampling.LANCZOS)
            self.bg_jogador_remoto = ImageTk.PhotoImage(img_remoto)

        # Cache para mini pedras
        if not hasattr(self, "mini_pedras"):
            self.mini_pedras = {}

        pedra_size = 32
        gap = 2

        # --- Jogador Local (embaixo SEMPRE) ---
        y_base_local = self.WINDOW_HEIGHT
        self.canvas.create_image(
            self.PLAYER_INFO_X,
            y_base_local,
            image=self.bg_jogador_local,
            anchor="sw"
        )
        sombra_altura = 120
        y_nome = y_base_local - sombra_altura + 15
        y_pontos = y_nome + 25
        y_pedra = y_pontos + 30

        jogador_local = self.tabuleiro.jogadorLocal
        self.canvas.create_text(
            self.PLAYER_INFO_X + 15,
            y_nome,
            text=f"{jogador_local.pegarNome()} {'(Sua vez!)' if jogador_local.jogadorEmTurno else ''}",
            fill="white",
            anchor="nw",
            font=("Arial", 14, "bold" if jogador_local.jogadorEmTurno else "normal")
        )
        self.canvas.create_text(
            self.PLAYER_INFO_X + 15,
            y_pontos,
            text=f"Pontos: {jogador_local.pegarPontuacaoJogador()}",
            fill="white",
            anchor="nw",
            font=("Arial", 12)
        )
        pedras = jogador_local.pegarPedras()
        x_pedra = self.PLAYER_INFO_X + 15
        for pedra_enum, qtd in pedras.items():
            if qtd > 0:
                if pedra_enum not in self.mini_pedras:
                    img = Image.open(f"./resources/pedras/{pedra_enum.name.lower()}.png").resize((pedra_size, pedra_size), Image.Resampling.LANCZOS)
                    self.mini_pedras[pedra_enum] = ImageTk.PhotoImage(img)
                self.canvas.create_image(x_pedra, y_pedra, image=self.mini_pedras[pedra_enum], anchor="nw")
                self.canvas.create_text(x_pedra + pedra_size // 2, y_pedra + pedra_size + 4, text=str(qtd), fill="white", font=("Arial", 10), anchor="n")
                x_pedra += pedra_size + gap

        # --- Jogador Remoto (em cima SEMPRE) ---
        y_base_remoto = 0
        self.canvas.create_image(
            self.PLAYER_INFO_X,
            y_base_remoto,
            image=self.bg_jogador_remoto,
            anchor="nw"
        )
        y_nome_r = y_base_remoto + 15
        y_pontos_r = y_nome_r + 25
        y_pedra_r = y_pontos_r + 30

        jogador_remoto = self.tabuleiro.jogadorRemoto
        self.canvas.create_text(
            self.PLAYER_INFO_X + 15,
            y_nome_r,
            text=f"{jogador_remoto.pegarNome()} {'(Sua vez!)' if jogador_remoto.jogadorEmTurno else ''}",
            fill="white",
            anchor="nw",
            font=("Arial", 14, "bold" if jogador_remoto.jogadorEmTurno else "normal")
        )
        self.canvas.create_text(
            self.PLAYER_INFO_X + 15,
            y_pontos_r,
            text=f"Pontos: {jogador_remoto.pegarPontuacaoJogador()}",
            fill="white",
            anchor="nw",
            font=("Arial", 12)
        )
        pedras = jogador_remoto.pegarPedras()
        x_pedra = self.PLAYER_INFO_X + 15
        for pedra_enum, qtd in pedras.items():
            if qtd > 0:
                if pedra_enum not in self.mini_pedras:
                    img = Image.open(f"./resources/pedras/{pedra_enum.name.lower()}.png").resize((pedra_size, pedra_size), Image.Resampling.LANCZOS)
                    self.mini_pedras[pedra_enum] = ImageTk.PhotoImage(img)
                self.canvas.create_image(x_pedra, y_pedra_r, image=self.mini_pedras[pedra_enum], anchor="nw")
                self.canvas.create_text(x_pedra + pedra_size // 2, y_pedra_r + pedra_size + 4, text=str(qtd), fill="white", font=("Arial", 10), anchor="n")
                x_pedra += pedra_size + gap

    def habilitarBotaoReservarCarta(self):
        """Habilita o botão 'Reservar Carta'"""
        if "reservar_carta" in self.botoes:
            img = self.botoes["reservar_carta"]
            self.canvas.itemconfig("botao_reservar_carta", image=img)
            self.canvas.tag_bind("botao_reservar_carta", "<Button-1>", lambda event: self.clickReservarCarta())

    def comprarCartaReservada(self, indice_carta_reservada: int):
        """Compra uma carta da reserva do jogador"""
        cartas_reservadas = self.tabuleiro.jogadorLocal.cartasReservadas()
        if 0 <= indice_carta_reservada < len(cartas_reservadas):
            carta = cartas_reservadas[indice_carta_reservada]
            
            # Verifica se tem pedras suficientes
            if self.tabuleiro.verificarPedrasSuficientes(carta):
                # Remove pedras do jogador
                pedras_carta = carta.pegarPedrasDaCarta()
                self.tabuleiro.jogadorLocal.removerPedras(pedras_carta)
                
                # Remove da reserva e adiciona à mão
                self.tabuleiro.jogadorLocal.cartasReservadas.pop(indice_carta_reservada)
                self.tabuleiro.jogadorLocal.adicionarCarta(carta)
                
                # Adiciona pontos e bônus
                pontos = carta.pegarPontos()
                if pontos > 0:
                    self.tabuleiro.jogadorLocal.adicionarPontos(pontos)
                
                if carta.temBonus():
                    bonus = carta.pegarBonus()
                    self.tabuleiro.jogadorLocal.adicionarBonus(bonus)
                
                self.desenharTabuleiro()
                return True
            else:
                self.notificarJogadaInvalida("Você não tem pedras suficientes para comprar esta carta.")
                return False
        else:
            self.notificarJogadaInvalida("Carta reservada não encontrada.")
            return False

    def realizarReservaCarta(self):
        """Executa a reserva da carta selecionada"""
        if self.cartaSelecionada is None:
            return
        
        # Adiciona carta à reserva do jogador
        if self.tabuleiro.jogadorLocal.reservarCarta(self.cartaSelecionada):
            # Remove a carta do tabuleiro
            indice = self.tabuleiro.cartasNoTabuleiro.index(self.cartaSelecionada)
            self.tabuleiro.cartasNoTabuleiro[indice] = None
            
            # Repõe imediatamente uma nova carta
            nivel = self.cartaSelecionada.pegarNivel()
            self.reporTabuleiro(nivel)
            
            # Adiciona uma pedra de ouro se disponível
            if self.tabuleiro.pedrasNoTabuleiro[PedrasEnum.OURO] > 0:
                self.tabuleiro.jogadorLocal.adicionarPedraNaMao(PedrasEnum.OURO, 1)
                self.tabuleiro.pedrasNoTabuleiro[PedrasEnum.OURO] -= 1
            
            self.cartaSelecionada = None
            self.desenharTabuleiro()
        else:
            self.notificarJogadaInvalida("Não foi possível reservar esta carta.")

    def realizarCompraCarta(self):
        """Executa a compra da carta selecionada"""
        if self.cartaSelecionada is None:
            return
        
        # Remove pedras do jogador
        pedras_carta = self.cartaSelecionada.pegarPedrasDaCarta()
        self.tabuleiro.jogadorLocal.removerPedras(pedras_carta)
        
        # Adiciona carta ao jogador
        self.tabuleiro.jogadorLocal.adicionarCarta(self.cartaSelecionada)
        
        # Adiciona pontos e bônus
        pontos = self.cartaSelecionada.pegarPontos()
        if pontos > 0:
            self.tabuleiro.jogadorLocal.adicionarPontos(pontos)
        
        if self.cartaSelecionada.temBonus():
            bonus = self.cartaSelecionada.pegarBonus()
            self.tabuleiro.jogadorLocal.adicionarBonus(bonus)
        
        # Remove e repõe a carta no tabuleiro
        nivel = self.cartaSelecionada.pegarNivel()
        indice = self.tabuleiro.cartasNoTabuleiro.index(self.cartaSelecionada)
        self.tabuleiro.cartasNoTabuleiro[indice] = None
        
        # Repõe imediatamente uma nova carta
        self.reporTabuleiro(nivel)
        
        self.cartaSelecionada = None
        self.desenharTabuleiro()

    def realizarCompraPedras(self):
        """Executa a compra das pedras selecionadas"""
        if len(self.pedrasSelecionadas) < 2:
            return
        
        # Verifica se a seleção é válida
        if len(self.pedrasSelecionadas) == 2:
            # Duas pedras iguais
            if self.pedrasSelecionadas[0] != self.pedrasSelecionadas[1]:
                self.notificarJogadaInvalida("Para selecionar 2 pedras, elas devem ser iguais.")
                return
        elif len(self.pedrasSelecionadas) == 3:
            # Três pedras diferentes
            if len(set(self.pedrasSelecionadas)) != 3:
                self.notificarJogadaInvalida("Para selecionar 3 pedras, elas devem ser diferentes.")
                return
        
        # Verifica se há pedras suficientes no tabuleiro
        for pedra in self.pedrasSelecionadas:
            if self.tabuleiro.pedrasNoTabuleiro[pedra] < 1:
                self.notificarJogadaInvalida(f"Não há pedras suficientes do tipo {pedra.name} no tabuleiro.")
                return
        
        # Remove pedras do tabuleiro
        for pedra in self.pedrasSelecionadas:
            self.tabuleiro.pedrasNoTabuleiro[pedra] -= 1
        
        # Adiciona pedras ao jogador
        for pedra in self.pedrasSelecionadas:
            self.tabuleiro.jogadorLocal.adicionarPedraNaMao(pedra, 1)
        
        self.desenharTabuleiro()

    def clickFinalizarJogada(self):
        if len(self.pedrasSelecionadas) >= 2:
            self.realizarCompraPedras()

        if self.cartaSelecionada and len(self.pedrasSelecionadas)==0:
            # Verifica se está no modo de compra ou reserva
            if hasattr(self, 'modo_reserva') and self.modo_reserva:
                self.realizarReservaCarta()
            else:
                self.realizarCompraCarta()
            
            ultima_partida = self.tabuleiro.ehUltimaPartida()
            if ultima_partida:
                self.avaliarVencedor()

    
        self.pedrasSelecionadas = list()
        self.cartaSelecionada = None
        self.modo_reserva = False  # Reseta o modo de reserva
        
        # Troca o turno entre os jogadores
        self.tabuleiro.jogadorLocal.jogadorEmTurno = False
        self.tabuleiro.jogadorRemoto.jogadorEmTurno = True
        
        # Desabilita jogadas do jogador local
        self.desabilitarJogadas()
        
        self.atualizarTabuleiro(self.tabuleiro)
        self.finalizar_jogada_callback(self.tabuleiro)