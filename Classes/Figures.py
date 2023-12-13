import os
import sys

class Figures():
    """Esta classe gerencia a inserção de textos de figuras agrupadas por temas.
    Parâmetros de inicialização:
    label:str --> nome comum a todas as figuras de um tipo específico.
    figlist: List[str] --> Lista de paths de figuras de um tipo específico.
    """

    def __init__(self, figdir:str, leg:str, label:str=None, figlist:list=None):
        try:
            assert (label is None and figlist is None) or (label is not None and figlist is not None)
        except AssertionError:
            sys.exit("Classe não instaciada corretamente: Ou label ou figList devem ser None.")
        else:
            self.figdir = figdir
            self.leg = leg
            self.label = label
            self.figlist = figlist


    def procurarFigs(self):
        allfigs = os.listdir(path)
        for item in allfigs:
            


    def inserirFigs(self):
        if self.figlist is None:
            figsList = self.procurarFigs()
