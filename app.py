import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================
st.set_page_config(
    page_title="Corridas Strava",
    page_icon="🏃",
    layout="wide"
)

st.markdown("""
    <style>
        .metric-card {
            background-color: #f9f9f9;
            border-left: 5px solid #FC4C02;
            padding: 16px 20px;
            border-radius: 8px;
        }
        .metric-label {
            font-size: 13px;
            color: #888;
            margin-bottom: 4px;
        }
        .metric-value {
            font-size: 32px;
            font-weight: bold;
            color: #FC4C02;
        }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# LEITURA DA GOOGLE SHEET
# =========================================================
SHEET_ID = "1ObyAjbGdnlv0Jbi-ZrkgA5crMFvDBWA_"
ABA = "strava_corridas_usar"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={ABA}"

@st.cache_data(ttl=300)
def carregar_dados():
    df = pd.read_csv(URL, decimal=",")
    return df

df = carregar_dados()
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
dados_texto = df.to_string(index=False)

contexto = f"""
Você é um assistente analítico especializado em corrida e visualização de dados.

O usuário está analisando um dashboard Streamlit contendo:
- total de corridas
- distância por ano
- duração total
- pace médio
- evolução temporal das atividades

Regras:
- Nunca liste todos os valores numéricos brutos
- Forneça respostas resumidas e interpretativas
- Sempre priorize síntese ao invés de cálculos detalhados
- Use apenas os dados fornecidos
- Não invente informações
- Seja claro e objetivo
- Responda em português
- Caso a resposta não esteja nos dados, diga isso claramente

Dados:
{dados_texto}
"""

# =========================================================
# TÍTULO
# =========================================================
st.title("🏃 Dashboard de Corridas — Strava")
st.caption("Fonte: Strava via Google Sheets · atualizado automaticamente")
st.divider()

# =========================================================
# SCORECARDS
# =========================================================
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total de Corridas</div>
            <div class="metric-value">{len(df)}</div>
        </div>
    """, unsafe_allow_html=True)

with c2:
    total_km = df["Distancia_km"].sum()
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Distância Total (km)</div>
            <div class="metric-value">{total_km:,.1f}</div>
        </div>
    """, unsafe_allow_html=True)

with c3:
    total_min = df["Duracao_min"].sum()
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Duração Total (min)</div>
            <div class="metric-value">{total_min:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

with c4:
    pace_medio = df["Pace_min_km"].mean()
    pace_int = int(pace_medio)
    pace_seg = int((pace_medio - pace_int) * 60)
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Pace Médio (min/km)</div>
            <div class="metric-value">{pace_int}:{pace_seg:02d}</div>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# =========================================================
# GRÁFICOS — linha 1
# =========================================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("Corridas por Ano")
    corridas_por_ano = df.groupby("Ano").size().reset_index(name="Total")
    fig1 = px.bar(corridas_por_ano, x="Ano", y="Total", text="Total",
                  color_discrete_sequence=["#FC4C02"])
    fig1.update_traces(textposition="outside")
    fig1.update_layout(plot_bgcolor="white", showlegend=False,
                       xaxis_title="Ano", yaxis_title="Corridas")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Distância por Ano (km)")
    dist_ano = df.groupby("Ano")["Distancia_km"].sum().reset_index()
    fig2 = px.line(dist_ano, x="Ano", y="Distancia_km", markers=True,
                   color_discrete_sequence=["#FC4C02"])
    fig2.update_traces(line_width=3, marker_size=8)
    fig2.update_layout(plot_bgcolor="white", showlegend=False,
                       xaxis_title="Ano", yaxis_title="km")
    st.plotly_chart(fig2, use_container_width=True)

# =========================================================
# GRÁFICOS — linha 2
# =========================================================
col3, col4 = st.columns(2)

with col3:
    st.subheader("Duração Total por Ano (min)")
    dur_ano = df.groupby("Ano")["Duracao_min"].sum().reset_index()
    fig3 = px.bar(dur_ano, x="Ano", y="Duracao_min", text="Duracao_min",
                  color_discrete_sequence=["#FC4C02"])
    fig3.update_traces(textposition="outside", texttemplate="%{text:,.0f}")
    fig3.update_layout(plot_bgcolor="white", showlegend=False,
                       xaxis_title="Ano", yaxis_title="minutos")
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("Pace Médio por Ano (min/km)")
    pace_ano = df.groupby("Ano")["Pace_min_km"].mean().reset_index()
    fig4 = px.line(pace_ano, x="Ano", y="Pace_min_km", markers=True,
                   color_discrete_sequence=["#FC4C02"])
    fig4.update_traces(line_width=3, marker_size=8)
    fig4.update_layout(plot_bgcolor="white", showlegend=False,
                       xaxis_title="Ano", yaxis_title="min/km",
                       yaxis_autorange="reversed")
    st.plotly_chart(fig4, use_container_width=True)

st.divider()
st.subheader("💬 Converse com os dados")
pergunta = st.chat_input("Faça uma pergunta sobre os dados...")

if pergunta:

    prompt_final = contexto + f"\n\nPergunta do usuário:\n{pergunta}"

    resposta = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt_final
    )

    st.chat_message("user").write(pergunta)
    st.chat_message("assistant").write(resposta.text)

#st.write(df.head())
