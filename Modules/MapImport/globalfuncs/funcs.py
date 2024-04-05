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
