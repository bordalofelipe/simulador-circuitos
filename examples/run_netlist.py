import simulador
import matplotlib.pyplot as plt
import os

## @package run_netlist
# Exemplo de uso do simulador
# Leitura e simulacao a partir de arquivo Netlist
## @brief Importa um circuito a partir de um arquivo netlist
## @param filename Variável que representa o nome do arquivo netlist a ser importado
## @return Objeto Circuito com os componentes e parâmetros de simulação carregados do arquivo
## @details Utilizado para importar um arquivo netlist no formato SPICE e criar um objeto Circuito com todos os componentes e parâmetros de simulação especificados no arquivo. Suporta todos os tipos de componentes definidos no simulador.

# Define o caminho do arquivo .net (está na pasta 'tests' um nível acima)
netlist_path = os.path.join('tests', 'opamp_rectifier.net')


# Verifica se o arquivo existe antes de tentar ler
if not os.path.exists(netlist_path):
    print(f"ERRO: Arquivo não encontrado em: {netlist_path}")
    exit()

print(f"Lendo netlist: {netlist_path}")

circuito = simulador.import_netlist(netlist_path)

print(f"Circuito carregado com {len(circuito)} componentes.")

# Roda a simulação definida no comando .TRAN do arquivo
print("Iniciando simulação...")
resultado = circuito.run()

# Exporta o resultado
output_file = 'resultado_netlist.sim'
resultado.export(output_file)
print(f"Resultados salvos em {output_file}")

# Plotagem automática das tensões nodais
print("Plotando tensões dos nós disponíveis...")
# Pega as chaves do resultado (nomes dos nós) excluindo a coluna de tempo 't'

# --- Lógica de Seleção de Nós ---
filename = os.path.basename(netlist_path)

if 'pulse' in filename:
    # Teste 1: sinal pulsado
    nos_para_plotar = ['1']

elif 'sinusoidal' in filename:
    # Teste 2: sinal senoidal
    nos_para_plotar = ['1']

elif 'chua' in filename:
    # Teste 3: circuito chua
    nos_para_plotar = ['1', '2']

elif 'lc' in filename:
    # Teste 4: circuito LC
    nos_para_plotar = ['6']

elif 'dc_source' in filename:
    # Teste 5: retificador meia onda
    nos_para_plotar = ['1', '2']

elif 'opamp_rectifier' in filename:
    # Teste 6: retificador onda completa
    nos_para_plotar = ['1', '4']

elif 'oscilator' in filename:
    # Teste 7: oscilador
    nos_para_plotar = ['1', '2']

else:
    # A função plot_xt identifica todos os nós disponíveis e os plota.
    nos_para_plotar = None


print(f"Arquivo: {filename} -> Plotando nós: {nos_para_plotar}")

# Plota os nós selecionados
resultado.plot_xt(nos_para_plotar)

plt.title(f"Simulação via Netlist: {os.path.basename(netlist_path)}")
plt.grid(True)
plt.show()
