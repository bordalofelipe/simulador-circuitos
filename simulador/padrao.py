class Resistor(Componente):
    '''!
    @class Resistor
    @brief Representa um Resistor, derivado de ::Componente.
    @details O resistor é um componente linear passivo de dois terminais que obedece à lei de Ohm: V = R*I.

    @image latex resistor.png "Resistor"
    @image html resistor.png "Resistor"
    '''
    _linear = True
    _num_nos = 2
    _num_nos_mod = 0
    
    def __init__(self, name: str, nos: list[str], valor: float):
        '''!
        @brief Construtor do resistor.
        @param name Nome único do resistor (ex: "R1").
        @param nos Lista com os nomes dos dois nós: [nó_1, nó_2].
        @param valor Resistência em Ohms (float).
        
        @var valor
            Armazena o valor da resistência em Ohms.
        '''
        super().__init__(name, nos)
        self.valor = valor

    def __str__(self):
        '''!
        @brief Retorna representação do resistor como linha da netlist SPICE.
        @return String no formato "R<nome> <nó1> <nó2> <valor>".
        @details Este formato é compatível com o padrão de netlist SPICE.
        '''
        return 'R' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor)

    def estampaBE(self, Gn, I, t, tensoes):
        '''!
        @brief Adiciona a estampa de Análise Nodal do resistor às matrizes do sistema linear (Gn*V = I).
               
        @param Gn Matriz de condutância (admitância) do sistema (passada por referência).
        @param I Vetor de correntes (passado por referência).
        @param t Instante de tempo atual (não utilizado por ser um componente estático).
        @param tensoes Vetor de tensões nodais (não utilizado por ser um componente linear).
        @return Tupla (Gn, I) com as matrizes atualizadas.
        
        @details
        A estampa de um resistor R conectado entre os nós n1 e n2 é:
        
        @image latex resistor_stamp.png "Estampa do Resistor"
        @image html resistor_stamp.png "Estampa do Resistor"
        '''
        G = 1/self.valor
        n1 = self._posicao_nos[0]
        n2 = self._posicao_nos[1]
        
        Gn[n1, n1] += G
        Gn[n1, n2] -= G
        Gn[n2, n1] -= G
        Gn[n2, n2] += G
        
        return Gn, I