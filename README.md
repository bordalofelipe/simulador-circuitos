
# Simulador de Circuitos

Trabalho de Simulador de Circuitos Elétricos submetido para a disciplina de ITM.

![Python_App](https://img.shields.io/github/actions/workflow/status/bordalofelipe/simulador-circuitos/python-app.yml?label=pytest)
![Documentation](https://img.shields.io/github/actions/workflow/status/bordalofelipe/simulador-circuitos/documentation.yaml?label=Documentation)
## Funcionalidades

- Interface CLI e API Python
- Importar ou exportar netlists
- Plot do resultado em modo Y-T ou X-Y
- Importar ou exportar resultados de simulação
- Multiplataforma


## Documentação

[Documentação](https://bordalofelipe.github.io/simulador-circuitos)


## Uso

```python
import simulador

circuito = simulador.import_netlist('netlist.net')  # Importa circuito de netlist

# Adicionar resistor entre o terra e o nó 1
circuito.append(simulador.Resistor('Novo', 
  [simulador.GND, '1'], 1000))

resultado = circuito.run()  # Simula o circuito

resultado.export('resultado.sim')  # Salvar resultados

resultado.plot_xt()  # Plotar resultados
```

## Exemplos

Veja a pasta [examples](examples) para exemplos.
## Instalação

Baixe o simulador em [Releases](https://github.com/bordalofelipe/simulador-circuitos/releases).
    
## Rodando os testes

Os testes são fornecidos por `pytest`. Para rodar os testes, rode o seguinte comando

```bash
  pip install pytest
  pytest
```

