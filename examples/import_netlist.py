import simulador

# Exemplo de uso do simulador
# Importação de netlist atraves da interface programatica e simulação

circuito = simulador.import_netlist('my_first_netlist.net')  # Cria um objeto circuito a partir da netlist

print('O circuito tem', len(circuito), 'componentes:')
for componente in circuito:
    print(componente)

resultado = circuito.run()
resultado.export('my_first_simulation.sim')
