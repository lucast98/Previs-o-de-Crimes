# Autor: Lucas Tavares dos Santos

from worker import conn
from rq import Queue
from utils import find_crime, find_delegacia
from flask import Flask, render_template, jsonify, request
from fbprophet import Prophet
from getData import getDataAtURL
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

app = Flask(__name__)
q = Queue(connection=conn)

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


@app.route('/PlotSeries', methods=['GET', 'POST'])
def PlotSeries():
    select_ano = request.form.get("Anos", None)
    select_mun = request.form.get("Municipios", None)
    select_dp = request.form.get("Delegacias", None)
    select_crime = request.form.get("Crimes", None)

    if select_mun != None and select_mun != "" and select_dp != None and select_dp != "" and select_crime != None and select_crime != "":
        img = 'static/plot' + select_ano + select_mun + select_dp + select_crime + '.png'

        # obtem dados diretamente do site de dados estatistico da policia de SP
        array, date, municipio = q.enqueue(getDataAtURL, select_ano, select_mun, select_dp, select_crime)

        # cria um dicionario
        d = {'Ocorrencia': array, 'Data': date}

        # cria um dataframe com o pandas
        df = pd.DataFrame(d, columns=['Data', 'Ocorrencia'])
        df['Data'] = pd.to_datetime(df['Data'])

        df.set_index('Data')
        df.columns = ["ds", "y"]

        m = Prophet()
        m.fit(df)

        # Prevendo o futuro
        future = m.make_future_dataframe(periods=120, freq='MS')
        forecast = m.predict(future)

        m.plot(forecast, figsize=(8, 4))
        plt.xlabel('Data')
        plt.ylabel('Ocorrencias')
        plt.gca().set_ylim(bottom=0)
        plt.title("Série temporal das ocorrências de " + find_crime(select_crime) +
                  " registradas no " + find_delegacia(select_dp, municipio))
        plt.savefig(img, bbox_inches='tight')
        plt.clf()
        return render_template("previsao.html", image=img)
    return render_template("previsao.html")

if __name__ == "__main__":
    app.run()
