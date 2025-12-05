import simulador
import matplotlib.pyplot as plt

## @package plotting
# Exemplo de uso do simulador
# Diferentes opções de gráficos disponíveis atraves da interface programatica
## @brief Importa um resultado de uma simulação anterior
## @param filename Variável que representa o nome do arquivo de resultado a ser importado
## @return Objeto Resultado com os dados da simulação carregados do arquivo
## @details Utilizado para importar um resultado de uma simulação anterior e plotar as tensões nodais no tempo.

resultado = simulador.import_resultado('my_first_simulation.py')  # Importa resultado de uma simulação anterior


resultado.plot_xt()  # Plotar todos os nós no tempo
plt.show()
resultado.plot_xt('1')  # Plotar apenas um nó no tempo
plt.show()
resultado.plot_xt(['1', '2', '3'])  # Plotar apenas alguns nós no tempo
plt.show()
resultado.plot_xy('1', '2')  # Plotar dois nós em gráfico X-Y
