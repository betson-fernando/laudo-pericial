import sys
from os import path  # gradativamente trocar os por pathlib
from pathlib import Path
import requests
import numpy as np
import re
from textwrap import dedent
from globalfuncs.funcs import testNumber, testEmpty

sys.path.insert(0, str(Path(__file__).parents[1]))
import settings


class Local():
    """Esta classe tem como instância uma localidade:
    Variáveis de inicialização:
        --> locId (int): Identificador do local;
        --> coord (str, str): Coordenadas do local, no formato decimal, com separador decimal sendo o ponto (".");
        --> bairro (str): Bairro do local;
        --> rua (str, opcional): Rua do local;
        --> tipo (str, opcional): externo, interno, ou misto.
    
    Métodos:
        --> getMaps: retorna um mapa do local;
        --> info: retorna informações do local.
        --> toTex: retorna string pronta para uso no arquivo .tex.
    """
        
    idList = []
    
    def __init__(self, locId:int, coord:(str,str), municipio:str,  bairro:str, rua:str="", tipo:str=""):

        try:
            assert locId not in self.idList
        except AssertionError:
            sys.exit(f"\nIdentificador de local já existente.\nUse um diferente de {self.idList}.\nO programa será encerrado.")
        else:
            self.locId = locId
            self.idList.append(locId)
        
        
        try:
            # Esse try é apenas para garantir que os parâmetros da classe instaciada estão no formato correto. Não previne erros de usuários.
            assert isinstance(coord, tuple) and len(coord) == 2
            for item in coord:
                assert isinstance(item, str)
        except (ValueError, AssertionError):
            sys.exit("As coordenadas não foram digitadas da forma correta.\nO argumento deve ser uma tupla de duas strings de números float, com separador decimal de ponto (\".\").\nO programa será encerrado.")
        else:
            # Testes de erro de entrada do usuário.
            lat = testNumber("latitude", coord[0])
            lon = testNumber("longitude", coord[1])
            self.coord = (lat, lon)
                
        self.municipio = testEmpty("municipio", municipio)
        self.bairro = testEmpty("bairro", bairro)
        self.rua = rua  
        self.tipo = tipo
        
        
    def getMaps(self, addPlaces=[], zoom:int=np.NaN):
        """Este método cria uma imagem em formato .jpg do google maps.
        Entradas:
            --> addPlaces (list(Local)): informar outras instâncias de Local caso necessitar adicionar outras coordenadas na imagem;
            --> zoom (int): nível de zoom a ser aplicado na imagem. Caso addPlaces for vazio, o nível de zoom será obrigatório.
        Retorno:
            --> bytes: pronto para ser escrito em um arquivo.
        """

        places = [self] + addPlaces
        
        payload = {"size": "640x427",
           "scale": "2",
           "format": "jpeg",
           "maptype": "hybrid",
           "style": "feature:poi|visibility:off",
           "markers": [f"color:red|label:{place.locId}|size:mid|{place.coord[0]},{place.coord[1]}" for place in places],
           "key": settings.MAPS_API_KEY
       }
        

        if zoom is not np.NaN:
            payload["zoom"] = zoom
            return requests.get(settings.MAPS_URL, params=payload).content
                
        elif zoom is np.NaN and addPlaces != []:
            return requests.get(settings.MAPS_URL, params=payload).content
            
        else:
            sys.exit("Para obter mapa com apenas um marcador, o zoom deve ser informado.\nO programa será fechado.")
            
    def info(self):
        """Retorna informações do local.
        Este método não tem entradas, e o retorno é uma string.."""
        lat, long = self.coord
        return dedent(f"""
                Informações do local:
                Endereço: {self.rua + ',' if self.rua != '' else ''} {self.bairro}, {self.municipio} - PE
                Coordenadas: lat={lat}, long={long}
                Tipo de local: {self.tipo}.
                """)
                