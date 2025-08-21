class Componente():
    _linear = True
    _num_nos = 0
    _num_nos_mod = 0
    def __init__(self, name: str, nos: list[str]):
        '''Classe abstrata de componente'''
        self._nos_mod = []
        assert len(nos) == self._num_nos
        self.name = name
        self.nos = nos

    @property
    def linear(self):
        '''Retorna se componente é linear'''
        return self._linear

    @property
    def num_nos_mod(self):
        '''Retorna numero de nos necessarios na analise modificada'''
        return self._num_nos_mod
    
    def set_nos_mod(self, nos_mod: list[int]):
        '''Aloca nos necessarios na analise modificada'''
        assert len(nos_mod) == self._num_nos_mod
        self._nos_mod = nos_mod
    
    def set_posicao_nos(self, posicoes: list[int]):
        '''Aloca nos necessarios'''
        self._posicao_nos = posicoes
    
    def __str__(self):
        return 'Componente' 

    def estampaDC(self, Gn, I):
        raise NotImplementedError
    def estampaBE(self, Gn, I):
        raise NotImplementedError
    def estampaTrap(self, Gn, I):
        raise NotImplementedError
    def estampaFE(self, Gn, I):
        raise NotImplementedError

class Resistor(Componente):
    _linear = True
    _num_nos = 2
    _num_nos_mod = 0
    def __init__(self, name: str, nos: list[str], valor: float):
        '''
        Resistor
        nos: [no1, no2] nos do Resistor
        valor: resistencia
        '''
        super().__init__(name, nos)
        self.valor = valor
    
    def __str__(self):
        return 'R' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor)
    
    def estampaDC(self, Gn, I):
        pass

class Indutor(Componente):
    _linear = True
    _num_nos = 2
    _num_nos_mod = 0
    def __init__(self, name: str, nos: list[str], valor: float, ic=0.0):
        '''
        Indutor
        nos: [no_mais, no_menos] nos do Indutor
        valor: indutancia
        ic = 0.0: valor inicial
        '''
        super().__init__(name, nos)
        self.valor = valor
        self.ic = ic

    def __str__(self):
        if self.ic == 0.0:
            return 'L' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor)
        else:
            return 'L' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor) + ' IC=' + str(self.ic)
    
    def estampaDC(self, Gn, I):
        pass

class Capacitor(Componente):
    _linear = True
    _num_nos = 2
    _num_nos_mod = 0
    def __init__(self, name: str, nos: list[str], valor: float, ic=0.0):
        '''
        Capacitor
        nos: [no_mais, no_menos] nos do Capacitor
        valor: capacitancia
        ic = 0.0: valor inicial
        '''
        super().__init__(name, nos)
        self.valor = valor
        self.ic = ic

    def __str__(self):
        if self.ic == 0.0:
            return 'C' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor)
        else:
            return 'C' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor) + ' IC=' + str(self.ic)
    
    def estampaDC(self, Gn, I):
        pass

# tensao controlada por tensao
class FonteTensaoTensao(Componente):
    _linear = True
    _num_nos = 4
    _num_nos_mod = 1
    def __init__(self, name: str, nos: list[str], valor: float):
        '''
        Fonte de tensao controlada por tensao
        nos: [no_mais, no_menos] nos da fonte
        valor: ganho
        '''
        super().__init__(name, nos)
        self.valor = valor
    
    def __str__(self):
        return 'E' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor)
    
    def estampaDC(self, Gn, I):
        pass

# corrente controlada por corrente
class FonteCorrenteCorrente(Componente):
    _linear = True
    _num_nos = 4
    _num_nos_mod = 1
    def __init__(self, name: str, nos: list[str], valor: float):
        '''
        Fonte de corrente controlada por corrente
        nos: [no_mais, no_menos] nos da fonte
        valor: ganho
        '''
        super().__init__(name, nos)
        self.valor = valor
    
    def __str__(self):
        return 'F' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor)
    
    def estampaDC(self, Gn, I):
        pass

# corrente controlada por tensao
class FonteCorrenteTensao(Componente):
    _linear = True
    _num_nos = 4
    _num_nos_mod = 0
    def __init__(self, name: str, nos: list[str], valor: float):
        '''
        Fonte de corrente controlada por tensao
        nos: [no_mais, no_menos] nos da fonte
        valor: ganho
        '''
        super().__init__(name, nos)
        self.valor = valor
    
    def __str__(self):
        return 'G' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor)
    
    def estampaDC(self, Gn, I):
        pass

# tensao controlada por corrente
class FonteTensaoCorrente(Componente):
    _linear = True
    _num_nos = 4
    _num_nos_mod = 2
    def __init__(self, name: str, nos: list[str], valor: float):
        '''
        Fonte de tensao controlada por corrente
        nos: [no_mais, no_menos] nos da fonte
        valor: ganho
        '''
        super().__init__(name, nos)
        self.valor = valor
    
    def __str__(self):
        return 'H' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor)
    
    def estampaDC(self, Gn, I):
        pass

class Diodo(Componente):
    _linear = True
    _num_nos = 2
    _num_nos_mod = 2
    def __init__(self, name: str, nos: list[str]):
        '''
        Diodo
        nos: [no_mais, no_menos] nos do diodo
        '''
        super().__init__(name, nos)

    def __str__(self):
        return 'D' + self.name + ' ' + ' '.join(str(no) for no in self.nos)
    
    def estampaDC(self, Gn, I):
        pass

class AmpOp(Componente):
    _linear = True
    _num_nos = 3
    _num_nos_mod = 1
    def __init__(self, name: str, nos: list[str]):
        '''
        Amplificador Operacional
        nos: [no_mais, no_menos, no_saida] nos do amp op
        '''
        super().__init__(name, nos)
        
    def __str__(self):
        return 'O' + self.name + ' ' + ' '.join(str(no) for no in self.nos)
    
    def estampaDC(self, Gn, I):
        pass

class Mosfet(Componente):
    def __init__(self):
        '''Mosfet'''
        raise NotImplementedError

class FonteCorrente(Componente):
    _linear = True
    _num_nos = 2
    _num_nos_mod = 0
    def __init__(self, name: str, nos: list[str], args: list):
        '''
        Fonte de corrente
        nos: [no_mais, no_menos] nos da fonte
        list: parametros no estilo SPICE
        '''
        super().__init__(name, nos)
        self.args = args
    
    def __str__(self):
        return 'I' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + ' '.join(self.args)
    
    def estampaDC(self, Gn, I):
        pass

class FonteTensao(Componente):
    _linear = True
    _num_nos = 2
    _num_nos_mod = 1
    def __init__(self, name: str, nos: list[str], args: list):
        '''
        Fonte de tensao
        nos: [no_mais, no_menos] nos da fonte
        list: parametros no estilo SPICE
        '''
        super().__init__(name, nos)
        self.args = args
        
    def __str__(self):
        return 'V' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + ' '.join(self.args)
    
    def estampaDC(self, Gn, I):
        pass