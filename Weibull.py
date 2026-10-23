import streamlit as st 

import numpy as np 

from scipy.stats import weibull_min 

import plotly.graph_objects as go 

 

# Configuração da página do Streamlit 

st.set_page_config(page_title="Análise de Weibull Interativa", layout="wide") 

 

st.title("📊 Painel Dinâmico Interativo: Distribuição de Weibull") 

st.markdown("Passe o mouse sobre os gráficos para ativar o cursor em cruz e ler os valores de X e Y.") 

 

# --- BARRA LATERAL PARA ENTRADA DE PARÂMETROS --- 

st.sidebar.header("⚙️ Parâmetros de Entrada") 

 

beta = st.sidebar.slider( 

    label="Parâmetro de Forma (β - Shape)", 

    min_value=0.5, 

    max_value=10.0, 

    value=1.50, 

    step=0.25 

) 

 

eta = st.sidebar.slider( 

    label="Parâmetro de Escala (η - Scale)", 

    min_value=1.0, 

    max_value=500.0, 

    value=90.0, 

    step=1.0 

) 

 

n_amostra = st.sidebar.number_input( 

    label="Tamanho da Amostra (N)", 

    min_value=25, 

    max_value=10000, 

    value=1000, 

    step=25 

) 



st.sidebar.markdown(
    "**Desenvolvido por:**  \n"
    "Eng. Mecânico Gabriel Ramos"
)

st.sidebar.divider()
 

# --- PROCESSAMENTO DOS DADOS --- 

tempo_max_dinamico = float(weibull_min.ppf(0.995, c=beta, scale=eta)) 

tempo = np.linspace(0.001, tempo_max_dinamico, 1000) 

 

pdf = weibull_min.pdf(tempo, c=beta, scale=eta) 

confiabilidade = weibull_min.sf(tempo, c=beta, scale=eta) 

cdf_teorica = weibull_min.cdf(tempo, c=beta, scale=eta) 

 

np.random.seed(42) 

dados_simulados = weibull_min.rvs(c=beta, scale=eta, size=n_amostra) 

dados_ordenados = np.sort(dados_simulados) 

y_empirico = np.arange(1, n_amostra + 1) / n_amostra * 100 

 

 

# --- CONFIGURAÇÃO PADRÃO DO CURSOR EM CRUZ (CROSSHAIR) DO PLOTLY --- 

def aplicar_cursor_em_cruz(fig): 

    fig.update_xaxes( 

        showspikes=True, spikecolor="gray", spikethickness=1, 

        spikedash="dash", spikemode="across" 

    ) 

    fig.update_yaxes( 

        showspikes=True, spikecolor="gray", spikethickness=1, 

        spikedash="dash", spikemode="across" 

    ) 

    fig.update_layout( 

        hovermode="x unified",  # Agrupa os dados do ponto no eixo X 

        template="plotly_white", 

        margin=dict(l=50, r=50, t=50, b=50) 

    ) 

 

 

# --- CRIANDO AS ABAS --- 

aba1, aba2, aba3 = st.tabs([ 

    "📈 Densidade de Probabilidade f(t)", 

    "🛡️ Curva de Confiabilidade R(t)", 

    "📊 FDA Empírica vs Teórica" 

]) 

 

# --- ABA 1: PDF INTERATIVA --- 

with aba1: 

    fig1 = go.Figure() 

    fig1.add_trace(go.Scatter( 

        x=tempo, y=pdf, mode='lines', name='Densidade f(t)', 

        line=dict(color='#1f77b4', width=2.5), 

        fill='tozeroy', fillcolor='rgba(31, 119, 180, 0.1)' 

    )) 

    fig1.update_layout( 

        title="<b>Função de Densidade de Probabilidade - f(t)</b>", 

        xaxis_title="Tempo (Dias)", yaxis_title="Densidade" 

    ) 

    aplicar_cursor_em_cruz(fig1) 

 

    # Controle de escala Y inteligente para beta < 1 

    if beta < 1: 

        t_corte = weibull_min.ppf(0.02, c=beta, scale=eta) 

        y_max = weibull_min.pdf(t_corte, c=beta, scale=eta) 

        fig1.update_yaxes(range=[0, y_max * 1.5]) 

 

    st.plotly_chart(fig1, use_container_width=True) 

 

# --- ABA 2: CONFIABILIDADE INTERATIVA --- 

with aba2: 

    fig2 = go.Figure() 

    fig2.add_trace(go.Scatter( 

        x=tempo, y=confiabilidade, mode='lines', name='Confiabilidade R(t)', 

        line=dict(color='#2ca02c', width=2.5), 

        fill='tozeroy', fillcolor='rgba(44, 160, 44, 0.1)' 

    )) 

    fig2.update_layout( 

        title="<b>Curva de Confiabilidade (Sobrevivência) - R(t)</b>", 

        xaxis_title="Tempo (Dias)", yaxis_title="Confiabilidade R(t)" 

    ) 

    aplicar_cursor_em_cruz(fig2) 

    fig2.update_yaxes(range=[-0.02, 1.02]) 

 

    st.plotly_chart(fig2, use_container_width=True) 

 

# --- ABA 3: FDA EMPÍRICA VS TEÓRICA INTERATIVA (ESTILO MINITAB) --- 

with aba3: 

    fig3 = go.Figure() 

    # Linha empírica em formato de escada (line_shape='hv') 

    fig3.add_trace(go.Scatter( 

        x=dados_ordenados, y=y_empirico, mode='lines', line_shape='hv', 

        name='Empírica', line=dict(color='#b0bec5', width=1.5) 

    )) 

    # Linha teórica ajustada 

    fig3.add_trace(go.Scatter( 

        x=tempo, y=cdf_teorica * 100, mode='lines', 

        name='Weibull', line=dict(color='#b71c1c', width=2.5) 

    )) 

 

    fig3.update_layout( 

        title="<b>FDA Empírica de Dias até a falha<br>Distribuição de Weibull</b>", 

        xaxis_title="Dias até a falha", yaxis_title="Percentual (%)" 

    ) 

    aplicar_cursor_em_cruz(fig3) 

    fig3.update_yaxes(range=[-5, 105]) 

    fig3.update_xaxes(range=[0, tempo_max_dinamico]) 

 

    # Caixa de texto flutuante com os parâmetros estatísticos 

    texto_parametros = f"<b>Forma:</b> {beta:.3f}<br><b>Escala:</b> {eta:.2f}<br><b>N:</b> {n_amostra}" 

    fig3.add_annotation( 

        xref="paper", yref="paper", x=0.98, y=0.10, 

        text=texto_parametros, showarrow=False, align="left", 

        bgcolor="rgba(255, 255, 255, 0.9)", bordercolor="gray", borderwidth=1, borderpad=8 

    ) 

 

    st.plotly_chart(fig3, use_container_width=True) 

 

# --- METRICAS ADICIONAIS NO RODAPÉ --- 

st.markdown("---") 

col1, col2, col3 = st.columns(3) 

mttf = weibull_min.mean(c=beta, scale=eta) 

mediana = weibull_min.median(c=beta, scale=eta) 

 

with col1: 

    st.metric(label="Tempo Médio Até a Falha (MTTF)", value=f"{mttf:.2f} Dias") 

with col2: 

    st.metric(label="Vida Mediana (B50)", value=f"{mediana:.2f} Dias") 

with col3: 

    prob_eta = weibull_min.sf(eta, c=beta, scale=eta) * 100 

    st.metric(label="Confiabilidade no tempo t = η", value=f"{prob_eta:.1f}%") 

 

#   streamlit run Weibull.py 
