import simulador
import matplotlib.pyplot as plt

# Exemplo de uso do simulador
# Simulacao de retificador de meia onda com componente nao-linear (Diodo)

circuito = simulador.Circuito('.TRAN', 0.02, 1e-05, 'BE', 1)  # Cria um objeto circuito com simulação transiente de 20ms

# Parâmetros: Offset, Amplitude, Freq, Delay, Damping, Phase, Cycles
circuito.append(simulador.FonteTensao('Vin', ['1', simulador.GND], ['SIN', '0', '10', '60', '0', '0', '0', '5']))

circuito.append(simulador.Diodo('D1', ['1', '2']))  # Cria um diodo entre os nós 1 e 2
circuito.append(simulador.Resistor('Rload', ['2', simulador.GND], 1000.0))  # Cria um resistor de carga de 1kOhm

print("Iniciando simulação (Newton-Raphson)...")
resultado = circuito.run()  # Roda a simulação do circuito
resultado.export('diode_rectifier.sim')  # Exporta a simulação

# Plotagem dos resultados: Entrada (1) vs Saída Retificada (2)
resultado.plot_xt(['1', '2'])
plt.show()
