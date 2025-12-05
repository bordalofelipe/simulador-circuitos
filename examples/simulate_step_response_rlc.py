import simulador

## @package simulate_step_response_rlc
# Exemplo de uso do simulador
# Simulacao de resposta ao degrau em circuito RLC atraves da interface programatica
## @brief Configura um circuito com um circuito RLC e simula a resposta ao degrau
## @param tempo_total Variável que representa o tempo total de simulação em segundos
## @param passo Variável que representa o tamanho do passo de integração em segundos. O passo de integração é o intervalo de tempo entre dois instantes de tempo consecutivos.
## @param tipo_simulacao Variável que representa o tipo de método de integração: 'BE' (Backward Euler), 'FE' (Forward Euler) ou 'TRAP' (Trapezoidal).
## @param passo_interno Variável que representa o número de passos internos por passo principal. O passo interno é o intervalo de tempo entre dois instantes de tempo consecutivos dentro de um passo principal.
## @details Utilizado para configurar um circuito com um circuito RLC e simular a resposta ao degrau.

circuito = simulador.Circuito('.TRAN', 0.005, 1e-06, 'BE', 1)  # Cria um objeto circuito com simulação transiente de 5ms e passo de 1us

circuito.append(simulador.FonteTensao('V1', ['1', simulador.GND], ['PULSE', '0', '5', '0.001', '1e-9', '1e-9', '0.01', '0.02', '1']))

circuito.append(simulador.Resistor('R1', ['1', '2'], 200.0))  # Cria um resistor de amortecimento entre os nós 1 e 2
circuito.append(simulador.Indutor('L1', ['2', '3'], 0.01))  # Cria um indutor de 10mH entre os nós 2 e 3
circuito.append(simulador.Capacitor('C1', ['3', simulador.GND], 1e-06))  # Cria um capacitor de 1uF entre o nó 3 e GND (terra)

resultado = circuito.run()  # Roda a simulação do circuito
resultado.export('rlc_step_response.sim')  # Exporta a simulação

import matplotlib.pyplot as plt
resultado.plot_xt(['1', '3'])
plt.show()
