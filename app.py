import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================
st.set_page_config(
    page_title="Corridas Strava",
    page_icon="🏃",
    layout="centered"
)

# =========================================================
# LEITURA DA GOOGLE SHEET
# =========================================================
SHEET_ID = "1ObyAjbGdnlv0Jbi-ZrkgA5crMFvDBWA_"
ABA = "strava_corridas_usar"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={ABA}"

@st.cache_data(ttl=300)  # atualiza a cada 5 minutos
def carregar_dados():
    df = pd.read_csv(URL)
    return df

df = carregar_dados()

# =========================================================
# GRÁFICO: CORRIDAS POR ANO
# =========================================================
st.title("🏃 Corridas por Ano")

corridas_por_ano = df.groupby("Ano").size().reset_index(name="Total")

fig = px.bar(
    corridas_por_ano,
    x="Ano",
    y="Total",
    text="Total",
    color_discrete_sequence=["#FC4C02"]  # laranja Strava
)

fig.update_traces(textposition="outside")
fig.update_layout(
    xaxis_title="Ano",
    yaxis_title="Número de Corridas",
    plot_bgcolor="white",
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# =========================================================
# GRÁFICO: DISTÂNCIA TOTAL POR ANO
# =========================================================
st.title("📏 Distância por Ano (km)")

distancia_por_ano = df.groupby("Ano")["Distancia_km"].sum().reset_index()

fig2 = px.line(
    distancia_por_ano,
    x="Ano",
    y="Distancia_km",
    markers=True,
    color_discrete_sequence=["#FC4C02"]
)

fig2.update_traces(line_width=3, marker_size=8)
fig2.update_layout(
    xaxis_title="Ano",
    yaxis_title="Distância Total (km)",
    plot_bgcolor="white",
    showlegend=False
)

st.plotly_chart(fig2, use_container_width=True)

st.caption("Fonte: Strava via Google Sheets · atualizado automaticamente")
