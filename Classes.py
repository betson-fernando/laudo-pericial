import sys
from pathlib import Path
import re
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parents[1]))
from GlobalFuncs import plural, assertType


class Figuras:
    """Esta classe gerencia a inserção de textos de figuras agrupadas por temas.

    Parâmetros de inicialização:

    figdir:str --> Diretório no qual se encontram as figuras.
    label:str --> nome comum a todas as figuras de um tipo específico.   
    frase:str ou list[str] --> Frases que citam figuras. O local que conterá à referência às figuras deve estar com o token <ref>;
        as palavras que flexionam em número deverão estar no singular, entre barras duplas (|palavra|).
        Ex: "|A| <ref> |contém| referências à vítima".
        Caso houver uma figura, a frase ficará: "A figura \ref{vit1} contém referências à vítima";
        Caso houver duas figuras, a frase ficará: "As figuras \ref{vit1} e \ref{vit2} contêm referências à vítima";
        Caso houver mais que duas figuras: "As figuras \ref{vit1} a \ref{vit2} contêm referências à vítima";
        Caso a entrada for lista de strings, esta operação acima descrita será realizada sobre todos os itens.
    leg: str --> Legenda a ser utilizada.

    Outros parâmetros:

    ref: str --> String da referência à(s) figura(s);
    figsTex:str --> String que insere as figuras no arquivo .tex;
    selectedFigs: List(str) --> Lista de strings com os nomes das figuras (sem extensão) que contém a string "label".
    """

    def __init__(self, figdir: str, label: str, frase: str or list[str], leg: str):

        self.figDir = figdir
        self.leg = leg
        self.label = label
        self.figsTex = ""

        # Procurar figuras
        std = re.compile(r"\d*" + self.label + r"\d*")  # Definição do padrão dos nomes de figuras (sem extensão).

        while True:
            try:
                # Arquivos que têm self.label em seus nomes e com extensão '.jpg', ou '.JPG'
                # TODO: USAR A FUNÇÃO GLOB EM VEZ DE ITERDIR
                self.selectedFigs =[item.stem for item in Path(self.figDir).iterdir() if (re.fullmatch(std, item.stem) is not None and item.suffix.lower() == '.jpg')]
                self.numFigs = len(self.selectedFigs)


                if self.selectedFigs != [] and self.selectedFigs[0][0].isdecimal():
                    # AJEITAR ESTA GAMBIARRA! ELA PULA A VERIFICAÇÃO DE CONSISTÊNCIA NOS NÚMEROS DAS FIGURAS NO CASO DE DUPLO HOMICÍDIO, SIMPLESMENTE PORQUE NÃO IMPLEMENTEI AINDA.
                    break
                    
                # Assegurar que a lista de figuras vai de 1,2,3,...,numFigs
                if self.numFigs > 1: # Essa verificação não será executada se houver apenas uma figura, para dispensar a numeração. Ex.: "bolso.jpg"
                    condList = [(f'{self.label}{num}' in self.selectedFigs) for num in range(1, self.numFigs + 1)]  # Lista de booleanos B[i]. B[i] = True se figura[i] está na lista de figuras.
                    assert sum(condList) == self.numFigs # Assegurar que cada elemento da lista acima é verdadeiro, ou seja, toda figura[i] está na lista de figuras
            
            except AssertionError:
                print(f"Número de figuras: {self.numFigs}")
                print(f"Caminho: {self.figDir}")
                print(f"Lista de Figuras: {self.selectedFigs}")
                input(f"Assegurar que a lista de figuras '{self.label}' têm os números 1 a {self.numFigs}.")
            else:
                break


        match self.numFigs:
            case 0:
                self.ref = ""
                self.frase = "" if type(frase) == str else [""]*len(frase)
                self.figsTex = ""
            case 1:
                self.ref = f"\\ref{{{self.selectedFigs[0]}}}" # Não usar self.label, pois a figura única poderá ser f"{label}.jpg", ou f"{label}1.jpg"
                self.frase = frase.replace("<ref>", self.ref).replace("|", "") if type(frase) == str else [item.replace("<ref>", self.ref).replace("|", "") for item in frase]
                self.figsTex = f"\\f{{{self.selectedFigs[0]}}}{{{self.leg}}}"
            case _:
                self.ref = f"\\ref{{{self.label}1}} e \\ref{{{self.label}2}}" if self.numFigs == 2 else f"\\ref{{{self.label}1}} a \\ref{{{self.label}{self.numFigs}}}"
                self.frase = plural(frase.replace("<ref>", self.ref)) if type(frase) == str else [plural(item.replace("<ref>", self.ref)) for item in frase]
                
                for num in range(1, self.numFigs + 1):
                    self.figsTex += f"\\f{{{self.label}{num}}}{{{self.leg}}}\n"

from datetime import datetime


class Servidor:
    
    def __init__(self,  nome:str, cargo:str, operativa:str, mat:str, grupo:str):
        while nome in [None, ""]:
            nome = input("Digite o nome do Delegado que compareceu ao local: ")
        self.nome = nome
        self.mat = assertType('matrícula', mat, int)
        self.operativa = operativa
        self.cargo = cargo
        self.grupo = grupo
    
    def getTexto(self):
        textoMat = "" if self.mat in [None, ""] else f", inscrito no cadastro da {self.operativa} sob a matrícula {self.mat[0:3]}.{self.mat[3:6]}-{self.mat[6]}"
        textoGrupo = "" if self.grupo in [None, ""] else f", pertencente a(o) {self.grupo}"
        if self.grupo in [None, ""]:
            textoGrupo = ""
        elif "militar" in self.grupo.lower():
            textoGrupo = f", pertencente ao {self.grupo}º Batalhão desta corporação"
        else:
            textoGrupo = f", pertencente a(o) {input('Digitar o grupo ao qual o First Responder pertence')}"
            
        return f"{self.cargo} \\textbf{{{self.nome.upper()}}}{textoMat}{textoGrupo}"


class Vitima:
    
    nicList = []
    
    def __init__(self, nome:str, nic:int, tipoId:str, numId:str, dataNasc:datetime.date, filiacao:str):
        self.nome = nome
        
        nic = assertType("nic", nic, int)
        
        while nic in nicList:
            nic = assertType(input(f"O NIC {nic} já existe. Digite o número correto: "))
        self.nic = nic
        nicList.append(nic)
        
        self.tipoId = tipoId
        self.numId = numId
        self.dataNasc = assertType("data de nascimento", dataNasc, date)
        self.filiacao = filiacao
        
        if self.nome is not None and None in [tipoId, numId, dataNasc, filiacao]:
            print("Algumas informações da vítima não foram inseridas.\n Favor preencher:\n")
            if self.tipoId is None:
                self.tipoId = input("Tipo do documento de identificação: ")
            if self.numId is None:
                self.numId = input("Número do documento de identificação: ")
            if self.dataNasc is None:
                self.dataNasc = input("Data de nascimento (formato: dd/mm/aaaa): ")
            if self.filiacao is None:
                self.filiacao = input("Filiação (apenas um dos genitores): ")
        
    def getIdade(self, dataPlant: datetime.date) -> str:
        """Esta função calcula a idade, baseado na data de nascimento (atributo da vítima) e na data da perícia (dataPlant).
        Entradas: dataPlant --> data do plantão.
        Retorno: string no formato [idade] [unidade de tempo]"""

        try:
            assert self.dataNasc == self.dataNasc and self.dataNasc != ""
        except AssertionError:
            print(f"A idade da vítima {self.nic} não pode ser calculada devido à ausência de sua data de nascimento.")
            return ""
        else:
            if self.dataNasc.__class__ is str:  # Caso for string, formate para datetime.date
                temp = self.dataNasc
                self.dataNasc = datetime.strptime(temp, "%d/%m/%Y")
            delta_date = monthdelta.monthmod(self.dataNasc, dataPlant)
            delta_mes = delta_date[0].months

            if delta_mes >= 12:
                idade_temp = int(delta_mes / 12)
                if idade_temp >= 2:
                    return f"{idade_temp} anos"
                else:
                    return "1 ano"

            elif 2 <= delta_mes <= 11:
                return f"{delta_mes} meses"

            elif delta_mes == 1:
                return "1 mês"
            else:
                idade_temp = delta_date[1].days
                if idade_temp >= 2:
                    return f"{idade_temp} dias"
                elif idade_temp == 1:
                    return "1 dia"
                else:
                    return "menos de um dia de vida"


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
           "key": environ.get('MAPS_API_KEY')
        }
        
        url = environ.get('MAPS_URL')
    
        if zoom is not np.NaN:
            payload["zoom"] = zoom
            return requests.get(url, params=payload).content
                
        elif zoom is np.NaN and addPlaces != []:
            return requests.get(url, params=payload).content
            
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