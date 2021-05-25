from bs4 import BeautifulSoup
from var import *
import requests
import pandas as pd
import datetime
import psycopg2 as db

conn = db.connect(host='localhost', database='crimes', 
                        user='postgres', password='123', port='5432')
cursor = conn.cursor()

# cabecalho do site com as estatistica da policia
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



def writeDB(c, d, city, police, crime):
    global index
    
    sql_command1 = "INSERT INTO {} VALUES ({}, '{}', '{}', '{}')".format("crime_localizacao", 
            index, city, police, crime)
    cursor.execute(sql_command1)
    conn.commit()

    for i in range(len(c)):
        sql_command2 = "INSERT INTO {} VALUES ({}, '{}', {})".format("crime_ocorrencia", 
                        index, d[i], c[i])
        cursor.execute(sql_command2)
    conn.commit()
    print(crime, c)
    c.clear()
    d.clear()
    index = index+1


def getMonthlyCrimes(c, d, start, rows):
    j = 1  # j representa os meses do ano
    while j < 13:
        if str(rows.findAll('td')[j])[len("<td>"):-len("</td>")] != "...":
            c.append(
                int((str(rows.findAll('td')[j])[len("<td>"):-len("</td>")]).replace('.', '')))
            d.append(datetime.date(start, j, 1))
        j = j+1
    return c, d

def getCrimes(soup, start):
    global c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15, c16, c17
    global d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11, d12, d13, d14, d15, d16, d17

    for rows in soup.find_all('tr'):
        # print(str(rows.findAll('td')[0])[len("<td>"):-len("</td>")])
        if str(rows.findAll('td')[0])[len("<td>"):-len("</td>")] == "HOMICÍDIO DOLOSO (2)":
            c1, d1 = getMonthlyCrimes(c1, d1, start, rows)  #Homicídio Doloso
        if str(rows.findAll('td')[0])[len("<td>"):-len("</td>")] == "HOMICÍDIO DOLOSO POR ACIDENTE DE TRÂNSITO":
            c2, d2 = getMonthlyCrimes(c2, d2, start, rows)  #Homicídio Doloso por acidente de trânsito
        if str(rows.findAll('td')[0])[len("<td>"):-len("</td>")] == "HOMICÍDIO CULPOSO POR ACIDENTE DE TRÂNSITO":
            c3, d3 = getMonthlyCrimes(c3, d3, start, rows)  #Homicídio Culposo por acidente de trânsito
        if str(rows.findAll('td')[0])[len("<td>"):-len("</td>")] == "HOMICÍDIO CULPOSO OUTROS":
            c4, d4 = getMonthlyCrimes(c4, d4, start, rows)  #Homicídio Culposo - Outros
        if str(rows.findAll('td')[0])[len("<td>"):-len("</td>")] == "TENTATIVA DE HOMICÍDIO":
            c5, d5 = getMonthlyCrimes(c5, d5, start, rows)  #Tentativa de Homicídio
        if str(rows.findAll('td')[0])[len("<td>"):-len("</td>")] == "LESÃO CORPORAL SEGUIDA DE MORTE":
            c6, d6 = getMonthlyCrimes(c6, d6, start, rows)  #Lesão Corporal seguida de morte
        if str(rows.findAll('td')[0])[len("<td>"):-len("</td>")] == "LESÃO CORPORAL DOLOSA":
            c7, d7 = getMonthlyCrimes(c7, d7, start, rows)  #Lesão Corporal Dolosa
        if str(rows.findAll('td')[0])[len("<td>"):-len("</td>")] == "LESÃO CORPORAL CULPOSA POR ACIDENTE DE TRÂNSITO":
            c8, d8 = getMonthlyCrimes(c8, d8, start, rows)  #Lesão Corporal Culposa por acidente de trânsito
        if str(rows.findAll('td')[0])[len("<td>"):-len("</td>")] == "LESÃO CORPORAL CULPOSA - OUTRAS":
            c9, d9 = getMonthlyCrimes(c9, d9, start, rows)  #Lesão Corporal Culposa - Outras
        if str(rows.findAll('td')[0])[len("<td>"):-len("</td>")] == "LATROCÍNIO":
            c10, d10 = getMonthlyCrimes(c10, d10, start, rows)  #Latrocínio
        if str(rows.findAll('td')[0])[len("<td>"):-len("</td>")] == "TOTAL DE ESTUPRO (4)":
            c11, d11 = getMonthlyCrimes(c11, d11, start, rows)  #Estupro
        if str(rows.findAll('td')[0])[len("<td>"):-len("</td>")] == "ROUBO - OUTROS":
            c12, d12 = getMonthlyCrimes(c12, d12, start, rows)  #Roubo - Outros
        if str(rows.findAll('td')[0])[len("<td>"):-len("</td>")] == "ROUBO DE VEÍCULO":
            c13, d13 = getMonthlyCrimes(c13, d13, start, rows)  #Roubo de veículo
        if str(rows.findAll('td')[0])[len("<td>"):-len("</td>")] == "ROUBO A BANCO":
            c14, d14 = getMonthlyCrimes(c14, d14, start, rows)  #Roubo a banco
        if str(rows.findAll('td')[0])[len("<td>"):-len("</td>")] == "ROUBO DE CARGA":
            c15, d15 = getMonthlyCrimes(c15, d15, start, rows)  #Roubo de carga
        if str(rows.findAll('td')[0])[len("<td>"):-len("</td>")] == "FURTO - OUTROS":
            c16, d16 = getMonthlyCrimes(c16, d16, start, rows)  #Furto - Outros
        if str(rows.findAll('td')[0])[len("<td>"):-len("</td>")] == "FURTO DE VEÍCULO":
            c17, d17 = getMonthlyCrimes(c17, d17, start, rows)  #Furto de veículo

def getDataAtURL(select_mun, select_dp, city, police):
    # inicio e fim dos dados da serie temporal
    start = 2001  
    end = datetime.datetime.now().year # ano atual, para sempre ter os dados atualizados
    
    # definicao das requisicoes
    regiao = 0  # todos
    municipio = int(select_mun)  # Sao Paulo
    dp = int(select_dp)  # 032 DP - Itaquera

    # persiste parametros a partir de requisicoes
    session = requests.Session()
    r = session.get(url, headers=header)

    # obtem html da pagina
    soup = BeautifulSoup(r.content, features="html.parser")

    # parametros que serao utilizados para fazer a requisicao a pagina
    view_state = soup.select("#__VIEWSTATE")[0]['value']
    view_state_generator = soup.select("#__VIEWSTATEGENERATOR")[0]['value']
    event_validation = soup.select("#__EVENTVALIDATION")[0]['value']

    # parametros com o ano e a regiao desejada
    params_regiao = {
        'ctl00$conteudo$ddlAnos': str(start),
        'ctl00$conteudo$ddlRegioes': str(regiao)
    }

    # parametros com o ano e o municipio desejado
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

    # requisicoes e parametros com o ano e a delegacia desejada
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

    # foi necessario fazer uma requisicao para a regiao e outra para o municipio primeiro
    session.post(url, data=params_regiao, headers=header,
                 cookies=r.cookies.get_dict())
    if dp != 0:
        session.post(url, data=params_municipio, headers=header,
                     cookies=r.cookies.get_dict())

    # loop para obter as estatisticas de cada ano
    while start <= end:
        # faz requisicao a pagina
        if dp != 0:
            r = session.post(url, data=params_delegacia,
                             headers=header, cookies=r.cookies.get_dict())
        else:
            r = session.post(url, data=params_municipio,
                             headers=header, cookies=r.cookies.get_dict())

        table = r.text[(r.text).find("<tr>"):(
            r.text).rfind("</tr>")]  # obtem tabela
        soup2 = BeautifulSoup(table, features="html.parser")
        getCrimes(soup2, start)
        
        start = start+1  # atualiza o valor do ano
        if dp != 0:
            # atualiza o ano nos parametros da requisicao
            params_delegacia.update({'ctl00$conteudo$ddlAnos': str(start)})
        else:
            # atualiza o ano nos parametros da requisicao
            params_municipio.update({'ctl00$conteudo$ddlAnos': str(start)})
    
    # escreve no bd
    writeDB(c1, d1, city, police, "Homicídio Doloso")
    writeDB(c2, d2, city, police, "Homicídio Doloso por acidente de trânsito")
    writeDB(c3, d3, city, police, "Homicídio Culposo por acidente de trânsito")
    writeDB(c4, d4, city, police, "Homicídio Culposo - Outros")
    writeDB(c5, d5, city, police, "Tentativa de Homicídio")
    writeDB(c6, d6, city, police, "Lesão Corporal seguida de morte")
    writeDB(c7, d7, city, police, "Lesão Corporal Dolosa")
    writeDB(c8, d8, city, police, "Lesão Corporal Culposa por acidente de trânsito")
    writeDB(c9, d9, city, police, "Lesão Corporal Culposa - Outras")
    writeDB(c10, d10, city, police, "Latrocínio")
    writeDB(c11, d11, city, police, "Estupro")
    writeDB(c12, d12, city, police, "Roubo - Outros")
    writeDB(c13, d13, city, police, "Roubo de veículo")
    writeDB(c14, d14, city, police, "Roubo a banco")
    writeDB(c15, d15, city, police, "Roubo de carga")
    writeDB(c16, d16, city, police, "Furto - Outros")
    writeDB(c17, d17, city, police, "Furto de veículo")


if __name__ == "__main__":
    
    for city in municipio:
        if int(city[0]) >= 0:
            select_mun = city[0]
            for police in delegacia[int(city[0])-1]:
                #if police[0] != '79':
                    select_dp = police[0]
                    print(city[1])
                    print(police[1])
                    getDataAtURL(select_mun, select_dp, city[1], police[1])
                    # index = index + 1
    cursor.close()
    conn.close()