#Autor: Lucas Tavares dos Santos

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from fbprophet import Prophet
from flask import Flask, render_template, request
from getData import getDataAtDB
from datetime import date
from fbprophet.diagnostics import cross_validation, performance_metrics
import itertools

def create_param_combinations(**param_dict):
    param_iter = itertools.product(*param_dict.values())
    params =[]
    for param in param_iter:
        params.append(param) 
    params_df = pd.DataFrame(params, columns=list(param_dict.keys()))
    return params_df

def single_cv_run(history_df, metrics, param_dict, parallel):
    m = Prophet(**param_dict)
    m.add_country_holidays(country_name='BR')
    history_df['cap'] = 2*history_df["y"].max()
    m.fit(history_df)
    df_cv = cross_validation(m, initial='3600 days', horizon = '1200 days', parallel=parallel)
    df_p = performance_metrics(df_cv, rolling_window=1)
    df_p['params'] = str(param_dict)
    print(df_p.head())
    df_p = df_p.loc[:, metrics]
    return df_p

param_grid = {  
                'changepoint_prior_scale': [0.05, 0.5, 5],
                'changepoint_range': [0.8, 0.9],
                'seasonality_prior_scale': [0.05, 0.5, 5],
                'seasonality_mode': ['additive', 'multiplicative']
              }
metrics = ['horizon', 'rmse', 'mdape', 'params'] 
results = []

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
    
    #obtém valores de selects da pagina
    select_ano = request.form.get("Anos", None)
    # select_mun = request.form.get("Municipios", None)
    select_mun = 'Santos'
    select_dp = request.form.get("Delegacias", None)
    select_crime = request.form.get("Crimes", None)

    if select_dp != None and select_dp != "" and select_crime != None and select_crime != "":
        
        #dá um nome para o arquivo do plot
        img = 'static/plot' + select_ano + 'Santos' + select_dp + select_crime + '.png'
        print(select_dp)
        #obtém o dataframe
        df = getDataAtDB(select_mun, select_dp, select_crime)
        #print(df.head())
        df['datas'] = pd.to_datetime(df['datas'])

        #altera colunas do dataframe
        df.set_index('datas')
        df.columns = ["ds", "y"]

        #cria um modelo
        m = Prophet(
            changepoint_prior_scale=0.05, 
            changepoint_range=0.8, 
            seasonality_prior_scale=0.05, 
            seasonality_mode='additive'
        )
        m.add_country_holidays(country_name='BR')
        m.fit(df)

        #prevendo o futuro
        future = m.make_future_dataframe(periods=12*(int(select_ano) - date.today().year), freq='MS')
        forecast = m.predict(future)

        #cria imagem do plot
        m.plot(forecast, figsize=(8,4))
        plt.xlabel('Data')
        plt.ylabel('Ocorrencias')
        plt.gca().set_ylim(bottom=0)
        if (select_dp != 'Todos'):
            plt.title("Série temporal das ocorrências de " + select_crime + " registradas no " + select_dp)
        else:
            plt.title("Série temporal das ocorrências de " + select_crime + " registradas na cidade de " + select_mun)
        plt.savefig(img, bbox_inches='tight')

        plt.clf() #limpa figura atual
        
        # df_cv = cross_validation(m, initial='3600 days', horizon = '1200 days', parallel="processes")
        # df_p = performance_metrics(df_cv)
        # print(df_p.head())
        
        #Otimização dos hiperparametros
        # params_df = create_param_combinations(**param_grid)
        # print(len(params_df.values))
        # for param in params_df.values:
        #     param_dict = dict(zip(params_df.keys(), param))
        #     cv_df = single_cv_run(df, metrics, param_dict, parallel="processes")
        #     results.append(cv_df)
        # results_df = pd.concat(results).reset_index(drop=True)
        # best_param = results_df.loc[results_df['rmse'] == min(results_df['rmse']), ['params']]
        # print(f'\n The best param combination is {best_param.values[0][0]}')
        # print(results_df)

        return render_template("previsao.html", image = img)

    return render_template("previsao.html")

if __name__ == "__main__":
    app.run()