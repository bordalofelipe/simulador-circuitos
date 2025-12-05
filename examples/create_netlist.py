import simulador

## @package create_netlist
# Exemplo de uso do simulador
# Criacao de netlist atraves da interface programática

## @brief Cria um circuito com os componentes e parâmetros de simulação
## @param simulacao Tipo de simulação, '.TRAN' para transiente, '.DC' para análise de corrente contínua
## @param tempo_total Variável que representa o tempo total de simulação em segundos
## @param passo Variável que representa o tamanho do passo de integração em segundos. O passo de integração é o intervalo de tempo entre dois instantes de tempo consecutivos.
## @param tipo_simulacao Variável que representa o tipo de método de integração: 'BE' (Backward Euler), 'FE' (Forward Euler) ou 'TRAP' (Trapezoidal). O método de integração é o algoritmo usado para calcular as tensões nodais ao longo do tempo.
## @param passo_interno Variável que representa o número de passos internos por passo principal. O passo interno é o intervalo de tempo entre dois instantes de tempo consecutivos dentro de um passo principal.
## @details Utilizada para armazenar os parâmetros de simulação e inicializar um circuito vazio com os parâmetros de simulação especificados.

circuito = simulador.Circuito('.TRAN', 0.005, 1e-05, 'BE', 1)  # Cria um objeto circuito com os parâmetros de simulação
circuito.append(simulador.FonteTensao('4000', ['1', simulador.GND], ['SIN', 1, 5, 1000, 0.002, 80, 90, 5]))  # Cria uma fonte de tensão senoidal entre os nós 1 e GND (terra)
circuito.append(simulador.Resistor('1000', ['1', '2'], 1000.0))  # Cria um resistor entre os nós 1 e 2
circuito.append(simulador.Resistor('1001', ['2', simulador.GND], 1000.0))  # Cria um resistor entre os nós 2 e GND (terra)
circuito.export('my_first_netlist.net')  # Exporta o circuito para uma netlist
