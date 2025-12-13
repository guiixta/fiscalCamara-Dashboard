import pandas as pd;
import dash
from dash import Dash, dcc, html
import plotly.graph_objects as go



def load_dataBase():
    df = pd.read_csv('https://raw.githubusercontent.com/guiixta/fiscalCamara-Dashboard/refs/heads/main/tabelaDespesa.csv');
    return df;

df = load_dataBase();

linksExternos = ['https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4']


app = Dash(__name__, external_scripts=linksExternos, title="O Fiscal da Câmara")


app.layout = html.Div([
    html.H4('Interactive color selection with simple Dash example'),
    html.P("Select color:"),
    dcc.Dropdown(
        id="dropdown",
        options=['Gold', 'MediumTurquoise', 'LightGreen'],
        value='Gold',
        clearable=False,
   )
])




if __name__ == '__main__':
    app.run(debug=True)
