#Autor: Lucas Tavares dos Santos

import requests
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import itertools
import statsmodels.api as sm
import numpy as np
from fbprophet import Prophet
from bs4 import BeautifulSoup
from flask import Flask, render_template, jsonify, request
from utils import find_crime, find_delegacia
app = Flask(__name__)

@app.route('/')
@app.route('/index.html')
def index():
    return render_template("index.html")

@app.route('/equipe.html')
def equipe():
    return render_template("equipe.html")

@app.route('/previsao.html')
def projeto():
    return render_template("previsao.html")

@app.route('/PlotSeries', methods=['GET','POST'])
def PlotSeries():
    select_ano = request.form.get("Anos", None)
    select_mun = request.form.get("Municipios", None)
    select_dp = request.form.get("Delegacias", None)
    select_crime = request.form.get("Crimes", None)

    if select_mun != None and select_mun != "" and select_dp != None and select_dp != "" and select_crime != None and select_crime != "":
        img = 'static/plot' + select_ano + select_mun + select_dp + select_crime + '.png'

        #inicio e fim dos dados da serie temporal
        if int(select_ano) == 0:
            start = 2001
            end = datetime.datetime.now().year #ano atual, para sempre ter os dados atualizados
        else:
            start = end = int(select_ano)
        
        #definicao das requisicoes
        regiao = 0 #todos
        municipio = int(select_mun) #Sao Paulo
        dp = int(select_dp) #032 DP - Itaquera

        array = [] #lista com quantidade de ocorrencias
        date = [] #data que as ocorrencias ocorreram

        #cabecalho do site com as estatistica da policia
        HOST = 'www.ssp.sp.gov.br'
        url = "http://www.ssp.sp.gov.br/Estatistica/Pesquisa.aspx"
        header = {
            'Host': HOST,
            'Origin': 'http://www.ssp.sp.gov.br',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }

        #persiste parametros a partir de requisicoes
        session = requests.Session()
        r = session.get(url, headers=header)

        #obtem html da pagina
        soup = BeautifulSoup(r.content, features="html.parser")

        #parametros que serao utilizados para fazer a requisicao a pagina
        view_state = soup.select("#__VIEWSTATE")[0]['value']
        view_state_generator = soup.select("#__VIEWSTATEGENERATOR")[0]['value']
        event_validation = soup.select("#__EVENTVALIDATION")[0]['value']

        #parametros com o ano e a regiao desejada
        params_regiao = {
            'ctl00$conteudo$ddlAnos': str(start),
            'ctl00$conteudo$ddlRegioes': str(regiao)
        }

        #parametros com o ano e o municipio desejado
        params_municipio = {
            '__EVENTTARGET': 'ctl00$conteudo$btnMensal',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': view_state,
            '__VIEWSTATEGENERATOR': view_state_generator,
            '__EVENTVALIDATION': event_validation,
            'ctl00$conteudo$ddlAnos': str(start),
            'ctl00$conteudo$ddlMunicipios': str(municipio),
        }

        #requisicoes e parametros com o ano e a delegacia desejada
        params_delegacia = {
            '__EVENTTARGET': 'ctl00$conteudo$btnMensal',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': view_state,
            '__VIEWSTATEGENERATOR': view_state_generator,
            '__EVENTVALIDATION': event_validation,
            'ctl00$conteudo$ddlAnos': str(start),
            'ctl00$conteudo$ddlDelegacias': str(dp)
        }

        #foi necessario fazer uma requisicao para a regiao e outra para o municipio primeiro
        session.post(url, data=params_regiao, headers=header, cookies=r.cookies.get_dict())
        if dp != 0:
            session.post(url, data=params_municipio, headers=header, cookies=r.cookies.get_dict())

        #loop para obter as estatisticas de cada ano
        while start <= end:
            #faz requisicao a pagina
            if dp != 0:
                r = session.post(url, data=params_delegacia, headers=header, cookies=r.cookies.get_dict())
            else:
                r = session.post(url, data=params_municipio, headers=header, cookies=r.cookies.get_dict())
                
            table = r.text[(r.text).find("<tr>"):(r.text).rfind("</tr>")] #obtem tabela
            soup2 = BeautifulSoup(table, features="html.parser")
            #Ocorrencias registradas por mes
            j = 1 #j representa os meses do ano
    
            for rows in soup2.find_all('tr'):
                if str(rows.findAll('td')[0])[len("<td>"):-len("</td>")] == select_crime:
                    while j < 13:
                        if str(rows.findAll('td')[j])[len("<td>"):-len("</td>")] != "...":
                            array.append(int((str(rows.findAll('td')[j])[len("<td>"):-len("</td>")]).replace('.','')))
                            date.append(datetime.date(start, j, 1))
                        j = j+1
                    break
            start = start+1 #atualiza o valor do ano
            if dp != 0:
                params_delegacia.update({'ctl00$conteudo$ddlAnos': str(start)}) #atualiza o ano nos parametros da requisicao
            else:
                params_municipio.update({'ctl00$conteudo$ddlAnos': str(start)}) #atualiza o ano nos parametros da requisicao

        #cria um dicionario
        d = {'Ocorrencia': array, 'Data': date}

        #cria um dataframe com o pandas
        df = pd.DataFrame(d,columns=['Data', 'Ocorrencia'])
        df['Data'] = pd.to_datetime(df['Data'])
        # print(df.head())
        # print(df.dtypes)

        df.set_index('Data')
        df.columns = ["ds", "y"]
        
        m = Prophet()
        m.fit(df)

        #Prevendo o futuro
        future = m.make_future_dataframe(periods=120, freq='MS')
        forecast = m.predict(future)

        m.plot(forecast, figsize=(8,4))
        plt.xlabel('Data')
        plt.ylabel('Ocorrencias')
        plt.gca().set_ylim(bottom=0)
        plt.title("Série temporal das ocorrências de " + find_crime(select_crime) + " registradas no " + find_delegacia(select_dp, municipio))
        plt.savefig(img, bbox_inches='tight')
        plt.clf()
        return render_template("previsao.html", image = img)
    return render_template("previsao.html")

if __name__ == "__main__":
    app.run()