import simulador

# Exemplo de uso do simulador
# Simulacao atraves da interface programatica

circuito = simulador.Circuito('.TRAN', 0.005, 1e-05, 'BE', 1)  # Cria um objeto circuito com os parâmetros de simulação
circuito.append(simulador.FonteTensao('4000', ['1', simulador.GND], ['SIN', 1, 5, 1000, 0.002, 80, 90, 5]))  # Cria uma fonte de tensão senoidal entre os nós 1 e GND (terra)
circuito.append(simulador.Resistor('1000', ['1', '2'], 1000.0))  # Cria um resistor entre os nós 1 e 2
circuito.append(simulador.Resistor('1001', ['2', simulador.GND], 1000.0))  # Cria um resistor entre os nós 2 e GND (terra)

resultado = circuito.run()  # Roda a simulação do circuito
resultado.export('my_first_simulation.sim')  # Exporta a simulação
