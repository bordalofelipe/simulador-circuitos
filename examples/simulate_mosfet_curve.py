import simulador
import matplotlib.pyplot as plt

## @package simulate_mosfet_curve
# Exemplo de uso do simulador
# Simulacao da curva característica de um MOSFET
# Este exemplo simula a curva característica de um MOSFET N-channel e plota Id vs Vds para um valor fixo de Vgs.

circuito = simulador.import_netlist('tests/mosfet_curve.net')  # Importa a netlist do circuito com MOSFET

print("Iniciando simulação (Newton-Raphson)...")
resultado = circuito.run()  # Roda a simulação do circuito
resultado.export('mosfet_curve.sim')  # Exporta a simulação

# Plotagem dos resultados: Entrada (1) vs Saída Retificada (2)

# Calcula Vgs e Vds para o gráfico
# d = nó 1
# g = nó 2
# s = nó 3

vgs = [vg[0] - vs[0] for vg, vs in zip(resultado.tensoes('2'), resultado.tensoes('3'))]
vds = [vd[0] - vs[0] for vd, vs in zip(resultado.tensoes('1'), resultado.tensoes('3'))]

plt.plot(vds, [-i[0]*1000 for i in resultado.tensoes(resultado.nos[-2])])
plt.xlabel('Vds (V)')
plt.ylabel('Id (mA)')
plt.show()
