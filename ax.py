import pandas as pd;


def load_dataBase():
    df = pd.read_csv('https://raw.githubusercontent.com/guiixta/fiscalCamara-Dashboard/refs/heads/main/tabelaDespesa.csv');
    return df;

df = load_dataBase();

df['data_emissao'] = pd.to_datetime(df['data_emissao']);


print(df['data_emissao'])

