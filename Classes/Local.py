import sys
from os import path
import requests
import numpy as np

sys.path.insert(0, r'C:\Users\GEPH-IC\Documents\Betson\Laudo Pericial')
import settings

LOWZOOM = 17
HIGHZOOM = 20

class Local():

    idList = []
    
    def __init__(self, locId:str, coord:(float,float), municipio:str,  bairro:str, rua:str="", num:str=""):

        try:
            assert locId not in self.idList
        except AssertionError:
            sys.exit(f"\nIdentificador de local já existente.\nUse um diferente de {self.idList}.\nO programa será encerrado.")
        else:
            self.locId = locId
            self.idList.append(locId)
        
        self.municipio = municipio
        self.bairro = bairro
        self.rua = rua
        self.num = num
        self.coord = coord
        
        
    def getMaps(self, addPlaces=[], basePath:str="", zoom:int=""):
        """Este método cria uma imagem em formato .jpeg do google maps.
        Entradas:
        * path(str) --> Caminho do arquivo a ser criado. Se somente colocar o nome do arquivo, a imagem será criada  na pasta do executável;
        * zoom(int) --> Nível de zoom. Recomenda-se de 15 a 22, ou importe as variáveis pré-definidas LOWZOOM e HIGHZOOM;
        * markers (dict{str: str}): dicionário em que cada item é um marcador. A chave que cada item é o título do marcador, e o valor são suas coordenadas, no formato decimal.
                                    Ex.: {'1': '-7.954582,-34.985879', '2': '-7.951234,-34.985546'}
        """

        if addPlaces:
            coords = [place.coord for place in addPlaces]
            coords.append(self.coord)
        
            
            lats=[]
            longs=[]
            for item in coords:
                lats.append(float(item[0]))
                longs.append(float(item[1]))
        
            # Dimensões máximas (lat e long) ocupadas pelos marcadores.
            deltaLat = max(lats)-min(lats)
            deltaLong = max(longs)-min(longs)

            # Escolhe o zoom máximo que abrange todos os pontos.
            # Justificativa para a fórmula, é que o espaço abrangido pelo mapa, em (lat, long), é de (0.00509, 0.00684)*2^(17-zoom), resolvendo pra zoom dá a fórmula abaixo.
            # lowzoom = min(np.floor(17-np.log2(deltaLat/0.00509)), np.floor(17-np.log2(deltaLong/0.00684)), LOWZOOM)
            if zoom == "":
                zoomList = list(map(lambda x: min(np.floor(17-np.log2(deltaLat/0.00509)), np.floor(17-np.log2(deltaLong/0.00684)), x), [LOWZOOM, HIGHZOOM]))
            else:
                zoomList = [min(np.floor(17-np.log2(deltaLat/0.00509)), np.floor(17-np.log2(deltaLong/0.00684)), zoom)]
        else:
            if zoom == "":
                zoomList = [LOWZOOM, HIGHZOOM]
            else:
                zoomList = [zoom]
                
                

        """zoom: Controla o nível de detalhamento;
           size: controla o tamanho da imagem e, por consequência, a largura da janela de coordenadas. Se size dobrar, o mapa abrange mais áreas, sem, contudo, aumentar o detalhamento;
           scale: aumenta o tamanho da imagem, sem aumentar o detalhamento do zoom, nem o tamanho da janela de coordenadas. Simplesmente amplia a imagem definida por scale e zoom.
        """
        payload = {"size": "640x427",
                   "scale": "2",
                   "format": "jpeg",
                   "maptype": "hybrid",
                   "style": "feature:poi|visibility:off",
                   "markers": [f"color:red|label:{self.locId}|size:mid|{self.coord[0]},{self.coord[1]}"],
                   "key": settings.MAPS_API_KEY
                   }
        if addPlaces:
            payload["markers"].append([f"color:yellow|label:{place.locId}|size:mid|{place.coord[0]},{place.coord[1]}" for place in addPlaces])
            
        for cont in range(0, len(zoomList)):
            payload["zoom"] = int(zoomList[cont])
            r = requests.get(settins.MAPS_URL, params=payload)

            with open(path.join(basePath, f"mapa{cont+1}.jpg"), 'wb') as f:
                f.write(r.content)
                f.close()
            