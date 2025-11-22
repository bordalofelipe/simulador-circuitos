import simulador
import matplotlib.pyplot as plt

# Exemplo de uso do simulador
# Diferentes opções de gráficos disponíveis atraves da interface programatica

resultado = simulador.import_resultado('my_first_simulation.py')  # Importa resultado de uma simulação anterior


resultado.plot_xt()  # Plotar todos os nós no tempo
plt.show()
resultado.plot_xt('1')  # Plotar apenas um nó no tempo
plt.show()
resultado.plot_xt(['1', '2', '3'])  # Plotar apenas alguns nós no tempo
plt.show()
resultado.plot_xy('1', '2')  # Plotar dois nós em gráfico X-Y
