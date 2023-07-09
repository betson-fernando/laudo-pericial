import pandas as pd


def findLine(sheet: pd.DataFrame, index_str: str, message: str, exit_if_not_found: bool = False):
    """Esta função tem o objetivo de retornar a linha completa de um caso presente em uma planilha no formato DataFrame,
    além de substituir valores vazios ("NaN") por strings vazias.
    Caso a linha não for encontrada, retorna um DataFrame de linha única no qual todos os valores são strings vazias,
    além de levantar um erro com uma mensagem personalizada "message", e uma mensagem padrão.
    Entradas:
        --> sheet: planilha, no formato DataFrame.
        --> index_str: string indexadora, que pode ser o número do caso, ou id da ocorrência.
        --> message: Em caso de erro, uma mensagem padronizada será impressa.
            planilha o caso não foi encontrado.
        --> stop_if_not_found : True se "sheet" for a planilha preenchida na base, False, se for a
            preenchida no local.

    Saídas:
        Todas as linhas do caso especificado."""
    try:
        line = sheet.loc[index_str]
    except KeyError as err:
        print(message)
        raise err
        return None
        
    else:
        if type(line) == pd.Series:
            temp = pd.DataFrame(line).swapaxes(0, 1).fillna("")
            return temp.reset_index()
        else:
            return line.fillna("")
    

   
class Caso():
    def __init__(self, caso:str):
        self.caso = caso
    
    def importar(self, sheet: pd.DataFrame):
        try:
            linha = sheet.loc[self.caso]
        except KeyError as err:
            raise err
            print("Planilha não encontrada na base.")
            return None
            #DESATIVAR BOTÃO
        else:
            if type(linha) == pd.Series:
                linha = pd.DataFrame(linha).swapaxes(0, 1).fillna("").reset_index()
            else:
                linha = linha.fillna("")
                
            # DADOS DA PLANILHA PREENCHIDA NA BASE:

            # OBS.: NO FUTURO, SE FICAR PROIBIDO FAZER "linha[<str>].iloc[<int>]", posso usar "linha.loc[<int>, <str>]".
            self.tipo = linha['tipoexame']
            self.casoId = linha['caso_id']
            self.rep = linha['rep']
            self.req = linha['req']
            self.aux = linha['aux']
            self.delegado = linha['delegado']
            self.vtPericia = linha['vtPericia']
            self.horaCiente = linha['horaCiente']
            self.horaInicio = linha['horaInicio']
            self.horaFim = linha['horaFim']
            

            self.dataCiente = linha['dataPlant']
            # TODO: TESTAR PARA HORÁRIOS DE MADRUGADA PARA ENTRAR NESSE IF E VER SE FUNCIONA = 1
            if self.dataCiente[0] != "" and 0 <= self.horaCiente[0].hour < 6:
                self.dataCiente.update(pd.Series(self.dataCiente + timedelta(days=1)))


class Vitima():
    def __init__(self, caso_id):
        
    
    def importar(self, sheet, casoId):
        try:
            linha = sheet.loc[index_str]
        except KeyError as err:
            print(message)
            raise err
            return None
        else:
            self.nome = linha['nomeVit']
            self.sexo = linha['sexo']
            # self.tipoDoc = linha
            self.numDoc = linha['numDoc']
            self.mae = linha['mae']
            self.dataNasc = linha['dataNasc']
            # self.nat = ...
            self.nic = linha['nic']
            self.arma = linha['arma']
            self.cal = linha['cal']
        
    def calc_idade(self, data1, data2, caso):
        data1 = self.dataNasc
        data2 = caso.dataCiente
        """Esta função calcula a idade, baseado na time de nascimento e na time da perícia.
            Entradas: <datetime.datetime d1> e <datetime.datetime d2>: as duas datas, não importando a ordem.
            Retorno: <idade>"""

        series_iter = range(nasc.__len__())  # Iterador para ser usado nesta função
        idade_res = pd.Series(index=series_iter, dtype=str)

        for cont in series_iter:

            try:
                assert nasc.iloc[cont] != ""
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


class IdDesc(Vitima):
    def __init__(self, nome=r'de \textbfIDENTIDADE DESCONHECIDA', dataNasc="", numDoc="", nat="", tipoDoc=""):
        
        pass
