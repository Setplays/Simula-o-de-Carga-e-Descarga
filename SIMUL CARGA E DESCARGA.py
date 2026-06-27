import pygame
import simpy
import random
import math
import sys
import matplotlib.pyplot as plt

LARGURA, ALTURA = 1000, 700
FPS = 60
NUM_ROBOS = 8

BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
CINZA = (220, 220, 220)
COR_ROBO = (50, 150, 255)                  
COR_ROBO_RETORNANDO = (255, 100, 100)      
COR_ROBO_DESCARREGANDO = (255, 200, 0)     
COR_BASE = (100, 200, 100)
COR_ALVO = (200, 0, 255)                   

RAIO_ROBO = 16
RAIO_ALVO = 6
TAMANHO_BASE = 60
VELOCIDADE_ROBO = 2.5
DISTANCIA_COLISAO = RAIO_ROBO * 3.0

class Alvo:
    def __init__(self):
        self.x = random.randint(100, LARGURA - 100)
        self.y = random.randint(150, ALTURA - 150)
        self.ativo = True

    def desenhar(self, tela):
        if self.ativo:
            pygame.draw.circle(tela, COR_ALVO, (self.x, self.y), RAIO_ALVO)
            pygame.draw.circle(tela, PRETO, (self.x, self.y), RAIO_ALVO, 1)

class Base:
    def __init__(self, x, y, id_base):
        self.x = x
        self.y = y
        self.id = id_base
        self.itens_coletados = 0

    def desenhar(self, tela, fonte):
        retangulo = pygame.Rect(self.x - TAMANHO_BASE//2, self.y - TAMANHO_BASE//2, TAMANHO_BASE, TAMANHO_BASE)
        pygame.draw.rect(tela, COR_BASE, retangulo)
        pygame.draw.rect(tela, PRETO, retangulo, 2)
        
        texto = fonte.render(f"B{self.id}: {self.itens_coletados}", True, PRETO)
        tela.blit(texto, (self.x - 20, self.y - TAMANHO_BASE//2 - 20))

class Robo:
    def __init__(self, id_robo, base, env):
        self.id = id_robo
        self.base = base
        self.env = env 
        self.x = base.x
        self.y = base.y
        self.capacidade_maxima = random.randint(3, 8)
        self.capacidade = 0
        self.estado = "COLETANDO" 
        self.alvo_atual = None
        self.descarregando = False

    def calcular_distancia(self, x1, y1, x2, y2):
        return math.hypot(x2 - x1, y2 - y1)

    def processo_descarregar(self):
        self.descarregando = True
        self.estado = "DESCARREGANDO"
        print(f"[Terminal] t={self.env.now:.1f}s | Robô {self.id} chegou na Base {self.base.id} com {self.capacidade} itens.")
        yield self.env.timeout(self.capacidade * 0.5)
        self.base.itens_coletados += self.capacidade
        self.capacidade = 0
        self.estado = "COLETANDO"
        self.descarregando = False

    def atualizar(self, alvos, robos):
        if self.descarregando:
            return 

        if self.capacidade >= self.capacidade_maxima and self.estado == "COLETANDO":
            self.estado = "RETORNANDO"
            self.alvo_atual = None

        destino_x, destino_y = self.x, self.y

        if self.estado == "RETORNANDO":
            destino_x, destino_y = self.base.x, self.base.y
            if self.calcular_distancia(self.x, self.y, self.base.x, self.base.y) < TAMANHO_BASE // 2:
                self.env.process(self.processo_descarregar())
        
        elif self.estado == "COLETANDO":
            if self.alvo_atual and not self.alvo_atual.ativo:
                self.alvo_atual = None

            if not self.alvo_atual:
                alvos_disponiveis = [a for a in alvos if a.ativo]
                if alvos_disponiveis:
                    self.alvo_atual = min(alvos_disponiveis, key=lambda a: self.calcular_distancia(self.x, self.y, a.x, a.y))
            
            if self.alvo_atual:
                destino_x, destino_y = self.alvo_atual.x, self.alvo_atual.y
                if self.calcular_distancia(self.x, self.y, self.alvo_atual.x, self.alvo_atual.y) < RAIO_ROBO + RAIO_ALVO:
                    self.alvo_atual.ativo = False
                    self.alvo_atual = None
                    self.capacidade += 1

        dx = destino_x - self.x
        dy = destino_y - self.y
        distancia = math.hypot(dx, dy)

        mov_x, mov_y = 0, 0
        if distancia > 0:
            mov_x = (dx / distancia) * VELOCIDADE_ROBO
            mov_y = (dy / distancia) * VELOCIDADE_ROBO

        for outro_robo in robos:
            if outro_robo.id != self.id:
                dist = self.calcular_distancia(self.x, self.y, outro_robo.x, outro_robo.y)
                if dist < DISTANCIA_COLISAO and dist > 0:
                    sobreposicao = DISTANCIA_COLISAO - dist
                    dir_x = (self.x - outro_robo.x) / dist
                    dir_y = (self.y - outro_robo.y) / dist
                    mov_x += dir_x * sobreposicao * 0.2
                    mov_y += dir_y * sobreposicao * 0.2
                    mov_x += -dir_y * sobreposicao * 0.3
                    mov_y += dir_x * sobreposicao * 0.3

        vel_final = math.hypot(mov_x, mov_y)
        if vel_final > VELOCIDADE_ROBO:
            mov_x = (mov_x / vel_final) * VELOCIDADE_ROBO
            mov_y = (mov_y / vel_final) * VELOCIDADE_ROBO

        self.x = max(RAIO_ROBO, min(LARGURA - RAIO_ROBO, self.x + mov_x))
        self.y = max(RAIO_ROBO, min(ALTURA - RAIO_ROBO, self.y + mov_y))

    def desenhar(self, tela, fonte):
        if self.estado == "RETORNANDO":
            cor = COR_ROBO_RETORNANDO
        elif self.estado == "DESCARREGANDO":
            cor = COR_ROBO_DESCARREGANDO
        else:
            cor = COR_ROBO
            
        pygame.draw.circle(tela, cor, (int(self.x), int(self.y)), RAIO_ROBO)
        pygame.draw.circle(tela, PRETO, (int(self.x), int(self.y)), RAIO_ROBO, 2)
        
        texto = fonte.render(f"{self.capacidade}/{self.capacidade_maxima}", True, PRETO)
        rect_texto = texto.get_rect(center=(int(self.x), int(self.y)))
        tela.blit(texto, rect_texto)

def gerar_grafico(bases):
    ids_bases = [f"Base {b.id}" for b in bases]
    itens = [b.itens_coletados for b in bases]
    
    plt.figure(figsize=(10, 6))
    plt.bar(ids_bases, itens, color='skyblue', edgecolor='black')
    plt.title('Total de Itens Coletados por Robô/Base em 30 Segundos')
    plt.xlabel('Bases')
    plt.ylabel('Quantidade de Itens')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    total_geral = sum(itens)
    detalhamento_bases = "\n".join([f" - Base {b.id}: {b.itens_coletados} itens" for b in bases])
    
    texto_descritivo = (
        f"\n--- RELATÓRIO FINAL DE COLETA ---\n"
        f"A simulação foi encerrada após 30 segundos exatos de operação na área designada.\n"
        f"Neste período, os 8 robôs rastrearam alvos, realizaram manobras evasivas ao cruzar "
        f"caminhos uns com os outros e retornaram aos seus pontos de origem para o descarregamento "
        f"das cargas após atingirem suas capacidades máximas individuais.\n\n"
        f"Volume Total Transportado: {total_geral} itens.\n\n"
        f"Desempenho individual por unidade de armazenamento:\n"
        f"{detalhamento_bases}\n\n"
        f"O gráfico em exibição reflete visualmente os valores exatos de entrega listados acima."
    )
    print(texto_descritivo)
    
    plt.show()

def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Simulação de Carga e Descarga de itens")
    relogio = pygame.time.Clock()
    fonte_base = pygame.font.SysFont("Arial", 14, bold=True)
    fonte_robo = pygame.font.SysFont("Arial", 11, bold=True)

    env_simlib = simpy.Environment()

    bases = []
    espacamento = LARGURA // 5
    for i in range(NUM_ROBOS):
        if i < 4:
            x_pos = espacamento * (i + 1)
            y_pos = 80
        else:
            x_pos = espacamento * ((i - 4) + 1)
            y_pos = ALTURA - 80
        bases.append(Base(x_pos, y_pos, i + 1))

    robos = []
    for i in range(NUM_ROBOS):
        robos.append(Robo(id_robo=i+1, base=bases[i], env=env_simlib))

    alvos = [Alvo() for _ in range(30)]
    tempo_simulado = 0.0

    print("--- INICIANDO OPERAÇÃO (DURAÇÃO: 30 SEGUNDOS) ---")
    rodando = True
    while rodando and tempo_simulado < 30.0:
        dt_ms = relogio.tick(FPS) 
        dt_segundos = dt_ms / 1000.0
        tempo_simulado += dt_segundos

        env_simlib.run(until=tempo_simulado)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

        alvos_ativos = [a for a in alvos if a.ativo]
        if len(alvos_ativos) < 25 and random.random() < 0.1:
            alvos.append(Alvo())
        alvos = [a for a in alvos if a.ativo]

        for robo in robos:
            robo.atualizar(alvos, robos)

        tela.fill(CINZA)
        for base in bases: base.desenhar(tela, fonte_base)
        for alvo in alvos: alvo.desenhar(tela)
        for robo in robos: robo.desenhar(tela, fonte_robo)

        pygame.display.flip()

    pygame.quit()
    gerar_grafico(bases)
    sys.exit()

if __name__ == "__main__":
    main()