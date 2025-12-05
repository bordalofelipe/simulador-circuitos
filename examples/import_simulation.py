import simulador

## @package import_simulation
# Exemplo de uso do simulador
# Importar resultado atraves da interface programatica e plotar
## @brief Importa um resultado de uma simulação anterior
## @param filename Variável que representa o nome do arquivo de resultado a ser importado
## @return Objeto Resultado com os dados da simulação carregados do arquivo
## @details Utilizado para importar um resultado de uma simulação anterior e plotar as tensões nodais no tempo.

resultado = simulador.import_resultado('my_first_simulation.py')  # Importa resultado de uma simulação anterior

for t, nodes in resultado:  # Itera pelas tensões nodais no tempo
    print(t, nodes)

# TODO: implementar interface programática
resultado.plot_xt(['1', '2', '3'])
