import pandas as pd
import dash
from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px

def load_dataBase():
    # Alterado para leitura local para evitar lentidão/erros de rede na Vercel
    df = pd.read_csv('tabelaDespesa.csv')
    return df

def formatar_moeda(valor):
    if not valor: 
        return "R$ 0,00"
    
    sufixos = ['', ' K', ' M', ' B', ' T']
    magnitude = 0
    valor_aux = float(valor)

    while abs(valor_aux) >= 1000 and magnitude < len(sufixos) - 1:
        magnitude += 1
        valor_aux /= 1000.0

    casas = 2 if magnitude < 2 else 1
    
    valor_fmt = f'{valor_aux:,.{casas}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    
    return f'R$ {valor_fmt}{sufixos[magnitude]}'

# Carrega os dados globalmente
df = load_dataBase()

df['data_emissao'] = pd.to_datetime(df['data_emissao'])

min_mes = df['data_emissao'].dt.month.min()
max_mes = df['data_emissao'].dt.month.max()

# Função auxiliar para filtrar o DataFrame (não é um callback)
def filtrar_dataframe(tempo, estados, partidos):
    dff = df.copy()
    
    if tempo:
        dff = dff[dff['data_emissao'].dt.month.between(tempo[0], tempo[1])]

    if estados:
        if isinstance(estados, str): estados = [estados]
        dff = dff[dff['sigla_uf'].isin(estados)] #type: ignore

    if partidos:
        if isinstance(partidos, str): partidos = [partidos]
        dff = dff[dff['sigla_partido'].isin(partidos)]  #type: ignore       
    return dff

# Variaveis para filtros globais
datas_slide = sorted(list(df['data_emissao'].dropna().unique()))
mapa_meses = {
    1: 'Jan/24', 2: 'Fev/24', 3: 'Mar/24', 4: 'Abr/24', 5: 'Mai/24', 6: 'Jun/24',
    7: 'Jul/24', 8: 'Ago/24', 9: 'Set/24', 10: 'Out/24', 11: 'Nov/24', 12: 'Dez/24'
}

marksData = dict()
for i in range(min_mes, max_mes + 1):
    marksData[i] = mapa_meses[i]

estados = sorted(df['sigla_uf'].dropna().unique())

linksExternos = ['https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4']
estilos_externos = ['https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/bootstrap-icons.min.css']

app = Dash(__name__, external_scripts=linksExternos, external_stylesheets=estilos_externos, title="Análise de Despesas da Cota Parlamentar - Dashboard")

server = app.server

app.layout = html.Div(className="w-dvw h-dvh bg-lime-400 flex", children=[
    
    # Store removido daqui
    
    html.Div(className="w-[40%] bg-lime-950 flex flex-col", children=[
        html.Div(className='flex flex-col gap-2 mt-4 justify-center items-center', children=[
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
        ]),

        html.Div(className='w-full flex flex-col justify-center items-center mt-auto pb-4', children=[
            html.Span(className='w-full h-[1px] bg-lime-400'),
            html.Div(className='flex gap-1 mt-1', children=[
                html.H1(className='text-white cursor-default text-md', children='Fontes:'),
                html.A(className='decoration-none mr-2', href='https://basedosdados.org/dataset/3d388daa-2d20-49eb-8f55-6c561bef26b6?table=53b059b2-d2f7-4588-9b72-6d14149aa8e4', target='_blank', children=[
                    html.Img(className='w-auto h-6', src='./assets/basedosdados.png')
                ]),
                html.Div(className='relative flex flex-col items-center', children=[
                    html.Span(className='text-white font-bold cursor-default text-md peer underline', id='me', children='guiixta'),
                    html.Div(
                        id='painelRedes', 
                        className="""
                            hidden peer-hover:flex hover:flex 
                            flex-col absolute bottom-full left-1/2 -translate-x-1/2 z-50
                            w-max
                        """, 
                        children=[
                            html.Div(className='bg-black border border-white rounded p-2 flex flex-col gap-1', children=[
                                html.Span(className='text-white font-bold text-sm cursor-default whitespace-nowrap', children='Redes sociais'),
                                html.Div(className='flex gap-1 justify-center items-center', children=[
                                    html.A(className="decoration-white no-underline", href='https://github.com/guiixta/', target='_blank', children=[
                                        html.I(className='bi bi-github hover:text-neutral-500 cursor-pointer text-white')
                                    ]),
                                    html.A(className="decoration-white no-underline", href='https://linkedin.com/in/guilherme-ferreira-2b9a302a8', target='_blank', children=[
                                        html.I(className='bi bi-linkedin hover:text-neutral-500 cursor-pointer text-white')
                                    ]),
                                    html.A(className="decoration-white no-underline", href='mailto:guiferreirapessoa3@gmail.com', target='_blank', children=[
                                        html.I(className='bi bi-envelope-at-fill hover:text-neutral-500 cursor-pointer text-white')
                                    ])
                                ])
                            ])
                        ]
                    )
                ]) 
            ])
        ])
    ]),

    html.Div(className="w-[60%]", children=[
        html.Div(className="w-full overflow-y-scroll overflow-x-hidden max-h-[99%]", children=[
           html.Div(className='w-full flex flex-col justify-center items-center gap-2 mt-2', children=[
                html.H1(className='font-bold text-3xl text-center cursor-default text-lime-950', children='Análise de Despesas da Cota Parlamentar (2024)'),
                html.Span(className='w-full h-[1px] bg-lime-950')
           ]), 
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
                dcc.Graph(id="media-partido-grafico"),
                dcc.Graph(id='top5-parlamentar-grafico')
           ]) 
        ])
    ])
])

@callback(
    Output('top5-parlamentar-grafico', 'figure'),
    [
        Input('slider-tempo', 'value'),
        Input('estado-filter', 'value'),
        Input('partido-filter', 'value')    
    ]
)
def TopParlamentar(tempo, estados, partidos):
    dff = filtrar_dataframe(tempo, estados, partidos)
    
    if dff.empty: #type: ignore
        return {}
    
    ranking_parlamentar = dff.groupby(dff['nome_parlamentar']).agg({ #type: ignore
        'sigla_partido': 'first',
        'valor_liquido': 'sum'
    }).reset_index()

    ranking_parlamentar['nome_parlamentar'] = ranking_parlamentar['nome_parlamentar'].astype(str) + ' - ' + ranking_parlamentar['sigla_partido'].astype(str) 

    ranking_parlamentar = ranking_parlamentar.sort_values(by='valor_liquido', ascending=False).head(5)
    ranking_parlamentar.sort_values(by='valor_liquido', ascending=True)

    grfBarras = px.bar(ranking_parlamentar, y='nome_parlamentar', x='valor_liquido', orientation='h', title='Top 5: Parlamentares com Maior Gasto', labels={
        'nome_parlamentar': 'Parlamentar',
        'valor_liquido': 'Valor Gasto (R$)'
    }, color='nome_parlamentar', color_discrete_sequence=px.colors.qualitative.Bold)

    cor_fundo = '#002c22'
    cor_titulo = '#a3e635'
    cor_texto = '#ecfccb'

    grfBarras.update_layout(
        paper_bgcolor=cor_fundo,
        plot_bgcolor=cor_fundo,
        font_color=cor_texto,
        title_font_color=cor_titulo,
        showlegend=False,
        margin=dict(t=40, r=20, l=0, b=0),
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(title=None)
    )

    grfBarras.update_traces(
        texttemplate='R$ %{value:.2s}',
        textposition='inside',
        insidetextanchor='end',
        marker=dict(line=dict(color=cor_fundo, width=1))
    )
    
    return grfBarras

@callback(
    Output('media-partido-grafico', 'figure'),
    [
        Input('slider-tempo', 'value'),
        Input('estado-filter', 'value'),
        Input('partido-filter', 'value')    
    ]
)
def MediaGastosPartido(tempo, estados, partidos):
    dff = filtrar_dataframe(tempo, estados, partidos)

    if dff.empty: #type: ignore
        return {}

    ranking_partidos = dff.groupby(dff['sigla_partido']).agg({ #type: ignore 
        'valor_liquido': 'sum',
        'nome_parlamentar': 'nunique'
    }).reset_index()

    ranking_partidos['media'] = ranking_partidos['valor_liquido'] / ranking_partidos['nome_parlamentar']

    ranking_partidos = ranking_partidos.sort_values(by='media', ascending=True)

    grfBarras = px.bar(
        ranking_partidos, 
        x='sigla_partido', 
        y='media', 
        color='sigla_partido',
        title="Gasto Médio por Parlamentar", 
        labels={'sigla_partido': 'Partido', 'media': 'Média de Gasto (R$)'},
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    cor_fundo = '#1a2e05' 
    cor_linha = '#a3e635' 
    cor_texto = '#ecfccb' 

    grfBarras.update_layout(
        paper_bgcolor=cor_fundo,
        plot_bgcolor=cor_fundo,
        font_color=cor_texto,
        title_font_color=cor_linha,
        showlegend=False
    )

    grfBarras.update_yaxes(gridcolor='rgba(163, 230, 53, 0.1)') 
    grfBarras.update_xaxes(showgrid=False)     

    return grfBarras

@callback(
    Output('tipo-gastos-grafico', 'figure'),
    [
        Input('slider-tempo', 'value'),
        Input('estado-filter', 'value'),
        Input('partido-filter', 'value')    
    ]
)
def CategoriasGastos(tempo, estados, partidos):
    dff = filtrar_dataframe(tempo, estados, partidos)
    
    if dff.empty:#type: ignore
        return {}

    gastos_por_categoria = dff.groupby(dff['tipo_despesa'])['valor_liquido'].sum().reset_index() #type: ignore

    grfPizza = px.pie(
        gastos_por_categoria, 
        values="valor_liquido", 
        names="tipo_despesa", 
        title="Para Onde Vai o Dinheiro?",
        color_discrete_sequence=px.colors.qualitative.Bold,
        hole=0.4,
        labels={
            'valor_liquido': 'Valor Gasto (R$)',
            'tipo_despesa': 'Tipo'
        }
    )

    cor_fundo = '#002c22'
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
    [
        Input('slider-tempo', 'value'),
        Input('estado-filter', 'value'),
        Input('partido-filter', 'value')    
    ]
)
def CardsEvolucao(tempo, estados, partidos):
    dff = filtrar_dataframe(tempo, estados, partidos)
    
    if dff.empty: #type: ignore
        return "R$ 0,00", "-", {}

    mes_min = dff['data_emissao'].dt.month.min() #type: ignore
    mes_max = dff['data_emissao'].dt.month.max() #type: ignore

    valor_total = dff['valor_liquido'].sum()

    gasto_total_card = formatar_moeda(valor_total)

    gastos_por_mes = dff.groupby(dff['data_emissao'].dt.month)['valor_liquido'].sum().reset_index() #type: ignore
    if not gastos_por_mes.empty:
        indice_maior = gastos_por_mes['valor_liquido'].idxmax()
        mes_maior = gastos_por_mes.loc[indice_maior, 'data_emissao']
        nome_mes = mapa_meses.get(mes_maior, "Mês Desconhecido")
        mes_maior_card = f'{nome_mes}'
    else:
        mes_maior_card = "-"

    gastos_por_mes['mes_nome'] = gastos_por_mes['data_emissao'].replace(mapa_meses)

    grf_linhas = px.line(gastos_por_mes, x='mes_nome', y='valor_liquido', title=f'Evolução dos Gastos ({mapa_meses.get(mes_min, "")} - {mapa_meses.get(mes_max, "")})', labels={
        'mes_nome': 'Período',
        'valor_liquido': 'Valor Gasto (R$)'
    }, markers=True)

    cor_fundo = '#1a2e05' 
    cor_linha = '#a3e635' 
    cor_texto = '#ecfccb' 

    grf_linhas.update_layout(
        paper_bgcolor=cor_fundo,
        plot_bgcolor=cor_fundo,
        font_color=cor_texto,
        title_font_color=cor_linha 
    )

    grf_linhas.update_traces(
        line_color=cor_linha, 
        marker_color=cor_fundo, 
        marker_line_color=cor_linha, 
        marker_line_width=2
    )

    grf_linhas.update_yaxes(gridcolor='rgba(163, 230, 53, 0.1)') 
    grf_linhas.update_xaxes(showgrid=False)

    return gasto_total_card, mes_maior_card, grf_linhas

@callback(
    Output('partido-filter', 'options'),
    Input('estado-filter', 'value')
)
def PartidosPorEstado(estado):
    if not estado:
        partidos = sorted(df['sigla_partido'].dropna().unique()) 
        return partidos
    
    if isinstance(estado, str):
        estado = [estado]

    df_filtrado = df[df['sigla_uf'].isin(estado)]

    partidos_disponiveis = sorted(df_filtrado['sigla_partido'].unique()) #type: ignore

    return partidos_disponiveis

if __name__ == '__main__':
    app.run(debug=True)
