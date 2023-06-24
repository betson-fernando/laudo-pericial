import tkinter as tk
from tkinter import filedialog
import pandas as pd
from datetime import datetime

import shutil
import os

import subprocess
import numpy as np

# Definição de funções: #######################################


def fmt_time(time):
    """Esta função recebe um dado do tipo 'datetime.datetime' ou 'datetime.time' e converte em uma string do tipo
    'dd/mm/aaaa' ou 'HH:mm' (adicionando um '0' se necessário)."""

    data_str = ""
    if f"{type(time)}" == "<class 'datetime.datetime'>":
        dia = f"{time.day}"
        mes = f"{time.month}"
        if len(mes) == 1:
            mes = "0" + mes
        if len(dia) == 1:
            dia = "0" + dia
        data_str = dia + "/" + mes + "/" + f"{time.year}"
    elif f"{type(time)}" == "<class 'datetime.time'>":
        hora = f"{time.hour}"
        minuto = f"{time.minute}"
        if len(hora) == 1:
            hora = "0" + hora
        if len(minuto) == 1:
            minuto = "0" + minuto
        data_str = hora + "h" + minuto + "min"

    return data_str


t = datetime.utcfromtimestamp(np.datetime64('2020/11/11 09:00:00', 's').astype(int))
print(t)

t2 = fmt_time(t)

print(t2)