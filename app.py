import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import base64
import os

# Configuração da página
st.set_page_config(layout="wide", page_title="Dashboard PEP LGBT", initial_sidebar_state="expanded")

# Aplicar tema Light com CSS ajustado
st.markdown("""
    <style>
    .stMainBlockContainer {padding: 20px; background-color: #ffffff; color: #333333;}
    .stAppHeader {background-color: #ffffff;}
    .stSidebar {background-color: #f0f0f0; color: #333333;}
    h1, h2, h3, p {color: #333333; font-family: 'Arial', sans-serif;}
    .metric-card {background-color: #e0e0e0; padding: 10px; border-radius: 5px; text-align: center; color: #333333;}
    .stRadio > label {color: #333333;}
    .stSelectbox > label {color: #333333;}
    .stMarkdown {color: #333333;}
    .stWarning {color: #ff9900; background-color: #fff3e6; padding: 10px; border-radius: 5px;}
    </style>
""", unsafe_allow_html=True)

# Função para carregar dados com validação
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_excel("data/pep_data.xlsx", sheet_name="Banco_PEP_UDM")
        if df.empty:
            st.error("O arquivo de dados está vazio.")
            return None
        df['dt_disp'] = pd.to_datetime(df['dt_disp'], errors='coerce')
        return df
    except FileNotFoundError:
        st.error("Arquivo 'pep_data.xlsx' não encontrado.")
        return None
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {str(e)}")
        return None

# Função para download de dados filtrados
def download_csv(df, filename):
    csv = df.to_csv(index=False, encoding='utf-8-sig')
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">Download CSV</a>'
    return href

# Carregar dados
df = carregar_dados()
if df is None:
    st.stop()

# Sidebar com navegação e filtros
st.sidebar.title("Navegação e Filtros")
menu = st.sidebar.radio("Selecione a Página", ["🏠 Home", "💉 PEP", "🔒 PrEP"])

# Filtros globais
st.sidebar.header("Filtros")
estados = st.sidebar.multiselect("Estados", options=['BA', 'RJ'], default=['BA', 'RJ'])

# Definir intervalo de datas disponível
min_date = df['dt_disp'].min().date()
max_date = df['dt_disp'].max().date()

# Inputs de data separados com validação
data_inicio = st.sidebar.date_input("Data de Início", value=min_date, min_value=min_date, max_value=max_date)
data_fim = st.sidebar.date_input("Data de Fim", value=max_date, min_value=min_date, max_value=max_date)

# Validar intervalo de datas
if data_inicio < min_date or data_fim > max_date:
    st.sidebar.warning(f"Intervalo inválido! As datas devem estar entre {min_date} e {max_date}. Redefinindo para o intervalo padrão.")
    data_inicio = min_date
    data_fim = max_date

# Filtrar dados
df_filtrado = df[
    (df['UF_UDM'].isin(estados)) &
    (df['dt_disp'].dt.date >= data_inicio) &
    (df['dt_disp'].dt.date <= data_fim)
]

# Página Home
if menu == "🏠 Home":
    st.title("Dashboard PEP LGBT")
    st.markdown("""
    Este painel interativo tem como objetivo **visualizar e comparar a distribuição da Profilaxia Pós-Exposição (PEP)** 
    entre populações vulneráveis nos estados da **Bahia (BA)** e do **Rio de Janeiro (RJ)**.

    🔍 **Nota**: Os dados apresentados são fictícios ou reduzidos para fins de testes e desenvolvimento.

    ---
    ### Objetivos:
    - Facilitar a análise do acesso à PEP entre grupos populacionais.
    - Comparar comportamentos entre estados.
    - Contribuir com políticas públicas voltadas à população LGBTQIAPN+.

    ### Contexto dos Dados
    - **Por que BA x RJ?** Bahia (BA) e Rio de Janeiro (RJ) foram escolhidos por terem populações semelhantes (aproximadamente 14,8 milhões em BA e 16,7 milhões em RJ, segundo o IBGE 2025).
    - **Desequilíbrio nos Dados**: Apesar das populações similares, 90% dos dados são do RJ e apenas 10% da BA. Isso pode ser devido à:
      - **Área Geográfica**: A BA é muito maior (565.000 km² vs. 43.780 km² do RJ), com áreas rurais que dificultam a coleta de dados e a dispersão de PEP.
      - **Acesso à Saúde**: O RJ tem maior concentração urbana e infraestrutura de saúde, o que pode facilitar a distribuição e o registro de PEP.
      - **Coleta de Dados**: Os dados são coletados pela ANS, que pode ter melhor cobertura em áreas urbanas como o RJ.

    ### Possíveis Explicações para o Desequilíbrio
    - **Menor Dispersão de PEP na BA**: Pode haver menos acesso ou conscientização sobre PEP na BA, especialmente em áreas rurais.
    - **Desafios na Coleta de Dados**: A ANS pode ter coletado menos dados da BA devido a diferenças na infraestrutura de saúde ou nos processos de reporte.
    - **Recomendação**: Considere ambos os fatores ao interpretar os dados. Mais dados da BA podem ser necessários para uma análise completa.

    ### Próximos Passos
    - **Melhorar a Coleta de Dados**: Trabalhar com a ANS e o SUS para aumentar a cobertura de dados na BA, especialmente em áreas rurais.
    - **Expandir o Acesso ao PEP na BA**: Implementar programas de conscientização e distribuição de PEP em regiões menos atendidas da BA.
    - **Pesquisa Adicional**: Conduzir estudos para entender as barreiras ao acesso de PEP na BA e melhorar as políticas públicas.
    """)

# Página PEP
elif menu == "💉 PEP":
    st.title("📊 Análise Comparativa da Dispersão de PEP - BA x RJ")
    st.warning("Os dados foram coletados pela **Agência Nacional de Saúde (ANS)** e representam 90% de registros do RJ e apenas 10% da BA, o que pode impactar as comparações. Use os dados da BA com cautela devido ao tamanho limitado da amostra.")
    st.markdown("""
    🔗 **Fonte dos Dados**: [PEP - Profilaxia Pós-Exposição ao HIV](https://www.gov.br/aids/pt-br/assuntos/prevencao-combinada/pep-profilaxia-pos-exposicao-ao-hiv)
    """, unsafe_allow_html=True)

    # Verificar se há dados após filtragem
    if df_filtrado.empty:
        st.warning("Nenhum dado disponível com os filtros selecionados.")
        st.stop()

    # Métricas resumidas
    st.subheader("Resumo dos Dados")
    col1, col2, col3 = st.columns(3)
    with col1:
        total_registros = len(df_filtrado)
        st.markdown(f"<div class='metric-card'><strong>Total de Registros</strong><br>{total_registros}</div>", unsafe_allow_html=True)
    with col2:
        total_ba = len(df_filtrado[df_filtrado['UF_UDM'] == 'BA'])
        percent_ba = round((total_ba / total_registros * 100), 2) if total_registros > 0 else 0
        st.markdown(f"<div class='metric-card'><strong>Total BA</strong><br>{total_ba} ({percent_ba}%)</div>", unsafe_allow_html=True)
    with col3:
        total_rj = len(df_filtrado[df_filtrado['UF_UDM'] == 'RJ'])
        percent_rj = round((total_rj / total_registros * 100), 2) if total_registros > 0 else 0
        st.markdown(f"<div class='metric-card'><strong>Total RJ</strong><br>{total_rj} ({percent_rj}%)</div>", unsafe_allow_html=True)

    # Visualizações com percentuais
    st.subheader("Visualizações (Percentuais)")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Distribuição por Grupo Populacional")
        fig1 = px.histogram(df_filtrado, x='Pop', color='UF_UDM', barmode='group',
                            histnorm='percent',
                            labels={'Pop': 'Grupo Populacional', 'count': 'Percentual'},
                            title="Grupos Populacionais por Estado (Percentual)",
                            category_orders={'Pop': sorted(df_filtrado['Pop'].dropna().unique())},
                            text_auto=True)
        fig1.update_traces(textposition='auto', texttemplate='%{y:.2f}%', textfont=dict(color='#000000'))
        fig1.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#000000"),
            title=dict(text="Grupos Populacionais por Estado (Percentual)", font=dict(color="#000000")),
            xaxis=dict(
                title=dict(text="Grupo Populacional", font=dict(color="#000000")),
                tickfont=dict(color="#000000")
            ),
            yaxis=dict(
                title=dict(text="Percentual", font=dict(color="#000000")),
                tickfont=dict(color="#000000")
            )
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.markdown("#### Tipo de Exposição")
        fig2 = px.histogram(df_filtrado, x='tipo_exposicao', color='UF_UDM', barmode='group',
                            histnorm='percent',
                            labels={'tipo_exposicao': 'Tipo de Exposição', 'count': 'Percentual'},
                            title="Tipo de Exposição por Estado (Percentual)",
                            text_auto=True)
        fig2.update_traces(textposition='auto', texttemplate='%{y:.2f}%', textfont=dict(color='#000000'))
        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#000000"),
            title=dict(text="Tipo de Exposição por Estado (Percentual)", font=dict(color="#000000")),
            xaxis=dict(
                title=dict(text="Tipo de Exposição", font=dict(color="#000000")),
                tickfont=dict(color="#000000")
            ),
            yaxis=dict(
                title=dict(text="Percentual", font=dict(color="#000000")),
                tickfont=dict(color="#000000")
            )
        )
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("#### Trabalho Sexual")
        fig3 = px.histogram(df_filtrado, x='trabalho_sexual', color='UF_UDM', barmode='group',
                            histnorm='percent',
                            title="Trabalho Sexual por Estado (Percentual)",
                            labels={'trabalho_sexual': 'Trabalho Sexual', 'count': 'Percentual'},
                            text_auto=True)
        fig3.update_traces(textposition='auto', texttemplate='%{y:.2f}%', textfont=dict(color='#000000'))
        fig3.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#000000"),
            title=dict(text="Trabalho Sexual por Estado (Percentual)", font=dict(color="#000000")),
            xaxis=dict(
                title=dict(text="Trabalho Sexual", font=dict(color="#000000")),
                tickfont=dict(color="#000000")
            ),
            yaxis=dict(
                title=dict(text="Percentual", font=dict(color="#000000")),
                tickfont=dict(color="#000000")
            )
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown("#### Uso de Álcool/Drogas")
        fig4 = px.histogram(df_filtrado, x='alcool_drogas', color='UF_UDM', barmode='group',
                            histnorm='percent',
                            title="Uso de Álcool/Drogas por Estado (Percentual)",
                            labels={'alcool_drogas': 'Álcool/Drogas', 'count': 'Percentual'},
                            text_auto=True)
        fig4.update_traces(textposition='auto', texttemplate='%{y:.2f}%', textfont=dict(color='#000000'))
        fig4.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#000000"),
            title=dict(text="Uso de Álcool/Drogas por Estado (Percentual)", font=dict(color="#000000")),
            xaxis=dict(
                title=dict(text="Álcool/Drogas", font=dict(color="#000000")),
                tickfont=dict(color="#000000")
            ),
            yaxis=dict(
                title=dict(text="Percentual", font=dict(color="#000000")),
                tickfont=dict(color="#000000")
            )
        )
        st.plotly_chart(fig4, use_container_width=True)

    # Nova seção de comparação com valores brutos
    st.subheader("Visualizações (Valores Brutos)")
    col5, col6 = st.columns(2)
    with col5:
        st.markdown("#### Distribuição por Grupo Populacional (Bruto)")
        fig5 = px.histogram(df_filtrado, x='Pop', color='UF_UDM', barmode='group',
                            labels={'Pop': 'Grupo Populacional', 'count': 'Quantidade'},
                            title="Grupos Populacionais por Estado (Bruto)",
                            category_orders={'Pop': sorted(df_filtrado['Pop'].dropna().unique())},
                            text_auto=True)
        fig5.update_traces(textposition='auto', texttemplate='%{y}', textfont=dict(color='#000000'))
        fig5.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#000000"),
            title=dict(text="Grupos Populacionais por Estado (Bruto)", font=dict(color="#000000")),
            xaxis=dict(
                title=dict(text="Grupo Populacional", font=dict(color="#000000")),
                tickfont=dict(color="#000000")
            ),
            yaxis=dict(
                title=dict(text="Quantidade", font=dict(color="#000000")),
                tickfont=dict(color="#000000")
            )
        )
        st.plotly_chart(fig5, use_container_width=True)

    with col6:
        st.markdown("#### Tipo de Exposição (Bruto)")
        fig6 = px.histogram(df_filtrado, x='tipo_exposicao', color='UF_UDM', barmode='group',
                            labels={'tipo_exposicao': 'Tipo de Exposição', 'count': 'Quantidade'},
                            title="Tipo de Exposição por Estado (Bruto)",
                            text_auto=True)
        fig6.update_traces(textposition='auto', texttemplate='%{y}', textfont=dict(color='#000000'))
        fig6.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#000000"),
            title=dict(text="Tipo de Exposição por Estado (Bruto)", font=dict(color="#000000")),
            xaxis=dict(
                title=dict(text="Tipo de Exposição", font=dict(color="#000000")),
                tickfont=dict(color="#000000")
            ),
            yaxis=dict(
                title=dict(text="Quantidade", font=dict(color="#000000")),
                tickfont=dict(color="#000000")
            )
        )
        st.plotly_chart(fig6, use_container_width=True)

    # Download de dados filtrados
    st.subheader("Exportar Dados")
    st.markdown(download_csv(df_filtrado, "dados_filtrados_pep"), unsafe_allow_html=True)

# Página PrEP
elif menu == "🔒 PrEP":
    st.title("🔒 Análise de PrEP")
    st.markdown("""
    Esta seção está em desenvolvimento. Futuramente, será possível visualizar e comparar a distribuição da **Profilaxia Pré-Exposição (PrEP)** nos estados da Bahia (BA) e Rio de Janeiro (RJ).
    """)
    st.info("Aguarde atualizações para explorar os dados de PrEP!")