from tkinter import *
import random
from PIL import Image, ImageTk
from pathlib import Path
from typing import Dict, List

from model.tabuleiro import Tabuleiro
from model.jogador import Jogador
from model.enums.niveisEnum import NiveisEnum
from model.enums.pedrasEnum import PedrasEnum
from model.pedra import Pedra
from model.carta import Carta

class TelaJogo:
    def __init__(self, root: Tk, show_screen, jogador_local: Jogador, jogador_remoto: Jogador):
        self.root = root 
        self.frame = Frame(root)
        self.canvas = Canvas(self.frame)
        self.tabuleiro = Tabuleiro(jogadorLocal=jogador_local, jogadorRemoto=jogador_remoto)  # Inicializa com jogadores
        
        # Estruturas de dados
        self.cartas: List[ImageTk.PhotoImage] = list()
        self.pedras: List[ImageTk.PhotoImage] = list()
        self.botoes: Dict[str, ImageTk.PhotoImage] = dict()

        # Carrega os recursos
        self.carregarCartas()
        self.carregarPedras()
        self.carregarBotoes()
        self.atualizarInfosJogadores()
        
        # Configura layout
        self.configurarTela()

    def carregarCartas(self):
        """Carrega as imagens das cartas normais e de roubo"""
        # Cartas normais
        cartas_dir = Path("./resources/cartas")
        for carta_img in cartas_dir.glob("*.png"):
            try:
                img = Image.open(carta_img)
                img_tk = ImageTk.PhotoImage(img)
                self.cartas.append(img_tk)
                
                # Extrai informações do nome do arquivo
                infos = self.extrairInfosCarta(carta_img.stem)
                self.tabuleiro.adicionarCartaNova(infos["nivel"])
                
            except Exception as e:
                print(f"Erro ao carregar carta {carta_img}: {e}")

        # Cartas de roubo
        cartas_roubo_dir = Path("./resources/cartas_roubo")
        for carta_img in cartas_roubo_dir.glob("*.png"):
            try:
                img = Image.open(carta_img)
                img_tk = ImageTk.PhotoImage(img)
                self.cartas.append(img_tk)
                
                infos = self.extrairInfosCartaRoubo(carta_img.stem)
                self.tabuleiro.adicionarCartaNova(infos["nivel"])
                
            except Exception as e:
                print(f"Erro ao carregar carta de roubo {carta_img}: {e}")

    def extrairInfosCarta(self, nome_arquivo: str) -> Dict:
        """Extrai informações das cartas normais do nome do arquivo"""
        infos = {}
        partes = nome_arquivo.split('-')
        
        infos["bonus"] = partes[0].split(':')[1] if ":" in partes[0] else None
        infos["pontos"] = int(partes[1].split(':')[1])
        
        pedras = {}
        for parte in partes[2:-1]:
            pedra, qtd = parte.split(':')
            pedras[pedra] = int(qtd)
        infos["pedras"] = pedras
        
        infos["nivel"] = int(partes[-1].split(':')[1])
        
        return infos

    def extrairInfosCartaRoubo(self, nome_arquivo: str) -> Dict:
        """Extrai informações das cartas de roubo do nome do arquivo"""
        infos = {}
        partes = nome_arquivo.split('-')
        
        pedras = {partes[0]: 1, partes[1]: 1}
        infos["pedras"] = pedras
        infos["nivel"] = int(partes[2].split(':')[1])
        infos["cartaDeRoubo"] = True
        
        return infos

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
        
        # Desenha pedras
        for i, (pedra, qtd) in enumerate(self.tabuleiro.pedrasNoTabuleiro.items()):
            if qtd > 0 and i < len(self.pedras):
                x = 700 + (i % 3) * 60
                y = 100 + (i // 3) * 60
                self.canvas.create_image(x, y, image=self.pedras[i], anchor=NW, tags=f"pedra_{pedra.name}")
        
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

    def desenharBotoes(self):
        """Desenha os botões na tela"""
        botoes_pos = {
            "comprar_pedras": (50, 70),
            "comprar_carta": (60, 70),
            "reservar_carta": (350, 700),
            "oferta_de_troca": (10, 10)
        }
        
        for nome, img in self.botoes.items():
            if nome in botoes_pos:
                x, y = botoes_pos[nome]
                self.canvas.create_image(x, y, image=img, anchor=NW, tags=f"botao_{nome}")