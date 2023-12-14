from pylatex import Document, Command
from pylatex.position import Center
from pylatex.package import Package
from pylatex.utils import NoEscape
from num2words import num2words
import os


def add_pack(pack, opt=None):
    doc.packages.append(Package(pack, options=opt))


def comm(command, args=None, extra_args=None):
    doc.packages.append(Command(command, arguments=args, extra_arguments=extra_args))


def entrar(msg: str, poss: list = None):
    passou = 0
    res = ""
    while not passou:
        res = input(msg)
        if poss is not None and res not in poss:
            print(f"Valor inserido incorretamente. Insira um do(s) seguinte(s): {poss}: ")
        elif poss is None or res in poss:
            passou = 1
        else:
            print("Erro na função \"entrar\".")
            exit()
    return res


def add_figs(figs_list: list, leg: str, *args) -> list:
    r"""Esta função adiciona figuras e referências no latex, diferenciando se irá adicionar uma, duas ou mais figuras.

    Parâmetros:

    --> figs_list: Lista com os nomes das figuras;

    --> leg: Legenda (única) de todas as figuras";

    --> Argumentos adicionais. Cada argumento é uma Tupla de dois elementos correspondente a um termo , sendo o primeiro item da Tupla para o
    singular, e o segundo,  para o plural.

    --> Retorno: lista na qual o primeiro elemento é a string que referencia as figuras, o segundo, a string que insere as figuras, e os subsequentes, os termos correspondentes a *args,
    adaptados ao singular ou ao plural.

    .

    Ex1: S = add_figs(['a.jpg', 'b.jpg'], ''Legenda padrão.'', ('A figura', 'As figuras'), ('representa um exemplo', 'representam dois exemplos), ('caso', 'casos'))

    Retorno: ["\\ref{a.jpg} e \\ref{b.jpg}", "\\f{a.jpg}{Legenda padrão.}\\n\\f{b.jpg}{Legenda padrão.}", "As figuras", "representam dois exemplos", "casos"]

    Como usar: f"{S[2]} {S[0]} {S[3]} de {S(4}} em que tal fato ocorre:\\n{S[1]}

    Resultado:

    As figuras \\ref{a.jpg} e \\ref{b.jpg} representam dois exemplos de casos em que tal fato ocorre:

    \\f{a.jpg}{Legenda padrão.}

    \\f{b.jpg}{Legenda padrão.}

    .

     Ex2: S = add_figs(['a.jpg'], ''Legenda padrão.'', ('A figura', 'As figuras'), ('representa um exemplo', 'representam dois exemplos), ('caso', 'casos'))

    Retorno: ["\\ref{a.jpg}", "\\f{a.jpg}{Legenda padrão.}", "A figura", "representa um exemplo", "caso"]

    Como usar: f"{S[2]} {S[0]} {S[3]} de {S(4)} em que tal fato ocorre:\\n{S[1]}

    Resultado:

    A figura \\ref{a.jpg} representa um exemplo de caso em que tal fato ocorre:

    \\f{a.jpg}{Legenda padrão.}
        """

    fig_insert = ""
    ref_str = ""

    try:
        assert len(figs_list) != 0, f"Erro: A lista de figuras precisa ser não nula. O programa será interrompido."

        argres = []

        # Inserir figuras
        for fig in figs_list:
            fig_insert = fig_insert + r"\f{" + fig + "}{" + leg + "}\n"

        if len(figs_list) == 1:
            ref_str = r" \ref{" + figs_list[0] + "}"
            for arg in args:
                argres.append(arg[0])
        elif len(figs_list) == 2:
            ref_str = r" \ref{" + figs_list[0] + r"} e \ref{" + figs_list[1] + "}"
            for arg in args:
                argres.append(arg[1])
        elif len(figs_list) > 2:
            ref_str = r" \ref{" + figs_list[0] + r"} a \ref{" + figs_list[-1] + "}"
            for arg in args:
                argres.append(arg[1])

    except AssertionError as msg:
        print(msg)
        print(f"Legenda para referência: {leg}")
        argres = []
        exit()

    return [ref_str, fig_insert, *argres]


horaCiente = dataCiente = aux = horaInicio = horaFim = caso = PM = matPm = vt = 'XXXXX'
fig_path = "../MODELO HOMICÍDIO"

natureza = "HOMICÍDIO CONSUMADO"
titulo = "EXAME EM LOCAL COM" + natureza
rep = "11111/2021"
matPerito = "386.990-3"
perito = "Betson Fernando Delgado dos Santos Andrade"
gestor = "Diego Leonel"
matGestor = "XXXX"
rua = "Rua Nova Descoberta"
bairro = "Macaxeira"
cidade = "Recife"
fotos_destpath = r"C:\Users\Betson\Desktop\Backup - Betson\HD ext - Laudos\Enviado\0185.9.2021\Fotografias"
coord = "XXXXX"
tipo_local = "Externo"

fig_list = [f for f in os.listdir(fotos_destpath) if ('.JPG' in f) and ('DSC' not in f)]

doc = Document('base', documentclass='article', document_options=['a4paper', '12pt', 'oneside'], lmodern=False)

with open("Predoc.tex", "r") as pred:
    doc.packages.append(pred)

with doc.create(Center()):
    doc.append(NoEscape(r"\noindent \textbf{\emph{" + titulo + r"\\CASO Nº " + caso + r"\, - REP Nº " + rep + "}}"))


# HISTÓRICO  ================== HISTÓRICO  =================== HISTÓRICO =====================

doc.append(NoEscape(f"""
\\section{{HISTÓRICO DO CASO}}

À(s) {horaCiente} do dia {dataCiente}, o \\textbf{{GRUPO ESPECIALIZADO EM PERÍCIAS DE HOMICÍDIOS (GEPH-DHPP-IC), DO INSTITUTO DE CRIMINALISTICA PROFESSOR ARMANDO 
SAMICO}}, recebeu, por telefone, a requisição nº \\textbf{{{rep}}}, do Centro Integrado de Operações de Defesa Social do Estado de Pernambuco \\textbf{{(CIODS-PE)}}, no sentido de ser 
procedido ao competente Exame Pericial no endereço {rua}, {bairro}, {cidade} - PE.

O plantão deste instituto atendeu à solicitação, designando, portanto, uma equipe formada pelo Perito Criminal \\textbf{{{perito}}} e pelo Auxiliar de Perito \\textbf{{{aux}}}, em cuja 
localização chegou à(s) {horaInicio}, iniciando os trabalhos periciais, os quais foram concluídos à(s) {horaFim}.

"""))

# ============== OBJETIVO ============== OBJETIVO =================== OBJETIVO ================

if "homicídio" in natureza.lower() and "tentativa" not in natureza.lower():
    obj_str = """O presente Exame Técnico-Pericial objetiva pesquisar, reconhecer, registrar e coletar os elementos materiais produzidos na perpetração do fato, analisando-os e, deste 
    modo, consubstanciar elementos de convicção para caracterizar se naquele local ocorrera um crime, indicar os meios e os modos utilizados na produção do evento, estabelecer a 
    sua diagnose diferencial, dirimindo se o fato é característico de ação homicida, suicida ou acidental, e, ainda, se possível, constatar elementos materiais que levem à identificação 
    do(s) autor(es)."""
else:
    obj_str = """Deu Errado!!!!!."""

doc.append(NoEscape(f"\\section{{DO OBJETIVO PERICIAL}}\\n\\n{obj_str}"))


# ========= LOCAL =========== LOCAL =========== LOCAL =========== LOCAL ========================

tempo = entrar("""
Como se encontrava o tempo no momento?\n
1 - Sem precipitação\n
2 - Sem precipitação, mas com indícios de precipitação recente\n
3 - Leve precipitação (\"chuvisco\")\n
4 - Precipitação moderada\n
5 - Precipitação intensa\n\n
Digite o valor correspondente: """, ["1", "2", "3", "4", "5"])

tempo_str = {
    "1": "não havia precipitação pluvial no local",
    "2": "havia indícios recentes de precipitação pluvial, pelo fato de o solo se encontrar demasiadamente úmido",
    "3": "havia leve precipitação pluvial no local",
    "4": "havia moderada precipitação pluvial no local",
    "5": "havia intensa precipitação pluvial no local"}

luz = entrar("""
Como se encontrava a iluminação no local?\n
1 - Iluminação natural adequada\n
2 - Iluminação natural inadequada\n
3 - Iluminação artificial adequada\n
4 - Iluminação artificial inadequada\n
5 - Iluminação inexistente\n\n
Digite o valor correspondente: """, ["1", "2", "3", "4", "5"])

luz_str = {
    "1": "ela era provida por luz natural",
    "2": "ela era provida por luz natural, porém insuficicente, tornando a visibilidade limitada",
    "3": "ela era provida por luz artificial",
    "4": "ela era provida por luz artificial, porém insuficiente, tornando a visibilidade limitada",
    "5": "ela era inexistente, tornando a visibilidade limitada"}


mapa_add = add_figs([f for f in fig_list if 'mapa' in f], "Captura de tela de mapa, no qual o marcador vermelho indica o local da ocorrência. Fonte {\\sl Google Maps}.",
                    ("da figura", "das figuras"), ("mostra", "mostram"), ("obtida", "obtidas"))

cheg_add = add_figs([f for f in fig_list if 'cheg' in f], "Fotografias exibindo as adjacências do local onde se deu o fato.", ("na figura", "nas figuras"), ("mostra", "mostram"))

mapa_str = f"""
Esta localização se encontra representada através {mapa_add[2]} {mapa_add[0]}, que {mapa_add[3]} fotografias do local da ocorrência {mapa_add[4]} por satélite a partir da base de dados 
do {{\\sl Google Earth}}.
 
{mapa_add[1]}
"""

cheg_str = f"""

O ambiente imediato se deu na pista de rolamento da via em tela, tendo um dos corpos repousado sobre a calçada da via, na base do referido aclive, e o segundo, na pista de rolamento, 
próximo ao meio fio, conforme está exibido {cheg_add[2]} {cheg_add[0]}, que {cheg_add[3]} as condições do ambiente mediato e imediato no momento dos exames periciais:

%O ambiente imediato se deu no interior de uma residência, cujo trajeto desde o exterior até o acesso a esta é exibido {cheg_add[2]} {cheg_add[0]}:

{cheg_add[1]}

"""


doc.append(NoEscape(f"""

Quando da chegada da Equipe Técnica ao local, foi observado que {tempo_str[tempo]}. No que concerne à iluminação do local, {luz_str[luz]}.

Foi constatado também que a ocorrência se deu
    %em via de nome inexistente, mais especificamente nas coordenadas geográficas \\coord.
    no endereço {rua}, {bairro}, {cidade} - PE, mais especificamente nas coordenadas geográficas {coord}.
%

Tratava-se de uma área ocupada por casas de padrão aquisitivo baixo, urbanizada, de relevo diversificado, com as vias constituídas em paralelepípedo ou asfalto, e destinadas ao tráfego 
local.

Especificamente, no que concerne ao local mediato, a via pela qual se deu acesso à ocorrência permitia tráfego nos dois sentidos, possuía calçadas transitáveis por pedestres e, em 
suas margens, havia, de um lado, um acentuado aclive ("barreira"), e, de outro, um muro que guarnecia a área destinada a operações ferroviárias.

{cheg_str}


"""))

doc.append(NoEscape(r"""
\section{MATERIAIS}

Foram utilizados os seguintes materiais no presente exame pericial:

\begin{itemize}
    \item Setas para identificação de lesões, cedidas pelo próprio GEPH/DHPP;
    \item Câmera fotográfica digital NIKON D3500, fornecida pelo GEPH/DHPP;
    \item Luvas cirúrgicas de látex de borracha natural, fornecida pelo GEPH/DHPP;
    \item Marcadores de vestígios, numerados de 1 a 10 em superfície de cor amarela, cedidos pelo GEPH/DHPP;
    \item Outros equipamentos disponibilizados pelo GEPH/DHPP.
\end{itemize}
"""))

# ===== ISOLAMENTO ========= ISOLAMENTO ====== ISOLAMENTO ============== ISOLAMENTO ==========

# isol_opt[0]
isol_opt = [input("""\n\n
Sobre o isolamento do local:\n
1 - O isolamento abrangia todo o local imediato;\n
2 - O isolamento abrangia o local imediato, mas evidências ficaram fora dele;\n
3 - Não havia isolamento no local do fato.\n
Digite o valor correspondente: """)]
while not (isol_opt[0] in ['1', '2', '3']):
    isol_opt[0] = input("Digite o valor corretamente: ")

# isol_opt[1]
if isol_opt[0] != '1':
    isol_opt.append(input("\n\n"
                          "A falta de isolamento prejucou o local?\n"
                          "1 - Sim;\n"
                          "2 - Não.\n"
                          "Digite: "))
    while not (isol_opt[1] in ['1', '2']):
        isol_opt[1] = input("Digite o valor corretamente: ")
else:
    isol_opt.append('2')

isol_str = """
\\section{DO ISOLAMENTO E PRESERVAÇÃO DO LOCAL \\label{isolamento}}

No momento da chegada da Equipe Técnica, se faziam presentes alguns policiais militares, """

if PM != "":
    PM = f"sob o comando do(a) {PM}, "
    if matPm != "":
        matPm = f"matrícula {matPm}, "
    if vt != "":
        vt = f"viatura {vt}, "

isol_str = isol_str + PM + matPm + vt

if isol_opt[0] == 1:
    isol_str = isol_str + "e o isolamento abrangia todo o local imediato."
elif isol_opt[0] == 2:
    isol_str = isol_str + "e o isolamento, apesar de abranger todo o local imediato, não continha algumas evidências encontradas, como será exposto neste laudo."
else:
    isol_str = isol_str + "não havendo isolamento no local do fato por meio de fita ou outro instrumento que bloqueasse o acesso de transeuntes ao local."

if isol_opt[1] == 1:
    isol_str = isol_str + "Contudo, isto se mostrou irrelevante devido às características do ambiente mediato e à constante vigilância por parte dos responsáveis por guarnecer a área."

isol_str = isol_str + r"""É importante ressaltar que havia várias pessoas além das pertencentes às Operativas Policiais no momento dos Trabalhos Periciais. Portanto,
%É importante ressaltar que havia poucas pessoas além das pertencentes às Operativas Policiais no momento dos Trabalhos Periciais. Todavia,
%É importante ressaltar que não havia pessoas além das pertencentes às Operativas Policiais no momento dos Trabalhos Periciais. Todavia,
%
antes da presença da Polícia no local, transeuntes e/ou espectadores podem ter alterado, ocultado, ou removido, voluntariamente ou não, evidências de valor elucidativo no que concerne à autoria e/ou dinâmica das ações dos envolvidos na ocorrência em tela.
%Em decorrência disto, foram verificados sinais de alteração no local de crime, a saber, a cobertura da vítima por um lençol (figura \ref{lencol.jpg}), que pode levar, em alguns casos, a imprecisões na caracterização das manchas de sangue e lesões.

%\f{lencol.jpg}{Fotografia, obtida quando da chegada da Equipe Técnica, da vítima coberta por um lençol.}

%Também foram encontradas evidências de que seus bolsos foram alvo de busca, uma vez que se encontravam demasiadamente abertos, como mostra a figura \ref{bolso.jpg}.

%\f{bolso.jpg}{Fotografia do bolso da vítima.}

%Não se pode afirmar quem realizou a busca no bolso da vítima, porém podem ter sido subtraídos objetos como, por exemplo, aparelhos de telecomunicação celular, que poderiam fornecer a autoria do homicídio em tela."""

doc.append(NoEscape(isol_str))

pdf_path = 'test2'
doc.generate_tex(pdf_path)
doc.generate_pdf(filepath=pdf_path, compiler='pdflatex', clean_tex=False)
os.system(pdf_path + ".pdf")
