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
            float(value)
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

def textbf(string):
    """Esta função coloca um texto em negrito no Latex."""
    return r"\textbf{" + str(string) + "}"
    
def ref(string):
    """Esta função insere uma referência no Latex."""
    return r"\ref{" + str(string) + "}"
    
def fig(fileName, caption):
    """Esta função insere uma figura (conforme macro definida especificamente para meu latex.
    Entradas:
        --> fileName(str): Nome do arquivo, sem extensão (subtende-se '.jpg', e o arquivo deve ter este formato);
        --> caption(str): Legenda.
    """
    return r"\f{" + str(fileName) + "}{" + str(caption) + "}"
