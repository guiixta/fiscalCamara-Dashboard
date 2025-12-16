import pandas as pd;


def load_dataBase():
    df = pd.read_csv('https://raw.githubusercontent.com/guiixta/fiscalCamara-Dashboard/refs/heads/main/tabelaDespesa.csv');
    return df;

df = load_dataBase();

ranking_partidos = df.groupby(df['sigla_partido']).agg({
        'valor_liquido': 'sum',
        'nome_parlamentar': 'nunique'
}).reset_index()

print(ranking_partidos);
