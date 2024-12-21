from dotenv import find_dotenv, load_dotenv
from os import environ
import sys
from pathlib import Path
from Classes import Local
import numpy as np
import requests


def getMap(coordsDic:dict, savePath:Path or str, zoom:int = np.nan, ):
    
    # INÍCIO DOS TESTES DE CONSISTÊNCIA DOS ARGUMENTOS DA FUNÇÃO =================================

    # Se as coordenadas estão escritas no padrão
    try:
        assert len(coordsDic) > 0 and isinstance(coordsDic, dict)
    except AssertionError:
        sys.exit("O argumento das coordenadas deve ser um dicionário não vazio. Corrija e reexecute.")
        
    for item in coordsDic:
    
        coordsStr = coordsDic[item]
        coords = list(coordsStr.replace(' ','').split(','))
        
        while True:
            try:
                for coord in coords:
                    float(coord)
            except ValueError:
                coordsStr = input(f"As coordenadas do local {item} não foram digitadas no formato correto.\nDigite-as novamente (Ex.: -5.653423,-34.423564):")
                coords = list(coordsStr.replace(' ','').split(','))
            else:
                coordsDic[item] = coordsStr
                break
    
    # Se zoom é número natural
    try:
        int(zoom)
        assert int(zoom) > 0 and float(zoom) % 1 == 0
    except (ValueError, TypeError, AssertionError):
        sys.exit(f"O valor de zoom ({zoom}) não foi digitado corretamente. Corrija no arquivo 'configs.env'.\nO programa será encerrado.")
    
    # Se o diretório é válido
    try:
        assert Path(savePath).parent.is_dir()
    except AssertionError:
        sys.exit(f"O caminho para o diretório do arquivo \"{savePath}\" não é válido. Corrija e reexecute.")
    
    url = environ.get('MAPS_URL')
    
    # FINAL DOS TESTES DE CONSISTÊNCIA DOS ARGUMENTOS DA FUNÇÃO =================================

    payload = {"size": "640x427",
       "scale": "2",
       "format": "jpeg",
       "maptype": "hybrid",
       "style": "feature:poi|visibility:off",
       "markers": [f"color:red|label:{item}|size:mid|{coordsDic[item]}" for item in coordsDic],
       "key": environ.get('MAPS_API_KEY')
    }
    
    if zoom is not np.nan:
        payload["zoom"] = zoom
        
    elif (zoom is np.nan and len(coordsDic) == 1):
        sys.exit("Para obter mapa com apenas um marcador, o zoom deve ser informado.\nO programa será fechado.")

    figData = requests.get(url, params=payload).content
#===========================================================================================================================

    with open(savePath, 'wb') as mapa:
        mapa.write(figData)


if __name__ == "__main__":

    load_dotenv(Path(__file__).parent.joinpath('configs.env'))
    
    # numCoords = input("Insira o número de locais a serem")
    coordsDic = {1:input("Insira as coordenadas no formato do Google Maps: ")}
    
    getMap(coordsDic, Path("lowzoom.jpg"), environ.get('LOW_ZOOM'))
    getMap(coordsDic, Path("highzoom.jpg"), environ.get('HIGH_ZOOM'))

