import sys
from pathlib import Path
import re

sys.path.insert(0, str(Path(__file__).parents[1]))
from globalfuncs.funcs import plural


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
