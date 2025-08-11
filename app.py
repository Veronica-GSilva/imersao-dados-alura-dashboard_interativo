import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# --- Configuração da Página ---
# Define o título da página, o ícone e o layout para ocupar a largura inteira.
st.set_page_config(
    page_title="Análise de Salários na Área de Dados",
    page_icon="📊",
    layout="wide",
)

# --- Carregamento dos dados ---
df = pd.read_csv("https://raw.githubusercontent.com/Veronica-GSilva/imersao-dados-alura-DADOSRAW/refs/heads/main/dados-imersao-final.csv")
# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")

# Filtro de Ano
anos_disponiveis = sorted(df['Ano'].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

# Filtro de Senioridade
senioridades_disponiveis = sorted(df['Senioridade'].unique())
senioridades_selecionadas = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, default=senioridades_disponiveis)

# Filtro por Tipo de Contrato
contratos_disponiveis = sorted(df['Contrato'].unique())
contratos_selecionados = st.sidebar.multiselect("Tipo de Contrato", contratos_disponiveis, default=contratos_disponiveis)

# Filtro por Tamanho da Empresa
tamanhos_disponiveis = sorted(df['Tamanho_Empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_disponiveis, default=tamanhos_disponiveis)

# --- Filtragem do DataFrame ---
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
df_filtrado = df[
    (df['Ano'].isin(anos_selecionados)) &
    (df['Senioridade'].isin(senioridades_selecionadas)) &
    (df['Contrato'].isin(contratos_selecionados)) &
    (df['Tamanho_Empresa'].isin(tamanhos_selecionados))
]

# --- Conteúdo Principal ---
st.title("💰📊Análise de Salários na Área de Dados")
st.markdown("Explore os dados salariais na área de dados nos últimos anos")
st.markdown("Utilize os filtros à esquerda para refinar sua análise.")

# --- Métricas Principais (KPIs) ---
st.subheader("Métricas gerais (Salário anual em USD)")

if not df_filtrado.empty:
    salario_medio = df_filtrado['Usd'].mean()
    salario_maximo = df_filtrado['Usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["Cargo"].mode()[0]
else:
    salario_medio, salario_mediano, salario_maximo, total_registros, cargo_mais_comum = 0, 0, 0, ""

col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário Médio", f"${salario_medio:,.0f}")
col2.metric("Salário Máximo", f"${salario_maximo:,.0f}")
with col3:
    st.markdown("###### Total de Profissionais")
    st.markdown(f"<p style='font-size: 24px;'>{total_registros:,}</p>", unsafe_allow_html=True)
with col4:
    st.markdown("###### Cargo mais frequente:")
    # Quebra o nome do cargo em duas linhas usando <br>
    cargo_formatado = cargo_mais_frequente.replace(" ", "<br>")
    st.markdown(f"<p style='font-size: 24px; line-height: 1.2;'>{cargo_formatado}</p>", unsafe_allow_html=True)



st.markdown("---")

# --- Análises Visuais com Plotly ---
st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('Cargo')['Usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x='Usd',
            y='Cargo',
            orientation='h',
            title="Top 10 cargos por salário médio",
            labels={'Usd': 'Média salarial anual (USD)', 'Cargo': ''}
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='Usd',
            nbins=30,
            title="Distribuição de salários anuais",
        )
        grafico_hist.update_layout(title_x=0,
        xaxis_title="Faixa Salarial (USD)",
        yaxis_title="Quantidade de Profissionais")
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

col_graf3, col_graf4 = st.columns([1, 1.3])

with col_graf3:
    if not df_filtrado.empty:
        Modelo_Trabalho_contagem = df_filtrado['Modelo_Trabalho'].value_counts().reset_index()
        Modelo_Trabalho_contagem.columns = ['Modelo_Trabalho', 'Quantidade']
        grafico_Modelo_Trabalho = px.pie(
            Modelo_Trabalho_contagem,
            names='Modelo_Trabalho',
            values='Quantidade',
            title='Proporção<br> - Modelo de Trabalho',
            hole=0.5
        )
        grafico_Modelo_Trabalho.update_traces(textinfo='percent+label', textfont_size=11)
        grafico_Modelo_Trabalho.update_layout(margin=dict(t=40,b=0,l=0,r=80),title_x=0)
        st.plotly_chart(grafico_Modelo_Trabalho, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")

with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['Cargo'] == 'Data Scientist']
        media_ds_pais = df_ds.groupby('Residencia_ISO3')['Usd'].mean().reset_index()

        # Criar o globo
        grafico_paises = px.choropleth(
            media_ds_pais,
            locations='Residencia_ISO3',
            color='Usd',
            color_continuous_scale='rdylgn',
            title='Salário médio de Cientista de Dados<br>- Por País',
            labels={'Usd': 'Salário Médio (USD)', 'Residencia_ISO3': 'País'}
        )

        # Configura visual do globo
        grafico_paises.update_geos(
            projection_type="orthographic",
            showcoastlines=True,
            coastlinecolor="white",
            showland=True,
            landcolor="lightgray",
            oceancolor="rgba(0,120,200,0.8)",  # azul translúcido
            showocean=True,
            bgcolor="black"
        )

        # Configura o layout do gráfico (sem animação)
        grafico_paises.update_layout(
            height=500,  # Define uma altura fixa para evitar o corte
            margin=dict(t=80, b=20, l=20, r=20),
            title_x=0,
            paper_bgcolor="white",
            plot_bgcolor="white",
            title_font=dict(size=18, color="black"),
            coloraxis_colorbar=dict(
                title="USD",
                tickfont=dict(color="black"),
                titlefont=dict(color="black")
            )
        )

        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.")


# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")

# Crie uma cópia do dataframe para exibição, com as modificações
df_para_exibir = df_filtrado.drop(columns=['Residencia']) \
                            .rename(columns={'Residencia_ISO3': 'Residência'})

# Exiba o novo dataframe formatado
st.dataframe(df_para_exibir)
