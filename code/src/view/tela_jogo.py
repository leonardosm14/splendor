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
    def __init__(self, 
                 root: Tk, 
                 show_screen, 
                 jogador_local: Jogador, 
                 jogador_remoto: Jogador,
                 dog_server_interface: DogActor):
        self.root = root 
        self.frame = Frame(root)
        self.canvas = Canvas(self.frame)
        self.tabuleiro = Tabuleiro(jogadorLocal=jogador_local, jogadorRemoto=jogador_remoto)  # Inicializa com jogadores
        self.tabuleiro_inicio_partida = self.tabuleiro #utilizado para restaurar o estado inicial do tabuleiro naquela partida
        self.dog_server_interface = dog_server_interface

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
        self.atualizarInfosJogadores()
        
        # Configura layout
        self.configurarTela()

    def pegarTabuleiro(self) -> Tabuleiro:
        return self.tabuleiro

    def atualizarTabuleiro(self, tabuleiro: Tabuleiro):
        self.tabuleiro = tabuleiro
        self.tabuleiro_inicio_partida = tabuleiro
        self.atualizarInfosJogadores()
        self.desenharTabuleiro()
    
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
        self.tabuleiro.jogadorLocal().desabilitarJogador()

    def carregarCartas(self):
        """Carrega as imagens das cartas normais e de roubo"""
        def processarCarta(carta_img: Path, nivel: NiveisEnum = None):
            """Processa as informações de uma carta a partir do nome do arquivo"""
            infos = {"nivel": nivel} if nivel else {}
            cartas_info = carta_img.stem.split("-")
            
            if cartas_info[0].startswith("pontos"):
                infos["pontos"] = int(cartas_info[0].split(":")[1])
                if "bonus" in cartas_info[1]:
                    infos["bonus"] = cartas_info[1].split(":")[1]
                    infos["pedras"] = {
                        PedrasEnum[info.split(":")[0].upper()]: int(info.split(":")[1])
                        for info in cartas_info[2:] if ":" in info
                    }
                else:
                    infos["pedras"] = {
                        PedrasEnum[info.split(":")[0].upper()]: int(info.split(":")[1])
                        for info in cartas_info[1:] if ":" in info
                    }
            elif cartas_info[0] == "roubo":
                infos["tipo"] = "roubo"
                infos["pedras"] = {
                    PedrasEnum[info.upper()]: 1 for info in cartas_info[1:]
                }
            
            return infos

        def carregarCartasDeDiretorio(diretorio: Path, nivel: NiveisEnum = None):
            """Carrega cartas de um diretório específico"""
            for carta_img in diretorio.glob("*.png"):
                try:
                    infos = processarCarta(carta_img, nivel)
                    img = Image.open(carta_img)
                    img_tk = ImageTk.PhotoImage(img)
                    self.cartas[img_tk] = infos
                except Exception as e:
                    print(f"Erro ao carregar carta {carta_img}: {e}")

        # Diretórios das cartas
        diretorios_cartas = {
            NiveisEnum.NIVEL_1: Path("./resources/cartas/cartas-tabuleiro/cartas-nivel-1"),
            NiveisEnum.NIVEL_2: Path("./resources/cartas/cartas-tabuleiro/cartas-nivel-2"),
            NiveisEnum.NIVEL_3: Path("./resources/cartas/cartas-tabuleiro/cartas-nivel-3"),
        }
        cartas_roubo_dir = Path("./resources/cartas/cartas-de-roubo")

        # Carregar cartas normais
        for nivel, diretorio in diretorios_cartas.items():
            carregarCartasDeDiretorio(diretorio, nivel)

        # Carregar cartas de roubo
        carregarCartasDeDiretorio(cartas_roubo_dir)
        

    def carregarBotoes(self):
        """Carrega as imagens dos botões"""
        botoes_dir = Path("./resources/botoes")
        for botao_img in botoes_dir.glob("*.png"):
            try:
                img = Image.open(botao_img)
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
                img_tk = ImageTk.PhotoImage(img)
                self.pedras.append(img_tk)
            except Exception as e:
                print(f"Erro ao carregar pedra {pedra_img}: {e}")

    def configurarTela(self):
        """Configura os elementos gráficos da tela"""
        self.frame.pack(fill=BOTH, expand=True)
        self.canvas.pack(fill=BOTH, expand=True)
        
        # Adiciona imagens de fundo, cartas, pedras etc.
        self.desenharTabuleiro()

    def desenharTabuleiro(self):
        # Limpa o canvas
        self.canvas.delete("all")
        
        # Desenha cartas
        for i, carta_img in enumerate(self.cartas[:12]):  # Mostra apenas 12 cartas visíveis
            x = 100 + (i % 4) * 120
            y = 100 + (i // 4) * 180
            self.canvas.create_image(x, y, image=carta_img, anchor=NW, tags=f"carta_{i}")
            self.canvas.tag_bind(f"carta_{i}", "<Button-1>", lambda event, idx=i: self.interagirComCarta(idx))
        
        # Desenha pedras
        for i, (pedra, qtd) in enumerate(self.tabuleiro.pedrasNoTabuleiro.items()):
            if qtd > 0 and i < len(self.pedras):
                x = 700 + (i % 3) * 60
                y = 100 + (i // 3) * 60
                self.canvas.create_image(x, y, image=self.pedras[i], anchor=NW, tags=f"pedra_{pedra.name}")
                self.canvas.tag_bind(f"pedra_{pedra.name}", "<Button-1>", lambda event, pedra=pedra: self.interagirComPedra(pedra))
        
        # Desenha informações dos jogadores
        self.desenharInfosJogador(self.infosJogadorLocal, 50, 500, "local")
        self.desenharInfosJogador(self.infosJogadorRemoto, 650, 500, "remoto")
        
        # Desenha botões
        self.desenharBotoes()

    def desenharInfosJogador(self, infos: Dict, x: int, y: int, tag: str):
        """Desenha as informações de um jogador"""
        self.canvas.create_text(x, y, text=f"Jogador: {infos['nome']}", anchor=NW, tags=f"nome_{tag}")
        self.canvas.create_text(x, y+30, text=f"Pontos: {infos['pontos']}", anchor=NW, tags=f"pontos_{tag}")
        
        # Desenha pedras do jogador
        for i, (pedra, qtd) in enumerate(infos["pedras"].items()):
            if qtd > 0:
                self.canvas.create_image(x + (i % 3)*40, y+60 + (i//3)*40, 
                                        image=self.pedras[list(PedrasEnum).index(pedra)], 
                                        anchor=NW, 
                                        tags=f"pedra_{tag}_{pedra.name}")

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
        messagebox.showinfo("Troca de Pedras", f"Você selecionou a pedra {pedra.name} para troca.")
    
    
    def exibirPopupTroca(self):
        """Exibe um popup para troca de pedras"""
        popup = Toplevel(self.root)
        popup.title("Troca de Pedras")
        popup.geometry("300x200")
        
        Label(popup, text="Selecione as pedras que deseja trocar:").pack(pady=10)

        pedras_jogador_local = self.tabuleiro.jogadorLocal().pegarPedras()
        for pedra, qtd in pedras_jogador_local.items():
            if qtd > 0:
                pedra_button = Button(popup, text=f"{pedra.name} ({qtd})", 
                                      command=lambda p=pedra: self.selecionarPedra(p, "local"))
                pedra_button.pack(pady=5)

        pedras_jogador_remoto = self.tabuleiro.jogadorRemoto().pegarPedras()
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

        # Atualiza a tela para indicar que a pedra foi selecionada
        self.canvas.itemconfig(f"pedra_{pedra.name}", outline="red", width=3)

        if len(self.pedrasSelecionadas) >= 2:
            if self.pedrasSelecionadas[0] == self.pedrasSelecionadas[1]:
                sucesso = self.tabuleiro.pegarPedrasDoTabuleiro({pedra: 2})
                if sucesso:
                    self.habilitarBotaoFinalizarJogada()
            elif len(self.pedrasSelecionadas) == 3:
                p1, p2, p3 = self.pedrasSelecionadas
                if p1 == p3 or p2 == p3:
                    messagebox.showerror("Erro", "A terceira pedra selecionada não pode ser igual às anteriores.")
                    self.pedrasSelecionadas.pop()  # Remove a última pedra selecionada
                else:
                    sucesso = self.tabuleiro.pegarPedrasDoTabuleiro({p1: 1, p2: 1, p3: 1})
                    if sucesso:
                        self.habilitarBotaoFinalizarJogada()
        

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
            self.tabuleiro.jogadorLocal().adicionarPedra(pedra_bonus)
        
        self.tabuleiro.jogadorLocal().adicionarPontos(pontos_carta)
        self.tabuleiro.jogadorLocal().removerPedras(pedras_carta)
        self.tabuleiro.jogadorLocal().adicionarPedra(pedra_bonus)
        
        self.atualizarInfosJogadores()
        
        reservada = self.tabuleiro.verificaSeEstaReservada(self.cartaSelecionada)

        if not reservada:
            self.tabuleiro.removerCartaDoTabuleiro(self.cartaSelecionada)
            nivel_carta = self.tabuleiro.pegarNivelCarta(self.cartaSelecionada)
            self.reporTabuleiro(nivel_carta)

    def realizarCompraPedras(self):
        self.tabuleiro.adicionarPedrasNaMao(self.pedrasSelecionadas)
        self.atualizarInfosJogadores()

    def clickFinalizarJogada(self):
        if len(self.pedrasSelecionadas) >= 2:
            self.realizarCompraPedras()

        if self.cartaSelecionada and len(self.pedrasSelecionadas == 0):
            self.realizarCompraCarta()
            ultima_partida = self.tabuleiro.ehUltimaPartida()
            if ultima_partida:
                self.avaliarVencedor()

        self.atualizarTabuleiro()
        self.dog_server_interface.send_move(self.tabuleiro)
        self.tabuleiro.desabilitarJogador()

    def desenharBotoes(self):
        """Desenha os botões na tela"""
        botoes_pos = {
            "comprar_pedras": (50, 70),
            "comprar_carta": (60, 70),
            "reservar_carta": (350, 700),
            "oferta_de_troca": (10, 10),
            "finalizar_jogada": (700, 700)  # Botão para finalizar jogada
        }
        
        for nome, img in self.botoes.items():
            if nome in botoes_pos:
                x, y = botoes_pos[nome]
                self.canvas.create_image(x, y, image=img, anchor=NW, tags=f"botao_{nome}")
                if nome == "comprar_pedras":
                    self.canvas.tag_bind(f"botao_{nome}", "<Button-1>", lambda event: self.clickComprarPedras())
                elif nome == "comprar_carta":
                    self.canvas.tag_bind(f"botao_{nome}", "<Button-1>", lambda event: self.clickComprarCarta())
                elif nome == "oferta_de_troca":
                    self.canvas.tag_bind(f"botao_{nome}", "<Button-1>", lambda event: self.clickOfertaDeTroca())
                elif nome == "finalizar_jogada":
                    self.canvas.tag_bind(f"botao_{nome}", "<Button-1>", lambda event: self.enviarPartidaDOG())

    def desenharTabuleiro(self):
        """Desenha o tabuleiro com cartas e pedras"""
        self.canvas.delete("all")  # Limpa o canvas

        # Desenha cartas
        for i, carta_img in enumerate(self.cartas[:12]):  # Mostra apenas 12 cartas visíveis
            x = 100 + (i % 4) * 120
            y = 100 + (i // 4) * 180
            self.canvas.create_image(x, y, image=carta_img, anchor=NW, tags=f"carta_{i}")
            self.canvas.tag_bind(f"carta_{i}", "<Button-1>", lambda event, idx=i: self.clickCarta(idx))

        # Desenha pedras
        for i, (pedra, qtd) in enumerate(self.tabuleiro.pedrasNoTabuleiro.items()):
            if qtd > 0 and i < len(self.pedras):
                x = 700 + (i % 3) * 60
                y = 100 + (i // 3) * 60
                self.canvas.create_image(x, y, image=self.pedras[i], anchor=NW, tags=f"pedra_{pedra.name}")
                self.canvas.tag_bind(f"pedra_{pedra.name}", "<Button-1>", lambda event, pedra=pedra: self.clickPedra(pedra))

    ### Métodos para habilitar/desabilitar botões ###

    def habilitarBotaoComprarCarta(self):
        """Habilita o botão 'Comprar Carta'"""
        if "comprar_carta" in self.botoes:
            img = self.botoes["comprar_carta"]
            self.canvas.itemconfig("botao_comprar_carta", image=img)
            self.canvas.tag_bind("botao_comprar_carta", "<Button-1>", lambda event: self.clickComprarCarta())

    def desabilitarBotaoComprarCarta(self):
        """Desabilita o botão 'Comprar Carta'"""
        if "comprar_carta" in self.botoes:
            img = self.botoes["comprar_carta"]._PhotoImage__photo.zoom(1).subsample(1)
            img = img.copy()
            img.putalpha(128)  # Define transparência para simular desativação
            self.canvas.itemconfig("botao_comprar_carta", image=img)
            self.canvas.tag_unbind("botao_comprar_carta", "<Button-1>")

    def habilitarBotaoComprarPedras(self):
        """Habilita o botão 'Comprar Pedras'"""
        if "comprar_pedras" in self.botoes:
            img = self.botoes["comprar_pedras"]
            self.canvas.itemconfig("botao_comprar_pedras", image=img)
            self.canvas.tag_bind("botao_comprar_pedras", "<Button-1>", lambda event: self.clickComprarPedras())

    def desabilitarBotaoComprarPedras(self):
        """Desabilita o botão 'Comprar Pedras'"""
        if "comprar_pedras" in self.botoes:
            img = self.botoes["comprar_pedras"]._PhotoImage__photo.zoom(1).subsample(1)
            img = img.copy()
            img.putalpha(128)  # Define transparência para simular desativação
            self.canvas.itemconfig("botao_comprar_pedras", image=img)
            self.canvas.tag_unbind("botao_comprar_pedras", "<Button-1>")

    def habilitarBotaoOfertaDeTroca(self):
        """Habilita o botão 'Oferta de Troca'"""
        if "oferta_de_troca" in self.botoes:
            img = self.botoes["oferta_de_troca"]
            self.canvas.itemconfig("botao_oferta_de_troca", image=img)
            self.canvas.tag_bind("botao_oferta_de_troca", "<Button-1>", lambda event: self.clickOfertaDeTroca())

    def desabilitarBotaoOfertaDeTroca(self):
        """Desabilita o botão 'Oferta de Troca'"""
        if "oferta_de_troca" in self.botoes:
            img = self.botoes["oferta_de_troca"]._PhotoImage__photo.zoom(1).subsample(1)
            img = img.copy()
            img.putalpha(128)  # Define transparência para simular desativação
            self.canvas.itemconfig("botao_oferta_de_troca", image=img)
            self.canvas.tag_unbind("botao_oferta_de_troca", "<Button-1>")
    
    def habilitarReservarCarta(self):
        """Habilita o botão 'Reservar Carta'"""
        if "reservar_carta" in self.botoes:
            img = self.botoes["reservar_carta"]
            self.canvas.itemconfig("botao_reservar_carta", image=img)
            self.canvas.tag_bind("botao_reservar_carta", "<Button-1>", lambda event: self.clickComprarCarta())
    
    def desabilitarReservarCarta(self):
        """Desabilita o botão 'Reservar Carta'"""
        if "reservar_carta" in self.botoes:
            img = self.botoes["reservar_carta"]._PhotoImage__photo.zoom(1).subsample(1)
            img = img.copy()
            img.putalpha(128)  # Define transparência para simular desativação
            self.canvas.itemconfig("botao_reservar_carta", image=img)
            self.canvas.tag_unbind("botao_reservar_carta", "<Button-1>")
    
    def habilitarDesfazerJogada(self):
        """Habilita o botão 'Desfazer Jogada'"""
        if "desfazer_jogada" in self.botoes:
            img = self.botoes["desfazer_jogada"]
            self.canvas.itemconfig("botao_desfazer_jogada", image=img)
            self.canvas.tag_bind("botao_desfazer_jogada", "<Button-1>", lambda event: self.clickDesfazerJogada())
    
    def desabilitarDesfazerJogada(self):
        """Desabilita o botão 'Desfazer Jogada'"""
        if "desfazer_jogada" in self.botoes:
            img = self.botoes["desfazer_jogada"]._PhotoImage__photo.zoom(1).subsample(1)
            img = img.copy()
            img.putalpha(128)  # Define transparência para simular desativação
            self.canvas.itemconfig("botao_desfazer_jogada", image=img)
            self.canvas.tag_unbind("botao_desfazer_jogada", "<Button-1>")

    def habilitarBotaoFinalizarJogada(self):
        """Habilita o botão 'Finalizar Jogada'"""
        if "finalizar_jogada" in self.botoes:
            img = self.botoes["finalizar_jogada"]
            self.canvas.itemconfig("botao_finalizar_jogada", image=img)
            self.canvas.tag_bind("botao_finalizar_jogada", "<Button-1>", lambda event: self.enviarPartidaDOG())

    def desabilitarBotaoFinalizarJogada(self):
        """Desabilita o botão 'Finalizar Jogada'"""
        if "finalizar_jogada" in self.botoes:
            img = self.botoes["finalizar_jogada"]._PhotoImage__photo.zoom(1).subsample(1)
            img = img.copy()
            img.putalpha(128)  # Define transparência para simular desativação
            self.canvas.itemconfig("botao_finalizar_jogada", image=img)
            self.canvas.tag_unbind("botao_finalizar_jogada", "<Button-1>")

    # Métodos para habilitar/desabilitar cartas
    def habilitarCartas(self):
        """Habilita todas as cartas no tabuleiro"""
        for i in range(len(self.cartas)):
            self.canvas.tag_bind(f"carta_{i}", "<Button-1>", lambda event, idx=i: self.clickCarta(idx))

    def desabilitarCartas(self):
        """Desabilita todas as cartas no tabuleiro"""
        for i in range(len(self.cartas)):
            self.canvas.tag_unbind(f"carta_{i}", "<Button-1>")

    # Métodos para habilitar/desabilitar pedras
    def habilitarPedras(self):
        """Habilita todas as pedras no tabuleiro"""
        for pedra in self.tabuleiro.pedrasNoTabuleiro.keys():
            self.canvas.tag_bind(f"pedra_{pedra.name}", "<Button-1>", lambda event, pedra=pedra: self.clickPedra(pedra))

    def desabilitarPedras(self):
        """Desabilita todas as pedras no tabuleiro"""
        for pedra in self.tabuleiro.pedrasNoTabuleiro.keys():
            self.canvas.tag_unbind(f"pedra_{pedra.name}", "<Button-1>")

    def avaliarVencedor(self):
        pontos1 = self.tabuleiro.jogadorLocal().pegarPontuacaoJogador()
        pontos2 = self.tabuleiro.jogadorRemoto().pegarPontuacaoJogador()

        if pontos1 > pontos2:
            vencedor = self.tabuleiro.jogadorLocal().pegarNome()
            self.tabuleiro.jogadorLocal().jogadorVenceu()
            self.notificarVencedor(vencedor)
        elif pontos2 > pontos1:
            vencedor = self.tabuleiro.jogadorRemoto().pegarNome()
            self.tabuleiro.jogadorRemoto().jogadorVenceu()
            self.notificarVencedor(vencedor)
        else:
            self.tabuleiro.jogadorLocal().jogadorEmpatou()
            self.tabuleiro.jogadorRemoto().jogadorEmpatou()
            self.notificarEmpate()
        
        self.restaurarEstadoInicial()
    
    def identificarPossivelComprarCartas(self) -> bool:
        """Identifica se o jogador pode comprar cartas e habilita o botão de compra"""
        for carta in self.tabuleiro.cartasNoTabuleiro:
            if carta and self.tabuleiro.verificarPedrasSuficientes(carta):
                return True
        return False
    
    def habilitarTabuleiro(self):
        pontos = self.tabuleiro.jogadorRemoto().pegarPontuacaoJogador()
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
