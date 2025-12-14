import pandas as pd;
import dash
from dash import Dash, dcc, html, Input, Output, callback


def load_dataBase():
    df = pd.read_csv('https://raw.githubusercontent.com/guiixta/fiscalCamara-Dashboard/refs/heads/main/tabelaDespesa.csv');
    return df;

df = load_dataBase();

df['data_emissao'] = pd.to_datetime(df['data_emissao']);

min_mes = df['data_emissao'].dt.month.min();
max_mes = df['data_emissao'].dt.month.max();



# Variaveis para filtros globais
datas_slide = sorted(list(df['data_emissao'].dropna().unique()));
mapa_meses = {
    1: 'Jan/24', 2: 'Fev/24', 3: 'Mar/24', 4: 'Abr/24', 5: 'Mai/24', 6: 'Jun/24',
    7: 'Jul/24', 8: 'Ago/24', 9: 'Set/24', 10: 'Out/24', 11: 'Nov/24', 12: 'Dez/24'
}

marksData = dict();
for i in range(min_mes, max_mes + 1):
    marksData[i] = mapa_meses[i]



estados = sorted(df['sigla_uf'].dropna().unique());


linksExternos = ['https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4']


app = Dash(__name__, external_scripts=linksExternos, title="O Fiscal da Câmara")


app.layout = html.Div(className="w-dvw h-dvh bg-lime-400 flex", children=[
    html.Div(className="w-[40%] bg-lime-950", children=[
        html.Div(className='flex flex-col p-2 gap-2 justify-center items-center', children=[
            html.H1(className='font-bold text-white text-xl', children='Configurações'),

            html.Span(className="w-full h-[1px] bg-lime-400")
        ]),

        html.Div(className='flex flex-col p-2 gap-2', children=[
            dcc.Dropdown(id='estado-filter', options=estados, searchable=False, multi=True, placeholder="Selecione o(s) estado(s)"),
            dcc.Dropdown(id='partido-filter', searchable=False, placeholder="Selecionar o(s) partido(s)", multi=True),

            html.Label("Período:", className="text-lime-200 font-bold mt-4"),
            dcc.RangeSlider(
                min=min_mes, 
                max=max_mes,
                step=1,
                value=[min_mes, max_mes], 
                marks=marksData, 
                className="mt-4, py-2"
            )
        ])
    ]),

    html.Div(className="w-[60%]", children=[
        html.Div(className="w-full overflow-y-scroll overflow-x-hidden max-h-[80%]", children=[
            
        ])
    ])
])

@callback(
    Output('partido-filter', 'options'),
    Input('estado-filter', 'value')
)
def PartidosPorEstado(estado):
    if not estado:
        partidos = sorted(df['sigla_partido'].dropna().unique()); 
        return partidos
    
    if isinstance(estado, str):
        estado = [estado]

    df_filtrado = df[df['sigla_uf'].isin(estado)];

    partidos_disponiveis = sorted(df_filtrado['sigla_partido'].unique()) # type: ignore

    return partidos_disponiveis;


if __name__ == '__main__':
    app.run(debug=True)
