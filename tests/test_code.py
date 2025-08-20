import pytest
import simulador

def test_chua():
    c = simulador.Circuito('.TRAN', 1000, 0.1, 'BE', 1)
    c.append(simulador.Resistor('1004', ['1', '2'], 1.9))
    c.append(simulador.Indutor('3000', ['1', '0'], 1))
    c.append(simulador.Capacitor('2000', ['2', '0'], 0.31, ic=1))
    c.append(simulador.Capacitor('2001', ['1', '0'], 1, ic=1))
    c.export('tests/chua.net.test')

def test_dc_source():
    c = simulador.Circuito('.TRAN', 0.1, 1e-05, 'BE', 1)
    c.append(simulador.FonteTensao('7006', ['1', '0'], ['SIN', '0', '12', '60', '0.0', '0', '0', '6']))
    c.append(simulador.Diodo('1200', ['1', '2']))
    c.append(simulador.Resistor('1005', ['2', '0'], 1000.0))
    c.append(simulador.Capacitor('2005', ['2', '0'], 4.9999999999999996e-05))
    c.export('tests/dc_source.net.test')
    
def test_lc():
    pass
    
def test_mosfet_curve():
    pass

def test_oscilator():
    pass
    
def test_pulse():
    pass
    
def test_sinusoidal():
    pass