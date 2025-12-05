import simulador
import matplotlib.pyplot as plt

## @package simulate_ampop_inverter
# Exemplo de uso do simulador
# Simulacao de Amplificador Operacional Inversor atraves da interface programatica
## @brief Configura um circuito com um amplificador operacional inversor
## @param tempo_total Variável que representa o tempo total de simulação em segundos
## @param passo Variável que representa o tamanho do passo de integração em segundos. O passo de integração é o intervalo de tempo entre dois instantes de tempo consecutivos.
## @param tipo_simulacao Variável que representa o tipo de método de integração: 'BE' (Backward Euler), 'FE' (Forward Euler) ou 'TRAP' (Trapezoidal). O método de integração é o algoritmo usado para calcular as tensões nodais ao longo do tempo.
## @param passo_interno Variável que representa o número de passos internos por passo principal. O passo interno é o intervalo de tempo entre dois instantes de tempo consecutivos dentro de um passo principal.
## @details Utilizado para configurar um circuito com um amplificador operacional inversor e simular o circuito.

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
