import simulador

## @package import_netlist
# Exemplo de uso do simulador
# Importação de netlist atraves da interface programatica e simulação

## @brief Importa um circuito a partir de um arquivo netlist
## @param filename Variável que representa o nome do arquivo netlist a ser importado
## @return Objeto Circuito com os componentes e parâmetros de simulação carregados do arquivo
## @details Utilizado para importar um arquivo netlist no formato SPICE e criar um objeto Circuito com todos os componentes e parâmetros de simulação especificados no arquivo. Suporta todos os tipos de componentes definidos no simulador.

circuito = simulador.import_netlist('my_first_netlist.net')  # Cria um objeto circuito a partir da netlist

print('O circuito tem', len(circuito), 'componentes:')
for componente in circuito:
    print(componente)

resultado = circuito.run()
resultado.export('my_first_simulation.sim')
