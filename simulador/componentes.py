import numpy as np


## @brief Classe abstrata base para todos os componentes de circuito
# @details Esta classe define a interface comum para todos os componentes de circuito elétrico.
# Ela implementa o padrão de projeto Template Method, onde cada componente específico
# deve implementar suas próprias estampas para os diferentes métodos de integração.

# A classe utiliza análise nodal modificada para resolver circuitos, onde cada componente
# contribui com sua estampa para as matrizes de condutância (Gn) e corrente (I).

# @author Equipe do Simulador de Circuitos
# @date 2025
class Componente():

    ## Flag indicando se o componente é linear.
    _linear = True
    ## Número de nós do componente.
    _num_nos = 0
    ## Número de nós modificados.
    _num_nos_mod = 0
    ## Tamanho do passo (usado para simulação)
    passo = 0.0

    ## @brief Construtor da classe Componente
    # @param name Nome único do componente no circuito
    # @param nos Lista de nós conectados ao componente
    # @exception AssertionError Se o número de nós não corresponder ao esperado
    # @details Inicializa um componente com nome e nós específicos. Verifica se o número de nós fornecido corresponde ao número esperado para este tipo de componente.
    def __init__(self, name: str, nos: list[str]):
        self._nos_mod = []
        assert len(nos) == self._num_nos
        self.name = name
        self.nos = nos

    ## @var _nos_mod
    # Variáveis modificadas
    ## @var name
    # Nome do componente
    ## @var nos
    # Nós do componente

    ## @property linear
    # @brief Indica se o componente é linear ou não linear
    # @return True se o componente é linear, False caso contrário
    # @details Componentes lineares não requerem iteração de Newton-Raphson durante
    # a simulação, enquanto componentes não lineares (como diodos e MOSFETs) requerem.
    @property
    def linear(self):
        return self._linear

    ## @property num_nos_mod
    # @brief Retorna o número de nós extras necessários na análise nodal modificada
    # @return Número de nós extras necessários
    # @details Alguns componentes (como indutores e fontes de tensão) requerem nós
    # extras para representar correntes de malha na análise nodal modificada.
    @property
    def num_nos_mod(self):
        return self._num_nos_mod

    ## @brief Define os nós extras necessários para análise nodal modificada
    # @param nos_mod Lista dos índices dos nós extras nas matrizes Gn e I
    # @exception AssertionError Se o número de nós extras não corresponder ao esperado
    # @details Estes nós extras são usados para representar correntes de malha
    # ou outras variáveis de estado necessárias para a análise.
    def set_nos_mod(self, nos_mod: list[int]):
        assert len(nos_mod) == self._num_nos_mod
        self._nos_mod = nos_mod

    ## @brief Define as posições dos nós do componente nas matrizes do sistema
    # @param posicoes Lista das posições dos nós nas matrizes Gn e I
    # @details Estas posições são usadas para calcular corretamente as contribuições
    # do componente para as matrizes do sistema de equações.
    def set_posicao_nos(self, posicoes: list[int]):
        self._posicao_nos = posicoes

    ## @brief Retorna representação do componente como linha da netlist
    # @return String formatada representando o componente
    # @details Esta representação é usada para salvar o circuito em arquivo netlist
    # e deve seguir o formato padrão SPICE.
    def __str__(self):
        return 'Componente'

    ## @brief Atualiza as condições iniciais do componente
    # @param tensoes tensoes no instante anterior
    def update(self, tensoes):
        pass

    ## @brief Processa argumentos de fontes de tensão ou corrente e coloca nos argumentos do objeto
    def processa_argumentos_fonte(self, args):
        if args[0] == 'DC':
            self.tipo = 'DC'
            self.nivel_dc = float(args[1])
        elif args[0] == 'SIN':
            self.tipo = 'SIN'
            self.nivel_dc = float(args[1])
            self.amplitude = float(args[2])
            self.frequencia = float(args[3])
            self.atraso = float(args[4])
            self.amortecimento = float(args[5])
            self.defasagem = float(args[6])
            self.ciclos = float(args[7])
        elif args[0] == 'PULSE':
            self.tipo = 'PULSE'
            self.amplitude_1 = float(args[1])
            self.amplitude_2 = float(args[2])
            self.atraso = float(args[3])
            self.tempo_subida = float(args[4])
            self.tempo_descida = float(args[5])
            self.tempo_ligado = float(args[6])
            self.periodo = float(args[7])
            self.ciclos = float(args[8])

    ## @brief Define o valor da fonte de tensão ou corrente no instante t
    # @param t Variável que representa o instante de tempo atual
    # @return Valor da fonte de tensão ou corrente no instante t
    # @details Este valor é utilizado para calcular a contribuição da fonte na matriz de condutância e corrente.
    def calcular_valor_fonte(self, t):
        if self.tipo == 'DC':
            valor = self.nivel_dc
        elif self.tipo == 'SIN':
            tempo_total = self.atraso + self.ciclos/self.frequencia
            if t < self.atraso:
                valor = self.nivel_dc + self.amplitude*np.sin(np.pi*self.defasagem/180)
            elif t >= tempo_total:
                valor = self.nivel_dc + self.amplitude*np.exp(-self.amortecimento*(tempo_total - self.atraso))*np.sin(2*np.pi*self.frequencia*(tempo_total-self.atraso) + np.pi/180*self.defasagem)
            else:
                valor = self.nivel_dc + self.amplitude*np.exp(-self.amortecimento*(t - self.atraso))*np.sin(2*np.pi*self.frequencia*(t-self.atraso) + np.pi/180*self.defasagem)
        elif self.tipo == 'PULSE':
            T1 = self.amplitude_1
            T2 = self.amplitude_2
            TD = self.atraso
            PER = self.periodo

            TR = self.tempo_subida if self.tempo_subida > 0 else self.passo
            TF = self.tempo_descida if self.tempo_descida > 0 else self.passo

            PW = self.tempo_ligado
            N_CYCLES = self.ciclos

            T_TOTAL_SIM = TD + N_CYCLES * PER

            if t < TD:
                return T1

            if N_CYCLES > 0 and t >= T_TOTAL_SIM:
                return T1

            t_cycle = (t - TD) % PER

            T_RISE_END = TR
            T_HIGH_END = TR + PW
            T_FALL_END = TR + PW + TF

            if t_cycle < T_RISE_END:
                valor = T1 + (T2 - T1) * (t_cycle / TR)
                return valor

            elif t_cycle < T_HIGH_END:
                return T2

            elif t_cycle < T_FALL_END:
                t_on_fall = t_cycle - T_HIGH_END
                valor = T2 - (T2 - T1) * (t_on_fall / TF)
                return valor

            elif t_cycle < PER:
                return T1

            return T1

        return valor

    ## @brief Adiciona a estampa do componente usando método Backward Euler
    # @param Gn Matriz de condutância do sistema
    # @param I Vetor de correntes do sistema
    # @param t instante de tempo atual
    # @param tensoes Vetor de tensões nodais no tempo atual
    # @return Tupla (Gn, I) com as matrizes atualizadas
    # @details Método abstrato que deve ser implementado por cada componente específico.
    # O método Backward Euler é o padrão para simulação transiente.
    def estampaBE(self, Gn, I, t, tensoes):
        raise NotImplementedError

    ## @brief Adiciona a estampa do componente usando método Trapezoidal
    # @param Gn Matriz de condutância do sistema
    # @param I Vetor de correntes do sistema
    # @param t instante de tempo atual
    # @param tensoes Vetor de tensões nodais no tempo atual
    # @return Tupla (Gn, I) com as matrizes atualizadas
    # @details Método abstrato que deve ser implementado por cada componente específico.
    # O método Trapezoidal oferece melhor precisão que Backward Euler.
    def estampaTrap(self, Gn, I, t, tensoes):
        raise NotImplementedError

    ## @brief Adiciona a estampa do componente usando método Forward Euler
    # @param Gn Matriz de condutância do sistema
    # @param I Vetor de correntes do sistema
    # @param t instante de tempo atual
    # @param tensoes Vetor de tensões nodais no tempo atual
    # @return Tupla (Gn, I) com as matrizes atualizadas
    # @details Método abstrato que deve ser implementado por cada componente específico.
    # O método Forward Euler é menos estável que Backward Euler.
    def estampaFE(self, Gn, I, t, tensoes):
        raise NotImplementedError


## @brief Representa um resistor linear no circuito
# @details O resistor é um componente linear que obedece à lei de Ohm: V = R*I.
# @image html resistor.png "Estampa Resistor"
class Resistor(Componente):
    _linear = True
    _num_nos = 2
    _num_nos_mod = 0

    ## @brief Construtor do resistor
    # @param name Nome único do resistor
    # @param nos Lista com dois nós: [nó_a, nó_b]
    # @param valor Resistência em ohms
    # @details O resistor conecta dois nós e tem uma resistência específica.
    def __init__(self, name: str, nos: list[str], valor: float):
        super().__init__(name, nos)
        self.valor = valor
    ## @var valor
    # Resistência em ohms

    ## @brief Retorna representação do resistor como linha da netlist
    # @return String no formato "R<nome> <nó_a> <nó_b> <valor>"
    # @details Formato compatível com SPICE para resistor.
    def __str__(self):
        return 'R' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor)

    ## @brief Adiciona a estampa do resistor às matrizes do sistema
    # @param Gn Matriz de condutância do sistema
    # @param I Vetor de correntes do sistema
    # @param t instante de tempo atual
    # @param tensoes Vetor de tensões nodais (não usado para resistor)
    # @return Tupla (Gn, I) com as matrizes atualizadas
    # @details A estampa do resistor é a mesma para todos os métodos de integração:
    # - Gn[i,i] += 1/R
    # - Gn[i,j] -= 1/R
    # - Gn[j,i] -= 1/R
    # - Gn[j,j] += 1/R
    def estampaBE(self, Gn, I, t, tensoes):
        no_a = self._posicao_nos[0]
        no_b = self._posicao_nos[1]

        Gn[no_a, no_a] += 1/self.valor
        Gn[no_a, no_b] -= 1/self.valor
        Gn[no_b, no_a] -= 1/self.valor
        Gn[no_b, no_b] += 1/self.valor

        return Gn, I


## @brief Representa um indutor no circuito
# @details O indutor é um componente linear que armazena energia no campo magnético. Sua corrente e tensão estão relacionadas por: V = L * dI/dt.
# @image html indutor.png "Estampa do Indutor
class Indutor(Componente):
    _linear = True
    _num_nos = 2
    _num_nos_mod = 1

    ## @brief Construtor do indutor
    # @param name Nome único do indutor
    # @param nos Lista com dois nós: [nó_a, nó_b]
    # @param valor Indutância em henrys
    # @param ic Corrente inicial no indutor (padrão: 0.0 A)
    # @details O indutor conecta dois nós e tem uma indutância específica.
    def __init__(self, name: str, nos: list[str], valor: float, ic=0.0):
        super().__init__(name, nos)
        self.valor = valor
        self.ic = ic
        self.previous = ic
    ## @var valor
    # Indutância em henrys
    ## @var ic
    # Condição inicial
    ## @var previous
    # Valor da corrente no instante anterior

    ## @brief Atualiza o valor da corrente no indutor
    # @param tensoes Lista de tensões nodais no tempo atual
    # @details Utilizado para atualizar o valor da corrente no indutor baseado nas tensões nodais fora do método de iteração de Newton-Raphson.
    def update(self, tensoes):
        no_corrente = self._nos_mod[0]
        self.previous = tensoes[no_corrente]

    ## @brief Retorna representação do indutor como linha da netlist
    # @return String no formato "L<nome> <nó_a> <nó_b> <valor> [IC=<corrente_inicial>]"
    # @details Formato compatível com SPICE para indutor.
    def __str__(self):
        if self.ic != 0.0:
            return 'L' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor) + ' IC=' + str(self.ic)
        else:
            return 'L' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor)

    ## @brief Adiciona a estampa Backward Euler do indutor às matrizes do sistema
    # @param Gn Matriz de condutância do sistema
    # @param I Vetor de correntes do sistema
    # @param t instante de tempo atual
    # @param tensoes Vetor de tensões nodais no tempo atual
    # @return Tupla (Gn, I) com as matrizes atualizadas
    def estampaBE(self, Gn, I, t, tensoes):
        no_a = self._posicao_nos[0]
        no_b = self._posicao_nos[1]

        corrente_jx = self._nos_mod[0]

        Gn[no_a, corrente_jx] += 1
        Gn[no_b, corrente_jx] -= 1
        Gn[corrente_jx, no_a] -= 1
        Gn[corrente_jx, no_b] += 1
        Gn[corrente_jx, corrente_jx] += self.valor/self.passo

        if t == 0.0:
            I[corrente_jx] += (self.valor/self.passo)*self.ic
        else:
            I[corrente_jx] += (self.valor/self.passo)*self.previous

        return Gn, I


## @brief Representa um capacitor no circuito
# @details O capacitor é um componente linear que armazena energia no campo elétrico. Sua corrente e tensão estão relacionadas por: I = C * dV/dt.
# @image html capacitor.png "Estampa do Capacitor"
class Capacitor(Componente):
    _linear = True
    _num_nos = 2
    _num_nos_mod = 0

    ## @brief Construtor do capacitor
    # @param name Nome único do capacitor
    # @param nos Lista com dois nós: [nó_a, nó_b]
    # @param valor Capacitância em farads
    # @param ic Corrente no capacitor (valor inicial: 0.0 A)
    # @details O capacitor conecta dois nós e tem uma capacitância específica.
    def __init__(self, name: str, nos: list[str], valor: float, ic=0.0):
        super().__init__(name, nos)
        self.valor = valor
        self.ic = ic
        self.previous = ic
    ## @var valor
    # Capacitância em farads
    ## @var ic
    # Condição inicial
    ## @var previous
    # Valor da tensões no instante anterior

    ## @brief Retorna representação do capacitor como linha da netlist
    # @return String no formato "C<nome> <nó_a> <nó_b> <valor> [IC=<corrente_inicial>]"
    # @details Formato compatível com SPICE para capacitor.
    def __str__(self):
        if self.ic == 0.0:
            return 'C' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor)
        else:
            return 'C' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor) + ' IC=' + str(self.ic)

    ## @brief Atualiza o valor da tensão no capacitor
    # @param tensoes Lista de tensões nodais no tempo atual
    # @details Utilizado para atualizar o valor da tensão no capacitor baseado nas tensões nodais fora do método de iteração de Newton-Raphson.
    def update(self, tensoes):
        no_a = self._posicao_nos[0]
        no_b = self._posicao_nos[1]
        self.previous = (tensoes[no_a] - tensoes[no_b])

    ## @brief Adiciona a estampa Backward Euler do capacitor às matrizes do sistema
    # @param Gn Matriz de condutância do sistema
    # @param I Vetor de correntes do sistema
    # @param t instante de tempo atual
    # @param tensoes Vetor de tensões nodais no tempo atual
    # @return Tupla (Gn, I) com as matrizes atualizadas
    def estampaBE(self, Gn, I, t, tensoes):
        no_a = self._posicao_nos[0]
        no_b = self._posicao_nos[1]

        condutancia = self.valor / self.passo
        vab = self.previous

        Gn[no_a, no_a] += condutancia
        Gn[no_a, no_b] -= condutancia
        Gn[no_b, no_a] -= condutancia
        Gn[no_b, no_b] += condutancia

        if t == 0.0:
            I[no_a] += condutancia*self.ic
            I[no_b] -= condutancia*self.ic
        else:
            I[no_a] += condutancia*vab
            I[no_b] -= condutancia*vab
        return Gn, I


## @brief Representa um resistor não linear com característica de 3 segmentos no circuito
# @details O resistor não linear é modelado por uma curva tensão-corrente definida por 4 pontos (V1,I1), (V2,I2), (V3,I3), (V4,I4), formando 3 segmentos lineares. A condutância é calculada dinamicamente baseada na tensão atual.
# @image html resistor_nao_linear.png "Característica do Resistor Não Linear"
class ResistorNaoLinear(Componente):
    _linear = False
    _num_nos = 2
    _num_nos_mod = 0

    ## @brief Construtor do resistor não linear
    # @param name Nome único do resistor
    # @param nos Lista com dois nós: [nó_a, nó_b]
    # @param v1 Tensão do primeiro ponto em volts
    # @param i1 Corrente do primeiro ponto em aperes
    # @param v2 Tensão do segundo ponto em volts
    # @param i2 Corrente do segundo ponto em aperes
    # @param v3 Tensão do terceiro ponto em volts
    # @param i3 Corrente do terceiro ponto em aperes
    # @param v4 Tensão do quarto ponto em volts
    # @param i4 Corrente do quarto ponto em aperes
    # @details Os pontos devem estar ordenados por tensão crescente: V1 < V2 < V3 < V4
    def __init__(self, name: str, nos: list[str], v1: float, i1: float, v2: float, i2: float, v3: float, i3: float, v4: float, i4: float):
        super().__init__(name, nos)
        self.v1 = v1
        self.i1 = i1
        self.v2 = v2
        self.i2 = i2
        self.v3 = v3
        self.i3 = i3
        self.v4 = v4
        self.i4 = i4
        self.condutancia = Resistor(name + 'R', nos, 0)
        self.fonte = FonteCorrente(name + 'I', nos, ['DC', '0'])
    ## @var v1
    # Tensão do primeiro ponto em volts
    ## @var i1
    # Corrente do primeiro ponto em aperes
    ## @var v2
    # Tensão do segundo ponto em volts
    ## @var i2
    # Corrente do segundo ponto em aperes
    ## @var v3
    # Tensão do terceiro ponto em volts
    ## @var i3
    # Corrente do terceiro ponto em aperes
    ## @var v4
    # Tensão do quarto ponto em volts
    ## @var i4
    # Corrente do quarto ponto em aperes

    ## @brief Define as posições dos nós do resistor não linear nas matrizes do sistema
    # @param posicoes Lista das posições dos nós nas matrizes do sistema
    # @details Utilizado para calcular corretamente as contribuições do resistor não linear para as matrizes.
    def set_posicao_nos(self, posicoes: list[int]):
        self.condutancia.set_posicao_nos(posicoes)
        self.fonte.set_posicao_nos(posicoes)
        super().set_posicao_nos(posicoes)

    ## @brief Retorna representação do resistor não linear como linha da netlist
    # @return String no formato "N<nome> <nó_a> <nó_b> <v1> <i1> <v2> <i2> <v3> <i3> <v4> <i4>"
    # @details Formato específico para resistor não linear com 4 pontos.
    def __str__(self):
        return 'N' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.v1) + ' ' + str(self.i1) + ' ' + str(self.v2) + ' ' + str(self.i2) + ' ' + str(self.v3) + ' ' + str(self.i3) + ' ' + str(self.v4) + ' ' + str(self.i4)

    ## @brief Adiciona a estampa do resistor não linear às matrizes do sistema
    # @param Gn Matriz de condutância do sistema
    # @param I Vetor de correntes do sistema
    # @param t instante de tempo atual
    # @param tensoes Vetor de tensões nodais no tempo atual
    # @return Tupla (Gn, I) com as matrizes atualizadas
    def estampaBE(self, Gn, I, t, tensoes):
        no_a = self._posicao_nos[0]
        no_b = self._posicao_nos[1]

        vab = tensoes[no_a] - tensoes[no_b]
        if vab > self.v3:
            g0 = (self.i4 - self.i3)/(self.v4 - self.v3)
            i0 = self.i4 - g0*self.v4
        elif vab > self.v2:
            g0 = (self.i3 - self.i2)/(self.v3 - self.v2)
            i0 = self.i3 - g0*self.v3
        else:
            g0 = (self.i2 - self.i1)/(self.v2 - self.v1)
            i0 = self.i2 - g0*self.v2

        self.condutancia.valor = 1/g0
        self.fonte.args = ['DC', i0]
        self.fonte.nivel_dc = i0

        Gn, I = self.condutancia.estampaBE(Gn, I, t, tensoes)
        Gn, I = self.fonte.estampaBE(Gn, I, t, tensoes)
        return Gn, I


## @brief Representa uma fonte de tensão controlada por tensão no circuito
# @details A fonte de tensão controlada por tensão é um componente linear que
# gera uma tensão de saída proporcional à tensão de entrada. A relação é:
# V_out = A * V_in, onde A é o ganho de tensão.
# @image html fonte_tensao_tensao.png "Estampa da Fonte de Tensão Controlada por Tensão"
class FonteTensaoTensao(Componente):
    _linear = True
    _num_nos = 4
    _num_nos_mod = 1

    ## @brief Construtor da fonte de tensão controlada por tensão
    # @param name Nome único da fonte
    # @param nos Lista com os nomes dos quatro nós: [nó_a, nó_b, nó_c, nó_d]
    # @param valor Ganho de tensão
    # @details A fonte conecta quatro nós: dois para a saída e dois para o controle.
    def __init__(self, name: str, nos: list[str], valor: float):
        super().__init__(name, nos)
        self.valor = valor
    ## @var valor
    # Ganho de tensão

    ## @brief Retorna representação da fonte como linha da netlist
    # @return String no formato "E<nome> <nó_a> <nó_b> <nó_c> <nó_d> <ganho>"
    # @details Formato compatível com SPICE para fonte de tensão controlada por tensão.
    def __str__(self):
        return 'E' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor)

    ## @brief Adiciona a estampa da fonte de tensão controlada por tensão
    # @param Gn Matriz de condutância do sistema
    # @param I Vetor de correntes do sistema
    # @param t instante de tempo atual
    # @param tensoes Vetor de tensões nodais no tempo atual
    # @return Tupla (Gn, I) com as matrizes atualizadas
    def estampaBE(self, Gn, I, t, tensoes):
        no_a = self._posicao_nos[0]
        no_b = self._posicao_nos[1]
        no_c = self._posicao_nos[2]
        no_d = self._posicao_nos[3]

        corrente_jx = self._nos_mod[0]

        Gn[no_a, corrente_jx] += 1
        Gn[no_b, corrente_jx] -= 1
        Gn[corrente_jx, no_c] += self.valor
        Gn[corrente_jx, no_d] -= self.valor
        Gn[corrente_jx, no_a] -= 1
        Gn[corrente_jx, no_b] += 1

        return Gn, I


## @brief Representa uma fonte de corrente controlada por corrente no circuito
# @details A fonte de corrente controlada por corrente é um componente
# linear que define a corrente de saída como proporcional a uma corrente de controle:
# I_out = F * I_in.
# @image html fonte_corrente_corrente.png "Estampa da Fonte de Corrente Controlada por Corrente"
class FonteCorrenteCorrente(Componente):
    _linear = True
    _num_nos = 4
    _num_nos_mod = 1

    ## @brief Construtor da Fonte de corrente controlada por corrente
    # @param name Nome único da fonte
    # @param nos Lista com quatro nós: [nó_a, nó_b, nó_c, nó_d]
    # @param valor Ganho de corrente
    # @details A fonte impõe uma corrente entre os nós a e b proporcional à corrente entre c e d.
    def __init__(self, name: str, nos: list[str], valor: float):
        super().__init__(name, nos)
        self.valor = valor

    ## @var valor
    #  Ganho de corrente

    ## @brief Retorna representação da fonte como linha da netlist
    # @return String no formato "F<nome> <nó_a> <nó_b> <nó_c> <nó_d> <ganho>"
    # @details Formato compatível com SPICE para fonte de tensão controlada por tensão.
    def __str__(self):
        return 'F' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor)

    ## @brief Adiciona a estampa Backward Euler da fonte de corrente controlada por corrente às matrizes do sistema.
    # @param Gn Matriz de condutância do sistema
    # @param I Vetor de correntes do sistema
    # @param t instante de tempo atual (não usado para resistor)
    # @param tensoes Vetor de tensões nodais (não usado para resistor)
    # @return Tupla (Gn, I) com as matrizes atualizadas
    def estampaBE(self, Gn, I, t, tensoes):
        no_a = self._posicao_nos[0]
        no_b = self._posicao_nos[1]
        no_c = self._posicao_nos[2]
        no_d = self._posicao_nos[3]

        corrente_jx = self._nos_mod[0]

        Gn[no_a, corrente_jx] -= self.valor
        Gn[no_b, corrente_jx] += self.valor
        Gn[no_c, corrente_jx] += 1
        Gn[no_d, corrente_jx] -= 1
        Gn[corrente_jx, no_c] -= 1
        Gn[corrente_jx, no_d] += 1

        return Gn, I


## @brief Representa uma fonte de corrente controlada por tensão no circuito.
# @details A fonte de corrente controlada por tensão é um componente linear
# que obedece à relação de transcondutância: I = G * V.
# @image html fonte_corrente_tensao.png "Estampa da Fonte de Corrente Controlada por Tensão"
class FonteCorrenteTensao(Componente):
    _linear = True
    _num_nos = 4
    _num_nos_mod = 0

    ## @brief Construtor da Fonte de corrente controlada por tensão
    # @param name Nome único da fonte
    # @param nos Lista com quatro nós: [nó_a, nó_b, nó_c, nó_d]
    # @param valor Transcondutância em Siemens
    # @details A fonte impõe uma corrente de saída proporcional à tensão diferencial nos nós de controle.
    def __init__(self, name: str, nos: list[str], valor: float):
        super().__init__(name, nos)
        self.valor = valor

    ## @var valor
    # Transcondutância em Siemens

    ## @brief Retorna representação da fonte como linha da netlist
    # @return String no formato "G<nome> <nó_a> <nó_b> <nó_c> <nó_b> <ganho>"
    # @details Formato compatível com SPICE para fonte de tensão controlada por tensão.
    def __str__(self):
        return 'G' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor)

    ## @brief Adiciona a estampa da fonte de corrente controlada por tensão
    # @param Gn Matriz de condutância do sistema
    # @param I Vetor de correntes do sistema
    # @param t instante de tempo atual
    # @param tensoes Vetor de tensões nodais no tempo atual
    # @return Tupla (Gn, I) com as matrizes atualizadas
    def estampaBE(self, Gn, I, t, tensoes):
        no_a = self._posicao_nos[0]
        no_b = self._posicao_nos[1]
        no_c = self._posicao_nos[2]
        no_d = self._posicao_nos[3]

        Gn[no_a, no_c] += self.valor
        Gn[no_a, no_d] -= self.valor
        Gn[no_b, no_c] -= self.valor
        Gn[no_b, no_d] += self.valor

        return Gn, I


## @brief Representa uma fonte de tensão controlada por corrente no circuito
# @details A fonte de tensão controlada por corrente é um componente linear que
# gera uma tensão de saída proporcional à corrente de entrada. A relação é:
# V_out = A * I_in, onde A é o ganho de tensão.
# @image html fonte_tensao_corrente.png "Estampa da Fonte de Tensão Controlada por Corrente"
class FonteTensaoCorrente(Componente):
    _linear = True
    _num_nos = 4
    _num_nos_mod = 2

    ## @brief Construtor da Fonte de tensão controlada por corrente
    # @param name Nome único da fonte
    # @param nos Lista com quatro nós: [nó_a, nó_b, nó_c, nó_d]
    # @param valor Transresistência em Ohms
    # @details A fonte impõe uma tensão de saída proporcional à corrente que flui pelos nós de controle.
    def __init__(self, name: str, nos: list[str], valor: float):
        super().__init__(name, nos)
        self.valor = valor
    ## @var valor
    # Transresistência em Ohms

    ## @brief Retorna representação da fonte como linha da netlist
    # @return String no formato "H<nome> <nó_a> <nó_b> <nó_c> <nó_d> <ganho>"
    # @details Formato compatível com SPICE para fonte de tensão controlada por tensão.
    def __str__(self):
        return 'H' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor)

    ## @brief Adiciona a estampa da fonte de tensão controlada por corrente
    # @param Gn Matriz de condutância do sistema
    # @param I Vetor de correntes do sistema
    # @param t instante de tempo atual
    # @param tensoes Vetor de tensões nodais no tempo atual
    # @return Tupla (Gn, I) com as matrizes atualizadas
    def estampaBE(self, Gn, I, t, tensoes):
        no_a = self._posicao_nos[0]
        no_b = self._posicao_nos[1]
        no_c = self._posicao_nos[2]
        no_d = self._posicao_nos[3]

        corrente_jx = self._nos_mod[0]
        corrente_jy = self._nos_mod[1]

        Gn[no_a, corrente_jx] -= 1
        Gn[no_b, corrente_jx] += 1
        Gn[no_c, corrente_jy] -= 1
        Gn[no_d, corrente_jy] += 1
        Gn[corrente_jx, no_a] += 1
        Gn[corrente_jx, no_b] -= 1
        Gn[corrente_jy, no_c] += 1
        Gn[corrente_jy, no_d] -= 1
        Gn[corrente_jy, corrente_jx] += self.valor

        return Gn, I


## @brief Representa um diodo no circuito
# @details O diodo é um componente não linear que obedece a relação:
# I_out = I_in * (exp(V/Vt) -1).
# @image html diodo.png "Característica do Diodo"
class Diodo(Componente):
    _linear = False
    _num_nos = 2
    _num_nos_mod = 0

    ## @brief Construtor do Diodo
    # @param name Nome único do diodo
    # @param nos [nó_a, nó_b] nós do diodo
    # @details O diodo conecta dois nós permitindo o fluxo de corrente preferencialmente
    # do ânodo para o cátodo.
    def __init__(self, name: str, nos: list[str]):
        super().__init__(name, nos)
        self.condutancia = Resistor(name + 'R', nos, 0)
        self.fonte = FonteCorrente(name + 'I', nos, ['DC', '0'])

    ## @brief Define as posições dos nós do diodo nas matrizes do sistema
    # @param posicoes Lista das posições dos nós nas matrizes do sistema
    # @details Utilizado para calcular corretamente as contribuições do diodo para as matrizes.
    def set_posicao_nos(self, posicoes: list[int]):
        self.condutancia.set_posicao_nos(posicoes)
        self.fonte.set_posicao_nos(posicoes)
        super().set_posicao_nos(posicoes)

    ## @brief Retorna representação do diodo como linha da netlist
    # @return String no formato "D<nome> <nó_a> <nó_b>"
    # @details Formato específico para diodo com dois terminais.
    def __str__(self):
        return 'D' + self.name + ' ' + ' '.join(str(no) for no in self.nos)

    ## @brief Adiciona a estampa linearizada do diodo às matrizes do sistema.
    # @param Gn Matriz de condutância do sistema
    # @param I Vetor de correntes do sistema
    # @param t Instante de tempo atual
    # @param tensoes Vetor de tensões nodais
    # @return Tupla (Gn, I) com as matrizes atualizadas
    def estampaBE(self, Gn, I, t, tensoes):
        no_a = self._posicao_nos[0]
        no_b = self._posicao_nos[1]

        vab = tensoes[no_a] - tensoes[no_b]

        if vab > 0.9:
            vab = 0.9

        g0 = 3.7751345e-14*np.exp(vab/25e-3)/25e-3
        g0 = float(g0)
        if g0 == 0:
            print(f'AVISO: g0 = {g0} ; vab = {vab} ; np.exp(...) = {np.exp(vab/25e-3)} ; np.exp(...)/25e-3 = {np.exp(vab/25e-3)/25e-3}')
        id = 3.7751345e-14*(np.exp(vab/25e-3)-1)-g0*vab
        id = float(id)

        if g0 != 0:
            self.condutancia.valor = 1/g0
        self.fonte.args = ['DC', id]
        self.fonte.processa_argumentos_fonte(self.fonte.args)

        if g0 != 0:
            Gn, I = self.condutancia.estampaBE(Gn, I, t, tensoes)
        Gn, I = self.fonte.estampaBE(Gn, I, t, tensoes)
        return Gn, I


## @brief Representa um amplificador operacional ideal no circuito
# @details O amplificador operacional é um componente linear que
# gera uma tensão de saída proporcional à tensão diferencial de entrada. A relação é:
# V_out = A * (V+ - V-), onde A é o ganho de tensão.
# @image html amp_op.png "Estampa Amplificador Operacional"
class AmpOp(Componente):
    _linear = True
    _num_nos = 3
    _num_nos_mod = 1

    ## @brief Construtor do Amplificador Operacional
    # @param name Nome único do ampop
    # @param nos Lista com três nós: [nó_a, nó_b, nó_c]
    # @param valor Ganho de malha aberta
    # @details O ampop amplifica a diferença de tensão entre as entradas (V+ - V-) aplicando-a na saída.
    def __init__(self, name: str, nos: list[str]):
        super().__init__(name, nos)

    ## @brief Retorna representação do amplificador operacional ideal como linha da netlist
    # @return String no formato "O<nome> <nó_a> <nó_b> <nó_c>"
    # @details Formato compatível com SPICE para para amplificador operacional ideal com dois terminais.
    def __str__(self):
        return 'O' + self.name + ' ' + ' '.join(str(no) for no in self.nos)

    ## @brief Adiciona a estampa do amplificador operacional às matrizes do sistema.
    # @param Gn Matriz de condutância do sistema (insere a relação de ganho ou curto-virtual)
    # @param I Vetor de correntes do sistema (geralmente inalterado para o modelo linear)
    # @param t Instante de tempo atual (não utilizado, componente atemporal)
    # @param tensoes Vetor de tensões nodais (não utilizado para o modelo linear ideal)
    # @return Tupla (Gn, I) com as matrizes atualizadas
    def estampaBE(self, Gn, I, t, tensoes):
        no_a = self._posicao_nos[0]
        no_b = self._posicao_nos[1]
        no_c = self._posicao_nos[2]

        corrente_jx = self._nos_mod[0]

        Gn[no_c, corrente_jx] += 1

        Gn[corrente_jx, no_a] -= 1
        Gn[corrente_jx, no_b] += 1

        return Gn, I


## @brief Representa um MOSFET no circuito
# @details O MOSFET é um componente não linear que gera uma corrente de dreno com relação de: Id = K * (Vgs - Vth)^2
# @brief Transistor MOSFET (nível 1).
# @details Componente não linear de 3 terminais (Dreno, Porta, Fonte). Seu comportamento é dividido em três regiões: corte, triodo e saturação. A estampa é baseada no modelo companheiro do componente, que consiste em uma fonte de corrente controlada por tensão (Gm*Vgs), uma condutância de saída (Gds) e uma fonte de corrente equivalente (Ieq) para linearizar o comportamento em torno do ponto de operação atual.
# @image html mosfet.png "Característica do MOSFET"
class Mosfet(Componente):
    _num_nos = 3  # Dreno, Porta, Fonte
    _num_nos_mod = 0
    _linear = False

    ## @brief Construtor do MOSFET.
    # @param name Nome do componente.
    # @param nos Lista de nós no formato ['D', 'G', 'S'].
    # @param tipo Tipo do MOSFET: 'N' ou 'P'
    # @param W parâmetro W do MOSFET.
    # @param L parâmetro L do MOSFET.
    # @param lbda parâmetro lambda do MOSFET.
    # @param K parâmetro K do MOSFET.
    # @param Vth parâmetro Vth (tensão) do MOSFET.
    def __init__(self, name: str, nos: list[str], tipo: str, W: float, L: float, lbda: float, K: float, Vth: float):
        super().__init__(name, nos)
        assert tipo == 'N' or tipo == 'P'
        self.tipo = tipo
        self.W = W
        self.L = L
        self.lbda = lbda
        self.K = K
        self.Vth = Vth
        self.beta = self.K * (self.W / self.L)
        self.transcondutancia = FonteCorrenteTensao(name, [nos[0], nos[2], nos[1], nos[2]], 0.0)
        self.fonte = FonteCorrente(name, [nos[0], nos[2]], ['DC', 0.0])
        self.condutancia = Resistor(name, [nos[0], nos[2]], 1000)

    ## @var tipo
    # Tipo do MOSFET: 'N' ou 'P'
    ## @var
    # W parâmetro W do MOSFET.
    ## @var
    # L parâmetro L do MOSFET.
    ## @var
    # lbda parâmetro lambda do MOSFET.
    ## @var
    # K parâmetro K do MOSFET.
    ## @var Vth
    # parâmetro Vth (tensão) do MOSFET.

    ## @brief Define as posições dos nós do MOSFET nas matrizes do sistema
    # @param posicoes Lista das posições dos nós nas matrizes do sistema
    # @details Utilizado para calcular corretamente as contribuições do MOSFET para as matrizes.
    def set_posicao_nos(self, posicoes: list[int]):
        self.first_iter = True
        self.transcondutancia.set_posicao_nos([posicoes[0], posicoes[2], posicoes[1], posicoes[2]])
        self.fonte.set_posicao_nos([posicoes[0], posicoes[2]])
        self.condutancia.set_posicao_nos([posicoes[0], posicoes[2]])
        super().set_posicao_nos(posicoes)

    ## @brief Retorna representação do MOSFET como linha da netlist
    # @return String no formato "M<nome> <nó-drain> <nó-gate> <nó-source> <tipo> <W> <L> <lambda> <K> <Vth>"
    # @details Formato específico para MOSFET tipo P ou tipo N.
    def __str__(self):
        return 'M' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + self.tipo + ' ' + str(self.W) + ' ' + str(self.L) + ' ' + str(self.lbda) + ' ' + str(self.K) + ' ' + str(self.Vth)

    ## @brief Gera a estampa do MOSFET para o método de Euler para trás.
    # @details Utiliza as tensões da iteração anterior de Newton-Raphson
    # para calcular a região de operação e os parâmetros do modelo companheiro.
    def estampaBE(self, Gn, I, t, tensoes):
        d = self._posicao_nos[0]
        g = self._posicao_nos[1]
        s = self._posicao_nos[2]

        vd = tensoes[d]
        vg = tensoes[g]
        vs = tensoes[s]

        # Lógica de Inversão e Definição de Vgs/Vds (Baseado na Imagem 2)
        # Permite que o transistor conduza nos dois sentidos (Source vira Dreno)

        if self.tipo == 'N':
            if vd < vs:
                # Inverte Dreno e Fonte virtualmente
                print('AVISO: trocando drain por source')
                vd, vs = vs, vd

            # Cálculo dos potenciais efetivos
            if self.first_iter:
                vgs = 2.0
                self.first_iter = False
            else:
                vgs = vg - vs
            vds = vd - vs
        elif self.tipo == 'P':
            if vd > vs:
                # No PMOS, se D > S, inverte (condução reversa)
                print('AVISO: trocando drain por source')
                vd, vs = vs, vd

            if self.first_iter:
                vgs = -2.0
                self.first_iter = False
            else:
                vgs = -(vg - vs)
            vds = -(vd - vs)

        # Cálculo das Correntes e Condutâncias
        # Nota: Corrigi os erros de digitação do pdf (vds^2 no triodo e falta de 1+ no lambda)

        Vt = self.Vth
        Beta = self.beta   # Ajuste para modelo SPICE (KP/2)
        Lambda = self.lbda

        id_calc = 0.0
        gm = 0.0
        gds = 0.0

        # -- Corte --
        if vgs <= Vt:
            id_calc = 0.0
            gm = 0.0
            gds = 0.0

        else:
            Vov = vgs - Vt  # Overdrive Voltage
            termo_lambda = (1 + Lambda * vds)

            # -- Saturação --
            if vds > Vov:
                # Fórmula corrigida:
                id_calc = Beta * (Vov ** 2) * termo_lambda
                gm = 2 * Beta * Vov * termo_lambda
                gds = Beta * (Vov ** 2) * Lambda

            # -- Triodo --
            else:
                # Fórmula corrigida: [2(Vgs-Vt)Vds - Vds^2]
                parentesis_triodo = (2 * Vov * vds) - (vds ** 2)

                id_calc = Beta * parentesis_triodo * termo_lambda
                gm = Beta * (2 * vds) * termo_lambda
                gds = Beta * (2*Vov - 2*vds + 4*Lambda*Vov*vds - 3*Lambda*(vds**2))

        # Ajuste de sinal específico para PMOS (devido à convenção de corrente saindo do Dreno)
        if self.tipo == 'P':
            id_calc = -id_calc

        self.transcondutancia.valor = gm
        self.fonte.nivel_dc = id_calc - gm*vgs - gds*vds
        if gds != 0:
            self.condutancia.valor = 1/gds

        Gn, I = self.transcondutancia.estampaBE(Gn, I, t, tensoes)
        Gn, I = self.fonte.estampaBE(Gn, I, t, tensoes)
        if gds != 0:
            Gn, I = self.condutancia.estampaBE(Gn, I, t, tensoes)

        return Gn, I


## @brief Representa uma fonte de corrente no circuito
# @details A fonte de corrente é um componente que gera uma corrente constante.
# @image html fonte_corrente.png "Estampa da Fonte de Corrente"
class FonteCorrente(Componente):
    _linear = True
    _num_nos = 2
    _num_nos_mod = 0

    ## @brief Construtor da Fonte de corrente
    # @param name Nome único da fonte
    # @param nos Lista com dois nós: [nó_a, nó_b]
    # @param args Parâmetros em formato netlist
    # @details A fonte injeta uma corrente constante fluindo do nó a para o nó b.
    def __init__(self, name: str, nos: list[str], args: list):
        super().__init__(name, nos)
        self.processa_argumentos_fonte(args)
        self.args = args

    ## @var args
    # Parâmetros em formato netlist
    # @details Para fontes, temos três possibilidades para args:
    # - DC <valor> : Fonte DC de <valor> amperes
    # - SIN <valor-dc> <amplitude> <frequência> <atraso> <amortecimento> <defasagem> <ciclos> : Fonte senoidal
    # - PULSE <amplitude-1> <amplitude-2> <atraso> <tempo-subida <tempo-descida> <tempo-ligado> <período> <ciclos> : Fonte pulsada

    ## @brief Retorna representação da fonte de corrente como linha da netlist
    # @return String no formato "I<nome> <nó_a> <nó_b> <args>"
    # @details Para fontes, temos três possibilidades para args:
    # - DC <valor> : Fonte DC de <valor> amperes
    # - SIN <valor-dc> <amplitude> <frequência> <atraso> <amortecimento> <defasagem> <ciclos> : Fonte senoidal
    # - PULSE <amplitude-1> <amplitude-2> <atraso> <tempo-subida <tempo-descida> <tempo-ligado> <período> <ciclos> : Fonte pulsada
    def __str__(self):
        return 'I' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + ' '.join(str(arg) for arg in self.args)

    ## @brief Retorna representação da fonte de corrente como linha da netlist
    # @return String no formato "I<nome> <nó_a> <nó_b> <valor>"
    # @details Formato compatível com SPICE para fonte de corrente.
    def estampaBE(self, Gn, I, t, tensoes):
        corrente = self.calcular_valor_fonte(t)

        no_a = self._posicao_nos[0]
        no_b = self._posicao_nos[1]

        I[no_a] -= corrente
        I[no_b] += corrente
        return Gn, I


## @brief Representa uma fonte de tensão no circuito
# @details A fonte de tensão é um componente que gera uma tensão constante.
# @image html fonte_tensao.png "Estampa da Fonte de Tensão"
class FonteTensao(Componente):
    _linear = True
    _num_nos = 2
    _num_nos_mod = 1

    ## @brief Construtor da Fonte de tensão
    # @param name Nome único da fonte
    # @param nos Lista com dois nós: [nó_a, nó_b]
    # @param valor Tensão em Volts
    # @details A fonte fixa uma diferença de potencial constante entre os nós (Va - Vb = valor).
    def __init__(self, name: str, nos: list[str], args: list):
        super().__init__(name, nos)
        self.processa_argumentos_fonte(args)
        self.args = args

    ## @var args
    # Parâmetros em formato netlist
    # @details Para fontes, temos três possibilidades para args:
    # - DC <valor> : Fonte DC de <valor> amperes
    # - SIN <valor-dc> <amplitude> <frequência> <atraso> <amortecimento> <defasagem> <ciclos> : Fonte senoidal
    # - PULSE <amplitude-1> <amplitude-2> <atraso> <tempo-subida <tempo-descida> <tempo-ligado> <período> <ciclos> : Fonte pulsada

    ## @brief Retorna representação da fonte de corrente como linha da netlist
    # @return String no formato "V<nome> <nó_a> <nó_b> <args>"
    # @details Para fontes, temos três possibilidades para args:
    # - DC <valor> : Fonte DC de <valor> volts
    # - SIN <valor-dc> <amplitude> <frequência> <atraso> <amortecimento> <defasagem> <ciclos> : Fonte senoidal
    # - PULSE <amplitude-1> <amplitude-2> <atraso> <tempo-subida <tempo-descida> <tempo-ligado> <período> <ciclos> : Fonte pulsada
    def __str__(self):
        return 'V' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + ' '.join(str(arg) for arg in self.args)

    ## @brief Retorna representação da fonte de tensão como linha da netlist
    # @return String no formato "V<nome> <nó_a> <nó_b> <valor>"
    # @details Formato compatível com SPICE para fonte de tensão.
    def estampaBE(self, Gn, I, t, tensoes):
        tensao = self.calcular_valor_fonte(t)

        no_a = self._posicao_nos[0]
        no_b = self._posicao_nos[1]

        corrente_jx = self._nos_mod[0]

        Gn[no_a, corrente_jx] += 1
        Gn[no_b, corrente_jx] -= 1
        Gn[corrente_jx, no_a] -= 1
        Gn[corrente_jx, no_b] += 1

        I[corrente_jx] -= tensao
        return Gn, I
