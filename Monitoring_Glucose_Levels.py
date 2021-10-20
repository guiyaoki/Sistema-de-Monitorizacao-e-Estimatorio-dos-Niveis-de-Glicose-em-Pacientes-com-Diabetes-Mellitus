######################################################################################
#######################        Importando as Bibliotecas       #######################
######################################################################################
import imghdr
import smtplib
from datetime import datetime
from email.message import EmailMessage

import matplotlib
from scipy.interpolate import make_interp_spline

import matplotlib.pyplot as plt
import matplotlib.dates
import mysql.connector
import numpy

limite_sup = 180
limite_inf = 70


######################################################################################
#################################        Funções     #################################
######################################################################################
#   CRIAR DATABASE (Usuarios)
def Criar_Database():
    conexao = mysql.connector.connect(
        host='localhost',
        user='root',
        passwd='Guiyaoki27',
    )

    Database = input('\nInsira o nome do novo banco de dados: ')

    cursor = conexao.cursor()
    cursor.execute(f"CREATE DATABASE {Database}")  # Cria o banco de dados

    return Database


######################################################################################
#   CRIA TABELAS (Paciente)
def Criar_Table():
    table = input('\nEntre com o nome do paciente: ')
    email_paciente = 'pacientetcc.ufsc@gmail.com'
    password = 'tccpaciente'
    email_responsavel = str(input('Email do responsável: '))

    cursor.execute(f"CREATE TABLE {table}("
                   f"id INT AUTO_INCREMENT PRIMARY KEY,"
                   f"Data VARCHAR(255),"
                   f"Hora VARCHAR(255),"
                   f"Glicose VARCHAR(255))")

    com_sql = f'INSERT INTO usersemails(Paciente, EmailPaciente, Password, EmailResponsavel) VALUES (%s,%s,%s,%s)'
    valor = (f'{table}', f'{email_paciente}', f'{password}', f'{email_responsavel}')
    cursor.execute(com_sql, valor)
    conexao.commit()


######################################################################################
#    MOSTRA AS TABELAS CRIADAS (Pacientes Cadastrados)
def Paciente_Cadastrados():
    check_paciente = []

    cursor.execute("SHOW TABLES")
    # pacientes = cursor.fetchall()

    for pacientes_tuple in cursor:
        pacientes = pacientes_tuple[0]
        if pacientes != 'usersemails':
            check_paciente.append(pacientes)

    print(check_paciente)

    return check_paciente


######################################################################################
#   MOSTRA OS BANCOS DE DADOS
def Banco_Dados_Criados():
    Check_BD = []

    cursor.execute("SHOW DATABASES")
    for Check_BD_tuple in cursor:
        Check_BD.append(Check_BD_tuple[0])

    print(Check_BD)


######################################################################################
#    INSERINDO APENAS UMA LINHA NA TABELA
def Inserir_Dado(paciente):
    data_hora_atuais = datetime.now()
    data_atual = data_hora_atuais.strftime('%d/%m/%Y')
    hora_atual = data_hora_atuais.strftime('%H:%M')

    while True:
        try:
            glicose = input('\nInsira o valor da glicose: ')
            if int(glicose):
                pass
        except:
            print('Valor inserido inválido')
        else:
            break

    com_sql = f'INSERT INTO {paciente}(Data, Hora, Glicose) VALUES (%s,%s,%s)'
    valor = (f'{data_atual}', f'{hora_atual}', f'{glicose}')
    cursor.execute(com_sql, valor)
    conexao.commit()

    if int(glicose) > limite_sup or int(glicose) < limite_inf:
        cursor.execute(f'SELECT Glicose FROM {paciente}')  # busca a glicose
        glicose_busca_email = cursor.fetchall()  # busca os dados do paciente
        glicose_busca_email.reverse()
        glicose_busca_reverse_email = glicose_busca_email

        paciente_dados_email = []
        days_week_email = 0

        for glicose_value_tuple_email in glicose_busca_reverse_email:
            if days_week_email < 4:
                if glicose_value_tuple_email[0]:
                    glicose_value_email = int(glicose_value_tuple_email[0])
                    paciente_dados_email.append(glicose_value_email)
                    days_week_email += 1
            else:
                break

        paciente_dados_email.reverse()

        if paciente_dados_email[2] < limite_sup < paciente_dados_email[3]:
            print('Faça uma nova medição daqui a 30 minutos')

        if paciente_dados_email[1] < limite_sup < paciente_dados_email[2] < paciente_dados_email[3]:
            print('Faça uma nova medição daqui a 1 hora')

        if (limite_sup < paciente_dados_email[1] < paciente_dados_email[2] < paciente_dados_email[3]) or (
        all(i >= limite_sup for i in paciente_dados_email)) or (paciente_dados_email[3] < limite_inf):
            Send_Email(paciente, glicose, data_atual, hora_atual)


######################################################################################
#    Acessar Dados
def Acessar_Dados(paciente_busca, func_acesso, acessar=1, num_day=7):
    paciente_dados = []
    hora_dados = []
    data_dados = []
    data_hora_dados = []

    if acessar == 1:
        #   BUSCA AS HORAS NOS QUAIS FORAM INSERIDOS DADOS
        cursor.execute(f"SELECT Data, Hora FROM {paciente_busca} ")
        data_hora = cursor.fetchall()  # busca os dados do paciente
        data_hora.reverse()
        data_hora_reverse = data_hora

        #   BUSCA DO NUMERO DE DADOS PARA O CALCULO DO HB
        hb_num_dados = []
        while True:
            num_day_hb = [1, 3, 4, 6]

            for num_day_hb_item in num_day_hb:
                day_zero = 0
                hb_day_tuple_zero = ''
                hb_day = 0
                hb_dados = 0

                for hb_day_tuple in data_hora_reverse:
                    if hb_day_tuple[0] and hb_day_tuple[1]:
                        if day_zero == 0:
                            hb_dados += 1
                            hb_day_tuple_zero = hb_day_tuple[0]
                            hb_day += 1
                            day_zero = 1
                        else:
                            if hb_day_tuple[0] != hb_day_tuple_zero:
                                hb_day_tuple_zero = hb_day_tuple[0]
                                hb_day += 1
                                if hb_day > num_day_hb_item:
                                    break
                                hb_dados += 1
                            else:
                                hb_dados += 1

                hb_num_dados.append(hb_dados)

            if len(hb_num_dados) == len(num_day_hb):
                break
        #####################################################################
        #   BUSCA OS DIAS A SEREM PLOTTADOS NO GRAFICO
        week_list_reverse = []
        week_day = 0
        day_zero = 0
        week_day_tuple_zero = ''

        for week_day_tuple in data_hora_reverse:
            if week_day_tuple[0] and week_day_tuple[1]:
                if day_zero == 0:
                    week_list_reverse.append(week_day_tuple)
                    week_day_tuple_zero = week_day_tuple[0]
                    week_day += 1
                    day_zero = 1
                else:
                    if week_day_tuple[0] != week_day_tuple_zero:
                        week_day_tuple_zero = week_day_tuple[0]
                        week_day += 1
                        if week_day > num_day:
                            break
                        week_list_reverse.append(week_day_tuple)
                    else:
                        week_list_reverse.append(week_day_tuple)

        week_list_reverse.reverse()
        week_list = week_list_reverse

        i = 0
        for data_hora_value_tuple in week_list:
            if data_hora_value_tuple[0] and data_hora_value_tuple[1]:
                data_value = data_hora_value_tuple[0]
                data_dados.append(data_value)
                hora_value = data_hora_value_tuple[1]
                hora_dados.append(hora_value)

                if i == 0:
                    data_hora_dados.append(data_value + '  ' + hora_value)

                else:
                    if data_dados[i] != data_dados[i - 1]:
                        data_hora_dados.append(data_value + '  ' + hora_value)
                    else:
                        data_hora_dados.append(hora_value)

                i += 1
        ####################################################################
        ######################    BUSCA DA GLICOSE    ######################

        cursor.execute(f'SELECT Glicose FROM {paciente_busca}')  # busca a glicose
        glicose_busca = cursor.fetchall()  # busca os dados do paciente
        glicose_busca.reverse()
        glicose_busca_reverse = glicose_busca

        #####################################################################
        #   CALCULO DO HbA1c
        hb_average = []

        for len_average_hb_item in hb_num_dados:
            average_hb_num_dados = 0
            glicose_average = 0
            hb_average_item = 0
            for glicose_average_tuple in glicose_busca_reverse:
                if average_hb_num_dados < len_average_hb_item:
                    if glicose_average_tuple[0]:
                        glicose_average_item = int(glicose_average_tuple[0])
                        glicose_average = glicose_average + glicose_average_item
                        average_hb_num_dados += 1

            glicose_average = glicose_average / len_average_hb_item

            hb_average_item = glicose_average + 46.7
            hb_average_item = hb_average_item / 28.7

            hb_average.append(round(hb_average_item, 2))

        hb_average.reverse()

        hipo_hb = []
        hipe_hb = []
        normal_hb = []

        for dado_hb in hb_average:
            if dado_hb < 4:
                hipo_hb.append(dado_hb)
                hipe_hb.append(numpy.nan)
                normal_hb.append(numpy.nan)
            elif dado_hb > 6.5:
                hipo_hb.append(numpy.nan)
                hipe_hb.append(dado_hb)
                normal_hb.append(numpy.nan)
            else:
                hipo_hb.append(numpy.nan)
                hipe_hb.append(numpy.nan)
                normal_hb.append(dado_hb)

        hb_average_IFCC = []
        for dado_hb_IFCC in hb_average:
            hb_average_IFCC.append(round(10.929 * (dado_hb_IFCC - 2.15), 2))

        #####################################################################
        #   GRAFICO DOS RESULTADOS DOS NIVEIS DE GLICOSE
        days_week = 0

        for glicose_value_tuple in glicose_busca_reverse:
            if days_week < len(week_list):
                if glicose_value_tuple[0]:
                    glicose_value = int(glicose_value_tuple[0])
                    paciente_dados.append(glicose_value)
                    days_week += 1
            else:
                break

        paciente_dados.reverse()

        hipo_dados = []
        hipe_dados = []
        normal_dados = []

        for dado in paciente_dados:
            if dado < limite_inf:
                hipo_dados.append(dado)
                hipe_dados.append(numpy.nan)
                normal_dados.append(numpy.nan)
            elif dado > limite_sup:
                hipo_dados.append(numpy.nan)
                hipe_dados.append(dado)
                normal_dados.append(numpy.nan)
            else:
                hipo_dados.append(numpy.nan)
                hipe_dados.append(numpy.nan)
                normal_dados.append(dado)

        #####################################################################
        #   CONVERTER AS DATETIME DE STRING PARA DATETIME
        time_stri = []
        for time_stri_item in week_list:
            if time_stri_item[1]:
                time_stri.append(time_stri_item[1])

        time_data = []
        for time_item in time_stri:
            time_data.append(datetime.strptime(time_item, '%H:%M'))

        #####################################################################
        #   CONVERTENDO DATETIME PARA NUMERO PARA UTILIZAR SPLINE

        time = matplotlib.dates.date2num(time_data)

        time = list(map(lambda x: 10 * (x + 25567.0), time))  # 25567.0 representa o dia 01/01/1900 00:00
        # a cada 24h representa +1

        #####################################################################
        #   INTERPOLACAO
        Xnew = list(range(0, len(week_list)))
        Xnew_arr = numpy.array(Xnew)
        Ynew_arr = numpy.array(paciente_dados)
        X_Y_Spline = make_interp_spline(Xnew_arr, Ynew_arr)
        X_smooth = numpy.linspace(0, len(Xnew_arr) - 1, 100)
        Y_smooth = X_Y_Spline(X_smooth)

        Xnew_hb = list(range(0, len(num_day_hb)))
        Xnew_arr_hb = numpy.array(Xnew_hb)
        Ynew_arr_hb = numpy.array(hb_average)
        X_Y_Spline = make_interp_spline(Xnew_arr_hb, Ynew_arr_hb)
        X_smooth_hb = numpy.linspace(0, len(Xnew_arr_hb) - 1, 100)
        Y_smooth_hb = X_Y_Spline(X_smooth_hb)

        Ynew_arr_hb_IFCC = numpy.array(hb_average_IFCC)
        X_Y_Spline_IFCC = make_interp_spline(Xnew_arr_hb, Ynew_arr_hb_IFCC)
        Y_smooth_hb_IFCC = X_Y_Spline_IFCC(X_smooth_hb)

        #####################################################################
        #   GRAFICO DOS NIVEIS DE GLICOSE DURANTE DETERMINADO DIA
        plt.subplots(1, 2, gridspec_kw={'width_ratios': [3, 1]}, figsize=(15, 6))

        #####################################################################
        #################       CONFIGURACOES DO 1 GRAFICO  #################
        #####################################################################
        plt.subplot(1, 2, 1)

        plt.axhline(limite_inf, color='red', lw=2, alpha=0.5)
        plt.axhline(limite_sup, color='red', lw=2, alpha=0.5)
        plt.axhspan(ymin=limite_inf, ymax=limite_sup, alpha=0.05, color='green')

        plt.plot(X_smooth, Y_smooth, '-')
        plt.plot(data_hora_dados, hipe_dados, 'o', c='m', label='Hiperglicemia')
        plt.plot(data_hora_dados, normal_dados, 'o', c='g', label='Normal')
        plt.plot(data_hora_dados, hipo_dados, 'o', c='r', label='Hipoglicemia')

        plt.ylabel("Glicemia (mg/dL)")
        plt.legend(loc='upper left')

        plt.gcf().autofmt_xdate()
        plt.grid(b=True, which='major', color='#666666', linestyle='-')
        plt.minorticks_on()
        plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
        plt.title(f'Resultados do {paciente_busca} dos últimos {num_day} dias')

        #####################################################################
        #################       CONFIGURACOES DO 2 GRAFICO  #################
        #####################################################################
        ax2 = plt.subplot(1, 2, 2)
        ax22 = ax2.twinx()

        ax2.axhline(4, color='red', lw=2, alpha=0.5)
        ax2.axhline(6.5, color='red', lw=2, alpha=0.5)
        ax2.axhspan(ymin=4, ymax=6.5, alpha=0.05, color='green')

        ax22.axhline(47.54115, color='red', lw=2, alpha=0.5)
        ax22.axhline(20.21865, color='red', lw=2, alpha=0.5)
        ax22.axhspan(ymin=20.21865, ymax=47.54115, alpha=0.05, color='green')

        ax2.grid(b=True, which='major', color='#666666', linestyle='-')
        ax2.minorticks_on()
        ax2.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
        ax2.set_title('HbA1c Estimado')
        ax2.set_ylabel("DCCT (%)")

        ax22.set_ylabel('IFCC (mmol/mol)')

        x_time = ['3 Meses', '2 Meses', '1 Mês', '15 Dias']

        ax22.plot(X_smooth_hb, Y_smooth_hb_IFCC, lw=0.5)
        ax2.plot(X_smooth_hb, Y_smooth_hb, '-', lw=0.5)
        ax2.plot(x_time, hipe_hb, 'o', c='m', label='Hiperglicemia')
        ax2.plot(x_time, normal_hb, 'o', c='g', label='Normal')
        ax2.plot(x_time, hipo_hb, 'o', c='r', label='Hipoglicemia')

        #####################################################################
        #   SE A FUNCAO FOI CHAMADA PELA BUSCA DE DADOS -> PLOT
        #   SE A FUNCAO FOI CHAMADA PELO ENVIO DE EMAIL -> SALVA A F1GURA
        if func_acesso == 1:
            plt.show()
        elif func_acesso == 2:
            plt.savefig(f'{paciente_busca}.png', bbox_inches='tight')

    elif acessar == 2:
        #####################################################################
        #   MOSTRA TODOS OS DIAS NO QUAL FORAM INSERIDOS ALGUM DADO

        cursor.execute(f"SELECT Data FROM {paciente_busca} ")
        data = cursor.fetchall()  # busca os dados do paciente
        for data_value_tuple in data:
            if data_value_tuple[0]:
                data_value = data_value_tuple[0]
                if data_value not in data_dados:
                    data_dados.append(data_value)

        data_busca = input('\nObservar os dados do dia (dd/mm/aa): ')

        #####################################################################
        #   BUSCA OS VALORES DE GLICOSE PARA DETERMINADO DIA

        cursor.execute(f"SELECT Glicose FROM {paciente_busca} WHERE Data='{data_busca}'")
        glicose = cursor.fetchall()  # busca os dados do paciente
        for glicose_value_tuple_day in glicose:
            if glicose_value_tuple_day[0]:
                glicose_value = int(glicose_value_tuple_day[0])
                paciente_dados.append(glicose_value)

        #####################################################################
        #   BUSCA AS HORAS NOS QUAIS FORAM INSERIDOS DADOS

        cursor.execute(f"SELECT Hora FROM {paciente_busca} WHERE Data='{data_busca}'")
        hora = cursor.fetchall()  # busca os dados do paciente
        for hora_value_tuple_day in hora:
            hora_value = hora_value_tuple_day[0]
            hora_dados.append(hora_value)

        hipo_dados = []
        hipe_dados = []
        normal_dados = []

        for dado in paciente_dados:
            if dado < limite_inf:
                hipo_dados.append(dado)
                hipe_dados.append(numpy.nan)
                normal_dados.append(numpy.nan)
            elif dado > limite_sup:
                hipo_dados.append(numpy.nan)
                hipe_dados.append(dado)
                normal_dados.append(numpy.nan)
            else:
                hipo_dados.append(numpy.nan)
                hipe_dados.append(numpy.nan)
                normal_dados.append(dado)

        #####################################################################
        #   GRAFICO DOS NIVEIS DE GLICOSE DURANTE DETERMINADO DIA
        plt.axhline(limite_inf, color='red', lw=2, alpha=0.5)
        plt.axhline(limite_sup, color='red', lw=2, alpha=0.5)
        plt.axhspan(ymin=limite_inf, ymax=limite_sup, alpha=0.05, color='green')

        plt.plot(hora_dados, paciente_dados, '-')
        plt.plot(hora_dados, hipe_dados, 'o', c='m', label='Hiperglicemia')
        plt.plot(hora_dados, normal_dados, 'o', c='g', label='Normal')
        plt.plot(hora_dados, hipo_dados, 'o', c='r', label='Hipoglicemia')

        plt.title(f'Resultados do {paciente_busca} para o dia {data_busca}')
        plt.legend()
        plt.ylabel("Glicemia (mg/dl)")

        plt.grid(b=True, which='major', color='#666666', linestyle='-')
        plt.minorticks_on()
        plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
        plt.show()


######################################################################################
#    ATUALIZAR DADOS

def Atualizar_Dado(paciente_analisado):
    while True:
        try:
            id_update = input('\nInsira o id do dado a ser modificado: ')
            dado_update = input('Insira o valor a ser atualizado: ')
            con_sql = f'UPDATE {paciente_analisado} SET Glicose="{dado_update}" WHERE {paciente_analisado}.id = "{id_update}"'
            cursor.execute(con_sql)
            conexao.commit()
        except:
            print('Entre com valores válidos')
        else:
            break


######################################################################################
#    Deletar Paciente

def Deletar_Paciente():
    while True:
        try:
            paciente = input('\nNome do Paciente a ser deletado: ')
            con_sql = f"DROP TABLE {paciente}"
            cursor.execute(con_sql)
        except:
            print('Não existe esse paciente no Banco de Dados')
        else:
            break

    while True:
        try:
            cursor.execute(f"SELECT id FROM usersemails WHERE Paciente='{paciente}'")
            x = cursor.fetchall()  # busca os dados do paciente

            id_delete = 0
            for id_delete_tuple in x:
                id_delete = id_delete_tuple[0]

            con_mysql = f"DELETE FROM usersemails WHERE id='{id_delete}'"
            cursor.execute(con_mysql)
            conexao.commit()
        except:
            print('Entre com um valor válido')
        else:
            break

    return paciente


######################################################################################
#    DELETAR UM BANCO DE DADOS

def Deletar_BD():
    while True:
        try:
            Banco_deletado = input('\nNome do Banco a ser deletado: ')
            con_sql = f"DROP DATABASE {Banco_deletado}"
            cursor.execute(con_sql)
        except:
            print('Não existe esse banco de dados')
        else:
            break
    return Banco_deletado


######################################################################################
#    DELETAR UM DADO
def Deletar_Dado(paciente_analisado):
    while True:
        try:
            id_delete = input('\nInsira o id do dado a ser deletado: ')
            con_sql = f"DELETE FROM {paciente_analisado} WHERE id = '{id_delete}'"
            cursor.execute(con_sql)
            conexao.commit()
        except:
            print('Entre com um valor válido')
        else:
            break


######################################################################################
#   CRIA UMA TABELA PARA OS EMAILS, CASO AINDA NAO HAJA
def Check_Table_Email():
    AllTables_aux = []

    cursor.execute("SHOW TABLES")
    tabelas = cursor.fetchall()

    for AllTables_tuple in tabelas:
        AllTables = AllTables_tuple[0]
        if AllTables not in AllTables_aux:
            AllTables_aux.append(AllTables)

    if 'usersemails' not in AllTables_aux:
        cursor.execute(f"CREATE TABLE usersemails("
                       f"id INT AUTO_INCREMENT PRIMARY KEY,"
                       f"Paciente VARCHAR(255),"
                       f"EmailPaciente VARCHAR(255),"
                       f"Password VARCHAR(255),"
                       f"EmailResponsavel VARCHAR(255))")


######################################################################################
#   ENVIO DE EMAIL AUTOMATICO
def Send_Email(paciente, glicose, data_atual, hora_atual):
    password_dados = []
    email_pac_dados = []
    email_resp_dados = []

    cursor.execute(f"SELECT Password, EmailPaciente, EmailResponsavel FROM usersemails WHERE Paciente='{paciente}'")

    x = cursor.fetchall()  # busca os dados do paciente

    for Password_Email_Email_tuple in x:
        password_value = Password_Email_Email_tuple[0]
        password_dados.append(password_value)
        email_pac_value = Password_Email_Email_tuple[1]
        email_pac_dados.append(email_pac_value)
        email_resp_value = Password_Email_Email_tuple[2]
        email_resp_dados.append(email_resp_value)

    Message = ''
    if int(glicose) < limite_inf:
        Message = f'\nO nivel da glicose ultrapassou os limites estabelecidos\n' \
                  f'Causa: HIPOGLICEMIA\n' \
                  f'Dia: {data_atual}\n' \
                  f'Hora: {hora_atual}\n' \
                  f'Glicose: {glicose}\n'

    elif int(glicose) > limite_sup:
        Message = f'\nO nivel da glicose ultrapassou os limites estabelecidos\n' \
                  f'Causa: HIPERGLICEMIA\n' \
                  f'Dia: {data_atual}\n' \
                  f'Hora: {hora_atual}\n' \
                  f'Glicose: {glicose}\n'

    msg = EmailMessage()
    msg.set_content(Message)

    msg['Subject'] = f'ULTRAPASSOU OS LIMITES - Paciente: {paciente} '
    msg['From'] = email_pac_dados[0]
    msg['To'] = email_resp_dados[0]

    func_acesso = 2
    Acessar_Dados(paciente, func_acesso)

    with open(f'{paciente}.png', 'rb') as f:
        image_data = f.read()
        image_type = imghdr.what(f.name)
        image_name = f.name
    msg.add_attachment(image_data, maintype='image', subtype=image_type, filename=image_name)

    # Send the message via our own SMTP server.
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(email_pac_dados[0], password_dados[0])
    server.send_message(msg)
    server.quit()


######################################################################################
####################     INICIA CONEXAO COM BANCO DE DADOS        ####################
######################################################################################

conexao = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='Guiyaoki27'
)

cursor = conexao.cursor()

######################################################################################
#   CRIAR/DELETAR/ACESSAR BANCO DE DADOS
BDstage = True
while BDstage == True:
    print('\n--------------------------------------------------------------')
    print('1 - Criar Banco de dados\n'
          '2 - Deletar Banco de dados\n'
          '3 - Acessar Banco de dados\n'
          '4 - Exit\n')

    while True:
        try:
            Acesso_BD = int(input('Insira o numero da açao desejada: '))
        except:
            print('Entre com um número válido')
        else:
            break

    #########################################################################
    #   CRIA BANCO DE DADO
    if Acesso_BD == 1:
        print('\nBancos de Dados existentes:')
        Banco_Dados_Criados()

        Database = Criar_Database()
        conexao = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='Guiyaoki27',
            database=f'{Database}'
        )
        cursor = conexao.cursor()
        print(f'\nBanco de Dados ({Database}) criado com sucesso\n')

    #########################################################################
    #   DELETA UM BANCO DE DADOS
    elif Acesso_BD == 2:
        print('\nBancos de Dados existentes:')
        Banco_Dados_Criados()

        banco_deletado = Deletar_BD()
        print(f'\nO Banco {banco_deletado} foi deletado\n')

    #########################################################################
    #   ACESSA UM BANCO DE DADOS
    elif Acesso_BD == 3:
        print('\nBancos de Dados existentes:')
        Banco_Dados_Criados()

        while True:
            try:
                Database = input('\nQual Banco de Dados deseja acessar? ')

                #############################################################
                #   CARREGA O BANCO DE DADOS ESCOLHIDO
                conexao = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    passwd='Guiyaoki27',
                    database=f'{Database}'
                )
                cursor = conexao.cursor()
            except:
                print('Valor fora de alcance\nTente Novamente')
            else:
                break

        Check_Table_Email()

        BDstage = False
        PacienteStage = True

        #####################################################################
        #   INCLUSAO E EXCLUSAO DE PACIENTES DO BANCO DE DADOS
        while PacienteStage == True:
            print('\n++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            print('Lista de Pacientes ja criados:')
            check_pac = Paciente_Cadastrados()

            print('\nO que deseja fazer:')
            print('1 - Criar Paciente'
                  '\n2 - Acessar Paciente'
                  '\n3 - Deletar Paciente'
                  '\n4 - Return'
                  '\n5 - Exit')

            while True:
                try:
                    acao = int(input('\nInsira o numero correpondente a açao desejada: '))
                except:
                    print('Entre com um valor válido')
                else:
                    break

            #################################################################
            #   CRIA UM NOVO PACIENTE
            if acao == 1:
                Criar_Table()
                print('\nPaciente criado com sucesso\n')

            #################################################################
            ###########       INICIO DA INTERFACE DO USUARIO     ############
            #################################################################

            #   ACESSA UM PACIENTE
            elif acao == 2:
                paciente_analisado = input('\nInserir o nome do paciente: ')
                while paciente_analisado not in check_pac:
                    paciente_analisado = input(
                        '\nO paciente inserido não se encontra no banco de dados\nInserir um nome válido: ')

                pacienteTrue = True

                #############################################################
                #  MANIPULACAO DOS DADOS DO PACIENTE
                while pacienteTrue == True:
                    print('===============================================')

                    print('1 - Inserir dado ao paciente\n'
                          '2 - Buscar dados do paciente\n'
                          '3 - Editar dado\n'
                          '4 - Deletar um dado\n'
                          '5 - Return\n'
                          '6 - Exit\n')

                    while True:
                        try:
                            inserir_busca = int(input('Insira o numero correpondente a açao desejada: '))
                        except:
                            print('Entre com um valor válido')
                        else:
                            break

                    #########################################################
                    #   INSERE UM NOVO VALOR DE GLICOSE
                    if inserir_busca == 1:
                        Inserir_Dado(paciente_analisado)
                        print('\nDados inseridos com sucesso!\n')

                    #########################################################
                    #   BUSCA UM OS VALORES SALVOS NO BANCO DE DADOS
                    elif inserir_busca == 2:
                        print('\n1 - Buscar resultados dos ultimos dias\n'
                              '2 - Buscar por data\n')

                        while True:
                            try:
                                acessar = int(input('Entre com um número válido: '))
                                while acessar not in [1, 2]:
                                    acessar = int(input('Entre com um número válido: '))
                            except:
                                pass
                            else:
                                break

                        if acessar == 1:
                            num_day = int(input('Entre com o número de dias que deseja observar: '))

                        func_acesso = 1
                        Acessar_Dados(paciente_analisado, func_acesso, acessar, num_day)
                        print('\nDados acessados com sucesso!\n')

                    #########################################################
                    #   ATUALIZA/EDITA UM DADO
                    elif inserir_busca == 3:
                        cursor.execute(f'SELECT * FROM {paciente_analisado}')  # busca todos os dados
                        resultado = cursor.fetchall()  # busca os dados do paciente
                        for x in resultado:
                            print(x)

                        print('')

                        Atualizar_Dado(paciente_analisado)

                        print('\nDados atuaizados com sucesso!\n')

                    #########################################################
                    #   DELETAR UM DADO
                    elif inserir_busca == 4:
                        cursor.execute(f'SELECT * FROM {paciente_analisado}')  # busca todos 3os dados
                        resultado = cursor.fetchall()  # busca os dados do paciente
                        for x in resultado:
                            print(x)
                        print('')

                        Deletar_Dado(paciente_analisado)

                        print('\nDado deletado com sucesso!\n')

                    #########################################################
                    #########        FIM INTERFACE DO USUARIO       #########
                    #########################################################

                    #   RETORNA PARA A INCLUSAO E EXCLUSAO DE PACIENTES DO BANCO DE DADOS (LINHA 176)
                    elif inserir_busca == 5:
                        pacienteTrue = False

                    #########################################################
                    #   ENCERRA O PROGRAMA
                    elif inserir_busca == 6:
                        PacienteStage = False
                        break

                    #########################################################
                    #   RETORNA PARA MANIPULACAO DOS DADOS DO PACIENTE (LINHA 214)
                    else:
                        print('\nValor inserido fora do alcance')
                        pacienteTrue = True

            #################################################################
            #   DELETA UM PACIENTE
            elif acao == 3:
                paciente_deletado = Deletar_Paciente()
                print(f'Paciente {paciente_deletado} deletado\n')

            #################################################################
            #   RETORNA PARA CRIAR/DELETAR/ACESSAR BANCO DE DADOS (LINHA 125)
            elif acao == 4:
                BDstage = True
                PacienteStage = False

            #################################################################
            #   ENCERRA O PROGRAMA
            elif acao == 5:
                PacienteStage = False
                BDstage = False
                break

            #################################################################
            # RETORNA PARA INCLUSAO E EXCLUSAO DE PACIENTES DO BANCO DE DADOS (LINHA 176)
            else:
                PacienteStage = True
                print('\nValor fora do alcance')

    elif Acesso_BD == 4:
        BDstage = False
        break

    #########################################################################
    #   RETORNA PARA CRIAR/DELETAR/ACESSAR BANCO DE DADOS (LINHA 125)
    else:
        print('\nO valor inserido fora de alcance')