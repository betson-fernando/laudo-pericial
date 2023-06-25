import numpy as np

def testNumber(name, value):
    """Esta função tem o objetivo de forçar o usuário a digitar um valor que seja uma string de número válido.
       Entradas:
            --> name (str): nome do campo com erro para alertar o usuário;
            --> value(str): o valor a ser testado.
       Retorno (str): o valor, na forma de string, que pode ser convertido para número.
    """
    
    while True:
        try:
            temp = float(value)
        except ValueError:
            value = input(f"O valor {name} deveria ser uma string numérica, com separador decimal de ponto ('.').\nDigite corretamente: ")
        else:
            return value


def testEmpty(name, value):
    """Esta função tem o objetivo de forçar o usuário a digitar um valor que não seja vazio.
       Entradas:
            --> name (str): nome do campo com erro para alertar o usuário;
            --> value(str): o valor a ser testado.
       Retorno (str): o valor, na forma de string não vazia.
    """
    
    while value == "" or value is np.NaN:
        value = input(f"O campo '{name}' não foi preenchido. Digite-o: ")
    
    return value
