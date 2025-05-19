import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import base64
import os
import time

# Configuração da página
st.set_page_config(layout="wide", page_title="Dashboard PEP & PrEP LGBT", initial_sidebar_state="expanded")

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

# Função para download de dados filtrados
def download_csv(df, filename):
    csv = df.to_csv(index=False, encoding='utf-8-sig')
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">Download CSV</a>'
    return href

# Função para carregar dados PEP com colunas específicas
@st.cache_data(ttl=86400)
def carregar_dados_pep(data_inicio, data_fim, estados):
    file_path = os.path.join("data", "data.xlsx")
    if not os.path.exists(file_path):
        st.error(f"Arquivo '{file_path}' não encontrado no servidor.")
        return None
    try:
        with st.spinner("Carregando dados PEP..."):
            start_time = time.time()
            df = pd.read_excel(file_path, sheet_name="Banco_PEP_UDM", 
                              usecols=['dt_disp', 'UF_UDM', 'Pop', 'tipo_exposicao', 'trabalho_sexual', 'alcool_drogas'])
            if df.empty:
                st.error("O arquivo de dados PEP está vazio.")
                return None
            df['dt_disp'] = pd.to_datetime(df['dt_disp'], errors='coerce')
            # Filtrar dados
            df = df[
                (df['UF_UDM'].isin(estados)) &
                (df['dt_disp'].dt.date >= data_inicio) &
                (df['dt_disp'].dt.date <= data_fim)
            ].copy()
            return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados PEP: {str(e)}")
        return None

# Função para carregar dados PrEP com colunas específicas
@st.cache_data(ttl=86400)
def carregar_dados_prep(data_inicio, data_fim, estados):
    file_path = os.path.join("data", "data.xlsx")
    if not os.path.exists(file_path):
        st.error(f"Arquivo '{file_path}' não encontrado no servidor.")
        return None
    try:
        with st.spinner("Carregando dados PrEP..."):
            start_time = time.time()
            df = pd.read_excel(file_path, sheet_name="Banco_PrEP_UDM", 
                              usecols=['dt_disp', 'UF_UDM', 'tp_servico_atendimento', 'tp_esquema_prep', 'tp_testagem_hiv', 'IST_autorrelato'])
            if df.empty:
                st.error("O arquivo de dados PrEP está vazio.")
                return None
            df['dt_disp'] = pd.to_datetime(df['dt_disp'], errors='coerce')
            # Filtrar dados
            df = df[
                (df['UF_UDM'].isin(estados)) &
                (df['dt_disp'].dt.date >= data_inicio) &
                (df['dt_disp'].dt.date <= data_fim)
            ].copy()
            return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados PrEP: {str(e)}")
        return None


# Sidebar com navegação e filtros
st.sidebar.title("Navegação e Filtros")
menu = st.sidebar.radio("Selecione a Página", ["🏠 Home", "💉 PEP", "🔒 PrEP"])

# Filtros globais
st.sidebar.header("Filtros")
estados = st.sidebar.multiselect("Estados", options=['BA', 'RJ'], default=['BA', 'RJ'])

# Função para determinar o intervalo de datas com base nos dados
def get_date_range(df_func, *args):
    df = df_func(*args)
    if df is not None and not df.empty:
        min_date = df['dt_disp'].min().date()
        max_date = df['dt_disp'].max().date()
        return min_date, max_date
    return datetime(2020, 1, 1).date(), datetime(2025, 5, 19).date()  # Fallback caso os dados estejam vazios

# Inicializar datas com base na aba selecionada (ajustado dinamicamente)
if menu == "💉 PEP":
    min_date, max_date = get_date_range(carregar_dados_pep, None, None, estados)
    data_inicio = st.sidebar.date_input("Data de Início", value=min_date, min_value=min_date, max_value=max_date)
    data_fim = st.sidebar.date_input("Data de Fim", value=max_date, min_value=min_date, max_value=max_date)
elif menu == "🔒 PrEP":
    min_date, max_date = get_date_range(carregar_dados_prep, None, None, estados)
    data_inicio = st.sidebar.date_input("Data de Início", value=min_date, min_value=min_date, max_value=max_date)
    data_fim = st.sidebar.date_input("Data de Fim", value=max_date, min_value=min_date, max_value=max_date)
else:  # Home
    # Fallback para Home (pode ser ajustado conforme necessário)
    data_inicio = st.sidebar.date_input("Data de Início", value=None)
    data_fim = st.sidebar.date_input("Data de Fim", value=None)

# Página Home
if menu == "🏠 Home":
    st.title("Dashboard PEP & PrEP LGBT")
    st.markdown("""
    Este painel interativo tem como objetivo **visualizar e comparar a distribuição da Profilaxia Pós-Exposição (PEP) e Profilaxia Pré-Exposição (PrEP)** 
    entre populações vulneráveis nos estados da **Bahia (BA)** e do **Rio de Janeiro (RJ)**.

    ---
    ### Objetivos:
    - Facilitar a análise do acesso à PEP e PrEP entre grupos populacionais.
    - Comparar comportamentos entre estados.
    - Contribuir com políticas públicas voltadas à população LGBTQIAPN+.

    ### Contexto dos Dados
    - **Por que BA x RJ?** Bahia (BA) e Rio de Janeiro (RJ) foram escolhidos por terem populações semelhantes (aproximadamente 14,8 milhões em BA e 16,7 milhões em RJ, segundo o IBGE 2025).
    - **Desequilíbrio nos Dados**: Apesar das populações similares, 90% dos dados são do RJ e apenas 10% da BA. Isso pode ser devido à:
      - **Área Geográfica**: A BA é muito maior (565.000 km² vs. 43.780 km² do RJ), com áreas rurais que dificultam a coleta de dados e a dispersão.
      - **Acesso à Saúde**: O RJ tem maior concentração urbana e infraestrutura de saúde, o que pode facilitar a distribuição e o registro.
      - **Coleta de Dados**: Os dados são coletados pela ANS, que pode ter melhor cobertura em áreas urbanas como o RJ.

    ### Possíveis Explicações para o Desequilíbrio
    - **Menor Dispersão na BA**: Pode haver menos acesso ou conscientização sobre PEP na BA, especialmente em áreas rurais.
    - **Desafios na Coleta de Dados**: A ANS pode ter coletado menos dados da BA devido a diferenças na infraestrutura de saúde ou nos processos de reporte.
    - **Recomendação**: Considere ambos os fatores ao interpretar os dados. Mais dados da BA podem ser necessários para uma análise completa.

    ### Próximos Passos
    - **Melhorar a Coleta de Dados**: Trabalhar com a ANS e o SUS para aumentar a cobertura de dados na BA, especialmente em áreas rurais.
    - **Expandir o Acesso à dispensação na BA**: Implementar programas de conscientização e distribuição em regiões menos atendidas da BA.
    - **Pesquisa Adicional**: Conduzir estudos para entender as barreiras ao acesso na BA e melhorar as políticas públicas.
    """)

# Página PEP
elif menu == "💉 PEP":
    st.title("📊 Análise Comparativa da Dispersão de PEP - BA x RJ")
    st.warning("Os dados foram coletados pela **Agência Nacional de Saúde (ANS)** e representam 90% de registros do RJ e apenas 10% da BA, o que pode impactar as comparações. Use os dados da BA com cautela devido ao tamanho limitado da amostra.")
    st.markdown("""
    🔗 **Fonte dos Dados**: [PEP - Profilaxia Pós-Exposição ao HIV](https://www.gov.br/aids/pt-br/indicadores-epidemiologicos/painel-de-monitoramento/painel-pep)
    """, unsafe_allow_html=True)

    # Definir intervalo de datas com base nos dados PEP
    df = carregar_dados_pep(data_inicio, data_fim, estados)
    if df is None or df.empty:
        st.warning("Nenhum dado disponível com os filtros selecionados.")
        st.stop()

    # Métricas resumidas
    st.subheader("Resumo dos Dados")
    col1, col2, col3 = st.columns(3)
    with col1:
        total_registros = len(df)
        st.markdown(f"<div class='metric-card'><strong>Total de Registros</strong><br>{total_registros}</div>", unsafe_allow_html=True)
    with col2:
        total_ba = len(df[df['UF_UDM'] == 'BA'])
        percent_ba = round((total_ba / total_registros * 100), 2) if total_registros > 0 else 0
        st.markdown(f"<div class='metric-card'><strong>Total BA</strong><br>{total_ba} ({percent_ba}%)</div>", unsafe_allow_html=True)
    with col3:
        total_rj = len(df[df['UF_UDM'] == 'RJ'])
        percent_rj = round((total_rj / total_registros * 100), 2) if total_registros > 0 else 0
        st.markdown(f"<div class='metric-card'><strong>Total RJ</strong><br>{total_rj} ({percent_rj}%)</div>", unsafe_allow_html=True)

    # Visualizações com percentuais
    st.subheader("Visualizações (Percentuais)")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Distribuição por Grupo Populacional")
        fig1 = px.histogram(df, x='Pop', color='UF_UDM', barmode='group',
                            histnorm='percent',
                            labels={'Pop': 'Grupo Populacional', 'count': 'Percentual'},
                            title="Grupos Populacionais por Estado (Percentual)",
                            category_orders={'Pop': sorted(df['Pop'].dropna().unique())},
                            text_auto=True)
        fig1.update_traces(textposition='auto', texttemplate='%{y:.2f}%', textfont=dict(color='#000000'))
        fig1.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#000000"),
            title=dict(text="Grupos Populacionais por Estado (Percentual)", font=dict(color="#000000")),
            xaxis=dict(title=dict(text="Grupo Populacional", font=dict(color="#000000")), tickfont=dict(color="#000000")),
            yaxis=dict(title=dict(text="Percentual", font=dict(color="#000000")), tickfont=dict(color="#000000"))
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.markdown("#### Tipo de Exposição")
        fig2 = px.histogram(df, x='tipo_exposicao', color='UF_UDM', barmode='group',
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
            xaxis=dict(title=dict(text="Tipo de Exposição", font=dict(color="#000000")), tickfont=dict(color="#000000")),
            yaxis=dict(title=dict(text="Percentual", font=dict(color="#000000")), tickfont=dict(color="#000000"))
        )
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("#### Trabalho Sexual")
        fig3 = px.histogram(df, x='trabalho_sexual', color='UF_UDM', barmode='group',
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
            xaxis=dict(title=dict(text="Trabalho Sexual", font=dict(color="#000000")), tickfont=dict(color="#000000")),
            yaxis=dict(title=dict(text="Percentual", font=dict(color="#000000")), tickfont=dict(color="#000000"))
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown("#### Uso de Álcool/Drogas")
        fig4 = px.histogram(df, x='alcool_drogas', color='UF_UDM', barmode='group',
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
            xaxis=dict(title=dict(text="Álcool/Drogas", font=dict(color="#000000")), tickfont=dict(color="#000000")),
            yaxis=dict(title=dict(text="Percentual", font=dict(color="#000000")), tickfont=dict(color="#000000"))
        )
        st.plotly_chart(fig4, use_container_width=True)

    # Visualizações com valores brutos
    st.subheader("Visualizações (Valores Brutos)")
    col5, col6 = st.columns(2)
    with col5:
        st.markdown("#### Distribuição por Grupo Populacional (Bruto)")
        fig5 = px.histogram(df, x='Pop', color='UF_UDM', barmode='group',
                            labels={'Pop': 'Grupo Populacional', 'count': 'Quantidade'},
                            title="Grupos Populacionais por Estado (Bruto)",
                            category_orders={'Pop': sorted(df['Pop'].dropna().unique())},
                            text_auto=True)
        fig5.update_traces(textposition='auto', texttemplate='%{y}', textfont=dict(color='#000000'))
        fig5.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#000000"),
            title=dict(text="Grupos Populacionais por Estado (Bruto)", font=dict(color="#000000")),
            xaxis=dict(title=dict(text="Grupo Populacional", font=dict(color="#000000")), tickfont=dict(color="#000000")),
            yaxis=dict(title=dict(text="Quantidade", font=dict(color="#000000")), tickfont=dict(color="#000000"))
        )
        st.plotly_chart(fig5, use_container_width=True)

    with col6:
        st.markdown("#### Tipo de Exposição (Bruto)")
        fig6 = px.histogram(df, x='tipo_exposicao', color='UF_UDM', barmode='group',
                            labels={'tipo_exposicao': 'Tipo de Exposição', 'count': 'Quantidade'},
                            title="Tipo de Exposição por Estado (Bruto)",
                            text_auto=True)
        fig6.update_traces(textposition='auto', texttemplate='%{y}', textfont=dict(color='#000000'))
        fig6.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#000000"),
            title=dict(text="Tipo de Exposição por Estado (Bruto)", font=dict(color="#000000")),
            xaxis=dict(title=dict(text="Tipo de Exposição", font=dict(color="#000000")), tickfont=dict(color="#000000")),
            yaxis=dict(title=dict(text="Quantidade", font=dict(color="#000000")), tickfont=dict(color="#000000"))
        )
        st.plotly_chart(fig6, use_container_width=True)

    # Download de dados filtrados
    st.subheader("Exportar Dados")
    st.markdown(download_csv(df, "dados_filtrados_pep"), unsafe_allow_html=True)

# Página PrEP
elif menu == "🔒 PrEP":
    st.title("📊 Análise Comparativa da Dispersão de PrEP - BA x RJ")
    st.warning("Os dados foram coletados pela **Agência Nacional de Saúde (ANS)** e representam 80% de registros do RJ e apenas 20% da BA, o que pode impactar as comparações. Use os dados da BA com cautela devido ao tamanho limitado da amostra.")
    st.markdown("""
    🔗 **Fonte dos Dados**: [PrEP - Profilaxia Pré-Exposição ao HIV](https://www.gov.br/aids/pt-br/indicadores-epidemiologicos/painel-de-monitoramento/painel-prep)
    """, unsafe_allow_html=True)

    # Definir intervalo de datas com base nos dados PrEP
    df = carregar_dados_prep(data_inicio, data_fim, estados)
    if df is None or df.empty:
        st.warning("Nenhum dado disponível com os filtros selecionados.")
        st.stop()

    # Métricas resumidas
    st.subheader("Resumo dos Dados")
    col1, col2, col3 = st.columns(3)
    with col1:
        total_registros = len(df)
        st.markdown(f"<div class='metric-card'><strong>Total de Registros</strong><br>{total_registros}</div>", unsafe_allow_html=True)
    with col2:
        total_ba = len(df[df['UF_UDM'] == 'BA'])
        percent_ba = round((total_ba / total_registros * 100), 2) if total_registros > 0 else 0
        st.markdown(f"<div class='metric-card'><strong>Total BA</strong><br>{total_ba} ({percent_ba}%)</div>", unsafe_allow_html=True)
    with col3:
        total_rj = len(df[df['UF_UDM'] == 'RJ'])
        percent_rj = round((total_rj / total_registros * 100), 2) if total_registros > 0 else 0
        st.markdown(f"<div class='metric-card'><strong>Total RJ</strong><br>{total_rj} ({percent_rj}%)</div>", unsafe_allow_html=True)

    st.subheader("Visualizações (Percentuais)")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Tipo de Serviço de Atendimento")
        fig1 = px.histogram(df, x='tp_servico_atendimento', color='UF_UDM', barmode='group',
                            histnorm='percent',
                            labels={'tp_servico_atendimento': 'Tipo de Serviço', 'count': 'Percentual'},
                            title="Tipo de Serviço por Estado (Percentual)",
                            text_auto=True)
        fig1.update_traces(textposition='auto', texttemplate='%{y:.2f}%')
        fig1.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="#000000",
            xaxis=dict(title=dict(text="Tipo de Serviço", font=dict(color="#000000")), tickfont=dict(color="#000000")),
            yaxis=dict(title=dict(text="Percentual", font=dict(color="#000000")), tickfont=dict(color="#000000"))
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.markdown("#### Tipo de Esquema PrEP")
        fig2 = px.histogram(df, x='tp_esquema_prep', color='UF_UDM', barmode='group',
                            histnorm='percent',
                            labels={'tp_esquema_prep': 'Esquema PrEP', 'count': 'Percentual'},
                            title="Esquema PrEP por Estado (Percentual)",
                            text_auto=True)
        fig2.update_traces(textposition='auto', texttemplate='%{y:.2f}%')
        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="#000000",
            xaxis=dict(title=dict(text="Esquema PrEP", font=dict(color="#000000")), tickfont=dict(color="#000000")),
            yaxis=dict(title=dict(text="Percentual", font=dict(color="#000000")), tickfont=dict(color="#000000"))
        )
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("#### Tipo de Testagem HIV")
        fig3 = px.histogram(df, x='tp_testagem_hiv', color='UF_UDM', barmode='group',
                            histnorm='percent',
                            title="Testagem HIV por Estado (Percentual)",
                            labels={'tp_testagem_hiv': 'Testagem HIV', 'count': 'Percentual'},
                            text_auto=True)
        fig3.update_traces(textposition='auto', texttemplate='%{y:.2f}%')
        fig3.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="#000000",
            xaxis=dict(title=dict(text="Testagem HIV", font=dict(color="#000000")), tickfont=dict(color="#000000")),
            yaxis=dict(title=dict(text="Percentual", font=dict(color="#000000")), tickfont=dict(color="#000000"))
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown("#### IST Autorrelatada")
        fig4 = px.histogram(df, x='IST_autorrelato', color='UF_UDM', barmode='group',
                            histnorm='percent',
                            title="IST Autorrelatada por Estado (Percentual)",
                            labels={'IST_autorrelato': 'IST Autorrelatada', 'count': 'Percentual'},
                            text_auto=True)
        fig4.update_traces(textposition='auto', texttemplate='%{y:.2f}%')
        fig4.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="#000000",
            xaxis=dict(title=dict(text="IST Autorrelatada", font=dict(color="#000000")), tickfont=dict(color="#000000")),
            yaxis=dict(title=dict(text="Percentual", font=dict(color="#000000")), tickfont=dict(color="#000000"))
        )
        st.plotly_chart(fig4, use_container_width=True)

    # Visualizações com valores brutos
    st.subheader("Visualizações (Valores Brutos)")
    col5, col6 = st.columns(2)
    with col5:
        st.markdown("#### Tipo de Serviço de Atendimento (Bruto)")
        fig5 = px.histogram(df, x='tp_servico_atendimento', color='UF_UDM', barmode='group',
                            labels={'tp_servico_atendimento': 'Tipo de Serviço', 'count': 'Quantidade'},
                            title="Tipo de Serviço por Estado (Bruto)",
                            text_auto=True)
        fig5.update_traces(textposition='auto', texttemplate='%{y}')
        fig5.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="#000000",
            xaxis=dict(title=dict(text="Tipo de Serviço", font=dict(color="#000000")), tickfont=dict(color="#000000")),
            yaxis=dict(title=dict(text="Quantidade", font=dict(color="#000000")), tickfont=dict(color="#000000"))
        )
        st.plotly_chart(fig5, use_container_width=True)

    with col6:
        st.markdown("#### Tipo de Esquema PrEP (Bruto)")
        fig6 = px.histogram(df, x='tp_esquema_prep', color='UF_UDM', barmode='group',
                            labels={'tp_esquema_prep': 'Esquema PrEP', 'count': 'Quantidade'},
                            title="Esquema PrEP por Estado (Bruto)",
                            text_auto=True)
        fig6.update_traces(textposition='auto', texttemplate='%{y}')
        fig6.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="#000000",
            xaxis=dict(title=dict(text="Esquema PrEP", font=dict(color="#000000")), tickfont=dict(color="#000000")),
            yaxis=dict(title=dict(text="Quantidade", font=dict(color="#000000")), tickfont=dict(color="#000000"))
        )
        st.plotly_chart(fig6, use_container_width=True)

    # Download de dados filtrados
    st.subheader("Exportar Dados")
    st.markdown(download_csv(df, "dados_filtrados_prep"), unsafe_allow_html=True)