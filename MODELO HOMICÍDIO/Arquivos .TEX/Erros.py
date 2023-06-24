# Este programa encontra os erros mais comuns nos arquivos .tex.

import os
import re


def countbrack(string: str) -> bool:
    """Esta função conta as chaves de uma linha. Se alguma chave for aberta ou fechada erroneamente, retorna erro."""
    cont = 0
    for char in string:
        if char == "{":
            cont += 1
        elif char == "}":
            cont -= 1
            if cont < 0:
                return False
        elif char == "\n" and cont != 0:
            return False
    return True


def comment(sch: str, row: str) -> bool:
    """Esta função retorna True se o trecho em que 'sch' ocorre em 'row' estiver comentado. Caso contrário, retorna False. Se sch = '"", a função analise se toda a linha está comentada.

    Exemplo: comment("casa", "Eu vou % para casa") = True; comment("A casa é % bonita") = False.
    """

    subs = row.split(sch)[0]
    if "%" in subs and r"\%" not in subs:
        return True
    return False


# Lista arquivos de extensão .tex
os.chdir(os.path.dirname(os.path.realpath(__file__)))
files = [f for f in os.listdir() if '.tex' in f and '.bak' not in f and os.path.isfile(f)]

if len(files) == 0:
    input("Não há arquivo \".tex\" na pasta atual. Pressione \"Enter\" para sair.")
    file = ""
    exit()
if len(files) == 1:
    file = files[0]
else:
    passou = 0
    file = input("Digite o nome do arquivo \".tex\", incluindo a extensão:")
    while passou == 0:
        if file in files:
            passou = 1
        else:
            file = input("Arquivo não encontrado. Digite o nome correto, incluindo a extensão: ")

with open(file, "r", encoding='utf8') as f:
    lines = f.readlines()

ind = 0
for line in lines:
    if "begin{document}" in line:
        ind = lines.index(line)
        break

del lines[0:ind+1]

comm = [r"\horaciente", r"\rep", r"\req", r"\aux", r"\PM", r"\bat", r"\matPM", r"\coord", r"\idade", r"\CTPSnum", r"\nic", r"\rua", r"\bairro", r"\municipio", r"\nome", r"\filiacao", r"\rg", r"\datanasc", r"\dataciente", r"\horainicio", r"\horafim",
        r"\arma", r"\titulo", r"\tableofcontents", r"\setcounter", r"\newpage", r"\noindent", r"\caso", r"\CASO", r"\begin", r"\end", r"\centering", r"\section", r"\subsection", r"\subsubsection", r"\f",
        r"\setcounterpageref", r"\setcounterref", r"\vspace", r"\rule", r"\raggedleft", r"\label", r"\emph", r"\textbf", r"\sl", r"\bf", r"\ref", r"\item", r"\igfec", r"\hline", r"\multicolumn", r"\caption", r"\tipoinst",
        r"\MakeLowercase", r"\bal", r"\f", r"\fig", r"\extenso", r"\value", r"\thefigure", r"\thepgf", r"\today"]

fig_list = os.listdir("../Fotografias")

print("\n")
for line in lines:
    line_num = ind + lines.index(line) + 2

    # Analisa se a disposição e número de chaves está correta
    if not countbrack(line):
        print(f"Linha {line_num}: Número errado de chaves.")

    comm_match = re.findall(r"\\\w+", line)   # Encontra todos os comandos na linha

    if comm_match and line[0] != "%":   # Se houver ao menos um resultado cuja linha não seja comentada:
        for item in comm_match:
            if not comment(item, line):
                if item not in comm:
                    print(f"Linha {line_num}: Comando \"{item}\" não reconhecido.")
                elif item == r"\f":
                    fig = re.search(r"\\f{(([a-zA-Z]|[0-9])+)", line).group(1)

                    if (fig + ".jpg" not in fig_list) and (fig + ".JPG" not in fig_list):
                        print(f"Linha {line_num}: Figura \"{fig}.jpg\" não encontrada.")

input("\n\nPressione \"Enter\" para continuar.")
