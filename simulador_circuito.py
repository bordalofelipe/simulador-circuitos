import simulador as s

c = s.import_netlist('entrada.txt')

#c = s.Circuito('asdsad', 'asdad', 'asda', 'asd')

#c += Componente()
#c += Resistor()
# ...

c.export('netlist.txt')

resultado = c.run()

resultado.export('saida.txt')

resultado = s.import_resultado('entrada.txt')