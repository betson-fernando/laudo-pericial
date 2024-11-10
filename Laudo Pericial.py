import tkinter as tk
from tkinter import filedialog
import pandas as pd
from datetime import datetime, timedelta, time, date
import monthdelta
import sys
import shutil
from pathlib import Path
import re
import subprocess
import numpy as np
from dotenv import find_dotenv, load_dotenv
from os import environ

import urllib.request as urlreq
import urllib.error as urlerr
from zipfile import BadZipFile


SCRIPT_PATH = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_PATH))


from Classes import Figuras, Servidor, Vitima, Local, Observacoes, Bcolors, Conclusoes
from GlobalFuncs import textbf, ref, fig, getEnviron
from Modules.MapImport.GetMap import getMap


# Definição de funções: #######################################

def open_sheet(path: str, sheetname: str or int, hd_index: int, col_names: {str: str}, mappings={}) -> pd.DataFrame:

    # TODO: tentar usar xlrd --> workbook pra evitar o uso do dataframe
    
    
    """Esta função abre uma tabela presente fisicamente no computador.
     Entradas:
         path: endereço até a tabela;
         sheetname: nome da planilha. <str> ou <int>, sendo este último >=0;
         hd_index: índice da linha de cabeçalho da planilha. <int> >= 0;
         col_names: nomes das colunas a serem importadas. dict(<str>);
         mappings {str, obj}, default {}: dicionário relacionando colunas a funções a serem aplicadas a estas colunas.
     Saídas:
         sheet: arquivo .xlsx."""

    inv_col_names = {v: k for k, v in col_names.items()} # Criando um dicionário invertendo chaves e valores, para, no retorno da função, renomear os nomes das colunas para o padrão do programa.
    try:
        with open(path, "rb") as f_inner:
            sheet = pd.read_excel(f_inner, sheet_name=sheetname, header=hd_index, usecols=col_names.values(), engine='openpyxl').rename(columns=inv_col_names)

            for col, func in mappings.items():
                sheet[col] = sheet[col].apply(func)

    
    except KeyError as e1:
        if 'Worksheet' in str(e1):
            print(f"\nUma aba cujo nome foi informado na planilha de parâmetros não foi encontrada no arquivo \"{Path(path).name}\".\nDescrição do erro: '{str(e1)}'")
        else:
            print(f"\nErro desconhecido. Investigar e isolar!\nDescrição do erro: '{str(e1)}'")
        sheet = None
        exit()
    except FileNotFoundError:
        print(f"\nArquivo \"{Path(path).name}\" não encontrado. Acesse o arquivo \"Parametros.xlsx\" e corrija o "
              f"caminho.\nO programa será interrompido.")
        sheet = None
        shutil.rmtree(casodir_path)
        exit()
    except ValueError as e3:
        print(f"\nProvavelmente alguma coluna cujo nome foi informado na planilha de parâmetros não foi encontrada na "
              f"planilha {Path(path).name}>{sheetname}.\nDescrição do erro: '{str(e3)}'")
        sheet = None
        shutil.rmtree(casodir_path)
        exit()
    
    return sheet


def download_sheet(url: str, dest: str, stopiferror: bool = False):
    """Esta função tem o objeto de baixar uma planilha de uma URL.
    --> url : endereço onde se encontra a planilha;
    --> dest : endereço (contendo nome do arquivo) em que a planilha será salva. Cria arquivo se não existir.
    --> stopiferror: se houver qualquer erro no salvamento por fatores adversos, o programa será interrompido."""

    try:  # Tentar baixar a planilha em um arquivo temporário
        temp_path = Path(dest).parent.joinpath("temp.xlsx")
        urlreq.urlretrieve(url, temp_path)
    except urlerr.URLError:  # Erro de indisponibilidade de internet
        # TODO: Diferenciar o erro de sem internet com erro de url errada, que levanta o mesmo urlerr.URLError.
        # TODO: Testar se o erro de url errada gera este erro.
        print("ERRO: sem conexão com a internet, ou url incorreta. Neste caso, corrigir na planilha de parâmetros.")
        if stopiferror:
            print("Programa será abortado.")
            shutil.rmtree(casodir_path)
            exit()
    except [FileNotFoundError, PermissionError]:  # Erro de caminho errado
        print("ERRO: caminho físico informado para salvar a planilha inválido. Alterar na planilha de parâmetros.")
        if stopiferror:
            print("Programa será abortado.")
            shutil.rmtree(casodir_path)
            exit()
    else:  # Caso não houver os erros acima
        # TODO: Esta gambiarra abaixo foi efetuada apenas porque openpyxl, chamado por pandas, não fecha o arquivo automaticamente.
        #  Observar se futuras atualizações de pandas ou openpyxl resolvem isto. Caso sim, adaptar estas e as outras duas implementações similares no código.
        with open(temp_path, "rb") as f_inner:
            try:
                pd.read_excel(f_inner, sheet_name=0, engine='openpyxl')
            except BadZipFile:
                print(f"URL existente, mas não possui acesso público.\nNão será possível gravar o arquivo em {dest}.\nO programa será fechado.")
                shutil.rmtree(casodir_path)
                exit()
        try:
            Path(temp_path).replace(dest)  # Grava arquivo "temp_path" em "dest", e deleta o primeiro.
        except PermissionError:
            sys.exit(f"\nProvavelmente o arquivo {dest} está aberto. Feche-o e reexecute o programa.")

def entrar_caso() -> [str, str, str]:
    """Esta função solicita entrar o número do caso no formato correto, compara com o padrão, e, se estiver errado,
    solicita entrar novamente. Se estiver certo, retorna [número do caso, tipo do caso, ano do caso], tudo em str."""

    num = tipo = ano = ""
    match = None

    re1 = re.compile(r"""
    ([0-9]\.[0-9]{3}|[0-9]{1,4})  # Número do caso (pode ser no formato n, nn, nnn, nnnn, ou n.nnnn)
    \.                            # Separação entre número e tipo do caso (obrigatório .)
    ([01]?[0-9])                  # Tipo do caso (um dígito, ou dois dígitos sendo o primeiro o numeral 1)
    [/.]                          # Separação entre tipo de caso e ano (pode ser / ou .)
    ((2[0-9])*[2-9][0-9])$        # ano (quatro dígitos, maior que 2020 e menor que 2999, ou dois dígitos, maior que 20) 
    """, re.VERBOSE)

    while match is None:

        match = re1.match(input("Digite o número do caso:"))

        if match is None:
            print('Número do caso digitado fora do formato ou ano menor que 2020. Digite o valor corretamente.\n')
        else:
            num = match.group(1).lstrip('0')   # Remover zeros à esquerda, se houver
            tipo = match.group(2)
            ano = match.group(3)
            if '.' in num:  # Remove separador de milhares, se existir
                num = num[0] + num[2:]
            # num = (4 - num.__len__()) * '0' + num  # Adicione zeros na frente até o número ficar com 4 caracteres
            if ano.__len__() == 2:
                ano = '20' + ano
           
    return [num, tipo, ano]

# TODO: EXCLUIR ESTA FUNÇÃO APÓS ATUALIZAÇÃO
if(False):
    def calc_idade(nasc: datetime.date, plant: datetime.date) -> pd.Series(str):
        """
        Esta função calcula a idade, baseado na time de nascimento e na time da perícia.
        Entradas: <datetime.datetime d1> e <datetime.datetime d2>: as duas datas, não importando a ordem.
        Retorno: <str idade>"""

        
        series_iter = range(nasc.__len__())  # Iterador para ser usado nesta função
        idade_res = pd.Series(index=series_iter, dtype=str)

        for cont in series_iter:

            try:
                assert nasc.iloc[cont] == nasc.iloc[cont] and nasc.iloc[cont] != ""
            except AssertionError:
                print(f"A idade da vítima {cont + 1} não pode ser calculada devido à ausência de sua data de nascimento.")
                idade_res.iat[cont] = ""
            else:
                if nasc.iloc[cont].__class__ is str:  # Caso for string, formate para datetime.date
                    temp = nasc.iloc[cont]
                    nasc.iat[cont] = datetime.strptime(temp, "%d/%m/%Y")
                delta_date = monthdelta.monthmod(nasc.iloc[cont], plant.iloc[0])
                delta_mes = delta_date[0].months

                if delta_mes >= 12:
                    idade_temp = int(delta_mes / 12)
                    if idade_temp >= 2:
                        idade_res.iat[cont] = f"{idade_temp} anos"
                    else:
                        idade_res[cont] = "1 ano"

                elif 2 <= delta_mes <= 11:
                    idade_res.iat[cont] = f"{delta_mes} meses"

                elif delta_mes == 1:
                    idade_res.iat[cont] = "1 mês"
                else:
                    idade_temp = delta_date[1].days
                    if idade_temp >= 2:
                        idade_res.iat[cont] = f"{idade_temp} dias"
                    elif idade_temp == 1:
                        idade_res.iat[cont] = "1 dia"
                    else:
                        idade_res.iat[cont] = "menos de um dia de vida"
        return idade_res


def createdirs(casoDirName: str, origPath: str, destPath: str, delete_origPath: bool = False) -> str:
    """Esta função cria a estrutura de diretórios para salvar os arquivos do caso, copia imagens, e renomeia alguns
    arquivos.
    Argumentos:
    --> casoDirName (str): nome da pasta em que os arquivos do caso serão gravados. Esta pasta será gravada dentro de destPath;
    --> origPath (str): caminho para o diretório onde se encontra o caso;
    --> destPath (str): caminho para o diretório no qual será gravado a pasta do caso.
    --> delOrigPath (bool): Se 'True', deleta a pasta de origem ao finalizar. Padrão: 'False'
    A função retorna o caminho para a pasta criada (str)."""

    casoDirName = casoDirName.replace('/', '.')
    # Caminho para a pasta do caso em seu endereço final.

    caso_destpath = Path(destPath).joinpath(casoDirName)
    fotosOrigPath = Path(origPath).joinpath(casoDirName)


    shutil.copytree(Path(SCRIPT_PATH).joinpath("MODELO HOMICÍDIO"), caso_destpath)
    tex_destpath = Path(caso_destpath).joinpath("Arquivos .TEX")
    fotos_destpath = Path(caso_destpath).joinpath("Fotografias/Descartadas")
    Path(tex_destpath).joinpath("modelo.tex").rename(Path(tex_destpath).joinpath(f"{casoDirName}.tex"))
    shutil.copytree(fotosOrigPath, fotos_destpath)
    # TODO: garantir que todas as imagens foram copiadas (sugestão: shutil.disk_usage para comparar os tamanhos,
    #  shutil.scandir, ou filecmp.dircmp). Feito o anterior, excluir a pasta de origem.

    dir_comp = False  # Variável para futura comparação entre as pastas de origem e de destino.
    if delete_origPath and dir_comp:
        shutil.rmtree(fotosOrigPath)

    return caso_destpath

# Quando as classes forem implementadas, apagar função abaixo
def return_tgt_row(sheet: pd.DataFrame, index_str: str, message: str, exit_if_not_found: bool = False):


    """Esta função tem o objetivo de retornar a linha completa de um caso presente em uma planilha no formato DataFrame,
    além de substituir valores vazios ("NaN") por strings vazias.
    Caso a linha não for encontrada, retorna um DataFrame de linha única no qual todos os valores são strings vazias,
    além de levantar um erro referenciando a planilha "sheet_name".
    Entradas:
        --> sheet: planilha, no formato DataFrame.
        --> index_str: string indexadora, que pode ser o número do caso, ou id da ocorrência.
        --> sheet_name: Em caso de erro, a mensagem irá referenciar "sheet_name" para saber em qual
            planilha o caso não foi encontrado.
        --> stop_if_not_found : True se "sheet" for a planilha preenchida na base, False, se for a
            preenchida no local.

    Saídas:
        Todas as linhas do caso especificado."""
    try:
        line = sheet.loc[index_str]
    except KeyError:
        print(message)
        if exit_if_not_found:
            print("Como esta planilha é estritamente necessária, o aplicativo  será interrompido.")
            shutil.rmtree(casodir_path)
            return exit()
        else:
            # empty_line = pd.DataFrame(data=[[""]*len(sheet.columns)], columns=sheet.columns)
            return pd.DataFrame()
    else:
        if type(line) == pd.Series:
            #temp = pd.DataFrame(line).swapaxes(0, 1).fillna("")

            return pd.DataFrame(line).swapaxes(0, 1).fillna("").reset_index()
        else:
            return line.fillna("")


def fmt_values(value, name="", forceInput=False) -> str:
    """Esta função recebe um valor, e decide se é do tipo 'datetime.datetime', 'datetime.time', ou outro qualquer.
     Então, no caso de ser o primeiro tipo, converte em uma string do tipo 'dd/mm/aaaa'; no caso de ser o segundo, em
     'HH:mm' (adicionando um '0' se necessário); no caso de ser o terceiro, simplesmente retorna o valor de entrada.
     Caso for string vazia, e forceInput for True, será solicitado ao usuário um valor para o parâmetro value;
     Caso for string vazia, e forceInput for False, o programa continuará a executar silenciosamente.

     Entradas:
        --> value: valor a ser tratado;
        --> name: nome que identifica o valor para exibir mensagem, caso forceInput for True e o valor for vazio;
        --> forceInput (False): decide se solicita entrada por parte do usuário caso 'valor' for vazio."""

    if isinstance(value, (str, int, np.int64)):
        if value != "":
            data_str = value
        else:
            data_str = input(f"O campo \"{name}\" não foi preenchido. Digite o valor: ") if forceInput else textbf('PREENCHER PREENCHER PREENCHER')
    elif isinstance(value, float):
        data_str = int(value)
    elif isinstance(value, (datetime, np.datetime64)):
        if isinstance(value, np.datetime64):  # Se for datetime64, converta para datetime.
            value = pd.to_datetime(value)
            # TODO: Comentei a linha abaixo porque o método 'utcfromtimestamp' não funciona para anos abaixo de 1970 ou acima de 2053. Testar se funciona por várias vezes
            # value = datetime.utcfromtimestamp(np.datetime64(value, 's').astype(int))
        dia = f"{value.day}"
        mes = f"{value.month}"
        if len(mes) == 1:
            mes = "0" + mes
        if len(dia) == 1:
            dia = "0" + dia
        data_str = f"{dia}/{mes}/{value.year}"
    elif isinstance(value, time):
        hora = f"{value.hour}"
        minuto = f"{value.minute}"
        if len(hora) == 1:
            hora = "0" + hora
        if len(minuto) == 1:
            minuto = "0" + minuto
        data_str = f"{hora}h{minuto}min"

    else:
        print(f"Erro de programação. Um tipo de variável escabou na função fmt_values:"
              f"\nvalor: {value}; tipo: {str(type(value))}")
        data_str = value

    return data_str


def macro(name: str, value) -> str:
    r"""Esta função gera uma linha de macro segundo o padrão do Latex: "\newrobustcmd{\[macro_name]}{[macro_value]}".
    Ainda, se o argumento (macro_value) for vazio, insere o símbolo "%" para manter a linha inativa no Latex."""

    if value.__len__() == 1:
        res = f"\\newcommand{{\\{name}}}{{{fmt_values(value.iloc[0])}}}\n"
        if value.iloc[0] == "":
            res = "%" + res
    else:
        res = ""
        for item in value.values:
            res += f"\t\t\\or\n\t\t{fmt_values(item)}\n"
        res = f"\\newcommand{{\\{name}[1]}}{{\n\t\\ifcase#1\n{res}\t\t\\else\n\t\tPREENCHER\n\t\\fi}}\n"

    return res

def str_replace(dictio:{str:str}, orig_string: str) -> str:
    """Esta função tem o objetivo de encontrar tags em uma string original e substituí-las por outras strings.

    dictio: dicionário {str:str} cujas chaves são as tags, e valores são as strings que substituirão as tags;
    orig_string: string que contém as tags."""
    
    for tag, rep_str in dictio.items():
        orig_string = orig_string.replace(tag, rep_str)

    return orig_string
    
##############################################################

load_dotenv(Path(__file__).parent.joinpath('configs.env'))


# Parâmetros para ajustar:
open_vit = True  # Se há vítimas
open_veic = False  # Se há veículos
open_bal = False  # Se há elementos balísticos

[caso_num, caso_tipo, caso_ano] = entrar_caso()

casoTgt = caso_num + "." + caso_tipo + "/" + caso_ano


with open(Path(SCRIPT_PATH).joinpath("Parametros.xlsx"), "rb") as f:

    # file_io_obj = io.BytesIO(f.read())
    par = pd.read_excel(f, sheet_name=[0, 1], engine='openpyxl')
ender = par[0]
allcols = par[1]

header_index_base = int(ender.iloc[0, 1])  # Linha do cabeçalho da tabela preenchida na base (início em 0)
header_index_vit_base = int(ender.iloc[1, 1])  # Linha do cabeçalho da tabela de vítima preenchida na base (início em 0)
header_index_form = int(ender.iloc[2, 1])  # Linha do cabeçalho das tabelas dos formulários (início em 0)

casoOrigPath = ender.iloc[3, 1]  # Pasta de origem do arquivo das imagens
casoDestPath = ender.iloc[4, 1]  # Pasta de destino dos arquivos trabalhados pelo programa

tab_base_path = ender.iloc[5, 1]  # Caminho físico para a tabela preenchida na base
aba_base = ender.iloc[6, 1]  # Nome da aba para a tabela preenchida na base
aba_vit_base = ender.iloc[7, 1]  # Nome da aba da tabela de vítimas preenchida na base

tab_base_url = getEnviron('MAIN_SHEET_URL')  # URL para tabela preenchida na base
tab_form_url = getEnviron('FORMS_URL')  # URL para tabela dos formulários

tab_form_path = ender.iloc[9, 1]  # Caminho físico para a tabela dos formulários

aba_info = ender.iloc[11, 1]  # Nome da aba das informações gerais na tabela dos formulários
aba_vit_loc = ender.iloc[12, 1]  # Nome da aba das informações da vítima na tabela dos formulários
aba_veic = ender.iloc[13, 1]  # Nome da aba das informações do veículo na tabela dos formulários
aba_bal = ender.iloc[14, 1]  # Nome da aba das informações de balística na tabela dos formulários


if not Path(casoOrigPath).is_dir():
    print(f"{Bcolors.FAIL}O campo \"{ender.iloc[3, 0]}\" do arquivo \"Parâmetros.xlsx\" não é um diretório.\nCorrija e re-execute o aplicativo.{Bcolors.ENDC}")
    exit()
if not Path(casoDestPath).is_dir():
    print(f"{Bcolors.FAIL}O campo \"{ender.iloc[4, 0]}\" do arquivo \"Parâmetros.xlsx\" não é um diretório.\nCorrija e re-execute o aplicativo.{Bcolors.ENDC}")
    exit()

casoDirName = (4 - casoTgt.index('.'))*'0' + casoTgt.replace('/', '.')   # Completar com zeros na frente e trocar '/' por '.' . Ex.: 8.9/2024 -> 0008.9.2024

if not Path(casoOrigPath).joinpath(casoDirName).is_dir():
    print(f"{Bcolors.FAIL}A pasta relativa ao caso {casoTgt} não existe. O programa será encerrado.{Bcolors.ENDC}")
    exit()
    
casodir_path = createdirs(casoDirName, casoOrigPath, casoDestPath)

#       O trecho abaixo recebe a planilha dos nomes dos títulos das colunas, e a separa em pares de colunas, todos eles
# dicionários, a saber, os nomes das colunas da planilha preenchida na base, de informações gerais, da vítima, do
# veículo, e de balística. Cada par de colunas tem a seguinte estrutura:
# COLUNA A: nomes das variáveis, que não devem ser modificadas, uma vez que são utilizadas no programa;
# COLUNA B: títulos das colunas presentes nas tabelas preenchidas pelo perito ou auxiliar (tabela da base, informações gerais, vítima, veículo,...)
col_base = dict(zip(allcols.iloc[1:, 0], allcols.iloc[1:, 1]))
col_vit_base = dict(zip(allcols.iloc[1:, 2], allcols.iloc[1:, 3]))
col_info = dict(zip(allcols.iloc[1:, 4], allcols.iloc[1:, 5]))
col_vit_loc = dict(zip(allcols.iloc[1:, 6], allcols.iloc[1:, 7]))
col_veic = dict(zip(allcols.iloc[1:, 8], allcols.iloc[1:, 9]))
col_bal = dict(zip(allcols.iloc[1:, 10], allcols.iloc[1:, 11]))

# A "gambiarra" abaixo serve para remover valores "NaN" de cada um dos dicionários que informam os valores das colunas.
col_base = {k: col_base[k] for k in col_base if k == k and col_base[k] == col_base[k]}
col_vit_base = {k: col_vit_base[k] for k in col_vit_base if k == k and col_vit_base[k] == col_vit_base[k]}
col_info = {k: col_info[k] for k in col_info if k == k and col_info[k] == col_info[k]}
col_vit_loc = {k: col_vit_loc[k] for k in col_vit_loc if k == k and col_vit_loc[k] == col_vit_loc[k]}
col_veic = {k: col_veic[k] for k in col_veic if k == k and col_veic[k] == col_veic[k]}
col_bal = {k: col_bal[k] for k in col_bal if k == k and col_bal[k] == col_bal[k]}


# INFORMAÇÕES GERAIS PREENCHIDAS NA BASE ------------------------------------------------------------------------------------------------------------------------
sheet_base = open_sheet(tab_base_path, str(aba_base), header_index_base, col_base)
sheet_base.set_index("caso", inplace=True)

row_base = return_tgt_row(sheet_base, casoTgt, f"O caso {casoTgt} não foi encontrado na planilha preenchida na base.", False)

# TODO: ESTA LINHA ABAIXO AINDA NÃO FOI TESTADA PARA A HIPÓTESE EM QUE O CASO NÃO É ENCONTRADO NA TABELA OFFLINE.
if row_base.empty:
    # Se o caso não for encontrado, baixe a planilha da base e atualize a parte de informações gerais e vítimas.
    download_sheet(tab_base_url, tab_base_path, True)

    sheet_base = open_sheet(tab_base_path, str(aba_base), header_index_base, col_base)
    sheet_base.set_index("caso", inplace=True)
    row_base = return_tgt_row(sheet_base, casoTgt, f"O caso {casoTgt} não foi encontrado na planilha preenchida na base.", True)

# DADOS DA PLANILHA PREENCHIDA NA BASE:

# OBS.: NO FUTURO, SE FICAR PROIBIDO FAZER "row_base[<str>].iloc[<int>]", posso usar "row_base.loc[<int>, <str>]".

locais = [Local(1, (row_base['lat'].iloc[0], row_base['lon'].iloc[0]), row_base['municipio'].iloc[0], row_base['bairro'].iloc[0], row_base['rua'].iloc[0], row_base['tipoLoc'].iloc[0])]

tipoExame = row_base['tipoexame']
caso = row_base['index']
rep = row_base['rep']
dataPlant = row_base['dataPlant']
req = row_base['req']
aux = row_base['aux']
delegado = row_base['delegado']
vtPericia = row_base['vtPericia']
horaCiente = row_base['horaCiente']
horaInicio = row_base['horaInicio']
horaFim = row_base['horaFim']


dataCiente = dataPlant
# TODO: TESTAR PARA HORÁRIOS DE MADRUGADA PARA ENTRAR NESSE IF E VER SE FUNCIONA = 1
if dataCiente[0] != "" and 0 <= horaCiente[0].hour < 6:
    dataCiente.update(pd.Series(dataCiente + timedelta(days=1)))

tipoExameRes = fmt_values(tipoExame.iloc[0])
casoRes = fmt_values(caso.iloc[0])
repRes = fmt_values(rep.iloc[0], "rep", True)
dataCienteRes = fmt_values(dataCiente.iloc[0])
reqRes = fmt_values(req.iloc[0])
auxRes = fmt_values(aux.iloc[0])
delegadoRes = fmt_values(delegado.iloc[0], "delegado", True)
horaCienteRes = fmt_values(horaCiente.iloc[0])
horaInicioRes = fmt_values(horaInicio.iloc[0])
horaFimRes = fmt_values(horaFim.iloc[0])



download_sheet(tab_form_url, tab_form_path, True)

# FORM DE INFORMAÇÕES DO LOCAL ---------------------------------------------------------------------------------
sheet_info = open_sheet(tab_form_path, aba_info, header_index_form, col_info, mappings={'batPM': str})
sheet_info.set_index("caso", inplace=True)

row_info = return_tgt_row(sheet_info, casoTgt, f"O caso {casoTgt} não foi inserido no FORMULÁRIO DE INFORMAÇÕES GERAIS.", True)


firstResponder = Servidor(nome = row_info['nomePM'].iloc[0], cargo = "Policial Militar", operativa = "Polícia Militar", mat = row_info['matPM'].iloc[0], grupo = row_info['batPM'].iloc[0])


# INSERIR AS VÍTIMAS -------------------------------------------------------------------------------------------------------------------
string_vit = ""
if open_vit:
    sheet_vit_base = open_sheet(tab_base_path, str(aba_vit_base), header_index_vit_base, col_vit_base, mappings={'nic': float})
    sheet_vit_loc = open_sheet(tab_form_path, aba_vit_loc, header_index_form, col_vit_loc, mappings={'nic': float})

    sheet_vit_base.set_index("ocorrencia_id", inplace=True)
    sheet_vit_loc.set_index("caso", inplace=True)

    row_vit_base = return_tgt_row(sheet_vit_base, row_base["caso_id"], "Vítima não encontrada na planilha preenchida na BASE. Provavelmente não foi cadastrada.", False)
    row_vit_loc = return_tgt_row(sheet_vit_loc, casoTgt, "Caso não encontrado no FORMULÁRIO DE VÍTIMAS.", False)

    if row_vit_base.empty:
        # Se não houver vítima cadastrada, baixe a planilha e atualiza a parte de vítimas.
        download_sheet(tab_base_url, tab_base_path, True)

        sheet_vit_base = open_sheet(tab_base_path, str(aba_vit_base), header_index_vit_base, col_vit_base, dtype={'nic': int})
        sheet_vit_base.set_index("ocorrencia_id", inplace=True)
        row_vit_base = return_tgt_row(sheet_vit_base, row_base["caso_id"], "Vítima não encontrada na planilha preenchida na BASE. Provavelmente não foi cadastrada.", True)

    if row_vit_loc.empty:
        download_sheet(tab_form_url, tab_form_path, True)
        sheet_vit_loc = open_sheet(tab_form_path, aba_vit_loc, header_index_form, col_vit_loc, dtype={'nic': int})
        sheet_vit_loc.set_index("caso", inplace=True)
        row_vit_loc = return_tgt_row(sheet_vit_loc, casoTgt, "Caso não encontrado no FORMULÁRIO DE VÍTIMAS.", True)

    # TRANSFORMAÇÕES ESPECÍFICAS
    row_vit_loc = row_vit_loc.applymap(lambda x: str(int(x)) if ((type(x) == str and str(x).isnumeric()) or type(x) == float) else x)
    row_vit_base = row_vit_base.applymap(lambda x: str(int(x)) if ((type(x) == str and str(x).isnumeric()) or type(x) == float) else x)

    try:
        
        row_vit = row_vit_base.merge(row_vit_loc, sort=True, validate="1:1")
        assert row_vit.__len__() == row_vit_base.__len__() == row_vit_loc.__len__()
    except AssertionError:
        print(f"Foi encontrada uma inconsistência entre as vítimas.\nProvavelmente o NIC informado na base e o informado no form da vítima não correspondem.\n Compare:\n"
              f"NIC(s) preenchido(s) na base:  {[item for item in row_vit_base['nic']]}\n"
              f"NIC(s) preenchido(s) no form de vítimas:  {[item for item in row_vit_loc['nic']]}\n."
              f"O programa será encerrado. Corrija e re-execute.")
        row_vit = pd.DataFrame([])
        exit()
    except pd.errors.MergeError as e1:  # Quando as colunas do nic não têm o mesmo nome entre as planilhas.
        
        if 'one-to-one' in str(e1):
            print("Aparentemente, existem duas entradas de NICs ou na tabela dos forms, ou na tabela preenchida na base. Corrija e re-execute.")

        else:
            print(f"Aparentemente, o nome da coluna 'nic' não coincide na tabela da vítima preenchida na base e a tabela do formulário da vítima. Observe:\n"
                  f"Colunas da tabela de vítimas preenchida na base:\n"
                  f"{row_vit_base.columns}\n"
                  f"Colunas da tabela do formulário da vítima:\n"
                  f"{row_vit_loc.columns}\n"
                  f"O programa será encerrado. Corrija a planilha de formulário da vítima e re-execute.")
        exit()


    transpRowVit = row_vit.transpose().to_dict()
    
    vitimas = []
    for item in transpRowVit.values():
        vitima = Vitima(item)
        vitima.setIdade(dataCiente.iloc[0])
        vitimas.append(vitima)


# DADOS DO FORMULÁRIO DE INFORMAÇÕES DO VEÍCULO:
string_veic = ""
if open_veic:
    sheet_veic = open_sheet(tab_form_path, aba_veic, header_index_form, col_veic)
    row_veic = return_tgt_row(sheet_veic, casoTgt, "VEÍCULOS", False)

# DADOS DO FORMULÁRIO DE BALÍSTICA:
string_bal = ""
if open_bal:
    sheet_bal = open_sheet(tab_form_path, aba_bal, header_index_form, col_bal)
    row_bal = return_tgt_row(sheet_bal, casoTgt, "BALÍSTICA", False)

result_macros = string_vit + string_veic + string_bal


# Renomear Pasta do caso para incluir número da rep:
#repStr = fmt_values(rep.iloc[0]) #REP no formato de string
newName = f"{casoTgt.replace('/','.')} - {repRes.split('/')[0]}"  # Novo nome da pasta do caso ("caso - rep")
Path(casodir_path).rename(f"{casoDestPath}/{newName}") # Renomear para o novo nome acima
casodir_path = f"{casoDestPath}/{newName}" # Atualização do caminho para a pasta do caso.

file_path = f"{casodir_path}/Arquivos .TEX/{casoDirName.replace('/', '.')}.tex"
images_path = f"{casodir_path}/Fotografias/Descartadas"
# ======================================================================================================================
# ========================================== EDIÇÃO DO LAUDO ===========================================================
# ======================================================================================================================

with open(file_path, mode="r", encoding='utf-8') as f_in:
    file_str = f_in.read()
    f_in.close()

tipoExameRes = tipoExameRes.lower()
if tipoExameRes == "homicídio":
    tipoExameRes = "EXAME EM LOCAL COM HOMICÍDIO CONSUMADO"
elif tipoExameRes == "duplo homicídio":
    tipoExameRes = "EXAME EM LOCAL COM DUPLO HOMICÍDIO CONSUMADO"
elif tipoExameRes == "triplo homicídio":
    tipoExameRes = "EXAME EM LOCAL COM TRIPLO HOMICÍDIO CONSUMADO"
elif tipoExameRes == "morte a esclarecer":
    tipoExameRes = "EXAME EM LOCAL DE MORTE A ESCLARECER"
elif tipoExameRes == "suicídio":
    tipoExameRes == "EXAME EM LOCAL DE SUICÍDIO"
if tipoExameRes == "ossada":
    tipoExameRes = "EXAME EM LOCAL COM OSSADA"

rodape = "\\footskip=7.75mm\n\n\\cfoot{\\fontsize{10}{0} \\selectfont {\\sl{Laudo Pericial nº " + casoRes + " - REP nº " + repRes + r"} \hfill {Página \thepage}}\\\rule{16cm}{2pt}  \\\baselineskip=12pt\bf Rua Doutor João Lacerda, nº 395, bairro do Cordeiro, Recife/ PE – CEP: 50.711-280 \newline Administrativo/ Plantão: (81) 3184-3547 - E-mail: geph.dhpp@gmail.com}"

titulo = r"\centering \noindent \textbf{\emph{" + tipoExameRes + r"\\CASO Nº " + casoRes + "\, - REP Nº " + repRes + "}}"
titulo = r"\centering \noindent " + textbf(r"\emph{" + tipoExameRes + r"\\CASO Nº " + casoRes + r"\, - REP Nº " + repRes + "}")

# REMOVER ESTE TRECHO DE INFORMAÇÕES QUANDO HOUVER UMA GUI, E NÃO FOR MAIS NECESSÁRIO.
info = "\\begin{comment}\n"
info += f"Caso: {casoRes}\nREP: {repRes}\nDelegado: {delegadoRes}\n"
for local in locais:
    info += f"Local {local.locId}:\n{local.info()}"
info += "\\end{comment}"


# ============================= DECLARAÇÃO DAS FIGURAS =====================================

figExt = Figuras(images_path, "ext", ["|A| |figura| <ref> |mostra| as condições do ambiente mediato no momento dos exames periciais:", "O ambiente imediato se deu no interior de um lote, já exibido externamente |na| |figura| <ref>."], "Fotografia mostrando o local da ocorrência.")

figTer = Figuras(images_path, "ter", "Ao adentrar no terreno, foi constatado que ele era guarnecido por cerca improvisada composta por tela flexível e translúcida, com base em barro batido, conforme |figura| <ref>:", "Fotografia de terreno pertencente ao lote em tela.")
        
figInt = Figuras(images_path, "int", ["A residência, por sua vez, possuía dois acessos, sendo o principal (anterior) guarnecido por grade de aço e porta de alumínio. Em seu interior, havia sala de estar, três quartos (anterior, medial e posterior), banheiro, cozinha e área de serviço, conforme |figura| <ref>:", "O local imediato (onde se encontrava o cadáver) era o XXXXX, conforme pode ser observado |na| |figura| <ref>."], "Fotografia do interior da residência.")

# TODO: Varíaveis figLencol e figBolso estão duplicadas na classe Vítimas. Como otimizar isso?
figLencol = Figuras(images_path, "lencol", ["Em decorrência disto, foram verificados sinais de alteração no local de crime, a saber, a cobertura do cadáver por um cobertor (|figura| <ref>), que pode levar, em alguns casos, a imprecisões na caracterização das manchas de sangue e lesões.", "se encontrava envolto por um cobertor (|figura| <ref>). Após exposto, tal cadáver"], "Fotografia, obtida quando da chegada da Equipe Técnica, do cadáver coberta.")

figBolso = Figuras(images_path, "bolso", ["Também foram encontradas evidências de que seus bolsos foram alvo de busca, uma vez que se encontravam demasiadamente abertos, como mostra |a| |figura| <ref>:", "Não se pode afirmar quem realizou a busca no bolso do cadáver, porém podem ter sido subtraídos objetos como, por exemplo, aparelhos de telecomunicação celular, que poderiam fornecer a autoria do homicídio em tela."], "Fotografia do bolso do cadáver.")

figCam = Figuras(images_path, "cam", "Tais câmeras foram fotografadas, e estão exibidas |na| |figura| <ref>:", "Fotografia de câmera(s) no local.")

figBal = Figuras(images_path, "bal", "|A| |figura| <ref> |exibe|, no local da ocorrência, o(s) elemento(s) balístico(s) acima relatado(s)\n%, e as numerações presentes nas imagens (plaquetas amarelas) correspondem àquelas que identificam estes elementos na lista acima\n:", "Fotografia indicando a localização de elemento(s) balístico(s).")


figVit = Figuras(images_path, "vit", ["|Esta| |fotografia| |está| |exibida| |na| |figura| <ref>:",  "|figura| <ref>"], "Fotografia do cadáver em sua posição original.")

figVitMov = Figuras(images_path, "vitmov", ["Também |foi| |realizada| |fotografia| após a remoção da vítima até local adequado à Análise Perinecroscópica, conforme |figura| <ref>:", "(|figura| <ref>)"], "Fotografia do cadáver após a sua remoção a local adequado.")

figTat = Figuras(images_path, "tat", "Na sua epiderme |foi| |constatada| |tatuagem|, |fotografada| e |exibida| |na| |figura| <ref>:", "Fotografia de tatuagem no cadáver.")

figId = Figuras(images_path, "id", " (|Figura| <ref>)", "Fotografia de documento de identificação do cadáver.")

figPert = Figuras(images_path, "pert", "|Foi| |feito| |registro| |fotográfico| destes itens, que estão exibidos |na| |figura| <ref>:", "Fotografia de objeto(s) encontrado(s) com o cadáver.")

figLes = Figuras(images_path, "les", "|A| |figura| <ref> |exibe| as lesões acima relatadas\n%,e as numerações nas imagens correspondem àquelas que identificam as lesões na lista acima\n:", "Lesões constatadas no cadáver.")

figEsq = Figuras(images_path, "esq", r"|A| |figura| <ref> |exibe|, através de |esquema|, as lesões encontradas no cadáver. Em |tal| |esquema|, as lesões representadas por um círculo são características de entrada de projétil, enquanto as representadas por um ``X'', saída de projétil, e, por fim, as indicadas por um quadrado não puderam ter suas características identificadas no momento do Exame Pericial.", f"Esquema indicando os locais e tipos das lesões encontradas no cadáver. LEME, C-E-L. P. {textbf('Medicina Legal Prática Compreensível')}. Barra do Garças: Ed. do Autor, 2010.")

figBalVit = Figuras(images_path, "balvit", ["Após estes registros iniciais, foi procedida a manipulação do cadáver, durante a qual foi(foram) encontrado(s), sob ele, elemento(s) balístico(s), conforme |figura| <ref>:", r"Este(s) elemento(s) balístico(s) foi(foram) encaminhado(s) ao \bal."], "Fotografia de elemento(s) balístico(s) encontrado(s) dentro das vestes do cadáver.")

figVest = Figuras(images_path, "vest", ["|Todo| |o| |vestígio| |foi| devidamente |fotografado| no local, |selado| em |lacre| |numerado|, e novamente |fotografado| em |seu| |lacre|, conforme |figura| <ref>, antes de |ser| |enviado| |ao| |seu| |respectivo| |destino|. Detalhes |do| |envio| poderão ser |consultado|"], "Fotografia de vestígio lacrado. Na faixa vermelha está presente o número do lacre")


hist = f"""
\\section{{HISTÓRICO DO CASO}}

À(s) {horaCienteRes} do dia {dataCienteRes}, o {textbf("GRUPO ESPECIALIZADO EM PERÍCIAS DE HOMICÍDIOS (GEPH-DHPP-IC), DO INSTITUTO DE CRIMINALISTICA PROFESSOR ARMANDO SAMICO")}, recebeu, por telefone, a requisição nº {textbf(reqRes)}, do Centro Integrado de Operações de Defesa Social do Estado de Pernambuco {textbf("(CIODS-PE)")}, no sentido de ser procedido ao competente Exame Pericial no local abaixo mencionado.

O plantão deste instituto atendeu à solicitação, designando, portanto, uma equipe formada pelo Perito Criminal {textbf("BETSON FERNANDO DELGADO DOS SANTOS ANDRADE")} e pelo Agente de Perícia {textbf(auxRes)}, em cuja localização chegou à(s) {horaInicioRes}, iniciando os trabalhos periciais, os quais foram concluídos à(s) {horaFimRes}."""

objetivo = r"""
\section{DO OBJETIVO PERICIAL}

O presente Exame Técnico-Pericial objetiva pesquisar, reconhecer, registrar e coletar os elementos materiais produzidos na perpetração do fato, analisando-os  e, deste modo, consubstanciar elementos de convicção para caracterizar se naquele local ocorrera um crime, indicar os meios e os modos utilizados na produção  do evento, estabelecer a sua diagnose diferencial, dirimindo se o fato é característico de ação homicida, suicida ou acidental, e, ainda, se possível, constatar elementos materiais que levem à identificação do(s) autor(es)."""

materiais = r"""
\section{MATERIAIS}

Foram utilizados os seguintes materiais no presente exame pericial:

\begin{itemize}
	\item Setas para identificação de lesões, cedidas pelo próprio GEPH/DHPP;
	\item Câmera fotográfica digital NIKON D3500, fornecida pelo GEPH/DHPP;
	\item Luvas cirúrgicas de látex de borracha natural, fornecida pelo GEPH/DHPP;
	\item Marcadores de vestígios, numerados de 1 a 10 em superfície de cor amarela, cedidos pelo GEPH/DHPP;
	\item Outros equipamentos disponibilizados pelo GEPH/DHPP.
    
\end{itemize}"""

descLocalGeral = r"""
\section{DO LOCAL}

\subsection{CARACTERÍSTICAS GERAIS}

Quando da chegada da Equipe Técnica ao local, foi observado que o tempo se encontrava
	%desnublado
	parcialmente nublado
	%nublado
%, havendo leve precipitação pluvial no momento dos Trabalhos Periciais.
%, sendo encontrados indicativos de recente precipitação pluvial.
%, não havendo precipitação pluvial no momento dos Exames Periciais.
%
%No que tange à iluminação, a Equipe Técnica realizou a perícia no período noturno, e o local não era provido de iluminação artificial adequada, tornando a visibilidade limitada durante os Exames Periciais.

Tratava-se de uma área ocupada por casas de padrão aquisitivo baixo, povoada, plana, com as vias cobertas por paralelepípedos, e destinadas ao tráfego local.


"""

descLocalDetalhe = ''
for local in locais:
    mapName = f'mapa{str(local.locId)}'
    mapZoomName = f'mapazoom{str(local.locId)}'
    lat = local.coord[0]
    lon = local.coord[1]
    
    with open(Path(images_path).joinpath(mapName + '.jpg'), 'wb') as mapa, open(Path(images_path).joinpath(mapZoomName + '.jpg'), 'wb') as mapaZoom:
        mapa.write(local.getMaps(zoom=environ['LOW_ZOOM']))
        mapa.close()
        
        mapaZoom.write(local.getMaps(zoom=environ['HIGH_ZOOM']))
        mapaZoom.close()

    
    descLocalDetalhe += \
        r"""\subsection{""" + (f'Local {local.locId}: ' if len(locais) > 1 else '') + """AMBIENTES MEDIATO E IMEDIATO}\n\n"""\
        \
        \
        f"""
        Especificamente, no que concerne ao local mediato, a via pela qual se deu acesso à ocorrência permitia tráfego nos dois sentidos, possuía calçadas transitáveis por pedestres, com iluminação pública adequada e, em suas margens, havia casas de padrões similares às descritas acima.
        
        O ambiente imediato se deu no endereço {textbf(f"{local.rua}, {local.bairro}, {local.municipio} - PE")}. Mais especificamente, esta localidade pode ser representada pelas coordenadas geográficas cartesianas {textbf(f'{lat},{lon}')}, indicadas nas figuras {ref(mapName)} e {ref(mapZoomName)}, que mostram fotografias do local da ocorrência obtidas por meios aeroespaciais (fonte: {{\\sl Google Earth}}).

        {fig(f'{mapName}', 'Mapa em escala reduzida no qual o marcador vermelho indica o local da ocorrência.')}
        {fig(f'{mapZoomName}', 'Mapa em escala ampliada no qual o marcador vermelho indica o local da ocorrência.')}
         

        {figExt.frase[0]}
        
        {figExt.figsTex}
        
        
        """
        

    if local.tipo.lower() in ['interno', 'misto']:
        
        if figTer.numFigs + figInt.numFigs > 0: # Caso houver terreno ou interior de residência fotografados:
            descLocalDetalhe += figExt.frase[1] + "\n\n"
        
        # Descrição do terreno
        descLocalDetalhe += figTer.frase + "\n\n" + figTer.figsTex + "\n\n"
        
        descLocalDetalhe += figInt.frase[0] + "\n\n" + figInt.figsTex + "\n\n" + figInt.frase[1] + "\n\n"

isol = f"""
\\section{{ISOLAMENTO E PRESERVAÇÃO DO LOCAL \\label{{isolamento}}}}

No momento da chegada da Equipe Técnica, se faziam presentes alguns policiais militares, sob o comando do(a) {firstResponder.getTexto()}, 
%e o isolamento abrangia todo o local imediato.
%e o isolamento, apesar de abranger todo o local imediato, não continha algumas evidências encontradas, como será exposto neste laudo.
%não havendo isolamento no local do fato por meio de fita ou outro instrumento que bloqueasse o acesso de transeuntes ao local.
	% Contudo, isto se mostrou irrelevante devido às características do ambiente mediato e à constante vigilância por parte dos responsáveis por guarnecer a área.

É importante ressaltar que havia várias pessoas além das pertencentes às Operativas Policiais no momento dos Trabalhos Periciais. Portanto, 
%É importante ressaltar que havia poucas pessoas além das pertencentes às Operativas Policiais no momento dos Trabalhos Periciais. Todavia, 
%É importante ressaltar que não havia pessoas além das pertencentes às Operativas Policiais no momento dos Trabalhos Periciais. Todavia, 
%
antes da presença da Polícia no local, transeuntes e/ou espectadores podem ter alterado, ocultado, ou removido, voluntariamente ou não, evidências de valor elucidativo no que concerne à autoria e/ou dinâmica das ações dos envolvidos na ocorrência em tela."""

isol += figLencol.frase[0] + "\n\n" + figLencol.figsTex + "\n" + figBolso.frase[0] + "\n\n" + figBolso.figsTex + "\n\n" + figBolso.frase[1] + "\n"


# ============================================== SEÇÃO DE EXAMES ======================================================
exames = r"""
\section{EXAMES}

\subsection{DO LOCAL}

"""

if figCam.numFigs > 0: 

    exames += f"""
Ao chegar ao local, a Equipe Técnica constatou a existência de várias câmeras, a saber:

\\begin{{itemize}}

	\\item {textbf("Uma (01)")} câmera no Edifício Bella Vista, localizado na R. dos Navegantes;
	\\item {textbf("Três (03)")} câmeras no Edifício Praça do Mar, localizado na R. dos Navegantes, nº 4862;
	\\item {textbf("Uma (01)")} câmera no Edifício Canárias, localizado na R. Dr. Nilo Dornelas Câmara, nº 90;
	\\item {textbf("Uma (01)")} câmera na Galeria Cidade Sul, localizada na Av. Conselheiro Aguiar, nº 5025 (mais precisamente na esquina desta avenina com a R. Dr. Nilo Dornelas Câmara).

\\end{{itemize}}

{figCam.frase}

{figCam.figsTex}        
        
"""

if figBal.numFigs > 0:
    exames += f"""
    
        A equipe técnica analisou meticulosamente o local em busca de evidências relacionadas à ocorrência, encontrando elementos balísticos na quantidade e localização abaixo relacionados:

        \\begin{{enumerate}}

            \\item Estojo encontrado próximo ao cadáver;
            \\item Projétil encontrado próximo ao cadáver;
            \\item Estojo encontrado distante do cadáver, na direção da estação de tratamento de esgoto e da ponte sobre o Rio Capibaribe.

        \\end{{enumerate}}

        {figBal.frase}

        {figBal.figsTex}

        Estes elementos balísticos foram coletados, inseridos em invólucros plásticos, lacrados, e enviados ao \\bal.
        """
        
exames += r"""
%Por fim, foram encontrados dois aparelhos de telefonia celular próximos à entrada lateral já descrita neste laudo (ver figura \\ref{celular}) que, no entendimento do perito, podem estar relacionados ao crime:

%\\begin{itemize}

%	\\item \\textbf{Um (01)} celular da marca BLU, modelo Jenny TV 2.8 T276T I 13, IMEI 1 número 354278078362898, IMEI 2 número 35427807815297, com um chip da operadora OI com número de série 8955313929 862374013;
%	\\item \\textbf{Um (01)} celular da marca PANASONIC, modelo não identificado, IMEI 1 número 35424507221845, IMEI 2 número 354245072218483, com chip da operadora Claro com número de série 8955 0534 9701 7294 3471.

%\\end{itemize}

%\\f{celular}{Fotografia dos celulares encontrados.}

%É importante salientar que o local no qual os celulares foram encontrados não pode ser registrado em fotografia devido a defeitos de ordem técnica na câmera fotográfica utilizada pelo Perito Criminal.

"""

# EXCLUIR A VARIÁVEL EXAMES, E TROCAR PELO MÉTODO vitima.exames() quando disponível

for vitima in vitimas:
    exames += vitima.exames(images_path)

vestigios = f"""

\\section{{DOS VESTÍGIOS \\label{{vestigios}}}}

{figVest.frase[0]} no(s) Termo(s) de Encaminhamento de Vestígios (TEV) acostado(s) ao processo SEI pelo qual será enviado este Laudo Pericial.

{figVest.figsTex}

"""

dinamica = r"""

\section{DISCUSSÃO DA DINÂMICA DO FATO \label{dinamica}}

Analisando minuciosamente as evidências encontradas no local, as lesões no cadáver, e todo o contexto que correlaciona as mesmas, entende o Perito Criminal que:

\begin{itemize}
	\item Escrever aqui

\end{itemize}

"""

conclusoes = Conclusoes(vitimas)

conc = conclusoes.texto(dataCiente.iloc[0])

enc = r"""
%\newpage
\section{ENCERRAMENTO}

\setcounterpageref{pgf}{pagfim}
\setcounterref{reffig}{figure}
Eu, {\bf Betson Fernando Delgado dos Santos Andrade}, Perito Criminal deste Instituto de Criminalística no GEPH/DHPP, confeccionei o presente {\bf LAUDO PERICIAL DE """ + tipoExameRes + r"""}, consistindo de arquivo digital em formato pdf, assinado e certificado digitalmente por mim, possuindo\extenso{\value{figure}} (\thefigure) figuras com legendas explicativas, e \extenso{\value{pgf}}(\thepgf) páginas, em tamanho oficial, encimadas pelo timbre do Estado de Pernambuco.

SECRETARIA DE DEFESA SOCIAL – GERÊNCIA GERAL DE POLÍCIA CIENTÍFICA – INSTITUTO DE CRIMINALÍSTICA PROFESSOR ARMANDO SAMICO – GRUPO ESPECIALIZADO EM PERÍCIAS DE HOMICÍDIO (GEPH)-DO IC - DHPP."""

string_dict = {
'<MACROS>': result_macros, 
'<INFO>': info,
'<RODAPE>': rodape,
'<TÍTULO>': titulo,
'<HISTORICO>': hist, 
'<OBJETIVO>': objetivo, 
'<MATERIAIS>': materiais, 
'<DESC_LOCAL>': descLocalGeral + descLocalDetalhe,
'<ISOLAMENTO>': isol, 
'<EXAMES>': exames,
'<VESTÍGIOS>': vestigios if figVest.numFigs != 0 else "",
'<DINÂMICA>': dinamica,
'<CONCLUSÕES>': conc, 
'<ENCERRAMENTO>': enc}

new_str = str_replace(string_dict, file_str)

def beautify(s):
    s = re.sub(r"""( |\t)+    # Busca por qualquer caractere em branco horizontal, de 1 a infinitas vezes
                    (?=          # Olha para frente para uma destas sequências abaixo:
                        (\\\w*sec    # Procura por \sec, \subsec, \subsubsec, etc...
                        |\\f{        # Procura por \f{
                        |\\begin     # Procura por \begin
                        |\\end))     # Procura por \end
                        """, "", s, 0, re.X)
    
    s = re.sub(r"( |\t)+(?=\\item)", "\t", s)
    s = re.sub(r" {4}", "\t", s)    # Substituir quatro espaços em branco pelo tab
    
    return s
    
f_out = open(file_path, mode="w", encoding='utf-8')
f_out.write(beautify(new_str))
f_out.close()

# ======================================================================================================================
# ======================================= FINAL DA EDIÇÃO DO LAUDO =====================================================
# ======================================================================================================================

subprocess.Popen(file_path, shell=True, creationflags = subprocess.DETACHED_PROCESS)  # Abrir arquivo .tex para editar
subprocess.Popen(r'explorer "' + images_path.replace("/", "\\") + "\"")  # Abrir diretório de imagens para editar
    
obs = Observacoes(Path(images_path))
obs.print()

print(f"\n\nLaudo Pericial 4.0 >>> Execução terminada.\nResultado disponível em '{file_path}'\nAplicativo desenvolvido por BETSON FERNANDO (betson.fernando@gmail.com).\n\n")
# input("Tecle \"ENTER\" para sair.")

# TODO: INSERIR OS DADOS COLETADOS DIRETAMENTE NO MODELO DO LAUDO;
# TODO: INSERIR DADOS DE VEÍCULOS;
# TODO: COLOCAR AS VARIÁVEIS PARA MINÚSCULO, SE POSSÍVEL, COM EXCEÇÃO DOS NOMES.
# TODO: TESTAR MÚLTIPLOS HOMICÍDIOS (2)

