import simulador
import matplotlib.pyplot as plt

# Exemplo de uso do simulador
# Simulacao de Amplificador Operacional Inversor atraves da interface programatica

# Configuração: 10ms de tempo total, passo de 10us
circuito = simulador.Circuito('.TRAN', 0.01, 1e-05, 'BE', 1)

# Senoide: 1V amplitude, 100Hz
circuito.append(simulador.FonteTensao('Vin', ['in', simulador.GND],
    ['SIN', '0', '1', '100', '0', '0', '0', '5']))

# Resistores
circuito.append(simulador.Resistor('R1', ['in', 'neg'], 1000.0))   # Entrada
circuito.append(simulador.Resistor('R2', ['neg', 'out'], 2000.0))  # Realimentação

# AmpOp Ideal
circuito.append(simulador.AmpOp('Op1', [simulador.GND, 'neg', 'out']))

print("Iniciando simulação AmpOp...")
resultado = circuito.run()
resultado.export('opamp_inverter.sim')

# Plotagem
# Esperado: Vout deve ser uma senoide invertida com 2V de amplitude (Ganho = -R2/R1 = -2)
resultado.plot_xt(['in', 'out'])
plt.show()
