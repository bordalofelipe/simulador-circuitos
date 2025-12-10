import pytest
import simulador


def check_netlist(filename):
    ref = open(filename)
    test = open(filename + '.test')
    for line1, line2 in zip(ref, test):
        assert line1.strip() == line2.strip()


def test_chua():
    c = simulador.Circuito('.TRAN', 1000, 0.1, 'BE', 1)
    c.append(simulador.Resistor('1004', ['1', '2'], 1.9))
    c.append(simulador.Indutor('3000', ['1', '0'], 1))
    c.append(simulador.Capacitor('2000', ['2', '0'], 0.31, ic=1))
    c.append(simulador.Capacitor('2001', ['1', '0'], 1, ic=1))
    c.append(simulador.ResistorNaoLinear('9900', ['2', '0'], -2, 1.1, -1, 0.7, 1, -0.7, 2, -1.1))
    c.export('tests/chua.net.test')
    check_netlist('tests/chua.net')


def test_dc_source():
    c = simulador.Circuito('.TRAN', 0.1, 1e-05, 'BE', 1)
    c.append(simulador.FonteTensao('7006', ['1', '0'], ['SIN', 0, 12, 60, 0.0, 0, 0, 6]))
    c.append(simulador.Diodo('1200', ['1', '2']))
    c.append(simulador.Resistor('1005', ['2', '0'], 1000.0))
    c.append(simulador.Capacitor('2005', ['2', '0'], 4.9999999999999996e-05))
    c.export('tests/dc_source.net.test')
    check_netlist('tests/dc_source.net')


def test_lc():
    c = simulador.Circuito('.TRAN', 0.003, 3e-07, 'BE', 1)
    c.append(simulador.Indutor('3001', ['1', '0'], 0.001))
    c.append(simulador.Indutor('3002', ['2', '0'], 0.00025))
    c.append(simulador.Indutor('3003', ['3', '0'], 0.00011111111110000001))
    c.append(simulador.Capacitor('2002', ['1', '0'], 1e-06, ic=1))
    c.append(simulador.Capacitor('2003', ['2', '0'], 1e-06, ic=1))
    c.append(simulador.Capacitor('2004', ['3', '0'], 1e-06, ic=1))
    c.append(simulador.FonteTensaoTensao('7000', ['4', '0', '3', '0'], 1))
    c.append(simulador.FonteTensaoTensao('7001', ['5', '4', '2', '0'], 1))
    c.append(simulador.FonteTensaoTensao('7002', ['6', '5', '1', '0'], 1))
    c.export('tests/lc.net.test')
    check_netlist('tests/lc.net')


def test_mosfet_curve():
    c = simulador.Circuito('.TRAN', 0.1, 1e-5, 'BE', 1)
    c.append(simulador.FonteTensao('483502', ['1', '0'], ['PULSE', 0, 15, 0, 0.1, 0, 0, 1, 1]))
    c.append(simulador.FonteTensao('483503', ['2', '0'], ['DC', 7]))
    c.append(simulador.Mosfet('9913', ['1', '2', '3'], 'N', 1.9999999999999998e-05, 1e-06, 0.01, 9.999999999999999e-05, 0.5))
    c.append(simulador.Resistor('1026', ['3', '0'], 1))
    c.export('tests/mosfet_curve.net.test')
    check_netlist('tests/mosfet_curve.net')


def test_opamp_rectifier():
    c = simulador.Circuito('.TRAN', 0.004, 1e-06, 'BE', 1)
    c.append(simulador.FonteTensao('2000', ['1', '0'], ['SIN', 0, 2.5, 1000, 0.0, 0, 0, 4]))
    c.append(simulador.Resistor('1006', ['1', '2'], 1000.0))
    c.append(simulador.AmpOp('9901', ['0', '2', '3']))
    c.append(simulador.Resistor('1007', ['2', '4'], 1000.0))
    c.append(simulador.Diodo('1201', ['4', '3']))
    c.append(simulador.Diodo('1202', ['3', '5']))
    c.append(simulador.Resistor('1008', ['5', '2'], 1000.0))
    c.append(simulador.Resistor('1009', ['4', '6'], 1000.0))
    c.append(simulador.AmpOp('9902', ['5', '6', '7']))
    c.append(simulador.Resistor('1010', ['6', '7'], 1000.0))
    c.append(simulador.Resistor('1011', ['7', '0'], 100000.0))
    c.append(simulador.Capacitor('2006', ['7', '0'], 9.999999999999999e-05))
    c.export('tests/opamp_rectifier.net.test')
    check_netlist('tests/opamp_rectifier.net')


def test_oscilator():
    c = simulador.Circuito('.TRAN', 0.05, 1e-06, 'BE', 1)
    c.append(simulador.Resistor('1012', ['1', '2'], 51000.0))
    c.append(simulador.Capacitor('2007', ['2', '3'], 1e-09))
    c.append(simulador.Resistor('1013', ['3', '0'], 51000.0))
    c.append(simulador.Capacitor('2008', ['3', '0'], 1e-09))
    c.append(simulador.AmpOp('9903', ['3', '4', '1']))
    c.append(simulador.Resistor('1014', ['4', '0'], 47000.0))
    c.append(simulador.Resistor('1015', ['1', '4'], 100000.0))
    c.append(simulador.Resistor('1016', ['1', '5'], 1000000.0))
    c.append(simulador.Diodo('1203', ['5', '4']))
    c.append(simulador.Diodo('1204', ['4', '5']))
    c.export('tests/oscilator.net.test')
    check_netlist('tests/oscilator.net')


def test_pulse():
    c = simulador.Circuito('.TRAN', 0.01, 1e-05, 'BE', 1)
    c.append(simulador.FonteTensao('5003', ['1', '0'], ['PULSE', 0, 5, 0.002, 0.0002, 0.0002, 0.0005, 0.001, 10]))
    c.append(simulador.Resistor('1002', ['1', '2'], 1000.0))
    c.append(simulador.Resistor('1003', ['2', '0'], 1000.0))
    c.export('tests/pulse.net.test')
    check_netlist('tests/pulse.net')


def test_sinusoidal():
    c = simulador.Circuito('.TRAN', 0.005, 1e-05, 'BE', 1)
    c.append(simulador.FonteTensao('4000', ['1', '0'], ['SIN', 1, 5, 1000, 0.002, 80, 90, 5]))
    c.append(simulador.Resistor('1000', ['1', '2'], 1000.0))
    c.append(simulador.Resistor('1001', ['2', '0'], 1000.0))
    c.export('tests/sinusoidal.net.test')
    check_netlist('tests/sinusoidal.net')
