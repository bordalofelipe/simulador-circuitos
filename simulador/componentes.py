class Componente():
    '''!
    @brief Classe abstrata de componente
    Esta classe é herdada por componentes específicos (ex: Resistor, Capacitor, etc.), que implementam, principalmente, suas respectivas estampas
    '''
    _linear = True
    _num_nos = 0
    _num_nos_mod = 0
    passo = 0.0 # passo de tempo, definido por Circuito.run()
    def __init__(self, name: str, nos: list[str]):
        '''!
        @brief Construtor da classe
        @param name nome do componente
        @param nos lista de nos do componente
        '''
        self._nos_mod = []
        assert len(nos) == self._num_nos
        self.name = name
        self.nos = nos

    @property
    def linear(self):
        '''!
        @brief Retorna se componente é linear
        '''
        return self._linear

    @property
    def num_nos_mod(self):
        '''!
        @brief Retorna numero de nos necessarios na analise modificada
        '''
        return self._num_nos_mod

    def set_nos_mod(self, nos_mod: list[int]):
        '''!
        @brief Aloca nos necessarios na analise modificada
        @param nos_mod lista dos nos para analise modificada (posicoes nas matrizes Gn e In)
        '''
        assert len(nos_mod) == self._num_nos_mod
        self._nos_mod = nos_mod

    def set_posicao_nos(self, posicoes: list[int]):
        '''!
        @brief Aloca nos necessarios
        @param posicoes lista das posicoes nas matrizes Gn e In dos nos deste componente
        '''
        self._posicao_nos = posicoes

    def __str__(self):
        '''!
        @brief Retorna representação do objeto como linha da netlist
        '''
        return 'Componente' 

    def estampaBE(self, Gn, I, tensoes):
        raise NotImplementedError
    def estampaTrap(self, Gn, I, tensoes):
        raise NotImplementedError
    def estampaFE(self, Gn, I, tensoes):
        raise NotImplementedError

class Resistor(Componente):
    '''!
    @brief Esta classe implementa o Resistor e sua estampa
    '''
    _linear = True
    _num_nos = 2
    _num_nos_mod = 0
    def __init__(self, name: str, nos: list[str], valor: float):
        '''!
        @brief Construtor do Resistor
        @param nos [no1, no2] nos do Resistor
        @param valor resistencia
        '''
        super().__init__(name, nos)
        self.valor = valor

    def __str__(self):
        return 'R' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor)

    def estampaBE(self, Gn, I, tensoes):
        Gn[self._posicao_nos[0], self._posicao_nos[0]] += 1/self.valor
        Gn[self._posicao_nos[0], self._posicao_nos[1]] -= 1/self.valor
        Gn[self._posicao_nos[1], self._posicao_nos[0]] -= 1/self.valor
        Gn[self._posicao_nos[1], self._posicao_nos[1]] += 1/self.valor
        return Gn, I

class Indutor(Componente):
    '''!
    @brief Esta classe implementa o Indutor e sua estampa
    '''
    _linear = True
    _num_nos = 2
    _num_nos_mod = 1
    def __init__(self, name: str, nos: list[str], valor: float, ic=0.0):
        '''!
        @brief construtor do Indutor
        @param nos [no_mais, no_menos] nos do Indutor
        @param valor indutancia
        @param ic = 0.0 valor inicial
        '''
        super().__init__(name, nos)
        self.valor = valor
        self.ic = ic

    def __str__(self):
        if self.ic == 0.0:
            return 'L' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor)
        else:
            return 'L' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor) + ' IC=' + str(self.ic)

    def estampaBE(self, Gn, I, tensoes):
        Gn[self._posicao_nos[0], self._nos_mod[0]] = -1
        Gn[self._posicao_nos[1], self._nos_mod[0]] = 1
        Gn[self._nos_mod[0], self._posicao_nos[0]] = 1
        Gn[self._nos_mod[0], self._posicao_nos[1]] = -1
        Gn[self._nos_mod[0], self._nos_mod[0]] = (self.valor/self.passo)*self.ic

        I[self._nos_mod[0]] = self.valor/self.passo
        return Gn, I

class Capacitor(Componente):
    '''!
    @brief Esta classe implementa o Capacitor e sua estampa
    '''
    _linear = True
    _num_nos = 2
    _num_nos_mod = 0
    def __init__(self, name: str, nos: list[str], valor: float, ic=0.0):
        '''!
        @brief construtor do Capacitor
        @param nos [no_mais, no_menos] nos do Capacitor
        @param valor capacitancia
        @param ic = 0.0 valor inicial
        '''
        super().__init__(name, nos)
        self.valor = valor
        self.ic = ic

    def __str__(self):
        if self.ic == 0.0:
            return 'C' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor)
        else:
            return 'C' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor) + ' IC=' + str(self.ic)

    def estampaBE(self, Gn, I, tensoes):
        Gn[self._posicao_nos[0], self._posicao_nos[0]] += self.valor/self.passo
        Gn[self._posicao_nos[0], self._posicao_nos[1]] -= self.valor/self.passo
        Gn[self._posicao_nos[1], self._posicao_nos[0]] -= self.valor/self.passo
        Gn[self._posicao_nos[1], self._posicao_nos[1]] += self.valor/self.passo

        I[self._posicao_nos[0]] += (self.valor/self.passo)*self.ic
        I[self._posicao_nos[1]] -= (self.valor/self.passo)*self.ic
        return Gn, I

class ResistorNaoLinear(Componente):
    '''!
    @brief Esta classe implementa o Resistor Nao Linear com 3 segmentos e sua estampa
    '''
    _linear = False
    _num_nos = 2
    _num_nos_mod = 0
    def __init__(self, name: str, nos: list[str], v1: float, i1: float, v2: float, i2: float, v3: float, i3: float, v4: float, i4: float):
        '''!
        @brief construtor do Resistor Nao Linear
        Os pares Vi, Ii sao pontos da curva tensão vs corrente
        @param nos [no_mais, no_menos] nos do Resistor Nao Linear
        '''
        super().__init__(name, nos)
        self.v1 = v1
        self.i1 = i1
        self.v2 = v2
        self.i2 = i2
        self.v3 = v3
        self.i3 = i3
        self.v4 = v4
        self.i4 = i4

    def __str__(self):
        return 'N' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.v1) + ' ' + str(self.i1) + ' ' + str(self.v2) + ' ' + str(self.i2) + ' ' + str(self.v3) + ' ' + str(self.i3) + ' ' + str(self.v4) + ' ' + str(self.i4)

    def estampaBE(self, Gn, I, tensoes):
        return Gn, I

# tensao controlada por tensao
class FonteTensaoTensao(Componente):
    '''!
    @brief Esta classe implementa a Fonte de tensao controlada por tensao e sua estampa
    '''
    _linear = True
    _num_nos = 4
    _num_nos_mod = 1
    def __init__(self, name: str, nos: list[str], valor: float):
        '''!
        @brief Construtor da Fonte de tensao controlada por tensao
        @param nos [no_mais, no_menos] nos da fonte
        @param valor ganho
        '''
        super().__init__(name, nos)
        self.valor = valor

    def __str__(self):
        return 'E' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor)

    def estampaBE(self, Gn, I, tensoes):
        Gn[self._posicao_nos[0], self._nos_mod[0]] -= 1
        Gn[self._posicao_nos[1], self._nos_mod[0]] += 1
        Gn[self._posicao_nos[2], self._nos_mod[0]] += self.valor
        Gn[self._posicao_nos[3], self._nos_mod[0]] -= self.valor
        Gn[self._nos_mod[0], self._posicao_nos[0]] += 1
        Gn[self._nos_mod[0], self._posicao_nos[1]] -= 1
        return Gn, I

# corrente controlada por corrente
class FonteCorrenteCorrente(Componente):
    '''!
    @brief Esta classe implementa a Fonte de corrente controlada por corrente e sua estampa
    '''
    _linear = True
    _num_nos = 4
    _num_nos_mod = 1
    def __init__(self, name: str, nos: list[str], valor: float):
        '''!
        @brief Construtor da Fonte de corrente controlada por corrente
        @param nos [no_mais, no_menos] nos da fonte
        @param valor ganho
        '''
        super().__init__(name, nos)
        self.valor = valor

    def __str__(self):
        return 'F' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor)

    def estampaBE(self, Gn, I, tensoes):
        return Gn, I

# corrente controlada por tensao
class FonteCorrenteTensao(Componente):
    '''!
    @brief Esta classe implementa a Fonte de corrente controlada por tensao e sua estampa
    '''
    _linear = True
    _num_nos = 4
    _num_nos_mod = 0
    def __init__(self, name: str, nos: list[str], valor: float):
        '''!
        @brief Construtor da Fonte de corrente controlada por tensao
        @param nos [no_mais, no_menos] nos da fonte
        @param valor ganho
        '''
        super().__init__(name, nos)
        self.valor = valor

    def __str__(self):
        return 'G' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor)

    def estampaBE(self, Gn, I, tensoes):
        return Gn, I

# tensao controlada por corrente
class FonteTensaoCorrente(Componente):
    '''!
    @brief Esta classe implementa a Fonte de tensao controlada por corrente e sua estampa
    '''
    _linear = True
    _num_nos = 4
    _num_nos_mod = 2
    def __init__(self, name: str, nos: list[str], valor: float):
        '''!
        @brief Construtor da Fonte de tensao controlada por corrente
        @param nos [no_mais, no_menos] nos da fonte
        @param valor ganho
        '''
        super().__init__(name, nos)
        self.valor = valor

    def __str__(self):
        return 'H' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor)

    def estampaBE(self, Gn, I, tensoes):
        return Gn, I

class Diodo(Componente):
    '''!
    @brief Esta classe implementa o Diodo e sua estampa
    '''
    _linear = True
    _num_nos = 2
    _num_nos_mod = 2
    def __init__(self, name: str, nos: list[str]):
        '''!
        @brief Construtor do Diodo
        @param nos [no_mais, no_menos] nos do diodo
        '''
        super().__init__(name, nos)

    def __str__(self):
        return 'D' + self.name + ' ' + ' '.join(str(no) for no in self.nos)

    def estampaBE(self, Gn, I, tensoes):
        return Gn, I

class AmpOp(Componente):
    '''!
    @brief Esta classe implementa o Amplificador Operacional ideal e sua estampa
    '''
    _linear = True
    _num_nos = 3
    _num_nos_mod = 1
    def __init__(self, name: str, nos: list[str]):
        '''!
        @brief Construtor do Amplificador Operacional
        @param nos [no_mais, no_menos, no_saida] nos do amp op
        '''
        super().__init__(name, nos)

    def __str__(self):
        return 'O' + self.name + ' ' + ' '.join(str(no) for no in self.nos)

    def estampaBE(self, Gn, I, tensoes):
        return Gn, I

class Mosfet(Componente):
    '''!
    @brief Esta classe implementa o transistor MOSFET e sua estampa
    '''
    def __init__(self):
        '''!
        @brief Construtor do Mosfet
        '''
        raise NotImplementedError

class FonteCorrente(Componente):
    '''!
    @brief Esta classe implementa a Fonte de corrente e sua estampa
    '''
    _linear = True
    _num_nos = 2
    _num_nos_mod = 0
    def __init__(self, name: str, nos: list[str], args: list):
        '''!
        @brief Construtor Fonte de corrente
        @param nos [no_mais, no_menos] nos da fonte
        @param args parametros no estilo SPICE
        '''
        super().__init__(name, nos)
        self.args = args

    def __str__(self):
        return 'I' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + ' '.join(self.args)

    def estampaBE(self, Gn, I, tensoes):
        return Gn, I

class FonteTensao(Componente):
    '''!
    @brief Esta classe implementa a Fonte de tensao e sua estampa
    '''
    _linear = True
    _num_nos = 2
    _num_nos_mod = 1
    def __init__(self, name: str, nos: list[str], args: list):
        '''!
        @brief Construtor da Fonte de tensao
        @param nos [no_mais, no_menos] nos da fonte
        @param args parametros no estilo SPICE
        '''
        super().__init__(name, nos)
        self.args = args

    def __str__(self):
        return 'V' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + ' '.join(self.args)

    def estampaBE(self, Gn, I, tensoes):
        return Gn, I