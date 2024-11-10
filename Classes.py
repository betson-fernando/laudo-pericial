import sys
from pathlib import Path
import re
from datetime import datetime
import numpy as np
from textwrap import dedent
from os import environ
import requests
import codecs
import monthdelta

sys.path.insert(0, str(Path(__file__).parents[1]))
from GlobalFuncs import plural, assertType, testNumber, testEmpty, putNumbPoints, listToText, textbf, ref


class Veiculo:
    pass
    
    
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
        
        std = re.compile(f"^{self.label}\\d*\\.(jpg|jpeg)$")  # Definição do padrão dos nomes de figuras (com extensão).

        while True:
            try:
                # Arquivos que têm self.label em seus nomes e com extensão '.jpg', ou '.JPG'
                # TODO: USAR A FUNÇÃO GLOB EM VEZ DE ITERDIR
                self.selectedFigs =[item.stem for item in Path(self.figDir).iterdir() if re.fullmatch(std, item.name.lower()) is not None]
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
                self.ref = ref(self.selectedFigs[0]) # Não usar self.label, pois a figura única poderá ser f"{label}.jpg", ou f"{label}1.jpg"
                self.frase = frase.replace("<ref>", self.ref).replace("|", "") if type(frase) == str else [item.replace("<ref>", self.ref).replace("|", "") for item in frase]
                self.figsTex = f"\\f{{{self.selectedFigs[0]}}}{{{self.leg}}}"
            case _:
                self.ref = f"{ref(self.label + '1')} e {ref(self.label + '2')}" if self.numFigs == 2 else f"{ref(self.label + '1')} a {ref(self.label + str(self.numFigs))}"
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
        self.mat = putNumbPoints(self.mat[:-1]) + "-" + self.mat[-1]
        self.operativa = operativa
        self.cargo = cargo
        self.grupo = grupo
    
    def getTexto(self):
        textoMat = "" if self.mat in [None, ""] else f", inscrito no cadastro da {self.operativa} sob a matrícula {self.mat}"
        textoGrupo = "" if self.grupo in [None, ""] else f", pertencente ao {self.grupo}º Batalhão desta corporação"
            
        return f"{self.cargo} {textbf(self.nome.upper())}{textoMat}{textoGrupo}"


class Vitima:
    """Representa uma vítima. O único argumento é um dicionário com as seguintes chaves:
        --> nomeVit: Nome da vítima, tipo <str>
        --> dataNasc: Data de nascimento, tipo <datetime.datetime>
        --> filiacao: Nome da mãe (ou outro genitor caso não houver), tipo <str>
        --> tipoDoc: Tipo do documento, tipo <str>
        --> numDoc: Número do documento, tipo <str>
        --> sexo: Sexo biológico da vítima, tipo <str>
        --> nic: Número do NIC, tipo <str>
        --> idade: Idade da vítima
        --> cabelo: tipo do cabelo da vítima
        --> pele: tipo da pele da vítima
        --> bigode: descreve o bigode
        --> cavanhaque: descreve o cavanhaque
        --> vestimentas: descreve as vestimentas
        --> calcados: descreve os calçados
        --> posicCadaver: posicionamento do cadáver
        --> posicMSE: posicionamento do membro superior esquerdo
        --> posicMSD: posicionamento do membro superior direito
        --> posicMIE: posicionamento do membro inferior esquerdo
        --> posicMID: posicionamento do membro inferior direito
        --> instr: informa a arma, ou as armas, separadas por vírgula e espaço (", ")
        --> causa: causa da morte
            
    """
    
    nicList = []
    
    
    # def __init__(self, nome:str, nic:int, tipoDoc:str, numDoc:str, dataNasc:datetime.date, idade:int, filiacao:str, sexo:str, arma:list[str] or str): EXCLUIR SE COM A LINHA ABAIXO DER CERTO
    def __init__(self, dic:dict):
        
        self.nome = dic.get("nomeVit")
        while self.nome in ["", None]:
            self.nome = input(f"{Bcolors.WARNING} O nome da vítima não foi inserido na base de dados.\nInsira-o ou digite \"desconhecido\", caso não determinado.{Bcolors.ENDC}")
        
        dataNasc = dic.get("dataNasc")
        self.dataNasc = None if dataNasc is None else dataNasc
        
        self.filiacao = dic.get("mae")
        
        self.tipoDoc = dic.get("tipoDoc")
        while self.tipoDoc in ["", None] and 'desconhec' not in self.nome.lower():
            self.tipoDoc = input(f"{Bcolors.WARNING} O tipo do documento não foi informado. Insira-o ou digite \"desconhecido\", caso não determinado.{Bcolors.ENDC}")
            
        self.numDoc = dic.get("numDoc")
        while self.numDoc in ["", None] and 'desconhec' not in self.nome.lower():
            self.numDoc = input(f"{Bcolors.WARNING} O número do documento não foi informado. Insira-o ou digite \"desconhecido\", caso não determinado.{Bcolors.ENDC}")
            
        self.sexo = dic.get("sexo")
        
        nic = dic.get("nic")
        nic = assertType("nic", nic, int)
        
        while nic in self.nicList:
            nic = assertType(input(f"O NIC {nic} já existe. Digite o número correto: "))
        self.nic = nic
        
        self.nicList.append(nic)
        self.ordVit = len(self.nicList)  # Ordem da vítima para separação de fotos (Vítima 1, Vítima 2, etc...)
        
        self.cabelo = dic.get("cabelo")
        self.pele = dic.get("pele")
        self.barba = dic.get('barba')
        self.bigode = dic.get('bigode')
        self.cavanhaque = dic.get('cavanhaque')
        self.vestimentas = dic.get('vestimentas')
        self.calcados = dic.get('calcados')
        
        self.posicCadaver = dic.get('posicCadaver')
        self.posicMembros = {'mse': dic.get('posicMSE'), 'msd': dic.get('posicMSD'), 'mie': dic.get('posicMIE'), 'mid': dic.get('posicMID')}
        self.posicMSE = dic.get('posicMSE')
        self.posicMSD = dic.get('posicMSD')
        self.posicMIE = dic.get('posicMIE')
        self.posicMID = dic.get('posicMID')
        
        self.instr = dic.get("arma")
        self.causa = dic.get('causa')
        
        
        if self.nome is not None and None in [self.tipoDoc, self.numDoc, self.dataNasc, self.filiacao]:
            print("Algumas informações da vítima não foram inseridas.\n Favor preencher:\n")
            if self.tipoDoc is None:
                self.tipoDoc = input("Tipo do documento de identificação: ")
            if self.numDoc is None:
                self.numDoc = input("Número do documento de identificação: ")
            if self.dataNasc is None:
                self.dataNasc = input("Data de nascimento (formato: dd/mm/aaaa): ")
            if self.filiacao is None:
                self.filiacao = input("Filiação (apenas um dos genitores): ")
        
    def setIdade(self, dataPlant: datetime.date) -> str:
        """Esta função calcula a idade, baseado na data de nascimento (atributo da vítima) e na data da perícia (dataPlant).
        Entradas: dataPlant --> data do plantão.
        Retorno: string no formato [idade] [unidade de tempo]"""

        try:
            assert self.dataNasc == self.dataNasc and self.dataNasc != ""
        except AssertionError:
            print(f"A idade da vítima {self.nic} não pode ser calculada devido à ausência de sua data de nascimento.")
            textoIdade = ""
        else:
            if self.dataNasc.__class__ is str:  # Caso for string, formate para datetime.date
                temp = self.dataNasc
                self.dataNasc = datetime.strptime(temp, "%d/%m/%Y")

            delta_date = monthdelta.monthmod(self.dataNasc, dataPlant)
            delta_mes = delta_date[0].months

            if delta_mes >= 12:
                idade_temp = int(delta_mes / 12)
                if idade_temp >= 2:
                    textoIdade = f"{idade_temp} anos"
                else:
                    textoIdade = "1 ano"

            elif 2 <= delta_mes <= 11:
                textoIdade = f"{delta_mes} meses"

            elif delta_mes == 1:
                textoIdade = "1 mês"
            else:
                idade_temp = delta_date[1].days
                if idade_temp >= 2:
                    textoIdade = f"{idade_temp} dias"
                elif idade_temp == 1:
                    textoIdade = "1 dia"
                else:
                    textoIdade = "menos de um dia de vida"
        finally:
            self.idade = textoIdade
            
            
    def info(self):
        return dedent(f"""
            Vítima {self.ordVit}:
            
            Nome: {self.nome};
            NIC: {self.nic};
            Tipo do documento: {self.tipoDoc};
            Número do documento: {self.numDoc};
            Filiação: {self.filiacao};
            Data de Nascicmento: {self.dataNasc}.
        """)
        
        
    def exames(self, imagesPath):
    
        figLencol = Figuras(imagesPath, "lencol", "se encontrava envolto por um cobertor (|figura| <ref>). Após exposto, tal cadáver", "")

        figVit = Figuras(imagesPath, "vit", ["|Esta| |fotografia| |está| |exibida| |na| |figura| <ref>:",  "|figura| <ref>"], "Fotografia do cadáver em sua posição original.")

        figVitMov = Figuras(imagesPath, "vitmov", ["Também |foi| |realizada| |fotografia| após a remoção da vítima até local adequado à Análise Perinecroscópica, conforme |figura| <ref>:", "(|figura| <ref>)"], "Fotografia do cadáver após a sua remoção a local adequado.")

        figTat = Figuras(imagesPath, "tat", "Na sua epiderme |foi| |constatada| |tatuagem|, |fotografada| e |exibida| |na| |figura| <ref>:", "Fotografia de tatuagem no cadáver.")

        figId = Figuras(imagesPath, "id", " (|figura| <ref>)", "Fotografia de documento de identificação do cadáver.")

        figPert = Figuras(imagesPath, "pert", "|Foi| |feito| |registro| |fotográfico| destes itens, que estão exibidos |na| |figura| <ref>:", "Fotografia de objeto(s) encontrado(s) com o cadáver.")

        figLes = Figuras(imagesPath, "les", "|A| |figura| <ref> |exibe| as lesões acima relatadas\n%,e as numerações nas imagens correspondem àquelas que identificam as lesões na lista acima\n:", "Lesões constatadas no cadáver.")

        figEsq = Figuras(imagesPath, "esq", r"|A| |figura| <ref> |exibe|, através de |esquema|, as lesões encontradas no cadáver. Em |tal| |esquema|, as lesões representadas por um círculo são características de entrada de projétil, enquanto as representadas por um ``X'', saída de projétil, e, por fim, as indicadas por um quadrado não puderam ter suas características identificadas no momento do Exame Pericial.", "Esquema indicando os locais e tipos das lesões encontradas no cadáver. LEME, C-E-L. P. \textbf{Medicina Legal Prática Compreensível}. Barra do Garças: Ed. do Autor, 2010.")

        figBalVit = Figuras(imagesPath, "balvit", ["Após estes registros iniciais, foi procedida a manipulação do cadáver, durante a qual foi(foram) encontrado(s), sob ele, elemento(s) balístico(s), conforme |figura| <ref>:", r"Este(s) elemento(s) balístico(s) foi(foram) encaminhado(s) ao \bal."], "Fotografia de elemento(s) balístico(s) encontrado(s) dentro das vestes do cadáver.")

        figVest = Figuras(imagesPath, "vest", ["|Todo| |o| |vestígio| |foi| devidamente |fotografado| no local, |selado| em |lacre| |numerado|, e novamente |fotografado| em |seu| |lacre|, conforme |figura| <ref>, antes de |ser| |enviado| |ao| |seu| |respectivo| |destino|. Detalhes |do| |envio| poderão ser |consultado|"], "Fotografia de vestígio lacrado. Na faixa vermelha está presente o número do lacre")
        
        
        texto = f"""
        \\subsection{{DO CADÁVER{"" if len(self.nicList) == 1 else " " + str(self.ordVit)}}}

        Ao chegar no local da ocorrência, a Equipe Técnica constatou a presença de um cadáver, que {figLencol.frase} foi registrado em diferentes direções para permitir uma completa visualização da posição e condições iniciais em que foi encontrado. {figVit.frase[0]}

        {figVit.figsTex}

        {figVitMov.frase[0]}

        {figVitMov.figsTex}

        {figBalVit.frase[0]}

        {figBalVit.figsTex}

        {figBalVit.frase[1]}

        \\subsubsection{{IDENTIFICAÇÃO}}

        Mediante inspeção preliminar, foi constatado que este cadáver pertencia a um indivíduo do sexo masculino, tipo étnico faioderma, com cabelos ulótricos, barba e bigode presentes, de compleição normolínea, aparentando ter um metro e setenta centímetros de altura (1,70m) e aproximadamente 
            {self.idade}
            %vinte (20) anos 
        de idade (figura {ref('rosto')}).

        \\f{{rosto}}{{Fotografia do rosto do cadáver.}}

        {figTat.frase}

        {figTat.figsTex}
        
        """
        
        if 'desconhec' in self.nome.lower():  # IDENTIDADE DESCONHECIDA
            texto += "No momento dos exames periciais, não foram apresentados quaisquer documentos que identificassem o indivíduo cujo cadáver estava sob análise, motivo pelo qual sua identidade foi declarada como sendo desconhecida."
        
        elif figId.numFigs == 0:   # RECONHECIDO COM CADASTRO CONFIÁVEL NO SISTEMA
            texto += f"No momento dos exames periciais, não foram apresentados quaisquer documentos que identificassem o indivíduo cujo cadáver estava sob análise. Contudo, a informação de familiares, aliada a pesquisa no sistema \"Polícia Ágil\", da Secretaria de Defesa Social de Pernambuco, revelou se tratar de {textbf(self.nome)}, filho(a) de {self.filiacao}."
            
            if self.numDoc not in ["", None]:
                texto += f"Seu número do R.G. era {str(self.numDoc)}. Era nascido "
            else:
                texto += "Nascido"
            texto += f"em {self.dataNasc.day}/{self.dataNasc.month}/{self.dataNasc.year}, possuía, portanto, {self.idade} {figId.frase}."
        
        elif 'rg' in self.tipoDoc.lower():
            texto += f"No momento dos exames periciais, foi encontrada uma Carteira de Identidade pertencente ao indivíduo cujo cadáver estava sob análise, constatando que seu nome era {textbf(self.nome)}, filho(a) de {self.filiacao}. Seu número do R.G. era {self.numDoc}, com nascimento em {self.dataNasc.day}/{self.dataNasc.month}/{self.dataNasc.year}, possuindo, portanto, {self.idade} {figId.frase}."
        
        elif 'cnh' in self.tipoDoc.lower():
            texto += f"No momento dos exames periciais, foi apresentada a Carteira Nacional de Habilitação (CNH) do indivíduo cujo cadáver estava sob análise, constatando que seu nome era {textbf(self.nome)}, filho(a) de {self.filiacao}. Seu número do R.G. era {self.numDoc}, com nascimento em {self.dataNasc.day}/{self.dataNasc.month}/{self.dataNasc.year}, possuindo, portanto, {self.idade} {figId.frase}."
        
        elif 'ctps' in self.tipoDoc.lower():
            texto += f"No momento dos exames periciais, foi apresentada a Carteira de Trabalho e Previdência Social do indivíduo cujo cadáver estava sob análise, constatando que seu nome era {textbf(self.nome)}, filho(a) de {self.filiacao}. Seu número do R.G. era {self.numDoc}, com nascimento em {self.dataNasc.day}/{self.dataNasc.month}/{self.dataNasc.year}, possuindo, portanto, {self.idade} {figId.frase}."

        # NÃO ESTÁ FUNCIONANDO A INSERÇÃO DAS FIGURAS ID.
        {figId.figsTex}
        
        
        texto += f"Foi atribuído ao cadáver o Número de Identificação Cadavérica (NIC) {self.nic}, colocada a Pulseira de Identificação Cadavérica (PIC) "
        texto += r"""(figura \ref{pic}), e preenchido o Boletim de Identificação Cadavérica (BIC) (figura \ref{bic}).

        \f{pic}{Fotografia da PIC colocada no cadáver.}
        \f{bic}{Fotografia do BIC preenchido e encaminhado ao Instituto de Medicina Legal (IML).}
        """

        texto += f"""
        \\subsubsection{{VESTES E ACESSÓRIOS}}
         
        O cadáver ora periciado trajava {self.vestimentas}, {'e estava descalço' if 'descalço' in self.calcados.lower() else 'e calçava ' + self.calcados}, conforme {figVitMov.frase[1] if figVitMov.numFigs != 0 else figVit.frase[1]}."""

        if figPert.numFigs > 0:

            texto += r"""
            Ao analisar as adjacências e os bolsos presentes nas vestimentas do cadáver, foram encontrados os seguintes itens pessoais:

            \begin{itemize}
                \item
                \item
                \item
            \end{itemize}
            
            """

            texto += f"{figPert.frase}\n\n{figPert.figsTex}"
        
        texto += f"""
            \\subsubsection{{POSIÇÃO}}
             
            Quando da chegada da Equipe Técnica, o cadáver estava em {self.posicCadaver.lower()}, com o membro superior direito {self.posicMSD.lower()}, membro superior esquerdo {self.posicMSE.lower()}, membro inferior direito {self.posicMID.lower()}, e membro inferior esquerdo {self.posicMIE.lower()} ({figVit.frase[1]}).

            \\subsubsection{{PERINECROSCOPIA}}

            %TODO : Descrever rigidez, manchas hipostáticas, etc

            Mediante Análise Perinecroscópica detalhada, foram constatadas lesões perfurocontusas provocadas por projéteis disparados por arma de fogo, a saber:

            \\begin{{enumerate}}
                \\item Lesão similar àquelas provocadas por saída de projétil na região epigástrica;
                \\item Lesão similar àquelas provocadas por saída de projétil na região epigástrica;
                \\item Lesão similar àquelas provocadas por entrada de projétil no flanco esquerdo;
                \\item Lesão similar àquelas provocadas por saída de projétil na região torácica direita;
                \\item Lesão similar àquelas provocadas por saída de projétil na região infraclavicular direita;
                \\item Lesão similar àquelas provocadas por entrada de projétil no terço superior do braço direito;
                \\item Lesão similar àquelas provocadas por entrada de projétil na região auricular direita;
                \\item Lesão provocada por projétil disparado por arma de fogo no lado direito da região frontal;
                \\item Lesão provocada por projétil disparado por arma de fogo na região nasal;
                \\item Lesão provocada por projétil disparado por arma de fogo na região ilíaca direita;
                \\item Lesão similar àquelas provocadas por entrada de projétil na região lombar esquerda;
                \\item Lesão similar àquelas provocadas por entrada de projétil na região lombar direita;
                \\item Lesão similar àquelas provocadas por entrada de projétil na região dorsal direita;
                \\item Lesão similar àquelas provocadas por entrada de projétil na região escapular direita;
                \\item Lesão similar àquelas provocadas por entrada de projétil na porção posterior do antebraço direito;
                \\item Lesão similar àquelas provocadas por saída de projétil na porção anterior do antebraço direito;
                \\item Lesão similar àquelas provocadas por entrada de projétil na região supraescapular direita;
                \\item Lesão similar àquelas provocadas por entrada de projétil na região cervical;
                \\item Lesão similar àquelas provocadas por entrada de projétil na região occipital;
                \\item Lesão similar àquelas provocadas por entrada de projétil na região auricular esquerda.
            \\end{{enumerate}}

            {figLes.frase}

            {figLes.figsTex}

            {figEsq.frase}

            {figEsq.figsTex}

            Tais lesões, bem como possivelmente outras que não foram encontradas quando da perícia no local, deverão ser adequadamente descritas e fotografadas quando da Perícia Tanatoscópica, a ser realizada por médicos legistas do Instituto de Medicina Legal Antônio Persivo Cunha - IML.

            %É importante ressaltar que foi encontrada uma lesão típica de defesa no antebraço direito (ver figura {ref('antebraco')}).

            """
        return texto
        

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

class Conclusoes():
    """Esta classe gera a seção de conclusões do laudo.
    Como argumento, recebe uma lista com os sujeitos envolvidos, podendo ser da classe Vitima(), Veiculo(), ou Local(), mas devendo apenas ter um único tipo na lista.
    """

    def __init__(self, objs):

        
        for item in objs:
            if not isinstance(item, (Vitima, Veiculo, Local)):
                print(f"{Bcolors.FAIL}Erro na chamada da classe Conclusões. Um dos itens da lista não é instância das classes Vitima(), Veiculo(), ou Local().\nO programa será encerrado.{Bcolors.ENDC}")
                exit()
            if not isinstance(item, type(objs[0])):
                print(f"{Bcolors.FAIL}Erro na chamada da classe Conclusões. Foram encontrados itens da lista com tipos diferentes.\nO programa será encerrado.{Bcolors.ENDC}")
                exit()
                
        self.objs = objs
        self.tipo = type(objs[0])
        
    def texto(self, dataCiente):
        
        conc = r"""
            \section{CONCLUSÕES}

            Fundamentado nos exames realizados e em tudo quanto foi exposto no corpo deste laudo, o Perito Criminal por ele responsável conclui que """
        
        mesmaCausa = True
        
        for item in self.objs:
            if item.causa != self.objs[0]:
                mesmaCausa = False
        
        if self.tipo == Vitima:
            nomes = []
            causas = []
            instr = []
            for obj in self.objs:
                nomes.append(obj.nome)
                causas.append(obj.causa)
                instr.append(obj.instr)
                
            
            if len(self.objs) == 1:
                conc += f"o indivíduo {textbf(self.objs[0].nome if 'desconhec' not in self.objs[0].nome else 'de IDENTIDADE DESCONHECIDA')}, cujo cadáver foi encontrado no dia {textbf(f'{dataCiente.day}/{dataCiente.month}/{dataCiente.year}')}, no local já mencionado, "
                
                if "esclarecer" in self.objs[0].causa:
                    conc += r"""foi encontrado em estado de óbito, mas sem lesões aparentes nem circunstâncias que indicassem, naquele momento, um crime intencional. 
                    Portanto, as circunstâncias da morte restam \textbf{A ESCLARECER}."""
                else:
                    conc += r"""teve morte violenta em decorrência de lesões produzidas por instrumento(s) 
                    %
                    \tipoinst{ }
                    %
                    (""" + self.objs[0].instr.lower() +  r" ou similares) e que, pelas circunstâncias, caracteriza-se uma \textbf{AÇÃO HOMICIDA}."
            
            else:
                conc += f"os indivíduos {listToText(nomes)}, cujos cadáveres foram encontrados no dia {textbf(f'{dataCiente.day}/{dataCiente.month}/{dataCiente.year}')}, no local já mencionado, tiveram mortes violentas causadas por projéteis disparados por arma(s) de fogo e que, pelas circunstâncias, caracteriza-se uma {textbf('AÇÃO HOMICIDA')}"
                
                for nome in self.objs.nome:
                    teste = ""
        return conc
        
class Bcolors:

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    
class Observacoes:

    def __init__(self, endereco:Path):
        self.endereco = endereco
    
    def print(self):
        
        print('\033[96m\n')
        
        for item in self.endereco.glob('*.txt'):

            with codecs.open(item, 'r', 'utf-8') as f:
                text = f.read()
                print(f"\n{item.name}:\n{text}")
        
        print('\033[0m')
        
                