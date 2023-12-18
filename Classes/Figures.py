import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from globalfuncs.funcs import plural


class Figuras:
    """Esta classe gerencia a inserção de textos de figuras agrupadas por temas.

    Parâmetros de inicialização:

    figdir:str --> Diretório no qual se encontram as figuras.
    label:str --> nome comum a todas as figuras de um tipo específico.   
    intro:str --> chamada das figuras. O local que conterá à referência às figuras deve estar com o token <ref>;
        as palavras que flexionam em número deverão estar no singular, entre barras duplas (|palavra|).
        Ex: "|A| <ref> |contém| referências à vítima".
        Caso houver uma figura, a frase ficará: "A figura \ref{vit1} contém referências à vítima";
        Caso houver duas figuras, a frase ficará: "As figuras \ref{vit1} e \ref{vit2} contêm referências à vítima";
        Caso houver mais que duas figuras: "As figuras \ref{vit1} a \ref{vit2} contêm referências à vítima";
    leg: str --> Legenda a ser utilizada.

    Outros parâmetros:

    ref: str --> String da referência à(s) figura(s);
    figsTex:str --> String que insere as figuras no arquivo .tex;
    selectedFigs: List(str) --> Lista de strings com os nomes das figuras (sem extensão) que contém a string "label".
    """

    def __init__(self, figdir: str, label: str, intro: str, leg: str):

        self.figDir = figdir
        self.leg = leg
        self.label = label
        self.figsTex = ""

        # Procurar figuras
        
        while True:
            try:
                allFigs = os.listdir(self.figDir)
                self.selectedFigs = [item.replace(".jpg", "") for item in allFigs if self.label in item]
                numFigs = len(self.selectedFigs)
                print(f"Número de figuras: {numFigs}")
                # Lista de booleanos B[i]. B[i] = True se figura[i] está na lista de figuras.
                condList = [(f'{self.label}{num}' in self.selectedFigs) for num in range(1, numFigs + 1)]
                # Assegurar que cada elemento da lista acima é verdadeiro, ou seja, toda figura[i] está na lista de figuras
                assert sum(condList) == numFigs
            except AssertionError:
                input(f"Assegurar que a lista de figuras '{self.label}' têm os números 1 a {numFigs}.")
            else:
                break
            
        

        # Gerar introdução
        
        match numFigs:
            case 0:
                self.ref = ""
                self.intro = ""
            case 1:
                self.ref = f"\\ref{{{self.label}1}}"
                self.intro = intro.replace("<ref>", self.ref).replace("|", "")
            case 2:
                self.ref = f"\\ref{{{self.label}1}} e \\ref{{{self.label}2}}"
                self.intro = plural(intro.replace("<ref>", self.ref))
            case _:
                self.ref = f"\\ref{{{self.label}1}} a \\ref{{{self.label}{numFigs}}}"
                self.intro = plural(intro.replace("<ref>", self.ref))

        # Inserir figuras
        for num in range(1, numFigs + 1):
            self.figsTex += f"\\f{{{self.label}{num}}}{{{self.leg}}}\n"

"""
tres = Figuras(Path.joinpath(Path(__file__).parent, 'Figs'), "Fotografia das lesões da vítima sob análise.", "cheg", "|A| |figura| <ref> |contém| |a| |fotografia| "
                                                                        "da vítima:")
dois = Figuras(Path.joinpath(Path(__file__).parent, 'Figs'), "Fotografia das lesões da vítima sob análise.", "alt", "|A| |figura| <ref> |contém| |a| |fotografia| "
                                                                        "da vítima:")

um = Figuras(Path.joinpath(Path(__file__).parent, 'Figs'), "Fotografia das lesões da vítima sob análise.", "test", "|A| |figura| <ref> |contém| |a| |fotografia| "
                                                                        "da vítima:")

print("Três:\n")
print(f"{dois.intro}\n\n{dois.figsTex}")
input()"""