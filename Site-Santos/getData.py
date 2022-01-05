# from bs4 import BeautifulSoup
import psycopg2 as db
import pandas.io.sql as sqlio

def getDataAtDB(select_mun, select_dp, select_crime):
    conn = db.connect(host='localhost', database='crimes', 
                        user='postgres', password='123', port='5432')
    
    if select_dp == "Todos":
        sql_command = """
            SELECT o.datas, SUM(o.ocorrencia)
            FROM crime_ocorrencia o, crime_localizacao l
            WHERE o.id = l.id and l.municipio = '{}' and l.tipo = '{}'
            GROUP BY o.datas ORDER BY o.datas;
         """.format(select_mun, select_crime)
    else:
        sql_command = """
            SELECT o.datas, o.ocorrencia 
            FROM crime_ocorrencia o, crime_localizacao l 
            WHERE o.id = l.id and l.municipio = '{}' 
            and l.delegacia = '{}' and l.tipo = '{}'
        """.format(select_mun, select_dp, select_crime)
    dat = sqlio.read_sql_query(sql_command, conn)

    return dat