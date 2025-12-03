import numpy as np
from simulador.componentes import *

'''!
@var GND
    No terra
'''
GND = '0'


class Circuito():
    '''!
    @brief Representa um circuito elétrico completo com seus componentes e parâmetros de simulação
    @details Esta classe gerencia um circuito elétrico, seus componentes e executa simulações transientes
    usando análise nodal modificada. Suporta componentes lineares e não lineares, utilizando
    métodos de integração numérica (Backward Euler, Forward Euler, Trapezoidal) e iteração
    de Newton-Raphson para componentes não lineares.

    @author Equipe do Simulador de Circuitos
    @date 2025
    '''
    def __init__(self, simulacao: str, tempo_total: float, passo: float, tipo_simulacao: str, passo_interno: int):
        '''!
        @brief Construtor da classe Circuito
        @param simulacao Tipo de simulação (ex: '.TRAN' para transiente, '.DC' para análise de corrente contínua)
        @param tempo_total Tempo total de simulação em segundos
        @param passo Tamanho do passo de integração em segundos. O passo de integração é o intervalo de tempo entre dois instantes de tempo consecutivos.
        @param tipo_simulacao Tipo de método de integração: 'BE' (Backward Euler), 'FE' (Forward Euler) ou 'TRAP' (Trapezoidal). O método de integração é o algoritmo usado para calcular as tensões nodais ao longo do tempo.
        @param passo_interno Número de passos internos por passo principal. O passo interno é o intervalo de tempo entre dois instantes de tempo consecutivos dentro de um passo principal.
        @details Inicializa um circuito vazio com os parâmetros de simulação especificados.
        '''
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

    def __iter__(self):
        return iter(self.__componentes)

    def append(self, componente):
        '''!
        @brief Adiciona um componente ao circuito
        @param componente Componente a ser adicionado ao circuito
        @details Adiciona um componente à lista de componentes do circuito.
        '''
        if (isinstance(componente, Componente)):
            self.__componentes.append(componente)

    def remove(self, componente):
        return self.__componentes.remove(componente)

    def pop(self, index):
        return self.__delitem__(index)

    def __popular_nos(self):
        '''!
        @brief Popula a lista de nós do circuito a partir dos componentes
        @exception Exception Se o circuito não tiver nó terra
        @details Identifica todos os nós únicos dos componentes e garante que o nó terra (GND) seja o primeiro.
        '''
        self.__nos = [GND]  # garante que o no terra eh o primeiro
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
        '''!
        @brief Executa a simulação transiente do circuito
        @return Objeto Resultado contendo as tensões nodais ao longo do tempo
        @exception Exception Se a simulação falhar após M_MAX tentativas aleatórias
        @details Executa a simulação transiente usando análise nodal modificada. Para circuitos não lineares,
        utiliza iteração de Newton-Raphson. Suporta múltiplos métodos de integração numérica.
        '''
        self.__popular_nos()
        print('INFO: Circuito com ' + str(self.__nos) + ' nos')
        nao_linear = False
        for com in self.__componentes:  # aloca cada no para cada componente
            if not com.linear:
                nao_linear = True
            com.set_posicao_nos([self.__nos.index(item) for item in com.nos])
            # Analise modificada
            print('INFO: ' + str(com) + ' precisa de ' + str(com.num_nos_mod) + ' nos extras. Alocando nos: ', end=' ')
            com.set_nos_mod([len(self.__nos) + i for i in range(com.num_nos_mod)])  # informa indices
            print(com._nos_mod)
            for i in range(com.num_nos_mod):  # adiciona nos modificados na lista de todos os nos
                # self.__nos.append('mod' + str(len(self.__nos)))
                self.__nos.append('J' + str(len(self.__nos)) + str(com).split(' ')[0])  # sintaxe moreirao

        num_vars = len(self.__nos) - 1  # Número de variáveis (nós - 1, pois terra é 0)
        print('INFO: Circuito final com ' + str(num_vars) + ' variaveis')
        if nao_linear:
            print('INFO: Analise nao linear necessaria')

        # --- Parâmetros da Análise no Tempo ---
        N_MAX = 20
        M_MAX = 100
        STEP_FACTOR = 1e9
        TOLERANCIA = 0.00001

        resultado = Resultado(self.__nos[1:], [], [])  # pula o no terra
        # Simulação no tempo
        tempo = 0
        np.random.seed(512)
        while tempo < self.tempo_total:

            if tempo == 0:
                max_internal_step = 1
                passo = self.passo / STEP_FACTOR
            else:
                passo = self.passo

            previous = list(np.random.rand(num_vars))
            # Interno
            passo_interno_atual = 0
            while passo_interno_atual < max_internal_step:

                # Newton-Raphson
                stop_newton_raphson = False
                n_guesses = 0
                n_newton_raphson = 0
                while not stop_newton_raphson:

                    if nao_linear and n_newton_raphson == N_MAX:
                        if n_guesses >= M_MAX:
                            raise Exception(f"ERRO: Simulação falhou em t={tempo}s. O sistema é impossível de ser solucionado após {M_MAX} tentativas aleatórias.")
                        # Gera novo chute aleatório
                        print(f"AVISO: Falha na convergência (N={N_MAX}). Gerando chute aleatório {n_guesses+1}/{M_MAX}.")
                        previous = list(np.random.rand(num_vars))
                        n_guesses += 1
                        n_newton_raphson = 0

                    # --- Montagem da Estampa (dentro do loop N-R) ---
                    matrizGn = np.zeros((len(self.__nos), len(self.__nos)))
                    matrizI = np.zeros((len(self.__nos), 1))

                    for com in self.__componentes:
                        com.passo = passo  # IMPORTANTE: Usar o 'passo' calculado (pode ser o passo menor)

                        # As estampas não lineares usam 'previous' (o chute, x(t))
                        if self.tipo_simulacao == 'BE':
                            matrizGn, matrizI = com.estampaBE(matrizGn, matrizI, tempo, previous)
                        elif self.tipo_simulacao == 'FE':
                            matrizGn, matrizI = com.estampaFE(matrizGn, matrizI, tempo, previous)
                        elif self.tipo_simulacao == 'TRAP':
                            matrizGn, matrizI = com.estampaTrap(matrizGn, matrizI, tempo, previous)

                    # print(self.__nos)
                    # print(matrizGn, matrizI)

                    # Resolve o sistema Ax = b
                    tensoes = np.linalg.solve(matrizGn[1:, 1:], matrizI[1:])
                    tensoes = tensoes.flatten()  # Garante que é um vetor 1D
                    tensoes = [0.0] + list(tensoes)  # Ajusta o tensoes para considerar o nó terra

                    # Calcula a tolerância (máximo erro entre os nós)
                    tolerance = max([abs(i-j) for i, j in zip(tensoes, previous)])
                    # print(tolerance)
                    if nao_linear and (tolerance > TOLERANCIA):
                        # Não convergiu, próxima iteração
                        previous = tensoes
                        n_newton_raphson += 1
                    else:
                        stop_newton_raphson = True  # Convergiu ou é linear
                # --- Fim do loop Newton-Raphson ---

                # atualiza condicoes iniciais
                for com in self.__componentes:
                    com.update(tensoes)
                passo_interno_atual += 1

            # --- Fim do loop interno ---
            resultado.append(tempo, tensoes[1:])  # pula o no terra

            tempo += self.passo

        # --- Fim do loop do tempo ---

        print("INFO: Simulação concluída.")
        return resultado

    def export(self, filename: str):
        '''!
        @brief Exporta o circuito para um arquivo netlist
        @param filename Nome do arquivo onde salvar a netlist
        @details Salva o circuito no formato netlist compatível com SPICE, incluindo todos os componentes
        e parâmetros de simulação.
        '''
        with open(filename, 'w') as f:
            self.__popular_nos()
            f.write(str(len(self.__nos)-1) + '\n')  # por causa do no terra, tirar 1
            for com in self.__componentes:
                f.write(str(com) + '\n')
            f.write(self.simulacao + ' ' + str(self.tempo_total) + ' ' + str(self.passo) + ' ' + self.tipo_simulacao + ' ' + str(self.passo_interno))


def import_netlist(filename: str):
    '''!
    @brief Importa um circuito a partir de um arquivo netlist
    @param filename Nome do arquivo netlist a ser importado
    @return Objeto Circuito com os componentes e parâmetros de simulação carregados do arquivo
    @details Lê um arquivo netlist no formato SPICE e cria um objeto Circuito com todos os componentes
    e parâmetros de simulação especificados no arquivo. Suporta todos os tipos de componentes
    definidos no simulador.
    '''
    with open(filename) as f:
        line = f.readline()  # nao usamos primeira linha
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
                componentes.append(ResistorNaoLinear(c[0][1:], [c[1], c[2]], float(c[3]), float(c[4]), float(c[5]), float(c[6]), float(c[7]), float(c[8]), float(c[9]), float(c[10])))
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
                componentes.append(Mosfet(c[0][1:], [c[1], c[2], c[3]], c[4], float(c[5]), float(c[6]), float(c[7]), float(c[8]), float(c[9])))
            elif tipo == 'I':
                componentes.append(FonteCorrente(c[0][1:], [c[1], c[2]], c[3:]))
            elif tipo == 'V':
                componentes.append(FonteTensao(c[0][1:], [c[1], c[2]], c[3:]))
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
    '''!
    @brief Representa os resultados de uma simulação de circuito
    @details Esta classe armazena e gerencia os resultados de uma simulação transiente, incluindo
    as tensões nodais em cada instante de tempo. Fornece métodos para acessar, visualizar e exportar
    os dados da simulação.

    @author Equipe do Simulador de Circuitos
    @date 2025
    '''
    def __init__(self, nos: list[str], t: list[float], resultado: list[list[float]]):
        '''!
        @brief Construtor da classe Resultado
        @param nos Lista de nós do circuito
        @param t Lista de instantes de tempo
        @param resultado Lista de listas contendo as tensões nodais em cada instante de tempo
        @details Inicializa um objeto Resultado vazio ou com dados pré-existentes.
        '''
        self.__nos = nos
        self.__t = t
        self.__resultado = resultado

    @property
    def nos(self):
        '''!
        @brief Retorna a lista de nós
        '''
        return self.__nos

    @property
    def t(self):
        '''!
        @brief Retorna a lista de instantes de tempo
        '''
        return self.__t

    def tensoes(self, nos: str | list[str] | None = None):
        '''!
        @brief Obtem vetor de tensões nodais de todos ou alguns nós.
        @param nos Nó ou lista de nós para obter as tensões nodais. Por padrão, retorna as tensões de todos os nós
        @return Lista das tensões nodais
        @details O formato da saída é:
        [
            [tensao_no_1, tensao_no_2, tensao_no_3, ...], # instante t0
            [tensao_no_1, tensao_no_2, tensao_no_3, ...], # instante t1
            [tensao_no_1, tensao_no_2, tensao_no_3, ...], # instante t2
            ...
        ]
        '''
        if nos is None:
            return self.__resultado
        else:
            if type(nos) == str:
                nos = [nos]
            wanted = []
            for no in nos:
                wanted.append(self.__nos.index(no))
            filtrado = []
            for node in self.__resultado:
                node_filtrado = []
                for no_filtrado in wanted:
                    node_filtrado.append(node[no_filtrado])
                filtrado.append(node_filtrado)
            return filtrado

    def plot_xt(self, nos: str | list[str] | None = None, xlabel='Tempo (s)', ylabel='Tensão (V)'):
        '''!
        @brief Fazer gráfico das tensões nodais no tempo
        @param nos Nó ou lista de nós para colocar no gráfico. Por padrão, plota as tensões de todos os nós
        @returns Objeto de gráfico do Matplotlib
        '''
        import matplotlib.pyplot as plt
        if nos is None:
            plot = plt.plot(self.t, self.tensoes(nos), label=self.__nos)
        else:
            plot = plt.plot(self.t, self.tensoes(nos), label=nos)
        plt.legend()
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        return plot

    def plot_xy(self, no_x: str, no_y: str):
        '''!
        @brief Fazer gráfico X-Y das tensões nodais
        @param no_x Nó do eixo X
        @param no_y Nó do eixo Y
        @returns Objeto de gráfico do Matplotlib
        '''
        import matplotlib.pyplot as plt
        plot = plt.plot(self.tensoes(no_x), self.tensoes(no_y))
        plt.xlabel(no_x)
        plt.ylabel(no_y)
        return plot

    def __setitem__(self, index, tuple):
        assert len(tuple) == 2
        t = tuple[0]
        resultado = tuple[1]
        assert len(resultado) == len(self.__nos)
        self.__t[index] = t
        self.__resultado[index] = resultado

    def __getitem__(self, index):
        return self.__t[index], self.__resultado[index]

    def __delitem__(self, index):
        return self.__t.pop(index), self.__resultado.pop(index)

    def __len__(self):
        return len(self.__resultado)

    def __iter__(self):
        return iter(zip(self.__t, self.__resultado))

    def append(self, t: float, resultado: list[float]):
        assert len(resultado) == len(self.__nos)
        self.__t.append(t)
        self.__resultado.append(resultado)

    def remove(self, t):
        index = self.__t.index(t)
        return self.__delitem__(index)

    def pop(self, index):
        return self.__delitem__(index)

    def export(self, filename: str):
        with open(filename, 'w') as f:
            f.write('t ')
            f.write(' '.join(self.__nos))
            f.write('\n')
            for t, r in zip(self.__t, self.__resultado):
                f.write(str(t) + ' ')
                f.write(' '.join(str(round(i, 6)) for i in r))
                f.write('\n')
        return self.__resultado

    def to_numpy(self):
        return False

    def to_pandas(self):
        return False


def import_resultado(filename: str):
    '''!
    @brief Importa resultados de simulação a partir de um arquivo
    @param filename Nome do arquivo contendo os resultados da simulação
    @return Objeto Resultado com os dados carregados do arquivo
    @details Lê um arquivo de resultados no formato gerado pelo método export da classe Resultado,
    contendo as tensões nodais em cada instante de tempo da simulação.
    '''
    with open(filename) as f:
        line = f.readline()
        nos = line.replace('\n', '').split(' ')[1:]
        resultado = Resultado(nos, [], [])
        line = f.readline()
        while line != '':
            r = line.replace('\n', '').split(' ')
            r = filter(lambda i: i != '', r)
            r = [float(i) for i in r]
            t, r = r[0], r[1:]
            resultado.append(t, r)
            line = f.readline()
        return resultado


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print('Uso:', sys.argv[0], '<arquivo-netlist> <arquivo-saida>')
        print('Executa a simulação para a netlist armazenada em <arquivo-netlist> e salva os resultados em <arquivo-saida>')
        sys.exit()
    c = import_netlist(sys.argv[1])
    resultado = c.run()
    resultado.export(sys.argv[2])
