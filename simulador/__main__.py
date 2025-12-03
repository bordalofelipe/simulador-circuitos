import simulador
import sys

if len(sys.argv) != 3:
    print('Uso: python -m simulador <arquivo-netlist> <arquivo-saida>')
    print('Executa a simulação para a netlist armazenada em <arquivo-netlist> e salva os resultados em <arquivo-saida>')
    sys.exit()
c = simulador.import_netlist(sys.argv[1])
resultado = c.run()
resultado.export(sys.argv[2])
