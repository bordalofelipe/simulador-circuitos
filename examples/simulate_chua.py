import simulador
import matplotlib.pyplot as plt

# Exemplo baseado na Netlist fornecida pelo usuário
# Objetivo: Simular circuito não-linear com IC=1V nos capacitores

# Configura simulação: 1000s de tempo total, passo de 0.1s
# .TRAN 1000 0.1 BE 1
circuito = simulador.Circuito('.TRAN', 1000.0, 0.1, 'BE', 1)

# Componentes Lineares
# R1004 1 2 1.9
circuito.append(simulador.Resistor('1004', ['1', '2'], 1.9))

# L3000 1 0 1
circuito.append(simulador.Indutor('3000', ['1', simulador.GND], 1.0))

# C2000 2 0 0.31 IC=1
# Para simular IC=1V, injetamos um pulso de carga rápido.
# Q = C*V = 0.31 * 1 = 0.31 Coulombs.
# Usando um pulso de 0.1s (1 passo), a corrente deve ser 3.1A.
circuito.append(simulador.Capacitor('2000', ['2', simulador.GND], 0.31))
circuito.append(simulador.FonteCorrente('IC_C2', ['2', simulador.GND], 
    ['PULSE', '0', '3.1', '0', '1e-9', '1e-9', '0.1', '1001', '1']))

# C2001 1 0 1 IC=1
# Q = C*V = 1.0 * 1 = 1.0 Coulombs.
# Usando um pulso de 0.1s, a corrente deve ser 10A.
circuito.append(simulador.Capacitor('2001', ['1', simulador.GND], 1.0))
circuito.append(simulador.FonteCorrente('IC_C1', ['1', simulador.GND], 
    ['PULSE', '0', '10.0', '0', '1e-9', '1e-9', '0.1', '1001', '1']))

# N9900 2 0 -2 1.1 -1 0.7 1 -0.7 2 -1.1
# Resistor Não Linear (Piecewise Linear)
# Parâmetros passados como floats diretos
circuito.append(simulador.ResistorNaoLinear('9900', ['2', simulador.GND], 
    -2.0,  1.1,  # V1, I1
    -1.0,  0.7,  # V2, I2
     1.0, -0.7,  # V3, I3
     2.0, -1.1   # V4, I4
))

print("Iniciando simulação da Netlist customizada...")
resultado = circuito.run()
resultado.export('custom_netlist.sim')

# Plotagem no Tempo
plt.figure(1)
resultado.plot_xt(['1', '2'])
plt.title("Tensões Nodal no Tempo")
plt.xlabel("Tempo (s)")
plt.ylabel("Tensão (V)")
plt.grid(True)

# Plotagem no Plano de Fase (V1 vs V2) para ver ciclos limites/caos
plt.figure(2)
resultado.plot_xy('1', '2')
plt.title("Plano de Fase (V1 vs V2)")
plt.xlabel("Tensão Nó 1 (V)")
plt.ylabel("Tensão Nó 2 (V)")
plt.grid(True)

plt.show()