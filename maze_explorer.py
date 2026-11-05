import random
import time
import tkinter as tk
from collections import deque


PAREDE = 1
LIVRE = 0

LINHAS = 21
COLUNAS = 41
TAMANHO_CELULA = 19

COR_FUNDO = "#f3f5f9"
COR_PAINEL = "#ffffff"
COR_PAREDE = "#252b38"
COR_LIVRE = "#f8fafc"
COR_GERADA = "#cfe0fb"
COR_GERACAO_ATUAL = "#3978d4"
COR_EXPLORADA = "#a8d5f5"
COR_BUSCA_ATUAL = "#2878c7"
COR_CAMINHO = "#f4c95d"
COR_ENTRADA = "#35a879"
COR_SAIDA = "#df6268"
COR_TEXTO = "#202938"
COR_TEXTO_SECUNDARIO = "#647084"
COR_BORDA = "#e2e7ef"


class AplicacaoMaze:
    def __init__(self, janela):
        if LINHAS < 5 or COLUNAS < 5 or LINHAS % 2 == 0 or COLUNAS % 2 == 0:
            raise ValueError("LINHAS e COLUNAS devem ser ímpares e maiores ou iguais a 5.")

        self.janela = janela
        self.janela.title("Maze Explorer | Geração Procedural e BFS")
        self.janela.geometry("1180x760")
        self.janela.minsize(1080, 700)
        self.janela.configure(bg=COR_FUNDO)
        self.janela.protocol("WM_DELETE_WINDOW", self.fechar)

        self.entrada = (1, 0)
        self.saida = (LINHAS - 2, COLUNAS - 1)

        self.maze = []
        self.itens_celulas = []

        self.modo = None
        self.pausado = False
        self.callback_id = None
        self.geracao_finalizada = False

        self.pilha_geracao = []
        self.posicao_geracao_atual = None

        self.fila = deque()
        self.anteriores = {}
        self.posicao_busca_anterior = None
        self.caminho = []
        self.indice_caminho = 0
        self.tempo_processamento_busca = 0.0
        self.total_exploradas = 0

        self.velocidade_geracao = tk.IntVar(value=18)
        self.velocidade_busca = tk.IntVar(value=12)
        self.velocidade_caminho = tk.IntVar(value=28)

        self.status_var = tk.StringVar(value="Preparando o labirinto...")
        self.exploradas_var = tk.StringVar(value="0")
        self.passos_var = tk.StringVar(value="—")
        self.tempo_var = tk.StringVar(value="—")

        self.criar_interface()
        self.novo_maze()

    def criar_interface(self):
        principal = tk.Frame(self.janela, bg=COR_FUNDO)
        principal.pack(fill="both", expand=True, padx=24, pady=20)

        cabecalho = tk.Frame(principal, bg=COR_FUNDO)
        cabecalho.pack(fill="x", pady=(0, 18))

        tk.Label(
            cabecalho,
            text="Maze Explorer",
            bg=COR_FUNDO,
            fg=COR_TEXTO,
            font=("Segoe UI", 23, "bold"),
        ).pack(anchor="w")

        tk.Label(
            cabecalho,
            text="Geração procedural de labirintos e busca de caminho com BFS",
            bg=COR_FUNDO,
            fg=COR_TEXTO_SECUNDARIO,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(3, 0))

        conteudo = tk.Frame(principal, bg=COR_FUNDO)
        conteudo.pack(fill="both", expand=True)

        painel_controles = tk.Frame(
            conteudo,
            bg=COR_PAINEL,
            width=260,
            highlightbackground=COR_BORDA,
            highlightthickness=1,
        )
        painel_controles.pack(side="left", fill="y")
        painel_controles.pack_propagate(False)

        painel_visual = tk.Frame(
            conteudo,
            bg=COR_PAINEL,
            highlightbackground=COR_BORDA,
            highlightthickness=1,
        )
        painel_visual.pack(side="right", fill="both", expand=True, padx=(18, 0))

        self.criar_painel_controles(painel_controles)
        self.criar_painel_visual(painel_visual)

    def criar_painel_controles(self, painel):
        interno = tk.Frame(painel, bg=COR_PAINEL)
        interno.pack(fill="both", expand=True, padx=18, pady=18)

        tk.Label(
            interno,
            text="CONTROLES",
            bg=COR_PAINEL,
            fg=COR_TEXTO_SECUNDARIO,
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", pady=(0, 12))

        self.botao_novo = self.criar_botao(
            interno, "Novo labirinto", self.novo_maze, "#2563eb", "#1d4ed8"
        )
        self.botao_novo.pack(fill="x", pady=4)

        self.botao_resolver = self.criar_botao(
            interno, "Resolver", self.iniciar_resolucao, "#15956c", "#117a59"
        )
        self.botao_resolver.pack(fill="x", pady=4)

        self.botao_pausa = self.criar_botao(
            interno, "Pausar", self.alternar_pausa, "#e9edf4", "#dce3ed", COR_TEXTO
        )
        self.botao_pausa.pack(fill="x", pady=4)

        self.botao_limpar = self.criar_botao(
            interno, "Limpar visualização", self.limpar_visualizacao,
            "#e9edf4", "#dce3ed", COR_TEXTO
        )
        self.botao_limpar.pack(fill="x", pady=4)

        self.adicionar_divisor(interno, pady=(16, 12))

        tk.Label(
            interno,
            text="VELOCIDADE DAS ANIMAÇÕES",
            bg=COR_PAINEL,
            fg=COR_TEXTO_SECUNDARIO,
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", pady=(0, 4))

        self.criar_controle_velocidade(interno, "Geração (ms)", self.velocidade_geracao)
        self.criar_controle_velocidade(interno, "Busca (ms)", self.velocidade_busca)
        self.criar_controle_velocidade(interno, "Caminho (ms)", self.velocidade_caminho)

        self.adicionar_divisor(interno, pady=(10, 12))

        tk.Label(
            interno,
            text="LEGENDA",
            bg=COR_PAINEL,
            fg=COR_TEXTO_SECUNDARIO,
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        self.adicionar_legenda(interno, COR_PAREDE, "Parede")
        self.adicionar_legenda(interno, COR_LIVRE, "Corredor")
        self.adicionar_legenda(interno, COR_GERACAO_ATUAL, "Geração atual")
        self.adicionar_legenda(interno, COR_EXPLORADA, "Célula explorada")
        self.adicionar_legenda(interno, COR_CAMINHO, "Caminho encontrado")
        self.adicionar_legenda(interno, COR_ENTRADA, "Entrada")
        self.adicionar_legenda(interno, COR_SAIDA, "Saída")

    def criar_painel_visual(self, painel):
        topo = tk.Frame(painel, bg=COR_PAINEL)
        topo.pack(fill="x", padx=18, pady=(16, 8))

        tk.Label(
            topo,
            text="VISUALIZAÇÃO",
            bg=COR_PAINEL,
            fg=COR_TEXTO_SECUNDARIO,
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w")

        area_canvas = tk.Frame(painel, bg=COR_PAINEL)
        area_canvas.pack(fill="both", expand=True, padx=18, pady=8)

        largura = COLUNAS * TAMANHO_CELULA
        altura = LINHAS * TAMANHO_CELULA

        self.canvas = tk.Canvas(
            area_canvas,
            width=largura,
            height=altura,
            bg=COR_PAREDE,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(expand=True)

        faixa_estatisticas = tk.Frame(painel, bg="#f8fafc")
        faixa_estatisticas.pack(fill="x", padx=18, pady=(6, 12))

        self.criar_estatistica(faixa_estatisticas, "CÉLULAS EXPLORADAS", self.exploradas_var)
        self.criar_estatistica(faixa_estatisticas, "PASSOS DO CAMINHO", self.passos_var)
        self.criar_estatistica(faixa_estatisticas, "TEMPO DE PROCESSAMENTO", self.tempo_var)

        barra_status = tk.Frame(painel, bg=COR_PAINEL)
        barra_status.pack(fill="x", padx=18, pady=(0, 16))

        tk.Label(
            barra_status,
            textvariable=self.status_var,
            bg=COR_PAINEL,
            fg=COR_TEXTO,
            font=("Segoe UI", 9),
            anchor="w",
            justify="left",
        ).pack(fill="x")

    def criar_botao(self, painel, texto, comando, fundo, ativo, texto_cor="white"):
        return tk.Button(
            painel,
            text=texto,
            command=comando,
            bg=fundo,
            fg=texto_cor,
            activebackground=ativo,
            activeforeground=texto_cor,
            disabledforeground="#9aa4b2",
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            pady=9,
        )

    def criar_controle_velocidade(self, painel, titulo, variavel):
        escala = tk.Scale(
            painel,
            label=titulo,
            variable=variavel,
            from_=1,
            to=100,
            orient="horizontal",
            resolution=1,
            showvalue=True,
            length=210,
            sliderlength=14,
            highlightthickness=0,
            bd=0,
            bg=COR_PAINEL,
            fg=COR_TEXTO,
            activebackground="#2563eb",
            troughcolor="#e5eaf2",
            font=("Segoe UI", 8),
        )
        escala.pack(fill="x", pady=(0, 2))

    def criar_estatistica(self, painel, titulo, variavel):
        bloco = tk.Frame(painel, bg="#f8fafc")
        bloco.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        tk.Label(
            bloco,
            text=titulo,
            bg="#f8fafc",
            fg=COR_TEXTO_SECUNDARIO,
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w")

        tk.Label(
            bloco,
            textvariable=variavel,
            bg="#f8fafc",
            fg=COR_TEXTO,
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w", pady=(3, 0))

    def adicionar_legenda(self, painel, cor, texto):
        linha = tk.Frame(painel, bg=COR_PAINEL)
        linha.pack(fill="x", pady=2)

        amostra = tk.Canvas(
            linha, width=14, height=14, bg=COR_PAINEL, highlightthickness=0
        )
        amostra.pack(side="left", padx=(0, 8))
        amostra.create_rectangle(1, 1, 13, 13, fill=cor, outline=COR_BORDA)

        tk.Label(
            linha,
            text=texto,
            bg=COR_PAINEL,
            fg=COR_TEXTO,
            font=("Segoe UI", 8),
        ).pack(side="left")

    def adicionar_divisor(self, painel, pady=(10, 10)):
        tk.Frame(painel, bg=COR_BORDA, height=1).pack(fill="x", pady=pady)

    def desenhar_grade(self):
        self.canvas.delete("all")
        self.itens_celulas = []

        for linha in range(LINHAS):
            itens_linha = []
            for coluna in range(COLUNAS):
                x1 = coluna * TAMANHO_CELULA
                y1 = linha * TAMANHO_CELULA
                x2 = x1 + TAMANHO_CELULA
                y2 = y1 + TAMANHO_CELULA

                item = self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=COR_PAREDE,
                    outline="#333b4a",
                    width=1,
                )
                itens_linha.append(item)
            self.itens_celulas.append(itens_linha)

    def colorir_celula(self, posicao, cor):
        linha, coluna = posicao
        self.canvas.itemconfig(self.itens_celulas[linha][coluna], fill=cor)

    def desenhar_estado_base(self):
        for linha in range(LINHAS):
            for coluna in range(COLUNAS):
                cor = COR_LIVRE if self.maze[linha][coluna] == LIVRE else COR_PAREDE
                self.colorir_celula((linha, coluna), cor)

        self.colorir_celula(self.entrada, COR_ENTRADA)
        self.colorir_celula(self.saida, COR_SAIDA)

    def cancelar_callback(self):
        if self.callback_id is not None:
            try:
                self.janela.after_cancel(self.callback_id)
            except tk.TclError:
                pass
            self.callback_id = None

    def agendar(self, funcao, intervalo):
        if self.modo is not None and not self.pausado:
            self.callback_id = self.janela.after(max(1, int(intervalo)), funcao)

    def atualizar_botoes(self):
        em_execucao = self.modo is not None

        self.botao_resolver.configure(
            state="normal" if self.geracao_finalizada and not em_execucao else "disabled"
        )
        self.botao_limpar.configure(
            state="normal" if self.geracao_finalizada else "disabled"
        )
        self.botao_pausa.configure(
            state="normal" if em_execucao else "disabled",
            text="Retomar" if self.pausado else "Pausar",
        )

    def atualizar_estatisticas(self, exploradas=None, passos=None, tempo=None):
        if exploradas is not None:
            self.exploradas_var.set(str(exploradas))
        if passos is not None:
            self.passos_var.set(str(passos))
        if tempo is not None:
            self.tempo_var.set(tempo)

    def reiniciar_estatisticas(self):
        self.atualizar_estatisticas(0, "—", "—")

    def novo_maze(self):
        self.cancelar_callback()
        self.modo = "geracao"
        self.pausado = False
        self.geracao_finalizada = False

        self.maze = [[PAREDE for _ in range(COLUNAS)] for _ in range(LINHAS)]
        self.pilha_geracao = [(1, 1)]
        self.posicao_geracao_atual = (1, 1)
        self.maze[1][1] = LIVRE

        self.fila.clear()
        self.anteriores = {}
        self.caminho = []
        self.indice_caminho = 0
        self.posicao_busca_anterior = None
        self.tempo_processamento_busca = 0.0
        self.total_exploradas = 0
        self.reiniciar_estatisticas()

        self.desenhar_grade()
        self.colorir_celula((1, 1), COR_GERACAO_ATUAL)
        self.status_var.set("Gerando o labirinto...")
        self.atualizar_botoes()
        self.agendar(self.passo_geracao, self.velocidade_geracao.get())

    def passo_geracao(self):
        self.callback_id = None
        if self.modo != "geracao" or self.pausado:
            return

        if not self.pilha_geracao:
            self.finalizar_geracao()
            return

        linha_atual, coluna_atual = self.pilha_geracao[-1]
        vizinhos = []
        direcoes = ((-2, 0), (2, 0), (0, -2), (0, 2))

        for desloc_linha, desloc_coluna in direcoes:
            nova_linha = linha_atual + desloc_linha
            nova_coluna = coluna_atual + desloc_coluna

            if (
                1 <= nova_linha < LINHAS - 1
                and 1 <= nova_coluna < COLUNAS - 1
                and self.maze[nova_linha][nova_coluna] == PAREDE
            ):
                vizinhos.append((nova_linha, nova_coluna, desloc_linha, desloc_coluna))

        if vizinhos:
            self.colorir_celula((linha_atual, coluna_atual), COR_GERADA)

            nova_linha, nova_coluna, desloc_linha, desloc_coluna = random.choice(vizinhos)
            parede_linha = linha_atual + desloc_linha // 2
            parede_coluna = coluna_atual + desloc_coluna // 2

            self.maze[parede_linha][parede_coluna] = LIVRE
            self.maze[nova_linha][nova_coluna] = LIVRE

            self.colorir_celula((parede_linha, parede_coluna), COR_GERADA)
            self.colorir_celula((nova_linha, nova_coluna), COR_GERACAO_ATUAL)

            self.pilha_geracao.append((nova_linha, nova_coluna))
            self.posicao_geracao_atual = (nova_linha, nova_coluna)
        else:
            self.pilha_geracao.pop()
            self.colorir_celula((linha_atual, coluna_atual), COR_GERADA)

            if self.pilha_geracao:
                self.posicao_geracao_atual = self.pilha_geracao[-1]
                self.colorir_celula(self.posicao_geracao_atual, COR_GERACAO_ATUAL)
            else:
                self.posicao_geracao_atual = None

        if not self.pilha_geracao:
            self.finalizar_geracao()
            return

        self.status_var.set(
            f"Gerando o labirinto... {len(self.pilha_geracao)} posições na pilha de busca."
        )
        self.agendar(self.passo_geracao, self.velocidade_geracao.get())

    def finalizar_geracao(self):
        self.maze[self.entrada[0]][self.entrada[1]] = LIVRE
        self.maze[self.saida[0]][self.saida[1]] = LIVRE

        self.geracao_finalizada = True
        self.modo = None
        self.pausado = False
        self.desenhar_estado_base()
        self.status_var.set("Labirinto pronto. Clique em Resolver para executar a busca BFS.")
        self.atualizar_botoes()

    def iniciar_resolucao(self):
        if not self.geracao_finalizada or self.modo is not None:
            return

        self.cancelar_callback()
        self.desenhar_estado_base()
        self.reiniciar_estatisticas()

        self.fila = deque([self.entrada])
        self.anteriores = {self.entrada: None}
        self.posicao_busca_anterior = None
        self.caminho = []
        self.indice_caminho = 0
        self.total_exploradas = 0
        self.tempo_processamento_busca = 0.0

        self.modo = "busca"
        self.pausado = False
        self.status_var.set("Buscando a saída com busca em largura (BFS)...")
        self.atualizar_botoes()
        self.agendar(self.buscar_passo, 1)

    def buscar_passo(self):
        self.callback_id = None
        if self.modo != "busca" or self.pausado:
            return

        if not self.fila:
            self.finalizar_busca_sem_solucao()
            return

        inicio_etapa = time.perf_counter()
        posicao = self.fila.popleft()

        if (
            self.posicao_busca_anterior is not None
            and self.posicao_busca_anterior not in (self.entrada, self.saida)
        ):
            self.colorir_celula(self.posicao_busca_anterior, COR_EXPLORADA)

        if posicao not in (self.entrada, self.saida):
            self.colorir_celula(posicao, COR_BUSCA_ATUAL)

        self.posicao_busca_anterior = posicao
        self.total_exploradas += 1

        if posicao == self.saida:
            self.tempo_processamento_busca += time.perf_counter() - inicio_etapa
            self.caminho = self.reconstruir_caminho()
            self.atualizar_estatisticas(
                exploradas=self.total_exploradas,
                passos=max(0, len(self.caminho) - 1),
                tempo=f"{self.tempo_processamento_busca * 1000:.3f} ms",
            )
            self.modo = "caminho"
            self.indice_caminho = 0
            self.status_var.set("Saída encontrada. Exibindo o menor caminho...")
            self.atualizar_botoes()
            self.agendar(self.animar_caminho, self.velocidade_caminho.get())
            return

        linha, coluna = posicao
        direcoes = ((-1, 0), (1, 0), (0, -1), (0, 1))

        for desloc_linha, desloc_coluna in direcoes:
            vizinha = (linha + desloc_linha, coluna + desloc_coluna)
            nova_linha, nova_coluna = vizinha

            if (
                0 <= nova_linha < LINHAS
                and 0 <= nova_coluna < COLUNAS
                and self.maze[nova_linha][nova_coluna] == LIVRE
                and vizinha not in self.anteriores
            ):
                self.anteriores[vizinha] = posicao
                self.fila.append(vizinha)

        self.tempo_processamento_busca += time.perf_counter() - inicio_etapa
        self.atualizar_estatisticas(
            exploradas=self.total_exploradas,
            tempo=f"{self.tempo_processamento_busca * 1000:.3f} ms",
        )
        self.status_var.set(
            f"Buscando a saída... {self.total_exploradas} células exploradas."
        )
        self.agendar(self.buscar_passo, self.velocidade_busca.get())

    def reconstruir_caminho(self):
        caminho = []
        atual = self.saida

        while atual is not None:
            caminho.append(atual)
            atual = self.anteriores[atual]

        caminho.reverse()
        return caminho

    def animar_caminho(self):
        self.callback_id = None
        if self.modo != "caminho" or self.pausado:
            return

        if self.indice_caminho >= len(self.caminho):
            self.colorir_celula(self.entrada, COR_ENTRADA)
            self.colorir_celula(self.saida, COR_SAIDA)
            self.modo = None
            self.pausado = False
            passos = max(0, len(self.caminho) - 1)
            self.status_var.set(
                f"Busca concluída. O menor caminho encontrado tem {passos} passos."
            )
            self.atualizar_botoes()
            return

        posicao = self.caminho[self.indice_caminho]
        if posicao not in (self.entrada, self.saida):
            self.colorir_celula(posicao, COR_CAMINHO)

        self.indice_caminho += 1
        self.agendar(self.animar_caminho, self.velocidade_caminho.get())

    def finalizar_busca_sem_solucao(self):
        if (
            self.posicao_busca_anterior is not None
            and self.posicao_busca_anterior not in (self.entrada, self.saida)
        ):
            self.colorir_celula(self.posicao_busca_anterior, COR_EXPLORADA)

        self.modo = None
        self.pausado = False
        self.atualizar_estatisticas(
            exploradas=self.total_exploradas,
            passos="—",
            tempo=f"{self.tempo_processamento_busca * 1000:.3f} ms",
        )
        self.status_var.set("Não foi possível encontrar um caminho até a saída.")
        self.atualizar_botoes()

    def limpar_visualizacao(self):
        if not self.geracao_finalizada:
            return

        self.cancelar_callback()
        self.modo = None
        self.pausado = False
        self.fila.clear()
        self.anteriores = {}
        self.caminho = []
        self.indice_caminho = 0
        self.posicao_busca_anterior = None
        self.tempo_processamento_busca = 0.0
        self.total_exploradas = 0

        self.desenhar_estado_base()
        self.reiniciar_estatisticas()
        self.status_var.set("Visualização limpa. O labirinto continua disponível.")
        self.atualizar_botoes()

    def alternar_pausa(self):
        if self.modo is None:
            return

        if not self.pausado:
            self.pausado = True
            self.cancelar_callback()
            self.status_var.set("Animação pausada.")
        else:
            self.pausado = False
            self.status_var.set("Animação retomada.")
            if self.modo == "geracao":
                self.agendar(self.passo_geracao, 1)
            elif self.modo == "busca":
                self.agendar(self.buscar_passo, 1)
            elif self.modo == "caminho":
                self.agendar(self.animar_caminho, 1)

        self.atualizar_botoes()

    def fechar(self):
        self.cancelar_callback()
        self.janela.destroy()


if __name__ == "__main__":
    janela = tk.Tk()
    aplicacao = AplicacaoMaze(janela)
    janela.mainloop()
