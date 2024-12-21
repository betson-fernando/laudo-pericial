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
import pandas as pd


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

    def __init__(self, figdir: str, label: str, leg: str):

        self.figDir = figdir
        self.leg = leg
        self.label = label
        self.figsTex = ""

        # Procurar figuras
        
        std = re.compile(f"^{self.label}\\d*\\.(jpg|jpeg)$")  # Definição do padrão dos nomes de figuras (com extensão).

        # TODO: este while não responde a mudanças na pasta de figuras. Se eu corrigir o número de figuras, a exceção se mantém. Ele deveria sair do while quando eu corrigisse a numeração. Por algum motivo, Path(self.figDir).iterdir() chamado nas múltiplas passagens do loop while não altera se a pasta for atualizada.
        while True:
            try:
                # Arquivos que têm self.label em seus nomes e com extensão '.jpg', ou '.JPG'
                #Tentei usar glob em vez de iterdir, mas não vi vantagem, uma vez que preciso de um padrão de busca (regex) complexo para o glob.

                self.selectedFigs = [item.stem for item in Path(self.figDir).iterdir() if re.fullmatch(std, item.name.lower()) is not None]

                self.numFigs = len(self.selectedFigs)

                if self.selectedFigs != [] and self.selectedFigs[0][0].isdecimal():
                    # AJEITAR ESTA GAMBIARRA! ELA PULA A VERIFICAÇÃO DE CONSISTÊNCIA NOS NÚMEROS DAS FIGURAS NO CASO DE DUPLO HOMICÍDIO, SIMPLESMENTE PORQUE NÃO IMPLEMENTEI AINDA.
                    break
                    
                # Assegura que a lista de figuras vai de 1,2,3,...,numFigs
                if self.numFigs > 1: # Essa verificação não será executada se houver apenas uma figura, para dispensar a numeração. Ex.: "bolso.jpg"
                    condList = [(f'{self.label}{num}' in self.selectedFigs) for num in range(1, self.numFigs + 1)]  # Lista de booleanos B[i]. B[i] = True se figura[i] está na lista de figuras.
                    assert sum(condList) == self.numFigs # Assegurar que cada elemento da lista acima é verdadeiro, ou seja, toda figura[i] está na lista de figuras
            
            except AssertionError:
                sys.exit(f"{Bcolors.FAIL}Figuras '{self.label}' numeradas erroneamente. Assegurar que elas têm os números 1 a {self.numFigs}.\nO programa será fechado.{Bcolors.ENDC}") 
            else:
                break

        match self.numFigs:
            case 0:
                self.ref = ""
                self.figsTex = ""
            case 1:
                self.ref = ref(self.selectedFigs[0]) # Não usar self.label, pois a figura única poderá ser f"{label}.jpg", ou f"{label}1.jpg"
                self.figsTex = f"\\f{{{self.selectedFigs[0]}}}{{{self.leg}}}"
            case _:
                self.ref = f"{ref(self.label + '1')} e {ref(self.label + '2')}" if self.numFigs == 2 else f"{ref(self.label + '1')} a {ref(self.label + str(self.numFigs))}"
                for num in range(1, self.numFigs + 1):
                    self.figsTex += f"\\f{{{self.label}{num}}}{{{self.leg}}}\n"
                    
                    
    def textoFrase(self, frase:str):
        """Este método retorna um texto, cujas palavras irão flexionar para plural ou singular, a depender do número de figuras.
        Entrada: uma string com o formato adequado para a flexão de número (uso de |palavra|) e para a substituição das referências (uso de <ref>)
        Saída: frase com as palavras flexionadas em número, e as referências inseridas.
        """
    
        match self.numFigs:
            case 0:
                return "" if type(frase) == str else [""]*len(frase)
            case 1:
                return frase.replace("<ref>", self.ref).replace("|", "") if type(frase) == str else [item.replace("<ref>", self.ref).replace("|", "") for item in frase]
            case _:
                return plural(frase.replace("<ref>", self.ref)) if type(frase) == str else [plural(item.replace("<ref>", self.ref)) for item in frase]
    

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
        --> posicMembros: dicionário em que as chaves são os membros (ex.: 'inferior esquerdo'), e os valores, as respectivas posições (ex.: 'parcialmente estendido')
        --> instr: informa a arma, ou as armas, separadas por vírgula e espaço (", ")
        --> causa: causa da morte
            
    """
    
    nicList = []
    
    
    # def __init__(self, nome:str, nic:int, tipoDoc:str, numDoc:str, dataNasc:datetime.date, idade:int, filiacao:str, sexo:str, arma:list[str] or str): EXCLUIR SE COM A LINHA ABAIXO DER CERTO
    def __init__(self, dic:dict):
        
        self.nome = dic.get("nomeVit")
        while self.nome in ["", None]:
            self.nome = input(f"{Bcolors.WARNING}O nome da vítima não foi inserido na base de dados.\nInsira-o ou digite \"desconhecido\", caso não determinado.{Bcolors.ENDC}")
        
        self.dataNasc = self.setDataNasc(dic)
        
        self.filiacao = dic.get("mae")
        while self.filiacao.lower() in ["", None] and 'desconhec' not in self.nome.lower():
            self.filiacao = input(f"{Bcolors.WARNING}O nome de um dos genitores da vítima não foi inserido. Digite-o: {Bcolors.ENDC}")
        
        self.tipoDoc = dic.get("tipoDoc")
        while self.tipoDoc.lower() not in ["rg", "cnh", "carteira de trabalho", "desconhecido"] and 'desconhec' not in self.nome.lower():
            self.tipoDoc = input(f"{Bcolors.WARNING}O tipo do documento não foi informado corretamente. Digite \"rg\", \"cnh\", \"carteira de trabalho\", ou \"desconhecido\". {Bcolors.ENDC}")
            
        self.numDoc = dic.get("numDoc")
        while self.numDoc in ["", None] and 'desconhec' not in self.nome.lower():
            self.numDoc = input(f"{Bcolors.WARNING}O número do documento não foi informado. Insira-o ou digite \"desconhecido\": {Bcolors.ENDC}")
        
        self.sexo = dic.get("sexo").lower()
        while self.sexo not in ["masc", "fem", "indeterminado"]:
            self.sexo = input(f"{Bcolors.WARNING}O sexo da vítima não foi informado. Digite \"masc\", \"fem\", ou \"indeterminado\": {Bcolors.ENDC}")
        if 'masc' in self.sexo:
            self.sexo = 'masculino'
        elif 'fem' in self.sexo:
            self.sexo = 'feminino'
        else:
            self.sexo = 'indeterminado'
            
        nic = dic.get("nic")
        nic = assertType("nic", nic, int)
        while nic in self.nicList:
            nic = assertType(input(f"O NIC {nic} já existe. Digite o número correto: "))
        self.nic = nic
        
        self.nicList.append(nic)
        self.ordVit = len(self.nicList)  # Ordem da vítima para separação de fotos (Vítima 1, Vítima 2, etc...)
        
        self.cabelo = dic.get("cabelo").lower()
        self.pele = dic.get("pele").lower()
        
        self.pelosFaciais = {'barba': dic.get('barba').lower(), 'bigode': dic.get('bigode').lower(), 'cavanhaque': dic.get('cavanhaque').lower()}
        
        self.vestimentas = dic.get('vestimentas')
        self.calcados = dic.get('calcados').lower()
        
        self.posicCadaver = dic.get('posicCadaver')
        self.posicMembros = {'superior esquerdo': dic.get('posicMSE').lower(), 'superior direito': dic.get('posicMSD').lower(), 'inferior esquerdo': dic.get('posicMIE').lower(), 'inferior direito': dic.get('posicMID').lower()}
        
        self.instr = dic.get("arma").lower()
        self.causa = dic.get('causa').lower()
    
    
    def textoPelosFaciais(self):
        dicRes = {}
        
        # Este loop for agrupa uma lista de membros por posição, retornando um dicionário do tipo {posição: [membros]}
        for key, value in self.pelosFaciais.items():
            if value not in dicRes:
                dicRes[value] = [key]
            else:
                dicRes[value].append(key)
    
        texto = "com "
        
        numKeys = len(dicRes)
        num1 = 0
        
        for estado, pelos in dicRes.items():
            numPelos = len(pelos)

            for num2, pelo in enumerate(pelos):
                texto += pelo
                if num2 < numPelos - 2:
                    texto += ", "
                elif num2 == numPelos - 2:
                    texto += " e "
                else:
                    texto += " "
            
            if estado[-1] == 'o' and numPelos == 1 and pelos[0] == 'barba':
                # Se o estado flexionar em gênero, e houver apenas barba neste grupo, flexione o gênero (raspado -> raspada, aparado -> aparada, ...)
                texto += estado[:-1] + 'a'
            elif numPelos> 1:
                # Se o número de pelos for maior que 1, não flexione em gênero, mas flexione em número (raspado -> raspados, aparado -> aparados, ...)
                texto += estado + 's'
            else:
                # Todos os outros casos, não flexione.
                texto += estado
                
            if num1 < numKeys - 2:
                texto += ', '
            elif num1 == numKeys - 2:
                texto += ', e '
            
            num1 += 1

        return texto
    
    
    def textoPosicaoMembros(self):
        """Esta função usa self.posicMembros, que é um dicionário no qual as chaves são os membros, e seus valores,
        as posições dos membros, e agrupa os membros por posições iguais, retornando um texto para utilizar no laudo."""
        
        dicRes = {}
        
        # Este loop for agrupa uma lista de membros por posição, retornando um dicionário do tipo {posição: [membros]}
        for key, value in self.posicMembros.items():
            if value not in dicRes:
                dicRes[value] = [key]
            else:
                dicRes[value].append(key)
    
        texto = ""
        
        numKeys = len(dicRes)
        num1 = 0
        
        for posic, membros in dicRes.items():
            numMembros = len(membros)
            texto += "o membro " if len(membros) == 1 else "os membros "

            for num2, membro in enumerate(membros):
                texto += membro
                if num2 < numMembros - 2:
                    texto += ", "
                elif num2 == numMembros - 2:
                    texto += " e "
                else:
                    texto += " "
            
            texto += posic
            
            if numMembros > 1: texto += 's'
            
            if num1 < numKeys - 2:
                texto += ', '
            elif num1 == numKeys - 2:
                texto += ', e '
            
            num1 += 1

        return texto
    
    
    def setDataNasc(self, dic):
        dataNasc = dic.get("dataNasc")

        if dataNasc in [np.nan, "", None]:
            if 'desconhec' in self.nome.lower(): # Se for ID desconhecida, retorne None:
                return None
            else:                 # Se não for ID desconhecida, peça para inserir a data de nascimento.
                print(f"{Bcolors.WARNING}Data de nascimento não inserida. Insira no formato dd/mm/aaaa: {Bcolors.ENDC}")
                dataNasc = ""
                while True:
                    try:
                        return datetime.strptime(input(), "%d/%m/%Y")
                    except ValueError:
                        print(f"{Bcolors.WARNING}Data de nascimento no formato errado. Insira no formato dd/mm/aaaa: {Bcolors.ENDC}")  
                        
        elif dataNasc.__class__ is str:  # Caso for string, formate para datetime.date
        
            try:
                return datetime.strptime(dataNasc, "%d/%m/%Y")
            except ValueError:
                sys.exit(f"{Bcolors.FAIL}ERRO DE PROGRAMAÇÃO. A data de nascimento, em Vitima.setDataNasc(), NÃO TEM O FORMATO \"%d/%m/%Y\".{Bcolors.ENDC}")
            
        elif dataNasc.__class__ is pd.Timestamp:

            return dataNasc.to_pydatetime()
            
        else:
            sys.exit(f"{Bcolors.FAIL}ERRO DE PROGRAMAÇÃO.\nEm Vitima.setDataNasc(), a classe de dataNasc não está em 'str', 'pd.Timestamp', nem 'vazio'.{Bcolors.ENDC}")


    def setIdade(self, dataPlant: datetime.date) -> str:
        """Esta função calcula a idade, baseado na data de nascimento (atributo da vítima) e na data da perícia (dataPlant).
        Entradas: dataPlant --> data do plantão.
        Retorno: string no formato [idade] [unidade de tempo]"""

        try:
            assert self.dataNasc.__class__ is datetime
        except AssertionError:
            textoIdade = input(f"{Bcolors.WARNING}A idade da vítima NIC {self.nic} não pode ser calculada devido à ausência de sua data de nascimento.\nInsira sua idade aproximada (ex.: 20 anos), ou aperte 'ENTER' se não for possível determiná-la: {Bcolors.ENDC}")
        else:
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
        
    
    def exames(self, figLencol, figVit, figVitMov, figTat, figId, figPert, figLes, figEsqLes, figBalVit):
      
        texto = f"""
        \\subsection{{DO CADÁVER{'' if len(self.nicList) == 1 else ' ' + str(self.ordVit)}}}

        Ao chegar no local da ocorrência, a Equipe Técnica constatou a presença de um cadáver, que {figLencol.textoFrase('se encontrava envolto por um cobertor (|figura| <ref>). Após exposto, tal cadáver')} foi registrado em diferentes direções para permitir uma completa visualização da posição e condições iniciais em que foi encontrado. {figVit.textoFrase('|Esta| |fotografia| |está| |exibida| |na| |figura| <ref>:')}

        {figVit.figsTex}

        {figVitMov.textoFrase('Também |foi| |realizada| |fotografia| após a remoção da vítima até local adequado à Análise Perinecroscópica, conforme |figura| <ref>:')}

        {figVitMov.figsTex}

        {figBalVit.textoFrase('Após estes registros iniciais, foi procedida a manipulação do cadáver, durante a qual foi(foram) encontrado(s), sob ele, elemento(s) balístico(s), conforme |figura| <ref>:')}

        {figBalVit.figsTex}
        
        {figBalVit.textoFrase(r'Este(s) elemento(s) balístico(s) foi(foram) encaminhado(s) ao \bal.')}

        
        
        \\subsubsection{{IDENTIFICAÇÃO}}

        Mediante inspeção preliminar, foi constatado que este cadáver pertencia a um indivíduo do sexo {self.sexo.lower()}, tipo étnico {self.pele}, com cabelos ulótricos, {self.textoPelosFaciais() + ', ' if 'masc' in self.sexo.lower() else ''} de compleição normolínea, aparentando ter um metro e setenta centímetros de altura (1,70m)
        {' e aproximadamente ' + self.idade + ' de idade' if self.idade != '' else ''} (figura {ref('rosto')}).

        \\f{{rosto}}{{Fotografia do rosto do cadáver.}}

        {figTat.textoFrase('Na sua epiderme |foi| |constatada| |tatuagem|, |fotografada| e |exibida| |na| |figura| <ref>:')}

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
            texto += f"em {self.dataNasc.strftime('%d/%m/%Y')}, possuía, portanto, {self.idade} {figId.textoFrase(' (|figura| <ref>)')}."
        
        elif 'rg' in self.tipoDoc.lower():
            texto += f"No momento dos exames periciais, foi encontrada uma Carteira de Identidade pertencente ao indivíduo cujo cadáver estava sob análise, constatando que seu nome era {textbf(self.nome)}, filho(a) de {self.filiacao}. Seu número do R.G. era {self.numDoc}, com nascimento em {self.dataNasc.strftime('%d/%m/%Y')}, possuindo, portanto, {self.idade} {figId.textoFrase(' (|figura| <ref>)')}."
        
        elif 'cnh' in self.tipoDoc.lower():
            texto += f"No momento dos exames periciais, foi apresentada a Carteira Nacional de Habilitação (CNH) do indivíduo cujo cadáver estava sob análise, constatando que seu nome era {textbf(self.nome)}, filho(a) de {self.filiacao}. Seu número do R.G. era {self.numDoc}, com nascimento em {self.dataNasc.strftime('%d/%m/%Y')}, possuindo, portanto, {self.idade} {figId.textoFrase(' (|figura| <ref>)')}."
        
        elif 'ctps' in self.tipoDoc.lower():
            texto += f"No momento dos exames periciais, foi apresentada a Carteira de Trabalho e Previdência Social do indivíduo cujo cadáver estava sob análise, constatando que seu nome era {textbf(self.nome)}, filho(a) de {self.filiacao}. Seu número do R.G. era {self.numDoc}, com nascimento em {self.dataNasc.strftime('%d/%m/%Y')}, possuindo, portanto, {self.idade} {figId.textoFrase(' (|figura| <ref>)')}."

        
        texto += f"\n\n{figId.figsTex}\n\nFoi atribuído ao cadáver o Número de Identificação Cadavérica (NIC) {self.nic}, colocada a Pulseira de Identificação Cadavérica (PIC) "
        texto += r"""(figura \ref{pic}), e preenchido o Boletim de Identificação Cadavérica (BIC) (figura \ref{bic}).

        \f{pic}{Fotografia da PIC colocada no cadáver.}
        \f{bic}{Fotografia do BIC preenchido e encaminhado ao Instituto de Medicina Legal (IML).}
        """

        texto += f"""
        \\subsubsection{{VESTES E ACESSÓRIOS}}
         
        O cadáver ora periciado trajava {self.vestimentas}, {'e estava descalço' if 'descalço' in self.calcados.lower() else 'e calçava ' + self.calcados}, conforme {figVitMov.textoFrase('(|figura| <ref>)') if figVitMov.numFigs != 0 else figVit.textoFrase('|figura| <ref>')}."""

        if figPert.numFigs > 0:

            texto += f"""
            Ao analisar as adjacências e os bolsos presentes nas vestimentas do cadáver, foram encontrados os seguintes itens pessoais:

            \\begin{{itemize}}
                \\item
                \\item
                \\item
            \\end{{itemize}}
            
            {figPert.textoFrase('|Foi| |feito| |registro| |fotográfico| destes itens, que estão exibidos |na| |figura| <ref>:')}
            
            {figPert.figsTex}
            
            """
        
        texto += f"""
        
            \\subsubsection{{POSIÇÃO}}
             
            Quando da chegada da Equipe Técnica, o cadáver estava em {self.posicCadaver.lower()}, com {self.textoPosicaoMembros()} ({figVit.textoFrase('|figura| <ref>')}).

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
            
            {figLes.textoFrase('|A| |figura| <ref> |exibe| as lesões acima relatadas\n%,e |a| |numeração| |na| |imagem| |corresponde| |àquela| que |identifica| |a| |lesão| na lista acima:')}
            
            {figLes.figsTex}
            
            {figEsqLes.textoFrase(r'|A| |figura| <ref> |exibe|, através de |esquema|, as lesões encontradas no cadáver. Em |tal| |esquema|, as lesões representadas por um círculo são características de entrada de projétil, enquanto as representadas por um ``X'', saída de projétil, e, por fim, as indicadas por um quadrado não puderam ter suas características identificadas no momento do Exame Pericial.", "Esquema indicando os locais e tipos das lesões encontradas no cadáver. LEME, C-E-L. P. \textbf{Medicina Legal Prática Compreensível}. Barra do Garças: Ed. do Autor, 2010.')}
            
            {figEsqLes.figsTex}

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
        
        
    def getMaps(self, addPlaces=[], zoom:int=np.nan):
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
    
        if zoom is not np.nan:
            payload["zoom"] = zoom
            return requests.get(url, params=payload).content
                
        elif zoom is np.nan and addPlaces != []:
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
                conc += f"o indivíduo {textbf(self.objs[0].nome if 'desconhec' not in self.objs[0].nome else 'de IDENTIDADE DESCONHECIDA')}, cujo cadáver foi encontrado no dia {textbf(dataCiente.strftime('%d/%m/%Y'))}, no local já mencionado, "
                
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
                conc += f"os indivíduos {listToText(nomes)}, cujos cadáveres foram encontrados no dia {textbf(dataCiente.strftime('%d/%m/%Y'))}, no local já mencionado, tiveram mortes violentas causadas por projéteis disparados por arma(s) de fogo e que, pelas circunstâncias, caracteriza-se uma {textbf('AÇÃO HOMICIDA')}"
                
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
        