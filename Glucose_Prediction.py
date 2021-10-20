#############################################################################
#################        Importando as bibliotecas       ####################
#############################################################################

import pandas as pd
from openpyxl import load_workbook
import matplotlib.pyplot as plt
import matplotlib.dates
from datetime import datetime
import imghdr
import smtplib
import numpy
from scipy.interpolate import *
from math import *
from statistics import *
% matplotlib
qt

#############################################################################
# Ler os dados do Paciente (Excel)
data_csv = pd.read_excel('mateu_libre_ed.xlsx')

#############################################################################
# Organiza todas as horas de forma crescente
df_sort = data_csv.sort_values('Hora')
df_sort = df_sort.reset_index()

hora_lst = []
for item in range(len(df_sort['Hora'])):
    hora_lst.append(df_sort.loc[item]['Hora'])

hora = []
for item in hora_lst:
    hora.append(item.strftime('%H:%M'))

glicose = list(df_sort['Glicose medida (mg/dL)'])

#############################################################################
# Conta quantas medidas foram feitas no mesmo minuto
contador_repet = []
for item in sorted(set(hora)):
    contador_repet.append(hora.count(item))

#############################################################################
# Calcula a média de cada minuto e cria uma lista com os valores de cada minuto
mean_lst = []
rep_values = []
glicose2 = glicose

for item in range(len(sorted(set(hora)))):
    cont = 0
    values_mean = []
    while cont < contador_repet[item]:
        values_mean.append(glicose2[0])
        del glicose2[0]
        cont += 1
    mean_lst.append(numpy.mean(values_mean))
    rep_values.append(values_mean)

#############################################################################
# Converte cada miuto em um número e cria o dataframa
hora_org = list(sorted(set(hora)))
lst1 = range(len(hora_org))

time_data = []
for time_item in hora_org:
    time_data.append(datetime.strptime(time_item, '%H:%M'))
time = matplotlib.dates.date2num(time_data)
time = list(map(lambda x: (x + 25567.0), time))

df_org = pd.DataFrame(list(zip(hora_org, time, contador_repet, mean_lst, rep_values)),
                      columns=['Hora', 'Hora_num', 'Repetição', 'Media_Glicose', 'Valores_Mesmo_Min'])

#############################################################################
##################      Cálculos para a média de 30 minutos     #############
#############################################################################

# Desenvolvimento do eixo X com intervalo de 30 min
from datetime import datetime, timedelta

X_hora_h = []
X_interv = []
X_hora = []

start_date = datetime.strptime(df_org['Hora'].min(), '%H:%M')
end_date = datetime.strptime(df_org['Hora'].max(), '%H:%M')

interv_min = 30
interv = interv_min / 60


def daterange(start_date, end_date, interv):
    delta = timedelta(hours=interv)
    while start_date < end_date:
        yield start_date
        start_date += delta


for single_date in daterange(start_date, end_date, interv):
    X_interv.append(single_date.strftime("%H:%M"))

for single_date in daterange(start_date, end_date, 1):
    X_hora_h.append(single_date.strftime("%H:%M"))

for item in X_interv:
    if item in X_hora_h:
        X_hora.append(item)
    else:
        X_hora.append(numpy.nan)

#############################################################################
# Cria uma lista com os valores no intervalo de 30 min
minimo = df_org['Hora_num'][1]
interv_30_num = []
interv_30_date = []
interv_30 = []
cont = 30

for item in range(0, 48):
    interv_30_num.append(cont * minimo)
    cont += 30

interv_30_date = matplotlib.dates.num2date(interv_30_num)

for item in interv_30_date:
    interv_30.append(item.strftime('%H:%M'))

#############################################################################
# Conta quantos valores(minutos) tem no intervalo de 30 min
mean_lst_30 = []
mean_lst_2 = list(df_org['Media_Glicose'])
rep_values_2 = []
hora = df_org['Hora']
i = 0

for item in interv_30:
    cont = 0
    values_mean_2 = []
    while hora[i] < item:
        values_mean_2.append(mean_lst_2[0])
        del mean_lst_2[0]
        i += 1
    mean_lst_30.append(numpy.mean(values_mean_2))
    rep_values_2.append(values_mean_2)

df_org_30 = pd.DataFrame(list(zip(X_interv, mean_lst_30, rep_values_2)),
                         columns=['Hora', 'Media_Glicose', 'Valores_Mesmo_Min'])

#############################################################################
# Número de dados utilizados para a média de cada intervalo
num_rep = []

for item in range(0, len(df_org_30['Valores_Mesmo_Min'])):
    num_rep.append(len(df_org_30['Valores_Mesmo_Min'][item]))

df_org_30['Número de Dados Utilizados para o Cálculo da Média'] = num_rep

#############################################################################
# Desvio padrão
desv_padr_30 = []
i = 0

for item in df_org_30['Valores_Mesmo_Min']:
    if len(item) > 2:
        desv_padr_30.append(pstdev(rep_values_2[i]))
    else:
        desv_padr_30.append(numpy.nan)
    i += 1

df_org_30['Desvio_Padrao'] = desv_padr_30

#############################################################################
# Coeficiente de Variação-> Desvio/Media
coef_var = []
i = 0
for item in df_org_30['Media_Glicose']:
    coef_var.append((df_org_30['Desvio_Padrao'][i] / item) * 100)
    i += 1

df_org_30['Coeficiente_de_Variação_%'] = coef_var

#############################################################################
# Interpolação
Xnew = list(range(0, 48))
Xnew_arr = numpy.array(Xnew)
Ynew_arr = numpy.array(mean_lst_30)
X_Y_Spline = CubicSpline(Xnew_arr, Ynew_arr)
X_smooth_30 = numpy.linspace(0, len(Xnew_arr) - 1, 10000)
Y_smooth_30 = X_Y_Spline(X_smooth_30)

#############################################################################
# Encontrar Pontos de Máximo
from numpy import diff, sign

ponto_max = (diff(sign(diff(Y_smooth_30))) < 0).nonzero()[0] + 1

#############################################################################
# Plot 30min
plt.figure(figsize=(30, 6))

plt.plot(X_smooth_30, Y_smooth_30, '-', label='Estimativa pelo Método da Interpolação')
plt.plot(X_interv, mean_lst_30, 'x', label='Valores Obtidos', color='red')
plt.plot(X_smooth_30[ponto_max], Y_smooth_30[ponto_max], "o", label="Possível Intervalo de Alimentação", color='green')

plt.ylabel('Glicemia (mg/dL)')
plt.title('Estimativa da Rotina Alimentar do Paciente')
plt.legend()

plt.gcf().autofmt_xdate()
plt.grid(b=True, which='major', color='#666666', linestyle='-')
plt.minorticks_on()
plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)

#############################################################################
# Plot dos Desvios Padrões e Coeficiente de Variação
fig, desvio = plt.subplots(figsize=(30, 6))
cv = desvio.twinx()

desvio.bar(df_org_30['Hora'], df_org_30['Desvio_Padrao'], label='Desvio Padrão')
desvio.set_ylabel('Desvio Padrão (mg/dL)')
desvio.legend(loc='upper left')

Xnew_erro = list(range(0, 48))
Xnew_arr_erro = numpy.array(Xnew_erro)
Ynew_arr_erro = numpy.array(df_org_30['Coeficiente_de_Variação_%'])
X_Y_Spline = CubicSpline(Xnew_arr_erro, Ynew_arr_erro)
X_smooth_erro = numpy.linspace(0, len(Xnew_arr_erro) - 1, 10000)
Y_smooth_erro = X_Y_Spline(X_smooth_erro)

cv.plot(df_org_30['Hora'], df_org_30['Coeficiente_de_Variação_%'], 'x', color='red')
cv.plot(X_smooth_erro, Y_smooth_erro, '-', color='red', label='Coeficiente de Variação')
cv.axhline(30, color='red', lw=2, alpha=0.5)
cv.axhline(15, color='red', lw=2, alpha=0.5)
cv.set_ylabel('Coeficiente de Variação (%)')
cv.legend(loc='upper right')

plt.title('Dados Estatísticos')
plt.gcf().autofmt_xdate()
plt.grid(b=True, which='major', color='#666666', linestyle='-')
plt.minorticks_on()
plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
plt.show()

#############################################################################
# Plot do Coeficiente de variação e numero de dados utilizados na média
fig, dados_media = plt.subplots(figsize=(30, 6))
cv = dados_media.twinx()

dados_media.bar(df_org_30['Hora'], df_org_30['Número de Dados Utilizados para o Cálculo da Média'],
                label='Número de Dados')
dados_media.set_ylabel('Número de Dados Utilizados para a Média')
dados_media.legend(loc='upper left')

cv.plot(df_org_30['Hora'], df_org_30['Coeficiente_de_Variação_%'], 'x', color='red')
cv.plot(X_smooth_erro, Y_smooth_erro, '-', color='red', label='Coeficiente de Variação')
cv.axhline(30, color='red', lw=2, alpha=0.5)
cv.axhline(15, color='red', lw=2, alpha=0.5)
cv.set_ylabel('Coeficiente de Variação (%)')
cv.legend(loc='upper right')

plt.title('Dados Estatísticos')
plt.gcf().autofmt_xdate()
plt.grid(b=True, which='major', color='#666666', linestyle='-')
plt.minorticks_on()
plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
plt.show()

#############################################################################
# Predição dos valores
y_mesu = int(input('Entre com o valor da glicose: '))
print(f'O valor inserido eh: {y_mesu}')

# Busca do valor na hora desejada
hora = int(input('Entre apenas com a hora inserida: '))
mnt = int(input('Entre apenas com os minutos inserido: '))
minutos = hora * 60 + mnt

indice_value = floor(minutos * (10000 / (24 * 60)))
y_est = Y_smooth_30[indice_value]
print(f'O valor estimado eh: {y_est}')

# Erro
err = (y_mesu - y_est) / y_est
print(f'O erro eh: {err * 100}%')

# Prediction
mnt = mnt + 30
if mnt >= 60:
    hora += 1
    mnt = mnt - 60

minutos = hora * 60 + mnt

indice_value = floor(minutos * (10000 / (24 * 60)))
y_pred = Y_smooth_30[indice_value] * (1 + err)
print(f'O valor previsto na hora {hora}:{mnt} está no intervalo de: {Y_smooth_30[indice_value]} e {y_pred}')

#############################################################################
##########################      Média de 1 hora     #########################
#############################################################################

# Desenvolvmento do eixo X com intervalo de 30 min
from datetime import datetime, timedelta

X_hora_h_24 = []
X_interv_24 = []
X_hora_24 = []

start_date = datetime.strptime(df_org['Hora'].min(), '%H:%M')
end_date = datetime.strptime(df_org['Hora'].max(), '%H:%M')

interv_min = 30
interv = interv_min / 60


def daterange(start_date, end_date, interv):
    delta = timedelta(hours=interv)
    while start_date < end_date:
        yield start_date
        start_date += delta


for single_date in daterange(start_date, end_date, interv):
    X_interv_24.append(single_date.strftime("%H:%M"))

for single_date in daterange(start_date, end_date, 1):
    X_hora_h_24.append(single_date.strftime("%H:%M"))

for item in X_interv_24:
    if item in X_hora_h:
        X_hora_24.append(item)
    else:
        X_hora_24.append(numpy.nan)

#############################################################################
# Cria uma lista com os valores no intervalo de 30 min
minimo = df_org['Hora_num'][1]
interv_60_num = []
interv_60_date = []
interv_60 = []
cont = 60

for item in range(0, 24):
    interv_60_num.append(cont * minimo)
    cont += 60

interv_60_date = matplotlib.dates.num2date(interv_60_num)

for item in interv_60_date:
    interv_60.append(item.strftime('%H:%M'))

#############################################################################
# Conta quantos valores(minutos) tem no intervalo de 1 hora
mean_lst_24_aux = []
mean_lst_24 = []
rep_values_24 = []
mean_lst_2 = list(df_org['Media_Glicose'])
hora = df_org['Hora']
i = 0

for item in interv_60:
    values_mean_2 = []
    while hora[i] < item:
        values_mean_2.append(mean_lst_2[0])
        del mean_lst_2[0]
        i += 1
    mean_lst_24_aux.append(numpy.mean(values_mean_2))
    rep_values_24.append(values_mean_2)

for item in mean_lst_24_aux:
    mean_lst_24.append(item)
    mean_lst_24.append(numpy.nan)

df_org_24 = pd.DataFrame(list(zip(X_hora_h_24, mean_lst_24_aux, rep_values_24)),
                         columns=['Hora', 'Media_Glicose', 'Valores_Mesmo_Min'])

#############################################################################
# Número de dados utilizados para a média de cada intervalo
num_rep = []

for item in range(0, len(df_org_24['Valores_Mesmo_Min'])):
    num_rep.append(len(df_org_24['Valores_Mesmo_Min'][item]))

df_org_24['Número de Dados Utilizados para o Cálculo da Média'] = num_rep

#############################################################################
# Desvio padrão
desv_padr_24 = []
i = 0

for item in df_org_24['Valores_Mesmo_Min']:
    if len(item) > 2:
        desv_padr_24.append(pstdev(rep_values_2[i]))
    else:
        desv_padr_24.append(numpy.nan)
    i += 1

df_org_24['Desvio_Padrao'] = desv_padr_24

#############################################################################
# Coeficiente de Variação-> Desvio/Media
coef_var_24 = []
i = 0
for item in df_org_24['Media_Glicose']:
    coef_var_24.append((df_org_24['Desvio_Padrao'][i] / item) * 100)
    i += 1

df_org_24['Coeficiente_de_Variação_%'] = coef_var_24

#############################################################################
# Interpolação
Xnew_24 = list(range(0, 24))
Xnew_arr_24 = numpy.array(Xnew_24)
Ynew_arr_24 = numpy.array(mean_lst_24_aux)
X_Y_Spline_24 = CubicSpline(Xnew_24, Ynew_arr_24)
X_smooth_24 = numpy.linspace(0, len(Xnew_arr_24) - 1, 1000)
Y_smooth_24 = X_Y_Spline_24(X_smooth_24)

#############################################################################
# Pontos de Maximo
from numpy import diff, sign

ponto_max_24 = (diff(sign(diff(Y_smooth_24))) < 0).nonzero()[0] + 1

#############################################################################
# Plot Média de 1 hora
plt.figure(figsize=(15, 6))

plt.plot(df_org_24['Hora'], df_org_24['Media_Glicose'], 'x', label='Valores Obtidos', color='red')
plt.plot(X_smooth_24, Y_smooth_24, '-', label='Interpolação', color='orange')
plt.plot(X_smooth_24[ponto_max_24], Y_smooth_24[ponto_max_24], "o", label="Possível Intervalo de Alimentação",
         color='green')

plt.ylabel('Glicemia (mg/dL)')
plt.title('Estimativa da Rotina Alimentar do Paciente')

plt.gcf().autofmt_xdate()
plt.grid(b=True, which='major', color='#666666', linestyle='-')
plt.minorticks_on()
plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
plt.legend()
plt.show()

#############################################################################
# Plot dos Desvios Padrões e Coeficiente de Variação
fig, desvio = plt.subplots(figsize=(30, 6))
cv = desvio.twinx()

desvio.bar(df_org_24['Hora'], df_org_24['Desvio_Padrao'], label='Desvio Padrão')
desvio.set_ylabel('Desvio Padrão (mg/dL)')
desvio.legend(loc='upper left')

Xnew_erro = list(range(0, 24))
Xnew_arr_erro = numpy.array(Xnew_erro)
Ynew_arr_erro = numpy.array(df_org_24['Coeficiente_de_Variação_%'])
X_Y_Spline = CubicSpline(Xnew_arr_erro, Ynew_arr_erro)
X_smooth_erro = numpy.linspace(0, len(Xnew_arr_erro) - 1, 10000)
Y_smooth_erro = X_Y_Spline(X_smooth_erro)

cv.plot(df_org_24['Hora'], df_org_24['Coeficiente_de_Variação_%'], 'x', color='red')
cv.plot(X_smooth_erro, Y_smooth_erro, '-', color='red', label='Coeficiente de Variação')
cv.axhline(30, color='red', lw=2, alpha=0.5)
cv.axhline(15, color='red', lw=2, alpha=0.5)
cv.set_ylabel('Coeficiente de Variação (%)')
cv.legend(loc='upper right')

plt.title('Dados Estatísticos')
plt.gcf().autofmt_xdate()
plt.grid(b=True, which='major', color='#666666', linestyle='-')
plt.minorticks_on()
plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
plt.show()

#############################################################################
# Plot do Coeficiente de variacao e numero de dados utilizados na média
fig, dados_media = plt.subplots(figsize=(30, 6))
cv = dados_media.twinx()

dados_media.bar(df_org_24['Hora'], df_org_24['Número de Dados Utilizados para o Cálculo da Média'],
                label='Número de Dados')
dados_media.set_ylabel('Número de Dados Utilizados para a Média')
dados_media.legend(loc='upper left')

cv.plot(df_org_24['Hora'], df_org_24['Coeficiente_de_Variação_%'], 'x', color='red')
cv.plot(X_smooth_erro, Y_smooth_erro, '-', color='red', label='Coeficiente de Variação')
cv.axhline(30, color='red', lw=2, alpha=0.5)
cv.axhline(15, color='red', lw=2, alpha=0.5)
cv.set_ylabel('Coeficiente de Variação (%)')
cv.legend(loc='upper right')

plt.title('Dados Estatísticos')
plt.gcf().autofmt_xdate()
plt.grid(b=True, which='major', color='#666666', linestyle='-')
plt.minorticks_on()
plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
plt.show()

#############################################################################
##################      Plot Comparação 30 min e 1 hora     #################
#############################################################################

Xnew_24 = list(range(0, 48, 2))
Xnew_arr_24 = numpy.array(Xnew_24)
Ynew_arr_24 = numpy.array(mean_lst_24_aux)
X_Y_Spline_24 = CubicSpline(Xnew_24, Ynew_arr_24)
X_smooth_24 = numpy.linspace(0, 47, 1000)
Y_smooth_24 = X_Y_Spline_24(X_smooth_24)

plt.figure(figsize=(15, 6))

plt.plot(X_smooth_30, Y_smooth_30, '-', label='30min')
plt.plot(X_smooth_24, Y_smooth_24, '-', label='1hr')
plt.plot(X_interv, mean_lst_30, 'o')
plt.plot(X_hora_h_24, mean_lst_24_aux, 'o')

plt.ylabel('Glicemia (mg/dL)')
plt.title('Estimativa da Rotina Alimentar do Paciente')

plt.gcf().autofmt_xdate()
plt.grid(b=True, which='major', color='#666666', linestyle='-')
plt.minorticks_on()
plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
plt.legend()
plt.show()