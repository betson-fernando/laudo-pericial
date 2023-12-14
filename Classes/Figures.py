import os
from globalfuncs.funcs import plural


class Figuras:
    """Esta classe gerencia a inserção de textos de figuras agrupadas por temas.

    Parâmetros de inicialização:

    figdir:str --> Diretório no qual se encontram as figuras.
    leg: str --> Legenda a ser utilizada.
    label:str --> nome comum a todas as figuras de um tipo específico.
    intro:str --> chamada das figuras. O local que conterá à referência às figuras deve estar com o token <ref>;
        as palavras que flexionam em número deverão estar no singular, entre barras duplas (|palavra|).
        Ex: "|A| <ref> |contém| referências à vítima".
        Caso houver uma figura, a frase ficará: "A figura \ref{vit1} contém referências à vítima";
        Caso houver duas figuras, a frase ficará: "As figuras \ref{vit1} e \ref{vit2} contêm referências à vítima";
        Caso houver mais que duas figuras: "As figuras \ref{vit1} a \ref{vit2} contêm referências à vítima";

    Outros parâmetros:

    figsTex:str --> String que insere as figuras no arquivo .tex;
    selectedFigs: List(str) --> Lista de strings com os nomes das figuras (sem extensão) que contém a string "label";
    """

    def __init__(self, figdir: str, leg: str, label: str, intro: str):

        self.figDir = figdir
        self.leg = leg
        self.label = label
        self.figsTex = ""

        # Procurar figuras
        allFigs = os.listdir(self.figDir)
        self.selectedFigs = [item.replace(".jpg", "") for item in allFigs if self.label in item]

        # Gerar introdução
        numFigs = len(self.selectedFigs)
        match numFigs:
            case 0:
                self.intro = ""
            case 1:
                self.intro = intro.replace("<ref>", f"\\ref{{{self.label}1.jpg}}").replace("|", "")
            case 2:
                self.intro = plural(intro.replace("<ref>", f"\\ref{{{self.label}1.jpg}} e \\ref{{{self.label}2.jpg}}"))
            case _:
                print("Três")
                self.intro = plural(intro.replace("<ref>",
                                                  f"\\ref{{{self.label}1.jpg}} a \\ref{{{self.label}{numFigs}.jpg}}"))

        # Inserir figuras
        for num in range(1, numFigs + 1):
            self.figsTex += f"\\f{{{self.label}{num}}}{{{self.leg}}}\n"


tres = Figuras("Figs", "Fotografia das lesões da vítima sob análise.", "cheg", "|A| |figura| <ref> |contém| |a| |fotografia| "
                                                                        "da vítima:")
dois = Figuras("Figs", "Fotografia das lesões da vítima sob análise.", "alt", "|A| |figura| <ref> |contém| |a| |fotografia| "
                                                                        "da vítima:")

um = Figuras("Figs", "Fotografia das lesões da vítima sob análise.", "test", "|A| |figura| <ref> |contém| |a| |fotografia| "
                                                                        "da vítima:")


pass