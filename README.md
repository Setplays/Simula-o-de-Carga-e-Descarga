# Simulação Híbrida de Coleta Robótica (Pygame + SimPy)

Este projeto é um modelo de simulação computacional que combina **física contínua em 2D** com a lógica de **eventos discretos**. Ele simula o comportamento estocástico de uma frota de 8 robôs autônomos encarregados de coletar alvos em um ambiente fechado e descarregá-los em suas respectivas bases.

A simulação opera por exatos **30 segundos**, após os quais gera um relatório final no terminal e um gráfico analítico da produtividade de cada unidade.

---

## ⚙️ Principais Funcionalidades

* **Arquitetura Híbrida:** Utiliza `pygame` para a cinemática, renderização visual e checagem de colisões a 60 FPS, trabalhando em paralelo com `simpy` para gerenciar as filas e o tempo das ações logísticas (descarregamento).
* **Manobras Evasivas (Anticolisão):** Sistema de física baseado em repulsão vetorial e força tangencial, garantindo que os robôs "escorreguem" uns pelos outros de forma fluida sem colidir.
* **Capacidade Estocástica:** Cada robô recebe um limite de carga aleatório (entre 3 e 8 itens) no início da simulação, tornando o desempenho e o tráfego de retorno dinâmicos.
* **Bases Exclusivas:** 8 bases de descarregamento distribuídas estrategicamente pelas extremidades da tela, com rotas individuais para cada agente.
* **Visualização de Dados:** Geração automática de um gráfico de barras via `matplotlib` ao término da simulação, ilustrando o total de itens entregues por cada base.

---

## 🛠️ Tecnologias e Dependências

O projeto foi desenvolvido em **Python 3**. As seguintes bibliotecas externas são necessárias para a execução:

* `pygame` (Interface gráfica e loop contínuo)
* `simpy` (Motor de eventos discretos / logística)
* `matplotlib` (Geração do gráfico de resultados)

### Instalação

Abra o seu terminal e execute o comando abaixo para instalar todas as dependências de uma vez:

```bash
pip install pygame simpy matplotlib
