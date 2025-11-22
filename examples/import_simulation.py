import simulador

# Exemplo de uso do simulador
# Importar resultado atraves da interface programatica e plotar

resultado = simulador.import_resultado('my_first_simulation.py')  # Importa resultado de uma simulação anterior

for t, nodes in resultado:  # Itera pelas tensões nodais no tempo
    print(t, nodes)

# TODO: implementar interface programática
resultado.plot_xt(['1', '2', '3'])
