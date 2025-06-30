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
from model.carta import Carta

# Variável global para o valor mínimo de pontos para vitória
PONTOS_MINIMOS_VITORIA = 6

class TelaJogo:
    def __init__(self, root: Tk, show_screen, jogador_local: Jogador, jogador_remoto: Jogador, finalizar_jogada_callback, seed_partida=None):
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

        # Usa o seed fornecido ou usa o fixo 12345
        if seed_partida is not None:
            self.seed_partida = seed_partida
        else:
            self.seed_partida = 12345  # Seed fixo
        
        self.tabuleiro = Tabuleiro(jogadorLocal=jogador_local, jogadorRemoto=jogador_remoto, seed=self.seed_partida)
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
        
        # Variáveis para oferta de troca
        self.modo_oferta_troca = False
        self.pedra_local_selecionada = None
        self.pedra_remoto_selecionada = None
        self.oferta_pendente = None  # Armazena a oferta para o próximo jogador
        
        # Controles de habilitação
        self.pedras_habilitadas = False
        self.cartas_habilitadas = False

        # Cache para efeitos visuais
        self.efeitos_clique = {}
        self.pedras_selecionadas_visuais = set()

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
        if self.tabuleiro.pegarJogadorLocal().verificarHabilitado():
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
        
        # Preserva o seed da partida no novo tabuleiro
        if hasattr(self, 'seed_partida'):
            self.tabuleiro.seed_partida = self.seed_partida
        
        # Recarrega os baralhos se estiverem vazios (caso de tabuleiro recebido do servidor)
        self.recarregarBaralhos()
        
        # Recarrega as imagens das cartas para garantir que todas as cartas no tabuleiro
        # tenham suas imagens carregadas corretamente
        self.recarregarImagensCartas()
        
        self.desenharTabuleiro()
        
        # Verifica se é o turno do jogador local
        if self.tabuleiro.pegarJogadorLocal().jogadorEmTurno:
            self.tabuleiro.pegarJogadorLocal().habilitarJogador()
            self.habilitarJogadas()
        else:
            self.tabuleiro.pegarJogadorLocal().desabilitarJogador()
            self.desabilitarJogadas()
        
        # Verifica se há oferta pendente para o jogador atual (local ou remoto)
        self.verificarOfertaPendente()

    def recarregarBaralhos(self):
        """Recarrega os baralhos se estiverem vazios (caso de tabuleiro recebido do servidor)"""
        # Verifica se algum baralho está vazio
        baralhos_vazios = []
        for i, baralho in enumerate(self.tabuleiro.baralhos):
            if len(baralho.cartas) == 0:
                baralhos_vazios.append(i)
        
        if baralhos_vazios:
            # Recarrega apenas os baralhos vazios
            for nivel_idx in baralhos_vazios:
                nivel = NiveisEnum(nivel_idx + 1)
                self.recarregarBaralho(nivel)
            

    def recarregarBaralho(self, nivel: NiveisEnum):
        """Recarrega um baralho específico com cartas do nível correspondente"""
        # Usa o seed do tabuleiro se disponível, senão usa o seed da partida
        seed = getattr(self.tabuleiro, 'seed_partida', self.seed_partida)
        rng = random.Random(seed + nivel.value)  # Usa seed + nível para variação
        
        # Define o diretório baseado no nível
        if nivel == NiveisEnum.NIVEL1:
            diretorio = Path("./resources/cartas/cartas-tabuleiro/cartas-nivel-1")
            roubo = False
        elif nivel == NiveisEnum.NIVEL2:
            diretorio = Path("./resources/cartas/cartas-tabuleiro/cartas-nivel-2")
            roubo = False
        elif nivel == NiveisEnum.NIVEL3:
            diretorio = Path("./resources/cartas/cartas-tabuleiro/cartas-nivel-3")
            roubo = False
        else:
            print(f"Nível inválido para recarregar baralho: {nivel}")
            return
        
        # Carrega cartas únicas do diretório
        cartas_unicas = []
        # Ordena os arquivos para garantir consistência entre jogadores
        arquivos_cartas = sorted(diretorio.glob("*.png"), key=lambda x: x.name)
        
        for carta_img in arquivos_cartas:
            try:
                img = Image.open(carta_img)
                img = img.resize((self.CARD_WIDTH * 10, self.CARD_HEIGHT * 10), Image.Resampling.LANCZOS)
                img_tk = ImageTk.PhotoImage(img)
                id_base, pontos, pedras, cartaDeRoubo, bonus, habilitada = self.extrair_dados_carta(carta_img, nivel, roubo)
                
                cartas_unicas.append({
                    'img_tk': img_tk,
                    'id_base': id_base,
                    'pontos': pontos,
                    'pedras': pedras.copy(),
                    'cartaDeRoubo': cartaDeRoubo,
                    'bonus': bonus,
                    'habilitada': habilitada,
                    'nivel': nivel
                })
            except Exception as e:
                print(f"Erro ao carregar carta {carta_img}: {e}")
                
        # Cria 20 cartas para o baralho, reutilizando as cartas únicas
        cartas_por_nivel = 20
        baralho = self.tabuleiro.baralhos[nivel.value - 1]
        
        for i in range(cartas_por_nivel):
            # Seleciona uma carta única de forma cíclica
            carta_unica = cartas_unicas[i % len(cartas_unicas)]
            
            # Cria ID único para esta instância
            id_carta = hash(f"{carta_unica['id_base']}_{nivel.value}_{i}")
            
            # Instancia a carta
            self.tabuleiro.instanciarCartas(
                id=id_carta,
                pontos=carta_unica['pontos'],
                nivel=carta_unica['nivel'],
                pedras=carta_unica['pedras'],
                cartaDeRoubo=False,
                bonus=carta_unica['bonus'],
                habilitada=carta_unica['habilitada']
            )
            
            # Associa a imagem à carta
            self.carta_imgs[id_carta] = carta_unica['img_tk']
        
        # Embaralha o baralho com a mesma seed para garantir consistência
        if len(baralho.cartas) > 0:
            random.Random(seed + nivel.value).shuffle(baralho.cartas)
        else:
            print(f"ERRO: Baralho {nivel.name} ainda está vazio após recarregamento!")

    def recarregarImagensCartas(self):
        """Recarrega as imagens das cartas para todas as cartas no tabuleiro"""
        # Limpa o cache de imagens das cartas
        self.carta_imgs = {}
        
        # Recarrega todas as cartas do tabuleiro
        for carta in self.tabuleiro.cartasNoTabuleiro:
            if carta is not None:
                self.get_carta_img(carta)
        
        # Recarrega cartas dos jogadores também
        for carta in self.tabuleiro.pegarJogadorLocal().pegarCartas():
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
        
        Button(frame, text="OK", command=lambda: [desistencia_window.destroy(), self.sairJogo()], 
               font=("Arial", 10), bg="lightgray").pack(pady=10)
    
    def desabilitarJogador(self):
        self.tabuleiro.pegarJogadorLocal().desabilitarJogador()
    
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
        
        # Usa o nome do arquivo como ID base para garantir consistência
        # O ID final será gerado usando hash determinístico no método que chama esta função
        id_carta = nome
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
            return None
            
        except Exception as e:
            print(f"Erro ao carregar imagem da carta {carta.id}: {e}")
            return None

    def carregarCartas(self):
        self.carta_imgs = {}
        seed = self.seed_partida  # Use o seed da partida para consistência

        def carregarCartasDeDiretorio(diretorio: Path, nivel: NiveisEnum = None, roubo=False):
            # Primeiro, carrega todas as cartas únicas do diretório
            cartas_unicas = []
            # Ordena os arquivos para garantir consistência entre jogadores
            arquivos_cartas = sorted(diretorio.glob("*.png"), key=lambda x: x.name)
            
            for carta_img in arquivos_cartas:
                try:
                    img = Image.open(carta_img)
                    img = img.resize((self.CARD_WIDTH * 10, self.CARD_HEIGHT * 10), Image.Resampling.LANCZOS)
                    img_tk = ImageTk.PhotoImage(img)
                    id_base, pontos, pedras, cartaDeRoubo, bonus, habilitada = self.extrair_dados_carta(carta_img, nivel, roubo)
                    nivel_destino = NiveisEnum.NIVEL3 if roubo else nivel
                    
                    cartas_unicas.append({
                        'img_tk': img_tk,
                        'id_base': id_base,
                        'pontos': pontos,
                        'pedras': pedras.copy(),
                        'cartaDeRoubo': cartaDeRoubo,
                        'bonus': bonus,
                        'habilitada': habilitada,
                        'nivel': nivel_destino
                    })
                except Exception as e:
                    print(f"Erro ao carregar carta {carta_img}: {e}")
                        
            # Agora cria 20 cartas por deck, reutilizando as cartas únicas
            if not roubo:
                # Para cartas normais, cria 20 cartas por nível
                cartas_por_nivel = 20
                for i in range(cartas_por_nivel):
                    # Seleciona uma carta única de forma cíclica
                    carta_unica = cartas_unicas[i % len(cartas_unicas)]
                    
                    # Cria ID único para esta instância
                    id_carta = hash(f"{carta_unica['id_base']}_{nivel.value}_{i}")
                    
                    # Instancia a carta
                    self.tabuleiro.instanciarCartas(
                        id=id_carta,
                        pontos=carta_unica['pontos'],
                        nivel=carta_unica['nivel'],
                        pedras=carta_unica['pedras'],
                        cartaDeRoubo=False,
                        bonus=carta_unica['bonus'],
                        habilitada=carta_unica['habilitada']
                    )
                    
                    # Associa a imagem à carta (reutiliza a mesma imagem para todas as instâncias da mesma carta)
                    self.carta_imgs[id_carta] = carta_unica['img_tk']
                
            else:
                # Para cartas de roubo, cria apenas 3 cartas
                for i in range(3):
                    if i < len(cartas_unicas):
                        carta_unica = cartas_unicas[i]
                        id_carta = hash(f"{carta_unica['id_base']}_roubo_{i}")
                        
                        self.tabuleiro.instanciarCartas(
                            id=id_carta,
                            pontos=carta_unica['pontos'],
                            nivel=carta_unica['nivel'],
                            pedras=carta_unica['pedras'],
                            cartaDeRoubo=True,
                            bonus=carta_unica['bonus'],
                            habilitada=carta_unica['habilitada']
                        )
                        self.carta_imgs[id_carta] = carta_unica['img_tk']
                

        diretorios_cartas = {
            NiveisEnum.NIVEL1: Path("./resources/cartas/cartas-tabuleiro/cartas-nivel-1"),
            NiveisEnum.NIVEL2: Path("./resources/cartas/cartas-tabuleiro/cartas-nivel-2"),
            NiveisEnum.NIVEL3: Path("./resources/cartas/cartas-tabuleiro/cartas-nivel-3"),
        }
        cartas_roubo_dir = Path("./resources/cartas/cartas-tabuleiro/cartas-de-roubo")

        # Carrega cartas normais primeiro
        for nivel, diretorio in diretorios_cartas.items():
            carregarCartasDeDiretorio(diretorio, nivel)
        
        # Carrega cartas de roubo
        carregarCartasDeDiretorio(cartas_roubo_dir, NiveisEnum.NIVEL3, roubo=True)

        # Verifica se os baralhos foram carregados corretamente
        for i, baralho in enumerate(self.tabuleiro.baralhos):
            print(f"Baralho {i+1} ({baralho.nivel.name}): {len(baralho.cartas)} cartas")
            if len(baralho.cartas) > 0:
                print(f"  Primeiras 3 cartas: {[c.id for c in baralho.cartas[:3]]}")

        # Embaralhe cada baralho com a mesma seed para garantir consistência
        for i, baralho in enumerate(self.tabuleiro.baralhos):
            if len(baralho.cartas) > 0:
                random.Random(seed + i).shuffle(baralho.cartas)
            else:
                print(f"ERRO: Baralho {i+1} está vazio!")

        # Inicializa as cartas no tabuleiro
        self.tabuleiro.inicializar_cartas_tabuleiro()
        
        # Verifica se há cartas de roubo e as adiciona aos jogadores
        cartas_roubo_jogador = [c for c in self.tabuleiro.pegarJogadorLocal().pegarCartas() if c.cartaDeRoubo]

    def carregarBotoes(self):
        """Carrega e redimensiona as imagens dos botões"""
        botoes_dir = Path("./resources/botoes")

        for botao_img in botoes_dir.glob("*.png"):
            try:
                img = Image.open(botao_img)
                if botao_img.stem == "desfazer_jogada":
                    tamanho_botoes = (150, 80)
                elif botao_img.stem == "finalizar_jogada":
                    tamanho_botoes = (180, 90)  # Diminuído height de 100 para 90
                else:
                    tamanho_botoes = (150, 100)
                img = img.resize(tamanho_botoes, Image.Resampling.LANCZOS)
                img_tk = ImageTk.PhotoImage(img)
                self.botoes[botao_img.stem] = img_tk
            except Exception as e:
                print(f"Erro ao carregar botão {botao_img}: {e}")
        
        # Carrega o botão de settings separadamente
        try:
            img_settings = Image.open("./resources/botoes/settings.png")
            img_settings = img_settings.resize((60, 60), Image.Resampling.LANCZOS)  # Tamanho menor
            self.botoes["settings"] = ImageTk.PhotoImage(img_settings)
        except Exception as e:
            print(f"Erro ao carregar botão settings: {e}")

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
        if self.tabuleiro.pegarJogadorLocal().jogadorEmTurno:
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
    
    def clickOfertaDeTroca(self):
        """Ação ao clicar no botão 'Oferta de Troca'"""
        if not self.tabuleiro.pegarJogadorLocal().jogadorEmTurno:
            messagebox.showinfo("Não é sua vez", "Você só pode fazer oferta de troca no seu turno.")
            return
            
        # Verifica se o jogador tem pedras para trocar
        pedras_local = self.tabuleiro.pegarJogadorLocal().pegarPedras()
        pedras_remoto = self.tabuleiro.jogadorRemoto.pegarPedras()
        
        pedras_disponiveis_local = {pedra: qtd for pedra, qtd in pedras_local.items() if qtd > 0}
        pedras_disponiveis_remoto = {pedra: qtd for pedra, qtd in pedras_remoto.items() if qtd > 0}
        
        if not pedras_disponiveis_local:
            messagebox.showinfo("Sem pedras", "Você não tem pedras para trocar.")
            return
            
        if not pedras_disponiveis_remoto:
            messagebox.showinfo("Oponente sem pedras", "Seu oponente não tem pedras para trocar.")
            return
        
        # Desabilita outros botões
        self.desabilitarBotaoComprarPedras()
        self.desabilitarBotaoComprarCarta()
        self.desabilitarReservarCarta()
        self.desabilitarPedras()
        self.desabilitarCartas()
        
        # Habilita o modo de oferta de troca
        self.modo_oferta_troca = True
        self.habilitarDesfazerJogada()
        
        # Mostra popup para seleção
        self.exibirPopupOfertaTroca(pedras_disponiveis_local, pedras_disponiveis_remoto)

    def exibirPopupOfertaTroca(self, pedras_local, pedras_remoto):
        """Exibe popup para seleção de pedras na oferta de troca"""
        popup = Toplevel(self.root)
        popup.title("Oferta de Troca")
        popup.geometry("500x500")
        popup.resizable(False, False)
        popup.transient(self.root)
        
        # Frame principal
        main_frame = Frame(popup, bg="white")
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Título
        Label(main_frame, text="Selecione as pedras para troca", 
              font=("Arial", 16, "bold"), bg="white").pack(pady=(0, 20))
        
        # Frame para mostrar seleções
        frame_selecoes = Frame(main_frame, bg="white")
        frame_selecoes.pack(fill=X, pady=10)
        
        # Label para mostrar pedra local selecionada
        self.label_pedra_local = Label(frame_selecoes, text="Sua pedra: Nenhuma selecionada", 
                                      font=("Arial", 12), bg="white", fg="blue")
        self.label_pedra_local.pack()
        
        # Label para mostrar pedra remoto selecionada
        self.label_pedra_remoto = Label(frame_selecoes, text="Pedra do oponente: Nenhuma selecionada", 
                                       font=("Arial", 12), bg="white", fg="red")
        self.label_pedra_remoto.pack()
        
        # Frame para pedras do jogador local
        frame_local = Frame(main_frame, bg="white")
        frame_local.pack(fill=X, pady=10)
        
        Label(frame_local, text="Suas pedras:", font=("Arial", 12, "bold"), bg="white").pack(anchor=W)
        
        frame_pedras_local = Frame(frame_local, bg="white")
        frame_pedras_local.pack(fill=X, pady=5)
        
        self.pedra_local_selecionada = None
        self.pedra_remoto_selecionada = None
        
        # Botões para pedras do jogador local
        for pedra, qtd in pedras_local.items():
            if qtd > 0:
                frame_pedra = Frame(frame_pedras_local, bg="white")
                frame_pedra.pack(side=LEFT, padx=5)
                
                # Carrega imagem da pedra
                try:
                    img = Image.open(f"./resources/pedras/{pedra.name.lower()}.png")
                    img = img.resize((40, 40), Image.Resampling.LANCZOS)
                    img_tk = ImageTk.PhotoImage(img)
                    
                    btn = Button(frame_pedra, image=img_tk, 
                               command=lambda p=pedra: self.selecionarPedraLocal(p, popup),
                               relief=FLAT, bg="white")
                    btn.image = img_tk  # Mantém referência
                    btn.pack()
                    
                    Label(frame_pedra, text=f"{qtd}", font=("Arial", 10), bg="white").pack()
                except Exception as e:
                    print(f"Erro ao carregar imagem da pedra {pedra.name}: {e}")
                    btn = Button(frame_pedra, text=f"{pedra.name}\n({qtd})", 
                               command=lambda p=pedra: self.selecionarPedraLocal(p, popup),
                               relief=RAISED, bg="lightblue")
                    btn.pack()
        
        # Frame para pedras do jogador remoto
        frame_remoto = Frame(main_frame, bg="white")
        frame_remoto.pack(fill=X, pady=10)
        
        Label(frame_remoto, text="Pedras do oponente:", font=("Arial", 12, "bold"), bg="white").pack(anchor=W)
        
        frame_pedras_remoto = Frame(frame_remoto, bg="white")
        frame_pedras_remoto.pack(fill=X, pady=5)
        
        # Botões para pedras do jogador remoto
        for pedra, qtd in pedras_remoto.items():
            if qtd > 0:
                frame_pedra = Frame(frame_pedras_remoto, bg="white")
                frame_pedra.pack(side=LEFT, padx=5)
                
                # Carrega imagem da pedra
                try:
                    img = Image.open(f"./resources/pedras/{pedra.name.lower()}.png")
                    img = img.resize((40, 40), Image.Resampling.LANCZOS)
                    img_tk = ImageTk.PhotoImage(img)
                    
                    btn = Button(frame_pedra, image=img_tk, 
                               command=lambda p=pedra: self.selecionarPedraRemoto(p, popup),
                               relief=FLAT, bg="white")
                    btn.image = img_tk  # Mantém referência
                    btn.pack()
                    
                    Label(frame_pedra, text=f"{qtd}", font=("Arial", 10), bg="white").pack()
                except Exception as e:
                    print(f"Erro ao carregar imagem da pedra {pedra.name}: {e}")
                    btn = Button(frame_pedra, text=f"{pedra.name}\n({qtd})", 
                               command=lambda p=pedra: self.selecionarPedraRemoto(p, popup),
                               relief=RAISED, bg="lightcoral")
                    btn.pack()
        
        # Botões de ação
        frame_botoes = Frame(main_frame, bg="white")
        frame_botoes.pack(fill=X, pady=20)
        
        Button(frame_botoes, text="Cancelar", command=lambda: [popup.destroy(), self.cancelarOfertaTroca()],
               font=("Arial", 12), bg="lightgray").pack(side=LEFT, padx=5)
        
        Button(frame_botoes, text="Enviar Oferta", command=lambda: [popup.destroy(), self.enviarOfertaTroca()],
               font=("Arial", 12), bg="lightgreen").pack(side=RIGHT, padx=5)
        
        # Configura o popup após todos os widgets serem criados
        popup.update_idletasks()
        popup.focus_set()
        
        # Tenta definir o grab com tratamento de erro
        try:
            popup.grab_set()
        except Exception as e:
            print(f"Erro ao definir grab do popup: {e}")
            # Continua sem o grab se falhar

    def selecionarPedraLocal(self, pedra, popup):
        """Seleciona uma pedra do jogador local para troca"""
        self.pedra_local_selecionada = pedra
        # Atualiza o label para mostrar a seleção
        self.label_pedra_local.config(text=f"Sua pedra: {pedra.name} ✓", fg="green")
        messagebox.showinfo("Pedra Selecionada", f"Você selecionou {pedra.name} para trocar. Agora selecione uma pedra do oponente.")

    def selecionarPedraRemoto(self, pedra, popup):
        """Seleciona uma pedra do jogador remoto para troca"""
        if self.pedra_local_selecionada is None:
            messagebox.showwarning("Seleção Incompleta", "Primeiro selecione uma pedra sua para trocar.")
            return
            
        self.pedra_remoto_selecionada = pedra
        # Atualiza o label para mostrar a seleção
        self.label_pedra_remoto.config(text=f"Pedra do oponente: {pedra.name} ✓", fg="green")
        messagebox.showinfo("Pedra Selecionada", f"Você selecionou {pedra.name} do oponente para trocar. Clique em 'Enviar Oferta' para finalizar.")
        # NÃO fecha o popup automaticamente - deixa o usuário clicar em "Enviar Oferta"

    def cancelarOfertaTroca(self):
        """Cancela a oferta de troca"""
        self.modo_oferta_troca = False
        self.pedra_local_selecionada = None
        self.pedra_remoto_selecionada = None
        
        # Reabilita os botões
        if self.tabuleiro.pegarJogadorLocal().jogadorEmTurno:
            self.habilitarJogadas()
        self.desabilitarBotaoDesfazerJogada()
        
        messagebox.showinfo("Oferta Cancelada", "A oferta de troca foi cancelada.")

    def enviarOfertaTroca(self):
        """Envia a oferta de troca"""
        if self.pedra_local_selecionada and self.pedra_remoto_selecionada:
            try:
                # Cria a oferta para o oponente
                oferta = {
                    'pedra_local': self.pedra_local_selecionada,
                    'pedra_remoto': self.pedra_remoto_selecionada,
                    'jogador_origem': 'local'  # Indica que veio do jogador local
                }
                
                
                # Armazena a oferta no tabuleiro para ser enviada
                self.tabuleiro.oferta_pendente = oferta
                
                messagebox.showinfo("Oferta Enviada", 
                                  f"Oferta enviada: sua {self.pedra_local_selecionada.name} pela {self.pedra_remoto_selecionada.name} do oponente.")
                
                # Finaliza a jogada
                self.finalizarOfertaTroca()
            except Exception as e:
                print(f"Erro ao criar/enviar oferta: {e}")
                import traceback
                traceback.print_exc()
                messagebox.showerror("Erro", f"Erro ao enviar oferta: {e}")
        else:
            messagebox.showwarning("Seleção Incompleta", "Você precisa selecionar uma pedra sua e uma pedra do oponente antes de enviar a oferta.")

    def finalizarOfertaTroca(self):
        """Finaliza a oferta de troca e passa o turno"""
        self.modo_oferta_troca = False
        self.pedra_local_selecionada = None
        self.pedra_remoto_selecionada = None
        
        # Garante que não há oferta pendente no tabuleiro se não foi enviada
        if not hasattr(self.tabuleiro, 'oferta_pendente') or self.tabuleiro.oferta_pendente is None:
            self.tabuleiro.oferta_pendente = None
        
        # Troca o turno
        self.tabuleiro.pegarJogadorLocal().jogadorEmTurno = False
        self.tabuleiro.jogadorRemoto.jogadorEmTurno = True
        
        # Desabilita jogadas do jogador local
        self.desabilitarJogadas()
        
        self.atualizarTabuleiro(self.tabuleiro)
        self.finalizar_jogada_callback(self.tabuleiro)

    def verificarOfertaPendente(self):
        """Verifica se há uma oferta pendente para o jogador atual"""
        if not self.tabuleiro.oferta_pendente:
            print("Nenhuma oferta pendente encontrada")
            return
        
        # Verifica se a oferta é para o jogador atual
        # Como os jogadores são invertidos quando recebidos do servidor,
        # se o jogador local está em turno, a oferta deve ter vindo do remoto (que agora é local)
        # e vice-versa
        oferta_para_jogador_atual = (
            (self.tabuleiro.pegarJogadorLocal().jogadorEmTurno and 
             self.tabuleiro.oferta_pendente['jogador_origem'] == 'local') or
            (self.tabuleiro.jogadorRemoto.jogadorEmTurno and 
             self.tabuleiro.oferta_pendente['jogador_origem'] == 'remoto')
        )
        
        
        if oferta_para_jogador_atual:
            
            # Armazena a oferta localmente para processamento
            self.oferta_pendente = self.tabuleiro.oferta_pendente
            # Limpa a oferta do tabuleiro para evitar reprocessamento
            self.tabuleiro.oferta_pendente = None
            
            self.exibirPopupRespostaOferta()

    def exibirPopupRespostaOferta(self):
        """Exibe popup para resposta da oferta de troca"""
        oferta = self.oferta_pendente
        
        popup = Toplevel(self.root)
        popup.title("Oferta de Troca Recebida")
        popup.geometry("500x400")
        popup.resizable(False, False)
        popup.transient(self.root)
        
        # Frame principal
        main_frame = Frame(popup, bg="white")
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Título
        Label(main_frame, text="Oferta de Troca Recebida", 
              font=("Arial", 16, "bold"), bg="white").pack(pady=(0, 20))
        
        # Descrição da oferta
        descricao = f"O oponente quer trocar:"
        Label(main_frame, text=descricao, font=("Arial", 12), bg="white", justify=CENTER).pack(pady=10)
        
        # Frame para mostrar as pedras com imagens
        frame_pedras = Frame(main_frame, bg="white")
        frame_pedras.pack(pady=20)
        
        # Pedra do oponente (o que ele oferece)
        frame_oponente = Frame(frame_pedras, bg="white")
        frame_oponente.pack(side=LEFT, padx=30)
        
        Label(frame_oponente, text="Oponente oferece:", font=("Arial", 12, "bold"), bg="white").pack(pady=(0, 10))
        
        try:
            img = Image.open(f"./resources/pedras/{oferta['pedra_local'].name.lower()}.png")
            img = img.resize((80, 80), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            
            Label(frame_oponente, image=img_tk, bg="white").pack()
            Label(frame_oponente, text=oferta['pedra_local'].name, font=("Arial", 12), bg="white").pack()
        except Exception as e:
            Label(frame_oponente, text=oferta['pedra_local'].name, font=("Arial", 14), bg="lightblue", 
                  relief=RAISED, padx=20, pady=10).pack()
        
        # Seta
        Label(frame_pedras, text="↔", font=("Arial", 24, "bold"), bg="white", fg="orange").pack(side=LEFT, padx=20)
        
        # Sua pedra (o que você dá)
        frame_sua = Frame(frame_pedras, bg="white")
        frame_sua.pack(side=LEFT, padx=30)
        
        Label(frame_sua, text="Sua pedra:", font=("Arial", 12, "bold"), bg="white").pack(pady=(0, 10))
        
        try:
            img = Image.open(f"./resources/pedras/{oferta['pedra_remoto'].name.lower()}.png")
            img = img.resize((80, 80), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            
            Label(frame_sua, image=img_tk, bg="white").pack()
            Label(frame_sua, text=oferta['pedra_remoto'].name, font=("Arial", 12), bg="white").pack()
        except Exception as e:
            Label(frame_sua, text=oferta['pedra_remoto'].name, font=("Arial", 14), bg="lightcoral", 
                  relief=RAISED, padx=20, pady=10).pack()
        
        # Botões de resposta com efeitos visuais
        frame_botoes = Frame(main_frame, bg="white")
        frame_botoes.pack(fill=X, pady=30)
        
        # Botão Recusar
        btn_recusar = Button(frame_botoes, text="RECUSAR", 
                           command=lambda: [popup.destroy(), self.recusarOfertaTroca()],
                           font=("Arial", 14, "bold"), bg="red", fg="white", 
                           relief=RAISED, padx=30, pady=10, cursor="hand2")
        btn_recusar.pack(side=LEFT, padx=10, expand=True)
        
        # Botão Aceitar
        btn_aceitar = Button(frame_botoes, text="ACEITAR", 
                           command=lambda: [popup.destroy(), self.aceitarOfertaTroca()],
                           font=("Arial", 14, "bold"), bg="green", fg="white", 
                           relief=RAISED, padx=30, pady=10, cursor="hand2")
        btn_aceitar.pack(side=RIGHT, padx=10, expand=True)
        
        # Efeitos de hover nos botões
        def on_enter_btn(event, btn, cor_original, cor_hover):
            btn.configure(bg=cor_hover)
        
        def on_leave_btn(event, btn, cor_original):
            btn.configure(bg=cor_original)
        
        btn_recusar.bind("<Enter>", lambda e: on_enter_btn(e, btn_recusar, "red", "#ff4444"))
        btn_recusar.bind("<Leave>", lambda e: on_leave_btn(e, btn_recusar, "red"))
        btn_aceitar.bind("<Enter>", lambda e: on_enter_btn(e, btn_aceitar, "green", "#44ff44"))
        btn_aceitar.bind("<Leave>", lambda e: on_leave_btn(e, btn_aceitar, "green"))
        
        # Configura o popup após todos os widgets serem criados
        popup.update_idletasks()
        popup.focus_set()
        
        # Tenta definir o grab com tratamento de erro
        try:
            popup.grab_set()
        except Exception as e:
            print(f"Erro ao definir grab do popup de resposta: {e}")

    def aceitarOfertaTroca(self):
        """Aceita a oferta de troca"""
        oferta = self.oferta_pendente
        
        # Executa a troca: o jogador local recebe a pedra do oponente e dá sua pedra
        # Remove a pedra que o jogador local vai dar
        jogadorLocal = self.tabuleiro.pegarJogadorLocal()
        jogadorLocal.removerPedras({oferta['pedra_remoto']: 1})
        # Adiciona a pedra que o jogador local vai receber
        jogadorLocal.adicionarPedraNaMao(oferta['pedra_local'], 1)
        
        # Atualiza o jogador remoto: remove a pedra que ele vai dar e adiciona a que vai receber
        jogadorRemoto = self.tabuleiro.pegarJogadorRemoto()
        jogadorRemoto.removerPedras({oferta['pedra_local']: 1})
        jogadorRemoto.adicionarPedraNaMao(oferta['pedra_remoto'], 1)
        
        # Remove a oferta pendente
        self.oferta_pendente = None
        
        messagebox.showinfo("Troca Aceita", f"Troca realizada: você recebeu {oferta['pedra_local'].name} e deu {oferta['pedra_remoto'].name}.")
        
        # Atualiza o tabuleiro
        self.desenharTabuleiro()

    def recusarOfertaTroca(self):
        """Recusa a oferta de troca"""
        # Remove a oferta pendente
        self.oferta_pendente = None
        
        messagebox.showinfo("Troca Recusada", "Você recusou a oferta de troca.")
        
        # Atualiza o tabuleiro
        self.desenharTabuleiro()

    def clickPedra(self, pedra: PedrasEnum):
        """Método chamado quando uma pedra é clicada no tabuleiro"""
        # Verifica se as pedras estão habilitadas para seleção
        if not self.pedras_habilitadas:
            messagebox.showinfo("Pedras não habilitadas", "Clique em 'Comprar Pedras' para habilitar a seleção de pedras.")
            return
        
        # Ouro não pode ser comprado diretamente
        if pedra == PedrasEnum.OURO:
            messagebox.showinfo("Pedra de Ouro", "Pedras de ouro só podem ser obtidas ao reservar cartas!")
            return
            
        self.pedrasSelecionadas.append(pedra)

        # Aplica efeito visual de seleção
        self.aplicar_efeito_selecao_pedra(pedra)
        self.pedras_selecionadas_visuais.add(pedra)

        if len(self.pedrasSelecionadas) == 1:
            # Primeira pedra selecionada - mostra opções
            opcoes = f"Você selecionou {pedra.name}.\n\nAgora você pode:\n• Selecionar mais uma pedra {pedra.name} (para ter 2 iguais)\n• Selecionar duas pedras diferentes (para ter 3 diferentes)"
            messagebox.showinfo("Primeira Pedra Selecionada", opcoes)
            
        elif len(self.pedrasSelecionadas) == 2:
            if self.pedrasSelecionadas[0] == self.pedrasSelecionadas[1]:
                messagebox.showinfo(
                    "Pedras Selecionadas",
                    f"Você selecionou 2 pedras do tipo {pedra.name}.\nClique em 'Finalizar Jogada' para confirmar."
                )
                self.habilitarBotaoFinalizarJogada()
                self.desabilitarPedras()  # Desabilita imediatamente

            else:
                messagebox.showinfo(
                    "Pedras Selecionadas",
                    f"Você selecionou 2 pedras diferentes: {self.pedrasSelecionadas[0].name} e {self.pedrasSelecionadas[1].name}.\nAgora selecione uma terceira pedra diferente."
                )
        elif len(self.pedrasSelecionadas) == 3:
            p1, p2, p3 = self.pedrasSelecionadas
            if p1 == p2 or p1 == p3 or p2 == p3:
                messagebox.showerror(
                    "Erro",
                    "A terceira pedra selecionada não pode ser igual às anteriores. Tente novamente."
                )
                # Remove a última pedra e seu efeito visual
                self.pedrasSelecionadas.pop()
                self.remover_efeito_selecao_pedra(p3)
                self.pedras_selecionadas_visuais.discard(p3)
            else:
                messagebox.showinfo(
                    "Pedras Selecionadas",
                    f"Você selecionou 3 pedras diferentes: {p1.name}, {p2.name}, e {p3.name}.\nClique em 'Finalizar Jogada' para confirmar."
                )
                self.habilitarBotaoFinalizarJogada()
                self.desabilitarPedras()  # Desabilita imediatamente

    def notificarJogadaInvalida(self, mensagem: str):
        """Exibe uma mensagem de erro quando uma jogada inválida é realizada"""
        messagebox.showerror(
            title="Jogada inválida",
            message=mensagem,
            parent=self.root
        )

    def clickCarta(self, indiceCarta: int):
        """Método chamado quando uma carta é clicada no tabuleiro"""
        # Verifica se as cartas estão habilitadas para seleção
        if not self.cartas_habilitadas:
            messagebox.showinfo("Cartas não habilitadas", "Clique em 'Comprar Carta' ou 'Reservar Carta' para habilitar a seleção de cartas.")
            return
            
        # Verifica se há uma carta no índice selecionado
        if indiceCarta >= len(self.tabuleiro.cartasNoTabuleiro) or self.tabuleiro.cartasNoTabuleiro[indiceCarta] is None:
            self.notificarJogadaInvalida("Não há carta nesta posição!")
            return

        carta = self.tabuleiro.cartasNoTabuleiro[indiceCarta]
        self.cartaSelecionada = carta

        # Verifica se o jogador tem pedras suficientes apenas se não estiver no modo de reserva
        if not self.modo_reserva and not self.tabuleiro.verificarPedrasSuficientes(carta):
            self.notificarJogadaInvalida("Você não tem pedras suficientes para comprar esta carta!")
            self.cartaSelecionada = None
            return

        # Mostra mensagem de confirmação da seleção
        if self.modo_reserva:
            messagebox.showinfo("Carta Selecionada", f"Carta selecionada para reserva! Clique em 'Finalizar Jogada' para confirmar.")
        else:
            messagebox.showinfo("Carta Selecionada", f"Carta selecionada para compra! Clique em 'Finalizar Jogada' para confirmar.")

        self.habilitarBotaoFinalizarJogada()

    def reporTabuleiro(self, nivel: NiveisEnum):
        """Repõe uma carta no tabuleiro quando uma carta é removida"""
        try:
            # Verifica se o baralho existe
            if nivel.value - 1 >= len(self.tabuleiro.baralhos):
                print(f"ERRO: Baralho nível {nivel.value} não existe. Baralhos disponíveis: {len(self.tabuleiro.baralhos)}")
                return
            
            baralho = self.tabuleiro.baralhos[nivel.value - 1]
            
            # Se o baralho está vazio, não pode repor
            if len(baralho.cartas) == 0:
                return
            
            # Encontra a posição vazia no nível correspondente
            inicio_nivel = (nivel.value - 1) * 4
            fim_nivel = inicio_nivel + 4
                        
            # Verifica se o tabuleiro tem o tamanho correto
            if len(self.tabuleiro.cartasNoTabuleiro) < fim_nivel:
                return
            
            # Procura uma posição vazia no nível
            posicao_encontrada = False
            for i in range(inicio_nivel, fim_nivel):
                if self.tabuleiro.cartasNoTabuleiro[i] is None:
                    
                    # Tenta pegar cartas do baralho até encontrar uma que não seja de roubo
                    tentativas = 0
                    max_tentativas = min(10, len(baralho.cartas))
                    
                    while tentativas < max_tentativas and len(baralho.cartas) > 0:
                        nova_carta = baralho.pegarCartaDoBaralho()
                        if nova_carta is None:
                            break
                                                
                        # Se for carta de roubo, distribui para o jogador atual
                        if nova_carta.cartaDeRoubo:
                            self.tabuleiro.pegarJogadorLocal().adicionarCartaDeRoubo(nova_carta)
                            tentativas += 1
                            continue
                        else:
                            # Carta normal encontrada, coloca no tabuleiro
                            self.tabuleiro.cartasNoTabuleiro[i] = nova_carta
                            
                            # Carrega a imagem da carta para garantir que está disponível
                            self.get_carta_img(nova_carta)
                            
                            posicao_encontrada = True
                            break
                    
                    if posicao_encontrada:
                        break
                    else:
                        print(f"Não foi possível encontrar uma carta normal após {tentativas} tentativas")
                        break
                else:
                    print(f"Posição {i} não está vazia")
            
            if not posicao_encontrada:
                print("Nenhuma posição vazia encontrada para reposição ou não foi possível repor")
            
            
        except Exception as e:
            print(f"Erro ao repor tabuleiro: {e}")
            import traceback
            traceback.print_exc()

    def desenharCartasJogadores(self):
        """Desenha as cartas dos jogadores nas áreas específicas"""
        # Jogador local (embaixo, centralizado) - mostra cartas cortadas
        cartas_local = self.tabuleiro.pegarJogadorLocal().pegarCartas()
        if cartas_local:
            # Remove cartas de roubo da lista (elas são tratadas separadamente)
            cartas_normais = [c for c in cartas_local if not c.cartaDeRoubo]
            if cartas_normais:
                # Organiza em 3 colunas
                colunas = 3
                
                for i, carta in enumerate(cartas_normais):
                    coluna = i % colunas
                    linha = i // colunas
                    
                    # Posição centralizada na parte inferior, mas mais acima para dar espaço às cartas reservadas
                    x_base = self.WINDOW_WIDTH // 2
                    y_base = self.WINDOW_HEIGHT - 200  # Movido mais para cima para dar espaço às reservadas
                    
                    # Espaçamento entre colunas
                    x = x_base + (coluna - 1) * 80
                    y = y_base - linha * 30
                    
                    # Carrega a imagem da carta
                    img_tk = self.get_carta_img(carta)
                    if img_tk:
                        # Cria uma versão cortada da carta (mostra apenas a parte superior)
                        try:
                            # Encontra o arquivo da carta para recriar a imagem
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
                                        
                                        # Carrega a imagem e corta (mostra apenas a parte superior)
                                        pil_img = Image.open(carta_img).resize((self.CARD_WIDTH * 10, self.CARD_HEIGHT * 10), Image.Resampling.LANCZOS)
                                        # Corta apenas a parte superior da carta (primeiros 30% da altura)
                                        altura_corte = int(self.CARD_HEIGHT * 10 * 0.3)
                                        pil_img_cortada = pil_img.crop((0, 0, self.CARD_WIDTH * 10, altura_corte))
                                        img_tk_cortada = ImageTk.PhotoImage(pil_img_cortada)
                                        
                                        # Desenha a carta cortada
                                        self.canvas.create_image(
                                            x, y, 
                                            image=img_tk_cortada, 
                                            anchor='s',
                                            tags=f"carta_jogador_local_{i}"
                                        )
                                        break
                                else:
                                    continue
                                break
                        except Exception as e:
                            print(f"Erro ao criar carta cortada para jogador local: {e}")
                            # Fallback: mostra apenas os pontos
                            self.canvas.create_text(
                                x, y, 
                                text=str(carta.pontos), 
                                fill="white", 
                                font=("Arial", 16, "bold"),
                                tags=f"carta_jogador_local_{i}"
                            )

        # Jogador remoto (em cima, centralizado, invertido) - mostra cartas rotacionadas e cortadas
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
                    
                    # Carrega a imagem da carta
                    img_tk = self.get_carta_img(carta)
                    if img_tk:
                        # Cria uma versão rotacionada e cortada da carta
                        try:
                            # Encontra o arquivo da carta para recriar a imagem
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
                                        
                                        # Carrega a imagem, rotaciona 180° e corta
                                        pil_img = Image.open(carta_img).resize((self.CARD_WIDTH * 10, self.CARD_HEIGHT * 10), Image.Resampling.LANCZOS)
                                        pil_img = pil_img.transpose(Image.ROTATE_180)
                                        # Corta apenas a parte superior da carta rotacionada (primeiros 30% da altura)
                                        altura_corte = int(self.CARD_HEIGHT * 10 * 0.3)
                                        pil_img_cortada = pil_img.crop((0, 0, self.CARD_WIDTH * 10, altura_corte))
                                        img_tk_cortada = ImageTk.PhotoImage(pil_img_cortada)
                                        
                                        # Desenha a carta rotacionada e cortada
                                        self.canvas.create_image(
                                            x, y, 
                                            image=img_tk_cortada, 
                                            anchor='n',
                                            tags=f"carta_jogador_remoto_{i}"
                                        )
                                        break
                                else:
                                    continue
                                break
                        except Exception as e:
                            print(f"Erro ao criar carta rotacionada para jogador remoto: {e}")
                            # Fallback: mostra apenas os pontos
                            self.canvas.create_text(
                                x, y, 
                                text=str(carta.pontos), 
                                fill="white", 
                                font=("Arial", 16, "bold"),
                                tags=f"carta_jogador_remoto_{i}"
                            )

    def desenharCartasRouboJogador(self):
        """Desenha as cartas de roubo dos jogadores"""
        # Jogador local (embaixo) - apenas cartas de roubo que realmente pertencem ao jogador
        cartas_roubo_local = self.tabuleiro.pegarJogadorLocal().pegarCartas()
        cartas_roubo_local = [c for c in cartas_roubo_local if c.cartaDeRoubo]
        if cartas_roubo_local:
            for i, carta in enumerate(cartas_roubo_local):
                img_tk = self.get_carta_img(carta)
                if img_tk:
                    # Centralizado e cortado (exemplo: só metade da carta)
                    x = self.WINDOW_WIDTH // 2 + (i - len(cartas_roubo_local)//2) * (self.CARD_WIDTH*5)
                    y = self.WINDOW_HEIGHT - 250  # Movido mais para cima para dar espaço às reservadas
                    self.canvas.create_image(x, y, image=img_tk, anchor='s', tags=f"roubo_local_{i}")
                    
                    # Adiciona funcionalidade de clique para usar carta de roubo
                    self.canvas.tag_bind(f"roubo_local_{i}", "<Button-1>", lambda event, idx=i: self.clickCartaRoubo(idx))
                    self.configurar_cursor_clicavel(f"roubo_local_{i}")

        # Jogador remoto (em cima, invertido) - apenas cartas de roubo que realmente pertencem ao jogador
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
                                id_carta, pontos, pedras, cartaDeRoubo, bonus, habilitada = self.extrair_dados_carta(carta_img, None, True)
                                
                                # Compara as características da carta com o arquivo
                                if (carta.pontos == pontos and 
                                    carta.pedras == pedras and 
                                    carta.cartaDeRoubo == cartaDeRoubo and 
                                    carta.bonus == bonus):
                                    
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
                carta = self.tabuleiro.pegarCartaTabuleiro(idx)
                if carta is not None:
                    img_tk = self.get_carta_img(carta)
                    if img_tk:
                        x = deck_x + self.CARD_WIDTH + self.DECK_TO_CARDS_GAP + i * (self.CARD_WIDTH + self.HORIZONTAL_GAP)
                        self.canvas.create_image(x, y_pos, image=img_tk, anchor=NW, tags=f"carta_{nivel.name}_{idx}")
                        # Só habilita clique se for o turno do jogador E as cartas estiverem habilitadas
                        if self.tabuleiro.pegarJogadorLocal().jogadorEmTurno and self.cartas_habilitadas:
                            # Configura cursor para cartas clicáveis
                            self.configurar_cursor_clicavel(f"carta_{nivel.name}_{idx}")
                            self.canvas.tag_bind(f"carta_{nivel.name}_{idx}", "<Button-1>", lambda event, idx=idx: self.clickCarta(idx))

        self.tabuleiro.atualizarPedrasNoTabuleiro()
        self.desenharBotoes()
        self.desenharPedras()
        self.desenharInfosJogadores()
        self.desenharCartasJogadores()  # Adiciona o desenho das cartas dos jogadores
        self.desenharCartasRouboJogador()  # Adiciona o desenho das cartas de roubo dos jogadores
        self.desenharCartasReservadas()  # Adiciona o desenho das cartas reservadas
        self.desabilitarBotaoFinalizarJogada()
        self.desabilitarBotaoDesfazerJogada()

    def desenharBotoes(self):
        """Desenha os botões na tela com efeitos visuais"""
        h = 1080
        off = 200
        botoes_pos = {
            "comprar_pedras": (h, 100),
            "comprar_carta": (h, 200),
            "reservar_carta": (h, 300),
            "oferta_de_troca": (h, 400),
            "desfazer_jogada": (h, 500),  # Botão para desfazer jogada - abaixo dos outros
            "finalizar_jogada": (20, 50+off)  # Botão para finalizar jogada - mais à esquerda
        }
        
        for nome, img in self.botoes.items():
            if nome in botoes_pos:
                x, y = botoes_pos[nome]
                self.canvas.create_image(x, y, image=img, anchor=NW, tags=f"botao_{nome}")
                
                # Configura cursor e efeitos de clique
                self.configurar_cursor_clicavel(f"botao_{nome}")
                
                if nome == "comprar_pedras":
                    self.canvas.tag_bind(f"botao_{nome}", "<Button-1>", 
                                       lambda event: [self.aplicar_efeito_clique_botao("comprar_pedras"), self.clickComprarPedras()])
                elif nome == "comprar_carta":
                    self.canvas.tag_bind(f"botao_{nome}", "<Button-1>", 
                                       lambda event: [self.aplicar_efeito_clique_botao("comprar_carta"), self.clickComprarCarta()])
                elif nome == "reservar_carta":
                    self.canvas.tag_bind(f"botao_{nome}", "<Button-1>", 
                                       lambda event: [self.aplicar_efeito_clique_botao("reservar_carta"), self.clickReservarCarta()])
                elif nome == "oferta_de_troca":
                    self.canvas.tag_bind(f"botao_{nome}", "<Button-1>", 
                                       lambda event: [self.aplicar_efeito_clique_botao("oferta_de_troca"), self.clickOfertaDeTroca()])
                elif nome == "desfazer_jogada":
                    self.canvas.tag_bind(f"botao_{nome}", "<Button-1>", 
                                       lambda event: [self.aplicar_efeito_clique_botao("desfazer_jogada"), self.clickDesfazerJogada()])
                elif nome == "finalizar_jogada":
                    self.canvas.tag_bind(f"botao_{nome}", "<Button-1>", 
                                       lambda event: [self.aplicar_efeito_clique_botao("finalizar_jogada"), self.clickFinalizarJogada()])
        
        # Desenha o botão de settings no canto superior direito
        if "settings" in self.botoes:
            x_settings = self.WINDOW_WIDTH - 80  # 80 pixels da borda direita
            y_settings = 20  # 20 pixels do topo
            self.canvas.create_image(x_settings, y_settings, image=self.botoes["settings"], anchor=NW, tags="botao_settings")
            
            # Configura cursor e clique
            self.configurar_cursor_clicavel("botao_settings")
            self.canvas.tag_bind("botao_settings", "<Button-1>", 
                               lambda event: [self.aplicar_efeito_clique_botao("settings"), self.abrirMenuSettings()])

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
    
    def desabilitarBotaoDesfazerJogada(self):
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
            
            pil_img = Image.open("./resources/botoes/finalizar_jogada.png").resize((180, 90), Image.Resampling.LANCZOS).convert("RGBA")  # Ajustado para novo tamanho
            alpha = pil_img.split()[3]
            alpha = alpha.point(lambda p: int(p * 0.5))
            pil_img.putalpha(alpha)
            img = ImageTk.PhotoImage(pil_img)
            self.canvas.itemconfig("botao_finalizar_jogada", image=img)
            self.canvas.tag_unbind("botao_finalizar_jogada", "<Button-1>")
            self.botoes["finalizar_jogada_disabled"] = img

    # Métodos para habilitar/desabilitar cartas
    def habilitarCartas(self):
        """Habilita todas as cartas no tabuleiro e cartas reservadas com efeitos visuais"""
        self.cartas_habilitadas = True
        niveis = [NiveisEnum.NIVEL1, NiveisEnum.NIVEL2, NiveisEnum.NIVEL3]
        for nivel_idx, nivel in enumerate(niveis):
            for i in range(4):
                idx = nivel_idx * 4 + i
                carta = self.tabuleiro.cartasNoTabuleiro[idx]
                if carta is not None:
                    # Configura cursor para cartas clicáveis
                    self.configurar_cursor_clicavel(f"carta_{nivel.name}_{idx}")
                    
                    self.canvas.tag_bind(f"carta_{nivel.name}_{idx}", "<Button-1>", 
                                       lambda event, idx=idx: self.clickCarta(idx))
                    # Restaura a imagem normal da carta
                    img_tk = self.get_carta_img(carta)
                    if img_tk:
                        self.canvas.itemconfig(f"carta_{nivel.name}_{idx}", image=img_tk)
        
        # Habilita também as cartas reservadas se não estiver no modo de reserva
        if not self.modo_reserva:
            cartas_reservadas = self.tabuleiro.pegarJogadorLocal().pegarCartasReservadas()
            for i, carta in enumerate(cartas_reservadas):
                # Configura cursor para cartas reservadas clicáveis
                self.configurar_cursor_clicavel(f"carta_reservada_{i}")
                self.canvas.tag_bind(f"carta_reservada_{i}", "<Button-1>", 
                                   lambda event, idx=i: self.clickCartaReservada(idx))

    def desabilitarCartas(self):
        """Desabilita todas as cartas no tabuleiro e cartas reservadas, aplicando transparência quando não for o turno"""
        self.cartas_habilitadas = False
        if not hasattr(self, 'carta_imgs_transparentes'):
            self.carta_imgs_transparentes = {}
        niveis = [NiveisEnum.NIVEL1, NiveisEnum.NIVEL2, NiveisEnum.NIVEL3]
        for nivel_idx, nivel in enumerate(niveis):
            for i in range(4):
                idx = nivel_idx * 4 + i
                carta = self.tabuleiro.cartasNoTabuleiro[idx]
                if carta is not None:
                    # Remove cursor pointer e eventos de clique
                    self.canvas.tag_unbind(f"carta_{nivel.name}_{idx}", "<Button-1>")
                    self.canvas.tag_unbind(f"carta_{nivel.name}_{idx}", "<Enter>")
                    self.canvas.tag_unbind(f"carta_{nivel.name}_{idx}", "<Leave>")
                    
                    # Aplica transparência apenas se não for o turno do jogador
                    if not self.tabuleiro.pegarJogadorLocal().jogadorEmTurno:
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
        
        # Desabilita também as cartas reservadas
        cartas_reservadas = self.tabuleiro.pegarJogadorLocal().pegarCartasReservadas()
        for i, carta in enumerate(cartas_reservadas):
            # Remove cursor pointer e eventos de clique
            self.canvas.tag_unbind(f"carta_reservada_{i}", "<Button-1>")
            self.canvas.tag_unbind(f"carta_reservada_{i}", "<Enter>")
            self.canvas.tag_unbind(f"carta_reservada_{i}", "<Leave>")
            
            # Aplica transparência apenas se não for o turno do jogador
            if not self.tabuleiro.pegarJogadorLocal().jogadorEmTurno:
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
                                self.canvas.itemconfig(f"carta_reservada_{i}", image=img_transp)
                                break
                        else:
                            continue
                        break
                except Exception as e:
                    print(f"Erro ao aplicar transparência na carta reservada: {e}")
            else:
                # Se for o turno do jogador, garante que a imagem normal está sendo usada
                img_tk = self.get_carta_img(carta)
                if img_tk:
                    self.canvas.itemconfig(f"carta_reservada_{i}", image=img_tk)

    # Métodos para habilitar/desabilitar pedras
    def habilitarPedras(self):
        """Habilita todas as pedras no tabuleiro"""
        self.pedras_habilitadas = True
        for pedra in self.tabuleiro.pedrasNoTabuleiro.keys():
            self.canvas.tag_bind(f"pedra_{pedra.name}", "<Button-1>", lambda event, pedra=pedra: self.clickPedra(pedra))
            # Restaura a imagem normal da pedra
            if pedra in self.pedras:
                self.canvas.itemconfig(f"pedra_{pedra.name}", image=self.pedras[pedra])
            else:
                # Se a imagem original não está disponível, recarrega
                try:
                    caminho = f"./resources/pedras/{pedra.name.lower()}.png"
                    img = Image.open(caminho).resize((self.GEM_SIZE, self.GEM_SIZE), Image.Resampling.LANCZOS)
                    img_tk = ImageTk.PhotoImage(img)
                    self.pedras[pedra] = img_tk
                    self.canvas.itemconfig(f"pedra_{pedra.name}", image=img_tk)
                except Exception as e:
                    print(f"Erro ao recarregar imagem da pedra {pedra.name}: {e}")

    def desabilitarPedras(self):
        """Desabilita todas as pedras no tabuleiro, aplicando transparência quando não for o turno"""
        self.pedras_habilitadas = False
        from model.enums.pedrasEnum import PedrasEnum
        
        # Remove efeitos visuais de seleção
        for pedra in self.pedras_selecionadas_visuais:
            self.remover_efeito_selecao_pedra(pedra)
        self.pedras_selecionadas_visuais.clear()
        
        # Cria dicionário para imagens transparentes se não existir
        if not hasattr(self, 'pedras_transparentes'):
            self.pedras_transparentes = {}
        
        for pedra in self.tabuleiro.pedrasNoTabuleiro.keys():
            self.canvas.tag_unbind(f"pedra_{pedra.name}", "<Button-1>")
            # Remove cursor pointer
            self.canvas.tag_unbind(f"pedra_{pedra.name}", "<Enter>")
            self.canvas.tag_unbind(f"pedra_{pedra.name}", "<Leave>")
            
            # Aplica transparência apenas se não for o turno do jogador
            if not self.tabuleiro.pegarJogadorLocal().jogadorEmTurno:
                caminho = f"./resources/pedras/{pedra.name.lower()}.png"
                try:
                    pil_img = Image.open(caminho).resize((self.GEM_SIZE, self.GEM_SIZE), Image.Resampling.LANCZOS).convert("RGBA")
                    alpha = pil_img.split()[3]
                    alpha = alpha.point(lambda p: int(p * 0.5))
                    pil_img.putalpha(alpha)
                    img_transp = ImageTk.PhotoImage(pil_img)
                    self.canvas.itemconfig(f"pedra_{pedra.name}", image=img_transp)
                    # Mantém referência para não ser coletado (em dicionário separado)
                    self.pedras_transparentes[pedra] = img_transp
                except Exception as e:
                    print(f"Erro ao aplicar transparência na pedra {pedra.name}: {e}")
            else:
                # Se for o turno do jogador, garante que a imagem normal está sendo usada
                if pedra in self.pedras:
                    self.canvas.itemconfig(f"pedra_{pedra.name}", image=self.pedras[pedra])

    def avaliarVencedor(self):
        pontos1 = self.tabuleiro.pegarJogadorLocal().pegarPontuacaoJogador()
        pontos2 = self.tabuleiro.jogadorRemoto.pegarPontuacaoJogador()

        # Verifica se pelo menos um jogador atingiu a pontuação mínima
        if pontos1 >= PONTOS_MINIMOS_VITORIA or pontos2 >= PONTOS_MINIMOS_VITORIA:
            if pontos1 > pontos2:
                vencedor = self.tabuleiro.pegarNomeJogador()
                self.tabuleiro.pegarJogadorLocal().marcarVitoria()
                self.notificarVencedor(vencedor)
            elif pontos2 > pontos1:
                vencedor = self.tabuleiro.jogadorRemoto.pegarNome()
                self.tabuleiro.jogadorRemoto.marcarVitoria()
                self.notificarVencedor(vencedor)
            else:
                self.tabuleiro.pegarJogadorLocal().marcarEmpate()
                self.tabuleiro.jogadorRemoto.marcarEmpate()
                self.notificarEmpate()
        else:
            # Nenhum jogador atingiu a pontuação mínima ainda
            print("Nenhum jogador atingiu a pontuação mínima para vitória.")
            return
        
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
        if pontos >= PONTOS_MINIMOS_VITORIA:
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
                
                # Só habilita clique se for o turno do jogador, as pedras estiverem habilitadas E não for ouro
                if (self.tabuleiro.pegarJogadorLocal().jogadorEmTurno and 
                    self.pedras_habilitadas and 
                    pedra != PedrasEnum.OURO):  # Ouro nunca pode ser comprado diretamente
                    
                    # Configura cursor para pedras clicáveis
                    self.configurar_cursor_clicavel(f"pedra_{pedra.name}")
                    
                    self.canvas.tag_bind(f"pedra_{pedra.name}", "<Button-1>", 
                                       lambda event, pedra=pedra: self.clickPedra(pedra))
                
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
            img_local = Image.open("./resources/extra/sombra_inferior_esquerda.png").resize((self.PLAYER_INFO_WIDTH, 150), Image.Resampling.LANCZOS)  # Aumentado de 120 para 150
            self.bg_jogador_local = ImageTk.PhotoImage(img_local)
            img_remoto = Image.open("./resources/extra/sombra_superior_esquerda.png").resize((self.PLAYER_INFO_WIDTH, 150), Image.Resampling.LANCZOS)  # Aumentado de 120 para 150
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
        sombra_altura = 150  # Aumentado de 120 para 150
        y_nome = y_base_local - sombra_altura + 10  # Movido para cima (era 15)
        y_pontos = y_nome + 25
        y_pedra = y_pontos + 30

        jogador_local = self.tabuleiro.pegarJogadorLocal()
        self.canvas.create_text(
            self.PLAYER_INFO_X + 15,
            y_nome,
            text=f"{jogador_local.pegarNome()} {'(Em Turno)' if jogador_local.jogadorEmTurno else ''}",
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
        y_nome_r = y_base_remoto + 10  # Movido para cima (era 15)
        y_pontos_r = y_nome_r + 25
        y_pedra_r = y_pontos_r + 30

        jogador_remoto = self.tabuleiro.jogadorRemoto
        self.canvas.create_text(
            self.PLAYER_INFO_X + 15,
            y_nome_r,
            text=f"{jogador_remoto.pegarNome()} {'(Em Turno)' if jogador_remoto.jogadorEmTurno else ''}",
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
        cartas_reservadas = self.tabuleiro.pegarJogadorLocal().pegarCartasReservadas()
        if 0 <= indice_carta_reservada < len(cartas_reservadas):
            carta = cartas_reservadas[indice_carta_reservada]
            
            # Verifica se tem pedras suficientes
            if self.tabuleiro.verificarPedrasSuficientes(carta):
                # Remove pedras do jogador, usando ouro como coringa se necessário
                pedras_carta = carta.pegarPedrasDaCarta()
                pedras_jogador = self.tabuleiro.pegarJogadorLocal().pegarPedras()
                
                # Calcula quantas pedras de ouro serão usadas
                ouro_usado = 0
                
                for pedra, quantidade_necessaria in pedras_carta.items():
                    pedras_disponiveis = pedras_jogador.get(pedra, 0)
                    
                    if pedras_disponiveis < quantidade_necessaria:
                        # Precisa usar ouro como coringa
                        ouro_necessario = quantidade_necessaria - pedras_disponiveis
                        ouro_usado += ouro_necessario
                        
                        # Remove as pedras disponíveis do tipo específico
                        self.tabuleiro.pegarJogadorLocal().removerPedras({pedra: pedras_disponiveis})
                    else:
                        # Remove todas as pedras necessárias do tipo específico
                        self.tabuleiro.pegarJogadorLocal().removerPedras({pedra: quantidade_necessaria})
                
                # Remove as pedras de ouro usadas como coringa
                if ouro_usado > 0:
                    self.tabuleiro.pegarJogadorLocal().removerPedras({PedrasEnum.OURO: ouro_usado})
                
                # Remove da reserva e adiciona à mão
                self.tabuleiro.pegarJogadorLocal().cartasReservadas.pop(indice_carta_reservada)
                self.tabuleiro.pegarJogadorLocal().adicionarCarta(carta)
                
                # Adiciona pontos e bônus
                pontos = carta.pegarPontos()
                if pontos > 0:
                    self.tabuleiro.pegarJogadorLocal().adicionarPontos(pontos)
                
                if carta.temBonus():
                    bonus = carta.pegarBonus()
                    self.tabuleiro.pegarJogadorLocal().adicionarBonus(bonus)
                
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
        
        # Verifica se já tem 3 cartas reservadas (limite máximo)
        cartas_reservadas = self.tabuleiro.pegarJogadorLocal().pegarCartasReservadas()
        if len(cartas_reservadas) >= 3:
            self.notificarJogadaInvalida("Você já tem 3 cartas reservadas. Não pode reservar mais cartas.")
            return
        
        # Verifica se há cartas disponíveis no baralho para repor
        nivel = self.cartaSelecionada.pegarNivel()
        baralho = self.tabuleiro.baralhos[nivel.value - 1]
        
        # Adiciona carta à reserva do jogador
        if self.tabuleiro.pegarJogadorLocal().reservarCarta(self.cartaSelecionada):
            # Remove a carta do tabuleiro
            try:
                indice = self.tabuleiro.cartasNoTabuleiro.index(self.cartaSelecionada)
                self.tabuleiro.cartasNoTabuleiro[indice] = None
                
                # Repõe imediatamente uma nova carta do mesmo nível (se houver cartas disponíveis)
                if len(baralho.cartas) > 0:
                    self.reporTabuleiro(nivel)
                    
                else:
                    print(f"Não é possível repor carta - baralho nível {nivel.value} está vazio")
                
                # Adiciona uma pedra de ouro se disponível
                if self.tabuleiro.pedrasNoTabuleiro[PedrasEnum.OURO] > 0:
                    self.tabuleiro.pegarJogadorLocal().adicionarPedraNaMao(PedrasEnum.OURO, 1)
                    self.tabuleiro.pedrasNoTabuleiro[PedrasEnum.OURO] -= 1
                    messagebox.showinfo("Pedra de Ouro", "Você recebeu uma pedra de ouro por reservar a carta!")
                
                self.cartaSelecionada = None
                self.desenharTabuleiro()
            except ValueError as e:
                print(f"Erro ao encontrar carta no tabuleiro: {e}")
                self.notificarJogadaInvalida("Erro ao reservar carta: carta não encontrada no tabuleiro.")
                return
        else:
            print("Falha ao adicionar carta à reserva")
            self.notificarJogadaInvalida("Não foi possível reservar esta carta.")
            return

    def realizarCompraCarta(self):
        """Executa a compra da carta selecionada"""
        if self.cartaSelecionada is None:
            return
        
        # Remove pedras do jogador, usando ouro como coringa se necessário
        pedras_carta = self.cartaSelecionada.pegarPedrasDaCarta()
        pedras_jogador = self.tabuleiro.pegarJogadorLocal().pegarPedras()
        
        # Calcula quantas pedras de ouro serão usadas
        ouro_usado = 0
        
        for pedra, quantidade_necessaria in pedras_carta.items():
            pedras_disponiveis = pedras_jogador.get(pedra, 0)
            
            if pedras_disponiveis < quantidade_necessaria:
                # Precisa usar ouro como coringa
                ouro_necessario = quantidade_necessaria - pedras_disponiveis
                ouro_usado += ouro_necessario
                
                # Remove as pedras disponíveis do tipo específico
                self.tabuleiro.pegarJogadorLocal().removerPedras({pedra: pedras_disponiveis})
            else:
                # Remove todas as pedras necessárias do tipo específico
                self.tabuleiro.pegarJogadorLocal().removerPedras({pedra: quantidade_necessaria})
        
        # Remove as pedras de ouro usadas como coringa
        if ouro_usado > 0:
            self.tabuleiro.pegarJogadorLocal().removerPedras({PedrasEnum.OURO: ouro_usado})
        
        # Adiciona carta ao jogador
        self.tabuleiro.pegarJogadorLocal().adicionarCarta(self.cartaSelecionada)
        
        # Adiciona pontos e bônus
        pontos = self.cartaSelecionada.pegarPontos()
        if pontos > 0:
            self.tabuleiro.pegarJogadorLocal().adicionarPontos(pontos)
        
        if self.cartaSelecionada.temBonus():
            bonus = self.cartaSelecionada.pegarBonus()
            self.tabuleiro.pegarJogadorLocal().adicionarBonus(bonus)
        
        # Remove e repõe a carta no tabuleiro
        nivel = self.cartaSelecionada.pegarNivel()
        try:
            indice = self.tabuleiro.cartasNoTabuleiro.index(self.cartaSelecionada)
            self.tabuleiro.cartasNoTabuleiro[indice] = None
            
            # Verifica se há cartas disponíveis no baralho para repor
            baralho = self.tabuleiro.baralhos[nivel.value - 1]
            if len(baralho.cartas) > 0:
                # Repõe imediatamente uma nova carta do mesmo nível
                self.reporTabuleiro(nivel)
                
            else:
                print(f"Não é possível repor carta - baralho nível {nivel.value} está vazio")
            
        except ValueError as e:
            print(f"Erro ao encontrar carta no tabuleiro: {e}")
            self.notificarJogadaInvalida("Erro ao comprar carta: carta não encontrada no tabuleiro.")
            return
        
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
            self.tabuleiro.pegarJogadorLocal().adicionarPedraNaMao(pedra, 1)
        
        self.desenharTabuleiro()

    def clickFinalizarJogada(self):
        if len(self.pedrasSelecionadas) >= 2:
            self.realizarCompraPedras()

        if self.cartaSelecionada and len(self.pedrasSelecionadas)==0:
            # Verifica se é uma carta reservada ou do tabuleiro
            cartas_reservadas = self.tabuleiro.pegarJogadorLocal().pegarCartasReservadas()
            if self.cartaSelecionada in cartas_reservadas:
                # Compra carta reservada
                self.comprarCartaReservada(cartas_reservadas.index(self.cartaSelecionada))
            else:
                # Verifica se está no modo de compra ou reserva
                if hasattr(self, 'modo_reserva') and self.modo_reserva:
                    self.realizarReservaCarta()
                else:
                    self.realizarCompraCarta()
        
        # Verifica se algum jogador atingiu 15 pontos ou mais
        pontos_local = self.tabuleiro.pegarJogadorLocal().pegarPontuacaoJogador()
        pontos_remoto = self.tabuleiro.jogadorRemoto.pegarPontuacaoJogador()
        
        # Verifica se é necessário habilitar última partida
        if pontos_local >= PONTOS_MINIMOS_VITORIA or pontos_remoto >= PONTOS_MINIMOS_VITORIA:
            if not self.tabuleiro.ehUltimaPartida():
                # Primeira vez que alguém atingiu 15 pontos - habilita última partida
                self.tabuleiro.habilitarUltimaPartida()
                
                # Determina qual jogador atingiu 15 pontos primeiro
                if pontos_local >= PONTOS_MINIMOS_VITORIA and pontos_remoto < PONTOS_MINIMOS_VITORIA:
                    messagebox.showinfo("Última Chance!", 
                                      f"Você atingiu {pontos_local} pontos! O oponente tem uma última chance de tentar superar sua pontuação.")
                elif pontos_remoto >= PONTOS_MINIMOS_VITORIA and pontos_local < PONTOS_MINIMOS_VITORIA:
                    messagebox.showinfo("Última Chance!", 
                                      f"O oponente atingiu {pontos_remoto} pontos! Você tem uma última chance de tentar superar a pontuação dele.")
                else:
                    # Ambos atingiram 15 pontos simultaneamente
                    messagebox.showinfo("Última Chance!", 
                                      f"Ambos os jogadores atingiram {min(pontos_local, pontos_remoto)} pontos! Esta é a última rodada para definir o vencedor.")
        
        # Se já está na última partida, avalia o vencedor
        if self.tabuleiro.ehUltimaPartida():
            self.avaliarVencedor()
            # Envia o tabuleiro com status 'finished' para o adversário
            self.finalizar_jogada_callback(self.tabuleiro, status='finished')
            return  # Retorna sem trocar turno, pois o jogo acabou

        self.pedrasSelecionadas = list()
        self.cartaSelecionada = None
        self.modo_reserva = False  # Reseta o modo de reserva
        
        # Troca o turno entre os jogadores
        self.tabuleiro.pegarJogadorLocal().jogadorEmTurno = False
        self.tabuleiro.jogadorRemoto.jogadorEmTurno = True
        
        # Desabilita jogadas do jogador local
        self.desabilitarJogadas()
        
        self.atualizarTabuleiro(self.tabuleiro)
        self.finalizar_jogada_callback(self.tabuleiro, status='next')

    def desenharCartasReservadas(self):
        """Desenha as cartas reservadas do jogador local na área específica"""
        cartas_reservadas = self.tabuleiro.pegarJogadorLocal().pegarCartasReservadas()
        
        if cartas_reservadas:
            # Label "Reservadas" - posicionado muito abaixo, fora da tela visível
            self.canvas.create_text(
                self.WINDOW_WIDTH // 2,
                self.WINDOW_HEIGHT + 30,  # Fora da tela visível
                text="CARTAS RESERVADAS",
                fill="white",
                font=("Arial", 12, "bold"),
                anchor="n"
            )
            
            # Organiza em linha horizontal com espaçamento maior
            for i, carta in enumerate(cartas_reservadas):
                
                # Posição centralizada muito abaixo da tela, para que sejam cortadas
                x_base = self.WINDOW_WIDTH // 2
                y_base = self.WINDOW_HEIGHT + 80  # Muito abaixo da tela visível
                
                # Espaçamento maior entre cartas (120 pixels)
                x = x_base + (i - len(cartas_reservadas)//2) * 120
                y = y_base
                
                # Carrega a imagem da carta
                img_tk = self.get_carta_img(carta)
                if img_tk:
                    # Desenha a carta completa (será cortada pela borda da tela)
                    self.canvas.create_image(
                        x, y, 
                        image=img_tk, 
                        anchor='s',
                        tags=f"carta_reservada_{i}"
                    )
                    
                    # Adiciona clique para comprar carta reservada (só quando estiver no modo de compra)
                    if self.cartas_habilitadas and not self.modo_reserva:
                        # Configura cursor para cartas reservadas clicáveis
                        self.canvas.tag_bind(f"carta_reservada_{i}", "<Enter>", 
                                           lambda e, idx=i, x_pos=x, y_pos=y: self.hover_carta_reservada(idx, x_pos, y_pos, True))
                        self.canvas.tag_bind(f"carta_reservada_{i}", "<Leave>", 
                                           lambda e, idx=i, x_pos=x, y_pos=y: self.hover_carta_reservada(idx, x_pos, y_pos, False))
                        self.canvas.tag_bind(f"carta_reservada_{i}", "<Button-1>", lambda event, idx=i: self.clickCartaReservada(idx))
                    else:
                        # Se não está habilitada, só adiciona o efeito de hover
                        self.canvas.tag_bind(f"carta_reservada_{i}", "<Enter>", 
                                           lambda e, idx=i, x_pos=x, y_pos=y: self.hover_carta_reservada(idx, x_pos, y_pos, True))
                        self.canvas.tag_bind(f"carta_reservada_{i}", "<Leave>", 
                                           lambda e, idx=i, x_pos=x, y_pos=y: self.hover_carta_reservada(idx, x_pos, y_pos, False))
                    
                else:
                    # Fallback: mostra apenas os pontos
                    self.canvas.create_text(
                        x, y, 
                        text=str(carta.pontos), 
                        fill="white", 
                        font=("Arial", 16, "bold"),
                        tags=f"carta_reservada_{i}"
                    )
        else:
            print("Nenhuma carta reservada para desenhar")

    def hover_carta_reservada(self, idx, x_pos, y_pos, entrar):
        """Efeito de hover para cartas reservadas - faz a carta subir ou descer"""
        if entrar:
            # Move a carta para cima quando o mouse entra
            nova_y = y_pos - 50  # Move 50 pixels para cima
            self.canvas.moveto(f"carta_reservada_{idx}", x_pos, nova_y)
            # Configura cursor de mão
            self.canvas.configure(cursor="hand2")
        else:
            # Move a carta de volta para a posição original quando o mouse sai
            self.canvas.moveto(f"carta_reservada_{idx}", x_pos, y_pos)
            # Restaura cursor normal
            self.canvas.configure(cursor="arrow")

    def clickCartaReservada(self, indice_carta_reservada: int):
        """Método chamado quando uma carta reservada é clicada"""
        cartas_reservadas = self.tabuleiro.pegarJogadorLocal().pegarCartasReservadas()
        if 0 <= indice_carta_reservada < len(cartas_reservadas):
            carta = cartas_reservadas[indice_carta_reservada]
            
            # Verifica se tem pedras suficientes
            if self.tabuleiro.verificarPedrasSuficientes(carta):
                self.cartaSelecionada = carta
                messagebox.showinfo("Carta Reservada Selecionada", f"Carta reservada selecionada para compra! Clique em 'Finalizar Jogada' para confirmar.")
                self.habilitarBotaoFinalizarJogada()
            else:
                self.notificarJogadaInvalida("Você não tem pedras suficientes para comprar esta carta reservada.")
        else:
            self.notificarJogadaInvalida("Carta reservada não encontrada.")

    def criar_efeito_clique(self, img_original, tipo="botao"):
        """Cria uma versão com efeito de clique (mais escura)"""
        try:
            if isinstance(img_original, ImageTk.PhotoImage):
                # Converte de volta para PIL para aplicar efeito
                pil_img = Image.open(f"./resources/botoes/{tipo}.png").resize((150, 100), Image.Resampling.LANCZOS)
            else:
                pil_img = img_original.copy()
            
            # Aplica um efeito de escurecimento (multiplica por 0.7)
            pil_img = pil_img.convert("RGBA")
            data = pil_img.getdata()
            new_data = []
            for item in data:
                new_data.append((int(item[0] * 0.7), int(item[1] * 0.7), int(item[2] * 0.7), item[3]))
            pil_img.putdata(new_data)
            
            return ImageTk.PhotoImage(pil_img)
        except Exception as e:
            print(f"Erro ao criar efeito de clique: {e}")
            return img_original

    def aplicar_efeito_selecao_pedra(self, pedra_enum):
        """Aplica efeito visual de seleção na pedra"""
        if pedra_enum in self.pedras:
            try:
                # Carrega a imagem original da pedra
                img_path = f"./resources/pedras/{pedra_enum.name.lower()}.png"
                pil_img = Image.open(img_path).resize((self.GEM_SIZE, self.GEM_SIZE), Image.Resampling.LANCZOS)
                
                # Aplica um efeito de brilho (aumenta o brilho)
                pil_img = pil_img.convert("RGBA")
                data = pil_img.getdata()
                new_data = []
                for item in data:
                    r, g, b, a = item
                    # Aumenta o brilho em 30%
                    r = min(255, int(r * 1.3))
                    g = min(255, int(g * 1.3))
                    b = min(255, int(b * 1.3))
                    new_data.append((r, g, b, a))
                pil_img.putdata(new_data)
                
                # Adiciona uma borda dourada
                from PIL import ImageDraw
                draw = ImageDraw.Draw(pil_img)
                draw.rectangle([0, 0, self.GEM_SIZE-1, self.GEM_SIZE-1], outline=(255, 215, 0, 255), width=3)
                
                img_selecionada = ImageTk.PhotoImage(pil_img)
                self.efeitos_clique[f"pedra_selecionada_{pedra_enum.name}"] = img_selecionada
                
                # Atualiza a imagem no canvas
                self.canvas.itemconfig(f"pedra_{pedra_enum.name}", image=img_selecionada)
                
            except Exception as e:
                print(f"Erro ao aplicar efeito de seleção na pedra {pedra_enum.name}: {e}")

    def remover_efeito_selecao_pedra(self, pedra_enum):
        """Remove o efeito visual de seleção da pedra"""
        if pedra_enum in self.pedras:
            # Restaura a imagem original
            self.canvas.itemconfig(f"pedra_{pedra_enum.name}", image=self.pedras[pedra_enum])

    def aplicar_efeito_clique_botao(self, nome_botao):
        """Aplica efeito de clique no botão"""
        if nome_botao in self.botoes:
            try:
                # Cria versão com efeito de clique
                img_clique = self.criar_efeito_clique(self.botoes[nome_botao], nome_botao)
                self.efeitos_clique[f"botao_clique_{nome_botao}"] = img_clique
                
                # Aplica o efeito
                self.canvas.itemconfig(f"botao_{nome_botao}", image=img_clique)
                
                # Remove o efeito após 100ms
                self.root.after(100, lambda: self.remover_efeito_clique_botao(nome_botao))
                
            except Exception as e:
                print(f"Erro ao aplicar efeito de clique no botão {nome_botao}: {e}")

    def remover_efeito_clique_botao(self, nome_botao):
        """Remove o efeito de clique do botão"""
        if nome_botao in self.botoes:
            self.canvas.itemconfig(f"botao_{nome_botao}", image=self.botoes[nome_botao])

    def configurar_cursor_clicavel(self, tag, cursor="hand2"):
        """Configura o cursor para elementos clicáveis"""
        # Não configura o cursor para cartas reservadas pois elas já têm efeito de hover
        if not tag.startswith("carta_reservada_"):
            self.canvas.tag_bind(tag, "<Enter>", lambda e: self.canvas.configure(cursor=cursor))
            self.canvas.tag_bind(tag, "<Leave>", lambda e: self.canvas.configure(cursor="arrow"))

    def abrirMenuSettings(self):
        """Abre o menu de configurações"""
        # Cria uma janela de popup para o menu
        self.menu_settings = Toplevel(self.root)
        self.menu_settings.title("Menu")
        self.menu_settings.geometry("600x500")
        self.menu_settings.resizable(False, False)
        self.menu_settings.configure(bg='#352314')  # Mesma cor de fundo do jogo
        self.menu_settings.transient(self.root)
        
        # Centraliza a janela
        self.menu_settings.update_idletasks()
        x = (self.menu_settings.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.menu_settings.winfo_screenheight() // 2) - (500 // 2)
        self.menu_settings.geometry(f"600x500+{x}+{y}")
        
        # Frame principal
        main_frame = Frame(self.menu_settings, bg='#352314')
        main_frame.pack(fill=BOTH, expand=True, padx=40, pady=40)
        
        # Título
        Label(main_frame, text="MENU", 
              font=("Arial", 28, "bold"), 
              bg='#352314', fg='white').pack(pady=(0, 50))
        
        # Botão de voltar no canto superior esquerdo
        if "botao-voltar" in self.botoes:
            btn_voltar = Button(main_frame, 
                              image=self.botoes["botao-voltar"],
                              command=lambda: self.menu_settings.destroy(),
                              relief=FLAT, 
                              bg='#352314', 
                              bd=0,
                              highlightthickness=0,
                              activebackground='#352314')
            btn_voltar.place(x=0, y=0)  # Posiciona no canto superior esquerdo
            btn_voltar.bind("<Enter>", lambda e: self.menu_settings.configure(cursor="hand2"))
            btn_voltar.bind("<Leave>", lambda e: self.menu_settings.configure(cursor="arrow"))
        
        # Botões do menu com height ajustado para usar as mesmas medidas dos botões do jogo
        botoes_menu = [
            ("regras", "Regras", self.abrirRegras),
            ("creditos", "Créditos", self.abrirCreditos),
            ("sair", "Sair", self.sairJogo)
        ]
        
        for i, (nome_botao, texto, comando) in enumerate(botoes_menu):
            if nome_botao in self.botoes:
                # Frame para cada botão
                frame_botao = Frame(main_frame, bg='#352314')
                frame_botao.pack(pady=15)
                
                # Redimensiona os botões para usar as mesmas medidas dos botões do jogo
                if nome_botao == "sair":
                    # Botão sair usa o mesmo tamanho do botão "finalizar jogada" (180x90)
                    try:
                        img_original = Image.open(f"./resources/botoes/{nome_botao}.png")
                        img_redimensionada = img_original.resize((180, 90), Image.Resampling.LANCZOS)
                        img_tk = ImageTk.PhotoImage(img_redimensionada)
                    except Exception as e:
                        print(f"Erro ao redimensionar botão {nome_botao}: {e}")
                        img_tk = self.botoes[nome_botao]
                else:
                    # Botões regras e creditos usam o mesmo tamanho do botão "desfazer jogada" (150x80)
                    try:
                        img_original = Image.open(f"./resources/botoes/{nome_botao}.png")
                        img_redimensionada = img_original.resize((150, 80), Image.Resampling.LANCZOS)
                        img_tk = ImageTk.PhotoImage(img_redimensionada)
                    except Exception as e:
                        print(f"Erro ao redimensionar botão {nome_botao}: {e}")
                        img_tk = self.botoes[nome_botao]
                
                # Botão com imagem
                btn = Button(frame_botao, 
                           image=img_tk,
                           command=lambda cmd=comando: [self.menu_settings.destroy(), cmd()],
                           relief=FLAT, 
                           bg='#352314', 
                           bd=0,
                           highlightthickness=0,
                           activebackground='#352314')
                btn.image = img_tk  # Mantém referência
                btn.pack()
                
                # Efeitos de hover
                btn.bind("<Enter>", lambda e, b=btn: self.menu_settings.configure(cursor="hand2"))
                btn.bind("<Leave>", lambda e, b=btn: self.menu_settings.configure(cursor="arrow"))
        
        # Configura o popup
        self.menu_settings.focus_set()
        try:
            self.menu_settings.grab_set()
        except Exception as e:
            print(f"Erro ao definir grab do popup: {e}")

    def abrirRegras(self):
        """Abre a tela de regras"""
        # Destroi o frame atual da tela de jogo temporariamente
        self.canvas.pack_forget()
        
        # Cria a tela de regras com destino de volta para jogo
        from view.tela_regras import TelaRegras
        self.tela_regras_temp = TelaRegras(self.root, self.voltarParaJogo, "jogo")
        
        # Guarda referência para poder destruir depois
        self.tela_atual_temp = self.tela_regras_temp

    def abrirCreditos(self):
        """Abre a tela de créditos"""
        # Destroi o frame atual da tela de jogo temporariamente
        self.canvas.pack_forget()
        
        # Cria a tela de créditos com destino de volta para jogo
        from view.tela_creditos import TelaCreditos
        self.tela_creditos_temp = TelaCreditos(self.root, self.voltarParaJogo, "jogo")
        
        # Guarda referência para poder destruir depois
        self.tela_atual_temp = self.tela_creditos_temp

    def voltarParaJogo(self, destino):
        """Volta para a tela do jogo"""
        # Destroi a tela temporária
        if hasattr(self, 'tela_atual_temp'):
            if hasattr(self.tela_atual_temp, 'frame'):
                self.tela_atual_temp.frame.destroy()
            delattr(self, 'tela_atual_temp')
        
        # Restaura o canvas do jogo
        self.canvas.pack(expand=True, fill='both')
        
        # Redesenha o tabuleiro para garantir que está atualizado
        self.desenharTabuleiro()

    def sairJogo(self):
        """Sai do jogo e retorna à tela inicial"""
        # Confirma se o jogador quer realmente sair
        resposta = messagebox.askyesno("Sair do Jogo", 
                                      "Tem certeza que deseja sair? A partida será abandonada.")
        if resposta:
            self.show_screen("inicial")

    def clickCartaRoubo(self, indice_carta_roubo: int):
        """Método chamado quando uma carta de roubo é clicada"""
        cartas_roubo = self.tabuleiro.pegarJogadorLocal().pegarCartas()
        cartas_roubo = [c for c in cartas_roubo if c.cartaDeRoubo]
        
        if 0 <= indice_carta_roubo < len(cartas_roubo):
            carta_roubo = cartas_roubo[indice_carta_roubo]
            
            # Verifica se o adversário tem alguma das pedras que podem ser roubadas
            pedras_roubo = carta_roubo.pegarPedrasDaCarta()
            pedras_adversario = self.tabuleiro.jogadorRemoto.pegarPedras()
            
            pedras_disponiveis = []
            for pedra in pedras_roubo.keys():
                if pedras_adversario.get(pedra, 0) > 0:
                    pedras_disponiveis.append(pedra)
            
            if not pedras_disponiveis:
                messagebox.showinfo("Carta de Roubo", "O adversário não tem nenhuma das pedras que podem ser roubadas com esta carta.")
                return
            
            # Mostra confirmação para usar a carta de roubo
            pedras_texto = ", ".join([pedra.name for pedra in pedras_disponiveis])
            resposta = messagebox.askyesno("Usar Carta de Roubo", 
                                         f"Tem certeza que deseja usar esta carta de roubo?\n\n"
                                         f"Você pode roubar uma das seguintes pedras do adversário:\n{pedras_texto}")
            
            if resposta:
                self.usarCartaRoubo(carta_roubo, pedras_disponiveis)
        else:
            messagebox.showerror("Erro", "Carta de roubo não encontrada.")

    def usarCartaRoubo(self, carta_roubo, pedras_disponiveis):
        """Executa o roubo de pedra usando a carta de roubo"""
        # Se há apenas uma pedra disponível, rouba ela automaticamente
        if len(pedras_disponiveis) == 1:
            pedra_roubada = pedras_disponiveis[0]
        else:
            # Se há múltiplas pedras, deixa o jogador escolher
            pedra_roubada = self.escolherPedraParaRoubar(pedras_disponiveis)
            if pedra_roubada is None:
                return  # Usuário cancelou
        
        # Executa o roubo
        # Remove a pedra do adversário
        self.tabuleiro.jogadorRemoto.removerPedras({pedra_roubada: 1})
        # Adiciona a pedra ao jogador local
        self.tabuleiro.pegarJogadorLocal().adicionarPedraNaMao(pedra_roubada, 1)
        
        # Remove a carta de roubo do jogador
        cartas_jogador = self.tabuleiro.pegarJogadorLocal().pegarCartas()
        for i, carta in enumerate(cartas_jogador):
            if carta.id == carta_roubo.id:
                self.tabuleiro.pegarJogadorLocal().cartas.pop(i)
                break
        
        messagebox.showinfo("Roubo Realizado", f"Você roubou uma pedra {pedra_roubada.name} do adversário!")
        
        # Atualiza o tabuleiro
        self.desenharTabuleiro()

    def escolherPedraParaRoubar(self, pedras_disponiveis):
        """Permite ao jogador escolher qual pedra roubar"""
        popup = Toplevel(self.root)
        popup.title("Escolher Pedra para Roubar")
        popup.geometry("400x300")
        popup.resizable(False, False)
        popup.transient(self.root)
        
        # Frame principal
        main_frame = Frame(popup, bg="white")
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Título
        Label(main_frame, text="Escolha qual pedra roubar:", 
              font=("Arial", 16, "bold"), bg="white").pack(pady=(0, 20))
        
        pedra_escolhida = [None]  # Lista para armazenar a escolha
        
        # Botões para cada pedra disponível
        for pedra in pedras_disponiveis:
            try:
                # Carrega imagem da pedra
                img = Image.open(f"./resources/pedras/{pedra.name.lower()}.png")
                img = img.resize((60, 60), Image.Resampling.LANCZOS)
                img_tk = ImageTk.PhotoImage(img)
                
                frame_pedra = Frame(main_frame, bg="white")
                frame_pedra.pack(pady=10)
                
                btn = Button(frame_pedra, image=img_tk, 
                           command=lambda p=pedra: [pedra_escolhida.__setitem__(0, p), popup.destroy()],
                           relief=FLAT, bg="white")
                btn.image = img_tk
                btn.pack(side=LEFT, padx=10)
                
                Label(frame_pedra, text=pedra.name, font=("Arial", 12), bg="white").pack(side=LEFT, padx=10)
                
            except Exception as e:
                print(f"Erro ao carregar imagem da pedra {pedra.name}: {e}")
                btn = Button(main_frame, text=pedra.name, 
                           command=lambda p=pedra: [pedra_escolhida.__setitem__(0, p), popup.destroy()],
                           relief=RAISED, bg="lightblue", font=("Arial", 12))
                btn.pack(pady=10)
        
        # Botão cancelar
        Button(main_frame, text="Cancelar", command=lambda: [pedra_escolhida.__setitem__(0, None), popup.destroy()],
               font=("Arial", 12), bg="lightgray").pack(pady=20)
        
        # Configura o popup
        popup.focus_set()
        try:
            popup.grab_set()
        except Exception as e:
            print(f"Erro ao definir grab do popup: {e}")
        
        # Aguarda a escolha do usuário
        popup.wait_window()
        
        return pedra_escolhida[0]