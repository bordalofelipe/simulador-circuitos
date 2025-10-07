import pytest
import simulador

def netlist(filename):
    c = simulador.import_netlist('tests/' + filename)
    r = c.run()
    r.export('tests/' + filename.replace('.net', '.sim.test'))

def check_tolerances(filename):
    ref = simulador.import_resultado('tests/' + filename)
    test = simulador.import_resultado('tests/' + filename + '.test')
    total_error = 0
    total_samples = 0
    for r, t in zip(ref, test):
        nodes_ref = r[1]
        nodes_test = r[1]
        delta = [abs(i-j) for i, j in zip(nodes_ref, nodes_test)]
        total_error += max(delta)
        total_samples += 1
    total_error /= total_samples
    print(filename, f'teve erro médio de {total_error}')
    assert total_error < 10

def test_chua():
    netlist('chua.net')
    check_tolerances('chua.sim')

def test_dc_source():
    netlist('dc_source.net')
    check_tolerances('dc_source.sim')

def test_lc():
    netlist('lc.net')
    check_tolerances('lc.sim')

def test_mosfet_curve():
    netlist('mosfet_curve.net')
    check_tolerances('mosfet_curve.sim')

def test_oscilator():
    netlist('oscilator.net')
    check_tolerances('oscilator.sim')

def test_pulse():
    netlist('pulse.net')
    check_tolerances('pulse.sim')

def test_sinusoidal():
    netlist('sinusoidal.net')
    check_tolerances('sinusoidal.sim')