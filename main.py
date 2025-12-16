import pandas as pd;
import dash
from dash import Dash, dcc, html, Input, Output, callback
from pandas.core.algorithms import rank
import plotly.express as px

def load_dataBase():
    df = pd.read_csv('https://raw.githubusercontent.com/guiixta/fiscalCamara-Dashboard/refs/heads/main/tabelaDespesa.csv');
    return df;

def formatar_moeda(valor):
    if not valor: 
        return "R$ 0,00"
    
    sufixos = ['', ' K', ' M', ' B', ' T']
    magnitude = 0
    valor_aux = float(valor)

    while abs(valor_aux) >= 1000 and magnitude < len(sufixos) - 1:
        magnitude += 1
        valor_aux /= 1000.0

    # Ajusta casas decimais: 2 para valores exatos/pequenos, 1 para abreviados
    casas = 2 if magnitude < 2 else 1
    
    valor_fmt = f'{valor_aux:,.{casas}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    
    return f'R$ {valor_fmt}{sufixos[magnitude]}'

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

    dcc.Store(id="store-filtro-tempo"),


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
                className="mt-4, py-2",
                id='slider-tempo' 
            )
        ])
    ]),

    html.Div(className="w-[60%]", children=[
        html.Div(className="w-full overflow-y-scroll overflow-x-hidden max-h-[99%]", children=[
           html.Div(className='Cards flex gap-2 p-1 my-2 w-full', children=[
                html.Div(className="bg-white p-2 flex flex-col justify-center items-center w-[50%] border border-lime-950", children=[
                    html.H1(children='Gasto Total', className="text-sm"),
                    html.Span(id='gasto-total-card', className="font-bold text-2xl")
                ]),

                html.Div(className="bg-white p-2 flex flex-col justify-center items-center w-[50%] border border-lime-950", children=[
                    html.H1(children='Pico mensal', className="text-sm"),
                    html.Span(id='mes-maior-card', className="font-bold text-2xl")
                ])
           ]),

           html.Div(className='Graficos w-full px-1 flex flex-col gap-2', children=[
                dcc.Graph(id="evolucao-gastos-grafico"),
                dcc.Graph(id="tipo-gastos-grafico"),
                dcc.Graph(id="media-partido-grafico")
           ]) 
        ])
    ])
])



@callback(
    Output('media-partido-grafico', 'figure'),
    Input('store-filtro-tempo', 'data')
)
def MediaGastosPartido(data):
    if not data:
        return {}

    dff = pd.DataFrame(data);
 

    ranking_partidos = dff.groupby(dff['sigla_partido']).agg({
        'valor_liquido': 'sum',
        'nome_parlamentar': 'nunique'
    }).reset_index()

    ranking_partidos['media'] = ranking_partidos['valor_liquido'] / ranking_partidos['nome_parlamentar'];

    ranking_partidos = ranking_partidos.sort_values(by='media', ascending=True);

    grfBarras = px.bar(
        ranking_partidos, 
        x='sigla_partido', 
        y='media', 
        color='sigla_partido', # Cada coluna uma cor
        title="Gasto Médio por Parlamentar", 
        labels={'sigla_partido': 'Partido', 'media': 'Média de Gasto (R$)'},
        color_discrete_sequence=px.colors.qualitative.Bold # Paleta de cores vivas
    )

    cor_fundo = '#1a2e05'  # lime-950
    cor_linha = '#a3e635'  # lime-400
    cor_texto = '#ecfccb'  # lime-100

    grfBarras.update_layout(
        paper_bgcolor=cor_fundo,
        plot_bgcolor=cor_fundo,
        font_color=cor_texto,
        title_font_color=cor_linha,
        showlegend=False # Remove a legenda lateral pois é redundante
    )

    # Grade sutil igual ao gráfico de linha
    grfBarras.update_yaxes(gridcolor='rgba(163, 230, 53, 0.1)') 
    grfBarras.update_xaxes(showgrid=False)    

    return grfBarras

@callback(
    Output('tipo-gastos-grafico', 'figure'),
    Input('store-filtro-tempo', 'data')
)
def CategoriasGastos(data):
    if not data:
        return {}

    dff  = pd.DataFrame(data);

    gastos_por_categoria = dff.groupby(dff['tipo_despesa'])['valor_liquido'].sum().reset_index()

    grfPizza = px.pie(
        gastos_por_categoria, 
        values="valor_liquido", 
        names="tipo_despesa", 
        title="Para Onde Vai o Dinheiro?",
        color_discrete_sequence=px.colors.qualitative.Bold,
        hole=0.4,
        labels={
            'valor_liquido': 'Valor (R$)',
            'tipo_despesa': 'Tipo'
        }
    )

    cor_fundo = '#002c22' #1f3208
    cor_titulo = '#a3e635'
    cor_texto = '#ecfccb'

    grfPizza.update_layout(
        paper_bgcolor=cor_fundo,
        font_color=cor_texto,
        title_font_color=cor_titulo,
        legend=dict(
            font=dict(color=cor_texto)
        )
    )

    grfPizza.update_traces(
        textinfo='percent',
        marker=dict(line=dict(color=cor_fundo, width=2))
    )

    return grfPizza

@callback(
    Output('gasto-total-card', 'children'),
    Output('mes-maior-card', 'children'),
    Output('evolucao-gastos-grafico', 'figure'),
    Input('store-filtro-tempo', 'data')
)
def CardsEvolucao(data):
    if not data:
        return {}

    dff = pd.DataFrame(data);

    dff['data_emissao'] = pd.to_datetime(dff['data_emissao'])

    mes_min = dff['data_emissao'].dt.month.min()
    mes_max = dff['data_emissao'].dt.month.max()

    valor_total = dff['valor_liquido'].sum()

    gasto_total_card = formatar_moeda(valor_total);

    gastos_por_mes = dff.groupby(dff['data_emissao'].dt.month)['valor_liquido'].sum().reset_index();


    indice_maior = gastos_por_mes['valor_liquido'].idxmax();
    mes_maior = gastos_por_mes.loc[indice_maior, 'data_emissao'];
    nome_mes = mapa_meses.get(mes_maior, "Mês Desconhecido");

    mes_maior_card = f'{nome_mes}'

    gastos_por_mes['mes_nome'] = gastos_por_mes['data_emissao'].replace(mapa_meses)

    grf_linhas = px.line(gastos_por_mes, x='mes_nome', y='valor_liquido', title=f'Evolução dos Gastos ({mapa_meses.get(mes_min)} - {mapa_meses.get(mes_max)})', labels={
        'mes_nome': 'Período',
        'valor_liquido': 'Valor Gastos (R$)'
    }, markers=True)

    # Definindo as cores manualmente para bater com o Tailwind
    cor_fundo = '#1a2e05'  # lime-950
    cor_linha = '#a3e635'  # lime-400
    cor_texto = '#ecfccb'  # lime-100 (branco levemente esverdeado)

    grf_linhas.update_layout(
        paper_bgcolor=cor_fundo,
        plot_bgcolor=cor_fundo,
        font_color=cor_texto,
        title_font_color=cor_linha # Título em destaque
    )

    # Atualiza a cor da linha e dos marcadores (bolinhas)
    grf_linhas.update_traces(
        line_color=cor_linha, 
        marker_color=cor_fundo, # Miolo da bolinha escuro
        marker_line_color=cor_linha, # Borda da bolinha neon
        marker_line_width=2
    )

    # Deixa a grade bem sutil para não poluir
    grf_linhas.update_yaxes(gridcolor='rgba(163, 230, 53, 0.1)') # lime-400 com 10% opacidade
    grf_linhas.update_xaxes(showgrid=False)


    return gasto_total_card, mes_maior_card, grf_linhas


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

@callback(
    Output('store-filtro-tempo', 'data'),
    [
     Input('slider-tempo', 'value'),
     Input('estado-filter', 'value'),
     Input('partido-filter', 'value')   
    ]
)
def FiltrosGlobais(tempo: list, estado: list, partido: list):
    tempo_min = tempo[0];
    tempo_max = tempo[1];

    df_filtrado = df[df['data_emissao'].dt.month.between(tempo_min, tempo_max)];

    if estado:
        df_filtrado = df_filtrado[df_filtrado['sigla_uf'].isin(estado)] #type: ignore

    if partido:
        df_filtrado = df_filtrado[df_filtrado['sigla_partido'].isin(partido)] #type: ignore


    return df_filtrado.to_dict('records') #type: ignore



if __name__ == '__main__':
    app.run(debug=True)
