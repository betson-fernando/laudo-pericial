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


def findDotEnv(filePath):
    """Esta função recebe um caminho para um diretório e itera dentro de todas as pastas pai até encontrar o primeiro arquivo '.env'.
       Retorna o caminho para o arquivo .env, ou erro caso não houver nenhum."""
    
    
    from pathlib import Path  
    
    if type(filePath) == str:
        filePath = Path(filePath)
        
    if not filePath.is_dir():
        raise FileNotFoundError("O argumento da função não é um diretório válido.")
    
    for item in filePath.iterdir():  # Loop que analisa se há um arquivo .env na pasta FilePath
            if item.is_file() and item.suffix == '.env':
                return item
    
    # Se não encontrar na pasta FilePath, itere pelos pais até encontrar o arquivo .env ou gere um erro.
    parents = filePath.parents
    for cont in range(0, len(parents)):  #Loop que adiciona anda um passo em direção a target.
        for item in filePath.parents[cont].iterdir():  # Loop que analisa se há um arquivo .env na pasta FilePath.parents[cont]
            if item.is_file() and item.suffix == '.env':
                return(item)

    raise FileNotFoundError("Arquivo .env não encontrado.")
