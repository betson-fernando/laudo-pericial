from Local import Local
from dotenv import load_dotenv
from os import environ
import sys
from pathlib import Path
from globalfuncs.funcs import findDotEnv


dotenv_path = findDotEnv(Path(__file__).parent)
load_dotenv(dotenv_path)

coordsStr = input("Insira as coordenadas no formato do Google Maps: ")

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

local = Local(1, coords, municipio='x', bairro='x', rua="x", tipo='x')

lowZoom = local.getMaps(zoom = environ.get('LOW_ZOOM'))
highZoom = local.getMaps(zoom = environ.get('HIGH_ZOOM'))

with open('lowzoom.jpg', 'wb') as lowMap, open('highzoom.jpg', 'wb') as highMap: 
    lowMap.write(lowZoom)
    highMap.write(highZoom)
    lowMap.close()
    highMap.close()