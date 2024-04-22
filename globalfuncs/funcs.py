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

    with open(Path(__file__).parents[1].joinpath( "arquivos/dicPlural.json"), "r", encoding='utf-8') as d:
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
