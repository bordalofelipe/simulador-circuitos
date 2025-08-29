from simulador.componentes import *

'''
No terra
'''
GND = '0'

class Circuito():
    def __init__(self, simulacao: str, tempo_total: float, passo: float, tipo_simulacao: str, passo_interno: int):
        self.simulacao = simulacao
        self.tempo_total = tempo_total
        self.tipo_simulacao = tipo_simulacao
        self.passo = passo
        self.passo_interno = passo_interno
        # define algumas coisas internas
        self.__componentes: list[Componente] = []
        self.__nos = []

    def __setitem__(self, index, componente):
        if (isinstance(componente, Componente)):
            self.__componentes[index] = componente

    def __getitem__(self, index):
        return self.__componentes[index]

    def __delitem__(self, index):
        return self.__componentes.pop(index)

    def __len__(self):
        return len(self.__componentes)

    def append(self, componente):
        if (isinstance(componente, Componente)):
            self.__componentes.append(componente)

    def remove(self, componente):
        return self.__componentes.__delitem__(componente)

    def pop(self, index):
        return self.__delitem__(index)

    def __popular_nos(self):
        self.__nos = [GND] # garante que o no terra eh o primeiro
        hasGround = False
        for comp in self.__componentes:
            nos = comp.nos
            for no in nos:
                if no not in self.__nos:
                    self.__nos.append(no)
                if no == GND:
                    hasGround = True
        if not hasGround:
            raise Exception('Circuito sem no terra')

    def run(self):
        self.__popular_nos()
        print('Circuito com ' + str(self.__nos) + ' nos')
        nao_linear = False
        for com in self.__componentes: # aloca cada no para cada componente
            if not com.linear:
                nao_linear = True
            com.set_posicao_nos([self.__nos.index(item) for item in com.nos])
            ## Analise modificada
            print(str(com) + ' precisa de ' + str(com.num_nos_mod) + ' nos extras. Alocando nos: ', end=' ')
            com.set_nos_mod([len(self.__nos) + i for i in range(com.num_nos_mod)]) # informa indices
            print(com._nos_mod)
            for i in range(com.num_nos_mod): # adiciona nos modificados na lista de todos os nos
                #self.__nos.append('mod' + str(len(self.__nos)))
                self.__nos.append('J' + str(len(self.__nos)) + str(com).split(' ')[0]) # sintaxe moreirao
        print('Circuito final com ' + str(len(self.__nos)) + ' nos')
        if nao_linear:
            print('Analise nao linear necessaria')
        resultado = Resultado(self.__nos, [], []) # pula o no terra
        return resultado

    def export(self, filename: str):
        with open(filename, 'w') as f:
            self.__popular_nos()
            f.write(str(len(self.__nos)-1) + '\n') # por causa do no terra, tirar 1
            for com in self.__componentes:
                f.write(str(com) + '\n')
            f.write(self.simulacao + ' ' + str(self.tempo_total) + ' ' + str(self.passo) + ' ' + self.tipo_simulacao + ' ' + str(self.passo_interno))

def import_netlist(filename: str):
    with open(filename) as f:
        line = f.readline() # nao usamos primeira linha
        componentes = []
        line = f.readline()
        while line != '':
            line = line.replace('\n', '')
            tipo = line[0]
            c = line.split(' ')
            if tipo == 'R':
                componentes.append(Resistor(c[0][1:], [c[1], c[2]], float(c[3])))
            elif tipo == 'L':
                if len(c) == 5:
                    ic = c[4].replace('IC=', '')
                    componentes.append(Indutor(c[0][1:], [c[1], c[2]], float(c[3]), float(ic)))
                else:
                    componentes.append(Indutor(c[0][1:], [c[1], c[2]], float(c[3])))
            elif tipo == 'C':
                if len(c) == 5:
                    ic = c[4].replace('IC=', '')
                    componentes.append(Capacitor(c[0][1:], [c[1], c[2]], float(c[3]), float(ic)))
                else:
                    componentes.append(Capacitor(c[0][1:], [c[1], c[2]], float(c[3])))
            elif tipo == 'N':
                componentes.append(ResistorNaoLinear(c[0][1:], [c[1], c[2]], float(c[3]), float(c[4]), float(c[5]), float(c[6]), float(c[6]), float(c[7]), float(c[8]), float(c[9])))
            elif tipo == 'E':
                componentes.append(FonteTensaoTensao(c[0][1:], [c[1], c[2], c[3], c[4]], float(c[5])))
            elif tipo == 'F':
                componentes.append(FonteCorrenteCorrente(c[0][1:], [c[1], c[2], c[3], c[4]], float(c[5])))
            elif tipo == 'G':
                componentes.append(FonteCorrenteTensao(c[0][1:], [c[1], c[2], c[3], c[4]], float(c[5])))
            elif tipo == 'H':
                componentes.append(FonteTensaoCorrente(c[0][1:], [c[1], c[2], c[3], c[4]], float(c[5])))
            elif tipo == 'O':
                componentes.append(AmpOp(c[0][1:], [c[1], c[2], c[3]]))
            elif tipo == 'D':
                componentes.append(Diodo(c[0][1:], [c[1], c[2]]))
            elif tipo == 'M':
                raise NotImplementedError
                componentes.append(Mosfet(c[0][1:], [c[1], c[2], c[3]], c[4], c[5], c[6], c[7], c[8], c[9]))
            elif tipo == 'I':
                componentes.append(FonteCorrente(c[0][1:], [c[1], c[2]], c[2:]))
            elif tipo == 'V':
                componentes.append(FonteTensao(c[0][1:], [c[1], c[2]], c[2:]))
            elif tipo == '.':
                # arquivo acabou!
                break
            line = f.readline()
        params = line.split(' ')
        circuit = Circuito(params[0], float(params[1]), float(params[2]), params[3], int(params[4]))
        for comp in componentes:
            circuit.append(comp)
        return circuit
    return Circuito()

class Resultado():
    def __init__(self, nos: list[str], t: list[float], resultado: list[list[float]]):
        self.__nos = nos
        self.__t = t
        self.__resultado = resultado

    def __setitem__(self, index, resultado):
        assert len(resultado) == len(self.__nos)
        self.__resultado[index] = resultado

    def __getitem__(self, index):
        return self.__resultado[index]

    def __delitem__(self, index):
        return self.__resultado.pop(index)

    def __len__(self):
        return len(self.__resultado)

    def append(self, t: float, resultado: list[float]):
        assert len(resultado) == len(self.__nos)
        self.__t.append(t)
        self.__resultado.append(resultado)

    def remove(self, resultado):
        return self.__resultado.__delitem__(resultado)

    def pop(self, index):
        return self.__delitem__(index)

    def export(self, filename: str):
        with open(filename, 'w') as f:
            f.write('t ')
            f.write(' '.join(self.__nos))
            f.write('\n')
            for t, r in zip(self.__t, self.__resultado):
                f.write(str(t) + ' ')
                f.write(' '.join(str(i) for i in r))
                f.write('\n')
        return self.__resultado

    def to_numpy(self):
        return False

    def to_pandas(self):
        return False

def import_resultado(filename: str):
    with open(filename) as f:
        line = f.readline()
        nos = line.split(';')[1:]
        resultado = Resultado(nos, [], [])
        line = f.readline()
        while line != '':
            r = line.split(';')
            r = [float(i) for i in r]
            t, r = r[0], r[1:]
            resultado.append(t, r)
            line = f.readline()
        return resultado


if __name__ == '__main__':
    c = import_netlist('entrada.txt')
    resultado = c.run()
    resultado.export('saida.txt')