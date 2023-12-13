from Local import Local
import configs
from globalfuncs.funcs import testNumber, testEmpty

coordsStr = input("Insira as coordenadas no formato do Google Maps: ")

coords = tuple(coordsStr.replace(' ','').split(','))


while True:

    try:
        for coord in coords:
            float(coord)
    except ValueError:
        input("As coordenadas não foram digitadas no formato correto.\nDigite-as novamente (Ex.: -5.653423,-34.423564):")
    else:
        break
        


local = Local(1, coords, municipio='x', bairro='x', rua="x", tipo='x')

lowZoom = local.getMaps(zoom = configs.zoom['lowzoom'])
highZoom = local.getMaps(zoom = configs.zoom['highzoom'])

with open('lowzoom.jpg', 'wb') as lowMap, open('highzoom.jpg', 'wb') as highMap:
    lowMap.write(lowZoom)
    highMap.write(highZoom)
    lowMap.close()
    highMap.close()
 