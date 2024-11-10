from datetime import date


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
    
            
def assertType(name, value, valueType=float):
    """Esta função tem o objetivo de forçar o usuário a digitar um valor que seja uma string de um tipo válido.
       Entradas:
            --> name (str): nome do campo com erro para alertar o usuário;
            --> value (str): o valor a ser testado.
            --> valueType (int, float, ...): tipo de objeto que deve ser 'value'.
       Retorno (str): o valor, na forma de string, que pode ser convertido para o tipo especificado por valueType.
    """
    
    temp = value
    while True:
        try:
            if valueType == date:
                temp = str(temp)
                valueType(int(temp[6:10]), int(temp[3:5]), int(temp[0:2]))
            else:
                valueType(temp)
        except ValueError:
            temp = input(f"O valor {name} deveria ser uma string que pode ser convertida para {valueType},\n com separador decimal de ponto ('.'), e datas no formato dd/mm/aaaa, quando aplicável.\n"
                          f"Digite corretamente: ")
        else:
            return str(temp)


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


def textbf(string):
    """Esta função coloca um texto em negrito no Latex."""
    return r"\textbf{" + str(string) + "}"


def ref(string):
    """Esta função insere uma referência no Latex."""
    return r"\ref{" + str(string) + "}"


def fig(filename, caption):
    """Esta função insere uma figura conforme macro definida especificamente para meu latex.
    Entradas:
        --> fileName(str): Nome do arquivo, sem extensão (subtende-se '.jpg', e o arquivo deve ter este formato);
        --> caption(str): Legenda.
    """
    return r"\f{" + str(filename) + "}{" + str(caption) + "}"


def plural(frase: str):
    """Esta função torna palavras de uma frase em plural. Para selecionar as palavras que se deseja flexionar, basta
    colocá-las entre barras. Ex.: "|A| |funcionária| |irá| sair." --> As funcionárias irão sair."""

    import re
    import json
    from pathlib import Path

    pat = re.compile(r"\|(\w+)\|")
    matches = re.findall(pat, frase)

    with open(Path(__file__).parents[0].joinpath( "arquivos/dicPlural.json"), "r", encoding='utf-8') as d:
        dic = json.loads(d.read())
        d.close()

    for match in matches:
        try:
            rep = dic[match.lower()]
            if match[0].isupper():  # Se a primeira letra de match for maiúscula
                rep = rep[0].upper() + rep[1:]  # Colocar a primeira letra do plural de match em maiúscula

            frase = frase.replace(f"|{match}|", rep)
        except KeyError:
            print(f"Palavra '{match.lower()}' não existe no dicionário de flexão de número. Pulando este match.")

    return frase

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
        
def putNumbPoints(s: str):
    """Esta função recebe uma string numérica, e retorna a mesma string com pontos nas casas de milhares."""

    pointList = list(range(-len(s) + len(s)%3, 0, 3))  # Lista das posições em que os pontos de milhares serão inseridos na string
    remainder = s[:-len(s) + len(s)%3]   # Porção à esquerda da string antes do primeiro ponto
    
    res =  remainder + "." if len(remainder) > 0 else ""   # Iniciar a string a ser retornada com remainder e um ponto, ou com nada se remainder for vazia.

    for cont in range(0, len(pointList)-1): # Montar as strings com um ponto separador de milhares
        res += s[pointList[cont]:pointList[cont+1]] + "."

    res += s[pointList[len(pointList)-1]:]  # Adicionar os últimos três dígitos do número
    
    return(res)
    
def listToText(lst:list):

    texto = ""
    for num, item in enumerate(lst):
        if num == len(lst) - 2:
            texto += f"{item}, e "
        elif num == len(lst) - 1:
            texto += str(item)
        else:
            texto += f"{item}, "
    
    return texto