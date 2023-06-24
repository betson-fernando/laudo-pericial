import os


def img_order(s):
    # Esta função tem por objetivo ordenar arquivos do tipo "[s][int].[ext]" em um arquivo segundo o número [int], onde
    # [s] e [ext] são strings. Ela é útil porque em alguns casos a ordem fica errada baseado em apenas uma análise
    # simples do nome do arquivo. Por exemplo, "cheg10.jpg" está antes de "cheg2.jpg" segundo uma análise simples. Em
    # nosso caso, deveria ser o contrário.
    i2 = s.find(".")
    i1 = i2

    while s[i1-1].isnumeric():
        i1 -= 1

    return int(s[i1:i2])


def add_figs(callstr_sing, callstr_pl, subtitle, figure_flag, figure_list):
    # Esta função gera uma string que inclui várias figuras automaticamente no arquivo Latex. Essa string é composta por
    # uma chamada (exemplo: "As figuras \ref{fig1.jpg} a \ref{fig3.jpg} exibem as casas em destaque:") e pela inserção
    # das figuras propriamente ditas, esta última de forma automática, baseada no nome dos arquivos de imagem, que devem
    # conter a string figure_flag.

    # callstr_sing: complementação da chamada (tudo após a referência às figuras) no singular. No exemplo acima, esta
    #               entrada seria: "exibe as casas em destaque".
    # callstr_pl: o mesmo do anterior, mas no plural: Ainda no mesmo exemplo, seria: "exibem as casas em detaque".
    # subtitle: legenda, que é comum a todas as figuras.
    # figure_flag: termo de busca para selecionar as figuras de interesse dentro da lista figure_list. As figuras devem
    #              ter este termo em seus nomes. Sugestão para nomes de figuras: "cheg1.jpg", "cheg2.jpg", "cheg3.jpg",
    #              etc., onde o número em cada um dos nomes será a ordem em que elas serão inseridas.
    # figure_list: lista contendo todas as figuras, incluindo as que possuem a substring figure_flag em seus nomes.

    select_img = []

    for img in figure_list:
        if img.__contains__(figure_flag):
            select_img.append(img)

    select_img_len = select_img.__len__()

    if select_img_len == 0:
        callstr = ""

    else:
        if select_img_len == 1:
            str1 = r"A figura \ref{" + select_img[0] + r"} "
            callstr = str1 + callstr_sing + "\n\n"

        elif select_img_len == 2:
            str1 = r"As figuras \ref{" + select_img[0] + r"} e \ref{" + select_img[1] + r"} "
            callstr = str1 + callstr_pl + "\n\n"

        else:
            str1 = r"As figuras \ref{" + select_img[0] + r"} a \ref{" + select_img[select_img_len - 1] + r"} "
            callstr = str1 + callstr_pl + "\n\n"

    select_img.sort(key=img_order)
    str2 = ""
    for item in select_img:
        str2 += r"\f{" + item + "}{" + subtitle + "}\n"

    return callstr + str2


img_names = os.listdir(r"C:\Users\Betson\PycharmProjects\Laudo Pericial")
print(add_figs("exibe figura aleatória:", "exibem figuras aleatórias:", "aqui estão as figuras aleatórias.", "stdi",
               img_names))
