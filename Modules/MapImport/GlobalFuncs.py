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
            value = input(f"O valor {name} deveria ser uma string numérica, com separador decimal de ponto ('.').\n"
                          f"Digite corretamente: ")
        else:
            return value


def testEmpty(name, value):
    """Esta função tem o objetivo de forçar o usuário a digitar um valor que não seja vazio.
       Entradas:
            --> name (str): nome do campo com erro para alertar o usuário;
            --> value(str): o valor a ser testado.
       Retorno (str): o valor, na forma de string não vazia.
    """
    import numpy as np

    while value == "" or value is np.NaN:
        value = input(f"O campo '{name}' não foi preenchido. Digite-o: ")
    
    return value

def getEnviron(key: str):
    """Esta função recebe uma chave de uma variável de ambiente e retorna o seu valor.
    Resulta em erro se a chave não existir ou for vazia."""
    
    from os import environ
    
    try:
        value = environ[key]
        assert value != ''
        return value
    except KeyError as e:
        print(f"A chave {e} não foi encontrada no arquivo 'configs.env'. Corrija e reenvie.")
        return None
    except AssertionError:
        printf(f"O valor da chave {e} está vazio no arquivo 'configs.env'. Corrija e reenvie.")
        return None