from dotenv import find_dotenv, load_dotenv
from os import environ
import sys
from pathlib import Path
from Classes import Local
import numpy as np


def getMap(coordsStr:str, zoom:int = np.NaN, savePath:Path = Path()):
# COORDSSTR PARA DICIONÁRIO!
    while True:

        coords = list(coordsStr.replace(' ','').split(','))
        try:
            for coord in coords:
                float(coord)
        except ValueError:
            coordsStr = input("As coordenadas não foram digitadas no formato correto.\nDigite-as novamente (Ex.: -5.653423,-34.423564):")
            coords = list(coordsStr.replace(' ','').split(','))
        else:
            break
            
    coords = tuple(coords)

#========================================================================================================
    
    payload = {"size": "640x427",
       "scale": "2",
       "format": "jpeg",
       "maptype": "hybrid",
       "style": "feature:poi|visibility:off",
       "markers": [f"color:red|label:{place.locId}|size:mid|{place.coord[0]},{place.coord[1]}" for place in places],  # PARA DICIONÁRIO!
       "key": environ.get('MAPS_API_KEY')
    }
    
    url = environ.get('MAPS_URL')

    if zoom is not np.NaN:
        payload["zoom"] = zoom
        figData requests.get(url, params=payload).content
            
    elif zoom is np.NaN and True:   #Substituir True por um teste se tamanho o dicionário coordsStr é maior que 1.
        figData requests.get(url, params=payload).content
        
    else:
        sys.exit("Para obter mapa com apenas um marcador, o zoom deve ser informado.\nO programa será fechado.")
#===========================================================================================================================

    with open(savePath., 'wb') as mapa:
        mapa.write(figData)


if __name__ == "__main__":

    load_dotenv(Path(__file__).parent.joinpath('configs.env'))

    coordsStr = input("Insira as coordenadas no formato do Google Maps: ")
    
    getMap(coordsStr, environ.get('LOW_ZOOM'), Path("lowzoom.jpg"))
    getMap(coordsStr, environ.get('HIGH_ZOOM'), Path("highzoom.jpg"))

