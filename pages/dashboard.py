import pandas as pd
import streamlit as st
import plotly.express as px
import re
import time
import datetime
import numpy as np
import json
from sklearn.linear_model import LinearRegression

import pdfkit
import os
import streamlit as st
import pandas as pd
import numpy as np

from .utils import gerar_relatorio_html, load_previous_data, exportar_pdf


def run():

    def load_previous_data():
        try:
            with open("ticket_count.json", "r") as file:
                data = json.load(file)
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    # Função para salvar os dados se a data no JSON for diferente da data de hoje
    def save_data(total, delta):
        today_date = datetime.datetime.now().strftime("%Y-%m-%d")
        previous_data = load_previous_data()

        # Salvar apenas se a data for diferente
        if previous_data is None or previous_data.get("date") != today_date:
            data = {"date": today_date, "total": int(total), "delta": delta}
            with open("ticket_count.json", "w") as file:
                json.dump(data, file)

    with open(".\\styles\\style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.markdown("<header class='vrheader'>VR BELÉM</header>", unsafe_allow_html=True)

    # Carregar os dados
    df = pd.read_csv(".\\data\\survey_results.csv")
    df = df.drop_duplicates(subset=["ticket_id", "status"])
    df = df.sort_values(by=["ticket_id"]).drop_duplicates(
        subset=["ticket_id"], keep="last"
    )

    # Salvar o DataFrame atualizado de volta para o arquivo CSV
    # df.to_csv('..\\data\\survey_results.csv', index=False)

    df = df[df["type"] != "2"]
    df["createdDate"] = pd.to_datetime(df["createdDate"])
    df["year"] = df["createdDate"].dt.year
    df["month"] = df["createdDate"].dt.month
    df["day"] = df["createdDate"].dt.day
    df["Horas"] = df["createdDate"].dt.hour - 3
    df["minute"] = df["createdDate"].dt.minute
    df["Dia da Semana"] = df["createdDate"].dt.dayofweek
    df["Trimestre"] = df["createdDate"].dt.to_period("Q")

    df_matriz = pd.read_csv(".\\data\\matriz_ids.csv", encoding="utf-8")
    df_matriz["createdDate"] = pd.to_datetime(df_matriz["createdDate"])
    df_matriz["year"] = df_matriz["createdDate"].dt.year
    df_matriz["month"] = df_matriz["createdDate"].dt.month
    df_matriz["day"] = df_matriz["createdDate"].dt.day
    df_matriz["Horas"] = df_matriz["createdDate"].dt.hour - 3
    df_matriz["minute"] = df_matriz["createdDate"].dt.minute
    df_matriz["Dia da Semana"] = df_matriz["createdDate"].dt.dayofweek

    df = df[df["organization"] != "VRBA - SUPERMERCADO HIPERBOM"]

    # Dicionário de substituições
    substituicoes = {
        "VRPA - DISTRIBUIDORA BATISTA - L01- MATRIZ": "VRPA - EXPET",
        "VRPA - MOURAO SUPERMERCADOS (ID151)": "VRPA - MOURAO SUPERMERCADOS",
        "VRPA- SUPERMERCADO BATISTA - L04": "VRPA - SUPERMERCADO BATISTA - L01 - (G5)",
        "VRAP - CENTRAL DA ECONOMIA MACAPA - L01 - (G680)": "VRAP - CENTRAL DA ECONOMIA MACAPA - L02",
        "RVR - VRAP - SUPERMERCADO AP LOC - (G911)": "RVR - VRAP - SUPERMERCADO AP LOC",
        "VRPA - CASAS GAIA SUPERMERCADO - (ID343)": "VRPA - CASAS GAIA SUPERMERCADO",
        "VRPA - ATACAREJO MAMONAS - L01 - (G17)": "VRPA - ATACAREJO MAMONAS",
        "VRPA - SUPERMERCADO BATISTA - L01 - (G5)": "VRPA - SUPERMERCADO BATISTA",
    }

    # Aplicar substituições
    df["organization"] = df["organization"].replace(substituicoes)

    df["month_name"] = df["createdDate"].dt.strftime("%B")

    # pivot_df = df[
    #     df["organization"]
    #     != [
    #         "VRPA - JULINHO MOTO PECAS",
    #         "Unidade Belem",
    #         "Unidade Belem ",
    #         "DALLA - SUPERMERCADO BEIRA RIO",
    #         "VRPA - SANTOS SUPERMERCADO",
    #     ]
    # ]

    pivot_df = df.pivot_table(
        index="organization", columns="month_name", aggfunc="size", fill_value=0
    )

    months_order = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
    ]
    pivot_df = pivot_df.reindex(columns=months_order, fill_value=0)

    pivot_df["Média"] = round(pivot_df.mean(axis=1), 2)
    pivot_df["Total"] = pivot_df.drop(columns="Média").sum(axis=1)

    # Calculando a média diária dos meses
    df_full_months = pivot_df.drop(columns=["Média", "Total"])

    # Preparar os dados para a regressão linear
    X_train = np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]] * df_full_months.shape[0]).T
    y_train = df_full_months[
        [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
        ]
    ].values.T

    # Ajustar a dimensão de y_train
    y_train = y_train.reshape(-1, df_full_months.shape[0])

    model = LinearRegression()
    model.fit(X_train, y_train)

    X_test = np.array([[11]] * df_full_months.shape[0]).T
    predicted_total_Oct = model.predict(X_test)

    # Adicionar previsões ao DataFrame
    pivot_df["Predict. Novembro"] = predicted_total_Oct.flatten()
    pivot_df["Total C/ Predict"] = pivot_df["Total"] + pivot_df["Predict. Novembro"]

    # Formatar a coluna 'Média' para duas casas decimais
    pivot_df["Média"] = pivot_df["Média"].apply(lambda x: f"{x:.2f}")
    pivot_df["Média"] = pivot_df["Média"].astype(float)
    pivot_df = pivot_df.rename(
        columns={
            "January": "Janeiro",
            "February": "Fevereiro",
            "March": "Março",
            "April": "Abril",
            "May": "Maio",
            "June": "Junho",
            "July": "Julho",
            "August": "Agosto",
            "September": "Setembro",
            "October": "Outubro",
            "November": "Novembro",
        }
    )

    pivot_df = pivot_df.rename(index={"organization": "Organização"})

    # drop_list = [
    #     "VRPA - JULINHO MOTO PECAS",
    #     "Unidade Belem",
    #     "Unidade Belem ",
    #     "DALLA - SUPERMERCADO BEIRA RIO",
    #     "VRPA - SANTOS SUPERMERCADO",
    # ]

    # for value in drop_list:
    #     if value in pivot_df["Organização"]:
    #         print(value)
    #         pivot_df = pivot_df.drop([f"{value}"])

    # pivot_df = pivot_df.drop(
    #     [
    #         "VRPA - JULINHO MOTO PECAS",
    #         "Unidade Belem",
    #         "Unidade Belem ",
    #         "DALLA - SUPERMERCADO BEIRA RIO",
    #         "VRPA - SANTOS SUPERMERCADO",
    #     ]
    # )

    def highlight_min(s):
        is_min = (s < s["Média"]) & (s > 0)
        return ["color:red;background-color: orange" if v else "" for v in is_min]

    # Aplicar a função de estilização
    styled_pivot_df = pivot_df.style.apply(highlight_min, axis=1).format(
        {"Média": "{:.2f}", "Predict. Agosto": "{:.2f}"}
    )

    # Função para limpar os nomes das organizações
    def clean_org_name(org_name):
        while re.match(r"^(VRPA|VRAP|VRAM|RVR)\s*-\s*", org_name):
            org_name = re.sub(r"^(VRPA|VRAP|VRAM|RVR)\s*-\s*", "", org_name, count=1)
        org_name = re.sub(r"\s*-\s*L\d+\s*", "", org_name)
        org_name = re.sub(r"\s*-\s*\(G\d+\)\s*", "", org_name)
        org_name = re.sub(r"\s+", " ", org_name).strip()
        org_name = org_name.lower().title()
        return org_name

    df["organization"] = df["organization"].fillna(df["createdBy"])
    df["clean_organization"] = df["organization"].apply(clean_org_name)

    left, mid, mr, right = st.columns([1, 1, 6, 1])

    data_atual = datetime.datetime.now()
    dia1_mes_atual = datetime.date(data_atual.year, data_atual.month, 1)
    dia_atual = data_atual.date()

    meses = [
        "Janeiro",
        "Fevereiro",
        "Março",
        "Abril",
        "Maio",
        "Junho",
        "Julho",
        "Agosto",
        "Setembro",
        "Outubro",
        "Novembro",
        "Dezembro",
    ]

    anos_disponiveis = df["year"].unique()
    anos_disponiveis = sorted(
        anos_disponiveis, reverse=True
    )  # Ordenar do mais recente ao mais antigo

    ano_atual = datetime.datetime.now().year

    #

    ano_selecionado = left.selectbox("Selecione o ano", anos_disponiveis, index=0)
    mes_atual = datetime.datetime.now().month
    mes_selecionado = mid.selectbox("Selecione o mês", meses, index=mes_atual - 1)

    trimestres = [f"{ano_atual}.{i}" for i in range(1, 5)]
    trimestre_atual = (datetime.datetime.now().month - 1) // 3 + 1

    mes_numero = meses.index(mes_selecionado) + 1

    df_mes_selecionado = df[
        (df["year"] == ano_selecionado) & (df["month"] == mes_numero)
    ]
    df_mes_selecionado_matriz = df_matriz[
        (df_matriz["year"] == ano_selecionado) & (df_matriz["month"] == mes_numero)
    ]

    df_mes_selecionado["value_numeric"] = pd.to_numeric(
        df_mes_selecionado["value"], errors="coerce"
    )

    daily_stats = (
        df_mes_selecionado.groupby("day")
        .agg(
            total_atendimentos=("value", "count"),
            total_convertido_por_dia=("value_numeric", lambda x: x.notna().sum()),
            total_nao_convertido_por_dia=("value", lambda x: (x == "S/N").sum()),
            total_resolvidos_na_hora=(
                "resolvedInFirstCall",
                lambda x: (x == True).sum(),
            ),
            total_resolvidos_depois=(
                "resolvedInFirstCall",
                lambda x: (x == False).sum(),
            ),
            notas_positivas=("value_numeric", lambda x: (x >= 7).sum()),
            notas_negativas=("value_numeric", lambda x: (x < 6).sum()),
        )
        .reset_index()
    )

    daily_stats["satisfacao_diaria"] = np.where(
        daily_stats["total_convertido_por_dia"] > 0,
        (daily_stats["notas_positivas"] / daily_stats["total_convertido_por_dia"])
        * 100,
        0,
    )

    daily_stats["conversao_diaria"] = (
        daily_stats["total_convertido_por_dia"] / daily_stats["total_atendimentos"]
    ) * 100

    daily_stats_analyst = (
        df_mes_selecionado.groupby(["analyst", "day"])
        .agg(
            total_atendimentos=("value", "count"),
            total_convertido_por_dia=("value_numeric", lambda x: x.notna().sum()),
            total_nao_convertido_por_dia=("value", lambda x: (x == "S/N").sum()),
            total_resolvidos_na_hora=(
                "resolvedInFirstCall",
                lambda x: (x == True).sum(),
            ),
            total_resolvidos_depois=(
                "resolvedInFirstCall",
                lambda x: (x == False).sum(),
            ),
            notas_positivas=("value_numeric", lambda x: (x >= 7).sum()),
            notas_negativas=("value_numeric", lambda x: (x < 6).sum()),
        )
        .reset_index()
    )

    daily_stats_analyst["satisfacao_diaria"] = np.where(
        daily_stats_analyst["total_convertido_por_dia"] > 0,
        (
            daily_stats_analyst["notas_positivas"]
            / daily_stats_analyst["total_convertido_por_dia"]
        )
        * 100,
        0,
    )

    daily_stats_analyst["conversao_diaria"] = (
        daily_stats_analyst["total_convertido_por_dia"]
        / daily_stats_analyst["total_atendimentos"]
    ) * 100

    daily_stats_analyst_matriz = (
        df_mes_selecionado_matriz.groupby(["analista", "day"])
        .agg(
            total_atendimentos=("ticket_id", "count"),
        )
        .reset_index()
    )

    data = f"{mes_selecionado}/{ano_selecionado}"

    right.write("Relatório de Desempenho")
    html = gerar_relatorio_html(
        daily_stats, daily_stats_analyst_matriz, daily_stats_analyst, data
    )
    pdf_data = exportar_pdf(html)

    right.download_button(
        label="Baixar Relatório PDF",
        data=pdf_data,
        file_name=f"relatorio_{mes_selecionado}/{ano_selecionado}.pdf",
        mime="application/pdf",
    )

    # Filtrar os tickets com type igual a 3 ou type igual a None para os gráficos de donuts
    avaliados_mes = df_mes_selecionado[df_mes_selecionado["value"] != "S/N"]
    avaliados_mes.loc[:, "value"] = avaliados_mes["value"].astype(int)

    # Filtrar os tickets com type igual a 3 ou type igual a None

    # Filtrar os dados para obter apenas os tickets avaliados (excluindo valores NaN em 'type' e 'value')
    avaliados = df[df["value"] != "S/N"]
    avaliados.loc[:, "value"] = avaliados["value"].astype(int)

    # Calcular os totais e percentuais necessários para os gráficos
    total_atendimentos = len(df_mes_selecionado)
    total_avaliados = len(avaliados_mes)
    positivas = avaliados_mes[avaliados_mes["value"] >= 7]
    total_positivas = len(positivas)
    if total_avaliados > 0:
        percent_positivas = round((total_positivas / total_avaliados) * 100, 2)
        percent_negativas = 100 - percent_positivas
    else:
        percent_positivas = 100
        percent_negativas = 0

    # Dados para o gráfico de satisfação
    donut_data_positivas = pd.DataFrame(
        {
            "Tipo": ["Positivas", "Negativas"],
            "Percentual": [percent_positivas, percent_negativas],
        }
    )

    # Criar gráfico de satisfação
    donut_satisfacao = px.pie(
        donut_data_positivas,
        names="Tipo",
        values="Percentual",
        hole=0.5,
        color_discrete_sequence=["#94610B", "grey"],
        height=300,
        width=600,
    )

    donut_satisfacao.update_traces(
        hovertemplate="<b>%{label}: </b><br>%{percent}<br><extra></extra>",
        textinfo="percent+label",
        hoverinfo="label+percent",
        textposition="outside",
        outsidetextfont=dict(size=15),
    )

    donut_satisfacao.update_layout(
        showlegend=True,
        plot_bgcolor="rgba(0,0,0,0)",  # Fundo transparente
        paper_bgcolor="rgba(0,0,0,0)",  # Fundo transparente
        legend=dict(
            yanchor="bottom", y=0, xanchor="left", x=0, bgcolor="rgba(0,0,0,0)"
        ),
    )

    # Calcular taxas de conversão
    total_respondidos = total_avaliados
    if total_atendimentos > 0:
        percent_respondidos = round((total_respondidos / total_atendimentos) * 100, 2)
        percent_nao_respondidos = 100 - percent_respondidos
    else:
        percent_respondidos = 100
        percent_nao_respondidos = 0
    # Dados para o gráfico de conversão
    donut_data_conversao = pd.DataFrame(
        {
            "Tipo": ["Respondidos", "Não Respondidos"],
            "Percentual": [percent_respondidos, percent_nao_respondidos],
        }
    )

    # Criar gráfico de conversão
    donut_conversao = px.pie(
        donut_data_conversao,
        names="Tipo",
        values="Percentual",
        hole=0.5,
        color_discrete_sequence=["#94610B", "grey"],
        height=300,
        width=600,
    )
    donut_conversao.update_traces(
        hovertemplate="<b>%{label}: </b><br>%{percent}<br><extra></extra>",
        textinfo="percent+label",
        hoverinfo="percent+label",
        textposition="outside",
        outsidetextfont=dict(size=15),
    )

    donut_conversao.update_layout(
        showlegend=True,
        plot_bgcolor="rgba(0,0,0,0)",  # Fundo transparente
        paper_bgcolor="rgba(0,0,0,0)",  # Fundo transparente
        legend=dict(
            yanchor="bottom", y=0, xanchor="left", x=0, bgcolor="rgba(0,0,0,0)"
        ),
    )

    # Calcular dados para o gráfico da matriz
    total_matriz_count = len(df_mes_selecionado_matriz)
    if total_atendimentos > 0:
        percent_matriz = round((total_matriz_count / total_atendimentos) * 100, 2)
        percent_nao_matriz = 100 - percent_matriz
    else:
        percent_matriz = 0
        percent_nao_matriz = 100

    # Dados para o gráfico da matriz
    donut_data_matriz = pd.DataFrame(
        {
            "Tipo": ["Matriz VR", "VR Belém"],
            "Percentual": [percent_matriz, percent_nao_matriz],
        }
    )

    # Criar gráfico da matriz
    donut_matriz = px.pie(
        donut_data_matriz,
        names="Tipo",
        values="Percentual",
        hole=0.5,
        color_discrete_sequence=["#94610B", "grey"],
        height=300,
        width=600,
    )
    donut_matriz.update_traces(
        hovertemplate="<b>%{label}: </b><br>%{percent}<br><extra></extra>",
        textinfo="percent+label",
        textposition="outside",
        outsidetextfont=dict(size=17),
    )
    donut_matriz.update_layout(
        showlegend=True,
        plot_bgcolor="rgba(0,0,0,0)",  # Fundo transparente
        paper_bgcolor="rgba(0,0,0,0)",  # Fundo transparente
        legend=dict(
            yanchor="bottom", y=0, xanchor="left", x=0, bgcolor="rgba(0,0,0,0)"
        ),
    )

    # Criar um container para os gráficos de donuts
    with st.container():
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                '<div class="title"> &nbsp;  CONVERSÃO</div>', unsafe_allow_html=True
            )
            st.plotly_chart(donut_conversao)

        with col2:
            st.markdown(
                '<div class="title"> &nbsp;  SATISFAÇÃO</div>', unsafe_allow_html=True
            )
            st.plotly_chart(donut_satisfacao)

        with col3:
            st.markdown(
                '<div class="title"> &nbsp;  MATRIZ</div>', unsafe_allow_html=True
            )
            st.plotly_chart(donut_matriz)

    # Seletor de período
    l, m, r = st.columns([1, 7, 1])

    dia_sas = l.date_input(
        "Selecione o período",
        (dia_atual, dia_atual),
        format="DD.MM.YYYY",
        key="dia_sas",
    )
    st.write("Última atualização: ", time.strftime("%d/%m/%Y - %H:%M:%S"))
    if len(dia_sas) == 2:
        df_selecionado = avaliados[
            (avaliados["createdDate"].dt.date >= dia_sas[0])
            & (avaliados["createdDate"].dt.date <= dia_sas[1])
        ].copy()
    else:
        df_selecionado = avaliados[
            avaliados["createdDate"].dt.date == dia_sas[0]
        ].copy()

    notas_positivas = (
        df_selecionado.query('type == "3" & value >= 7').groupby("analyst").size()
    )

    notas_negativas = (
        df_selecionado.query("type == '3' and value < 6").groupby("analyst").size()
    )

    chart_data = notas_positivas.reset_index(name="Count")

    if len(dia_sas) == 2:
        df_periodo = df[
            (df["createdDate"].dt.date >= dia_sas[0])
            & (df["createdDate"].dt.date <= dia_sas[1])
        ]
    else:
        df_periodo = df[df["createdDate"].dt.date == dia_sas[0]]

    analista_avaliado = df_periodo.query('type == "3"')

    total_atdm_analista = df_periodo.groupby("analyst").size()

    total_atdm = df_periodo["ticket_id"].count()

    total_avaliados_analista = analista_avaliado.groupby("analyst").size()

    df_periodo["updateDate"] = pd.to_datetime(df_periodo["createdDate"])
    df_ultimo_status = df.sort_values(by=["ticket_id"]).drop_duplicates(
        subset="ticket_id", keep="last"
    )

    status_matriz = [
        "Em atendimento",
        "Aguardando resposta da Matriz",
        "Aguardando Retorno Cliente",
        "AGUARDANDO PRODUTO",
        "AGUARDANDO N2",
        "EM ANALISE N2",
        "Aguardando N2 - Fiscal",
        "Em Analise - Produto",
    ]

    df_status_matriz = df_matriz[df_matriz["status"].isin(status_matriz)]

    matriz_atdm_analista = df_status_matriz.groupby("analista").size()

    df_tickets_atdm = df_ultimo_status[
        (
            (df_ultimo_status["status"] == "Em atendimento")
            | (df_ultimo_status["status"] == "Aguardando resposta da Matriz")
        )
        # & (df_ultimo_status["createdDate"].dt.date != dia_atual)
    ]

    tickets_atdm_analista = df_tickets_atdm.groupby("analyst").size()

    # Convertendo as séries em DataFrames
    df_tickets_clientes = tickets_atdm_analista.reset_index(name="Clientes")
    df_tickets_matriz = matriz_atdm_analista.reset_index(name="Matriz")

    df_tickets_clientes.rename(columns={"analyst": "Analista"}, inplace=True)
    df_tickets_matriz.rename(columns={"analista": "Analista"}, inplace=True)

    # Realizando o merge, preenchendo valores ausentes com zero
    df_combined = pd.merge(
        df_tickets_clientes, df_tickets_matriz, on="Analista", how="outer"
    ).fillna(0)

    df_combined["Clientes"] = df_combined["Clientes"].astype(int)
    df_combined["Matriz"] = df_combined["Matriz"].astype(int)

    mask_total_atdm = total_atdm_analista > 0
    mask_total_tickets_atdm = tickets_atdm_analista > 0

    df_total_atendimentos = total_atdm_analista[mask_total_atdm].reset_index(
        name="Total Atendimentos"
    )
    df_total_tickets_em_atendimento = tickets_atdm_analista[
        mask_total_tickets_atdm
    ].reset_index(name="Tickets Em Atendimento")

    total_atdm_analista, total_avaliados_analista = total_atdm_analista.align(
        total_avaliados_analista, fill_value=0
    )

    # Criar gráfico de Conversão x Analista
    analista_data = pd.DataFrame(
        {
            "Analyst": total_atdm_analista.index,
            "Total_Atendimentos": total_atdm_analista.values,
            "Avaliados": total_avaliados_analista.values,
        }
    )

    analista_data["Avaliados"] = analista_data["Avaliados"]

    analista_data["% Avaliado"] = (
        analista_data["Avaliados"] / analista_data["Total_Atendimentos"]
    ) * 100
    analista_data["% Não avaliado"] = 100 - analista_data["% Avaliado"]

    # Transformar os dados para o formato longo (long format) para Plotly Express
    analista_long_data = pd.melt(
        analista_data,
        id_vars=["Analyst"],
        value_vars=["% Avaliado", "% Não avaliado"],
        var_name="Tipo",
        value_name="Percentual",
    )

    # Adicionar uma coluna para texto customizado
    analista_long_data["Texto"] = analista_long_data.apply(
        lambda row: f"{row['Percentual']:.2f}%" if row["Tipo"] == "% Avaliado" else "",
        axis=1,
    )

    total_clientes = df_combined["Clientes"].sum()
    total_matriz = df_combined["Matriz"].sum()

    total_tickets_abertos = total_clientes + total_matriz

    previous_data = load_previous_data()

    if previous_data:
        previous_total = previous_data["total"]
        # delta = previous_data.get("delta", total_tickets_abertos - previous_total)
        delta = total_tickets_abertos - previous_total
    else:
        previous_total = 0
        delta = 0

    # Container para os gráficos de barras
    nao_convertido = total_atdm - (notas_positivas.sum() + notas_negativas.sum())

    if isinstance(delta, (np.ndarray, pd.Series)):
        delta = (
            delta.iloc[0] if isinstance(delta, pd.Series) else delta[0]
        )  # Pega o primeiro elemento se for array ou Series

    # Certifique-se de que delta seja um int ou float
    delta = int(delta) if not isinstance(delta, (int, float)) else delta

    if datetime.datetime.now().hour == 18:
        save_data(total_tickets_abertos, delta)

    (
        metric_espaco1,
        metric_todos,
        metric_nao_convertido,
        metric_positivas,
        metric_negativas,
        metric_tickets,
        metric_espaco2,
    ) = st.columns([0.2, 0.6, 0.6, 0.6, 0.6, 0.6, 0.2])

    metric_todos.text("Total de atendimentos")
    metric_nao_convertido.text("Não convertidos")
    metric_positivas.text("Promotoras")
    metric_negativas.text("Detratoras")
    metric_tickets.text("Tickets em aberto")

    with metric_espaco1.container(border=0):
        st.text("")
    with metric_todos.container(border=0):
        st.metric(
            label="Total de atendimentos",
            label_visibility="hidden",
            value=total_atdm,
        )
    with metric_nao_convertido.container(border=0):
        st.metric(
            label="Não convertido",
            label_visibility="hidden",
            value=nao_convertido,
        )
    with metric_positivas.container(border=0):
        st.metric(
            label="Promotoras",
            label_visibility="hidden",
            value=notas_positivas.sum(),
        )
    with metric_negativas.container(border=0):
        st.metric(
            label="Detratoras",
            label_visibility="hidden",
            value=notas_negativas.sum(),
        )
    with metric_tickets.container(border=0):
        st.metric(
            label="Tickets em aberto",
            label_visibility="hidden",
            value=total_tickets_abertos,
            delta=delta,
            delta_color="inverse",
        )

    with metric_espaco2.container(border=0):
        st.text("")

    with st.container(border=1):

        st.markdown(
            '<div class="container" position= "relative">', unsafe_allow_html=True
        )
        convert_col1, satisf_col2 = st.columns(2)

        with convert_col1:
            st.markdown(
                '<div class="title">CONVERSÃO X ANALISTAS</div>', unsafe_allow_html=True
            )
            # Criar o gráfico de barras horizontal com Plotly Express
            conversao_analista = px.bar(
                analista_long_data,
                x="Percentual",
                y="Analyst",
                color="Tipo",
                orientation="h",
                labels={
                    "Percentual": "Percentual",
                    "analyst": "Analista",
                    "Tipo": "Tipo de Atendimento",
                },
                barmode="stack",
                text="Texto",  # Adicionar o texto customizado
                color_discrete_sequence=["#94610B", "grey"],
            )

            # Customizar o gráfico
            conversao_analista.update_layout(
                width=700,  # Ajuste a largura do gráfico
                height=420,  # Ajuste a altura do gráfico
                xaxis_title="Percentual",
                yaxis_title="Analista",
                plot_bgcolor="rgba(0,0,0,0)",  # Fundo transparente
                paper_bgcolor="rgba(0,0,0,0)",  # Fundo transparente
                legend=dict(
                    yanchor="top",
                    y=-0.3,
                    xanchor="right",
                    x=0,
                    bgcolor="rgba(0,0,0,0)",  # Torna o fundo da legenda transparente
                ),
            )

            conversao_analista.update_traces(
                hovertemplate="<b>%{y}</b><br>%{x:.2f}%<br><extra></extra>",
                customdata=analista_long_data[["Tipo"]],
                texttemplate="%{text}",  # Define o template para o texto
                textposition="inside",  # Define a posição do texto
                insidetextanchor="middle",  # Alinha o texto ao centro das barras
                insidetextfont=dict(
                    size=17,
                ),
            )

            st.plotly_chart(conversao_analista)

        with satisf_col2:
            st.markdown(
                '<div class="title">SATISFAÇÃO X ANALISTA</div>', unsafe_allow_html=True
            )
            satisfy_analista = px.bar(
                chart_data,
                x="analyst",
                y="Count",
                labels={
                    "Count": "Quantidade de Notas Positivas",
                    "analyst": "Analista",
                },
                color="analyst",  # Colore cada barra de forma diferente
                color_discrete_sequence=px.colors.qualitative.G10,
                text_auto=True,
            )

            # Customizar o gráfico (tamanho e layout)
            satisfy_analista.update_layout(
                width=900,  # Ajuste a largura do gráfico
                height=370,  # Ajuste a altura do gráfico
                xaxis_title="Analista",
                yaxis_title="Quantidade de Notas Positivas",
                plot_bgcolor="rgba(0,0,0,0)",  # Fundo transparente
                paper_bgcolor="rgba(0,0,0,0)",  # Fundo transparente
                showlegend=False,
            )

            satisfy_analista.update_traces(
                hovertemplate="<b>%{x}</b><br>%{y}<br><extra></extra>",
                textfont_size=18,
                textangle=-0,
                textposition="outside",
                cliponaxis=False,
            )

            st.plotly_chart(satisfy_analista)

        num_col1, opentickets_col2 = st.columns(2)

        with num_col1:
            st.markdown(
                '<div class="title">TOTAL DE ATENDIMENTOS POR ANALISTA</div>',
                unsafe_allow_html=True,
            )

            fig_total_atendimentos = px.bar(
                df_total_atendimentos,
                x="analyst",
                y="Total Atendimentos",
                color="analyst",
                color_discrete_sequence=px.colors.qualitative.G10,
                labels={
                    "analyst": "Analista",
                    "Total Atendimentos": "Total de Atendimentos",
                },
                text_auto=True,
            )

            fig_total_atendimentos.update_layout(
                width=700,  # Ajuste a largura do gráfico
                height=370,  # Ajuste a altura do gráfico
                xaxis_title="Analista",
                yaxis_title="Quantidade de Atendimentos",
                plot_bgcolor="rgba(0,0,0,0)",  # Fundo transparente
                paper_bgcolor="rgba(0,0,0,0)",  # Fundo transparente
                showlegend=False,
            )

            fig_total_atendimentos.update_traces(
                hovertemplate="<b>%{x}</b><br>%{y}<br><extra></extra>",
                textfont_size=18,
                textangle=-0,
                textposition="outside",
                cliponaxis=False,
            )

            st.plotly_chart(fig_total_atendimentos)

        with opentickets_col2:
            st.markdown(
                '<div class="title">TICKETS EM ABERTO</div>', unsafe_allow_html=True
            )

            open_tickets_analista = px.bar(
                df_combined.melt(
                    id_vars="Analista", var_name="Tipo", value_name="Tickets"
                ),
                x="Analista",
                y="Tickets",
                color="Tipo",
                barmode="group",
                color_discrete_sequence=px.colors.qualitative.G10,
                labels={
                    "Tickets": "Quantidade de Tickets",
                    "Tipo": "Tipo de Atendimento",
                },
                text_auto=True,
            )

            open_tickets_analista.update_layout(
                width=900,  # Ajuste a largura do gráfico
                height=370,  # Ajuste a altura do gráfico
                xaxis_title="Analista",
                yaxis_title="Tickets em Atendimento",
                plot_bgcolor="rgba(0,0,0,0)",  # Fundo transparente
                paper_bgcolor="rgba(0,0,0,0)",  # Fundo transparente
                showlegend=True,
            )

            open_tickets_analista.update_traces(
                hovertemplate="<b>%{x}</b><br>%{y}<br><extra></extra>",
                textfont_size=18,
                textangle=-0,
                textposition="outside",
                cliponaxis=False,
            )

            st.plotly_chart(open_tickets_analista)

        st.divider()
        df_selecionado["cleaned_organization"] = df_selecionado["organization"].apply(
            clean_org_name
        )

        # Agrupar os dados por organização e contar o número de avaliações no período selecionado
        org_avaliacoes = (
            df_selecionado.groupby("cleaned_organization")
            .size()
            .reset_index(name="Count")
        )
        # Obter as top 5 organizações com mais avaliações
        top_5_orgs = org_avaliacoes.nlargest(5, "Count")

        st.markdown(
            '<div class="title">AVALIAÇÃO X CLIENTES</div>', unsafe_allow_html=True
        )
        # Criar um filtro de seleção para organizações usando nomes limpos
        selected_orgs = st.multiselect(
            "Escolha as organizações",
            org_avaliacoes["cleaned_organization"].unique(),
            default=top_5_orgs["cleaned_organization"],
        )

        # Filtrar os dados para incluir apenas as organizações selecionadas
        filtered_avaliacoes = org_avaliacoes[
            org_avaliacoes["cleaned_organization"].isin(selected_orgs)
        ]

        # Criar o gráfico de barras horizontal com Plotly Express
        fig_barras_organizacao = px.bar(
            filtered_avaliacoes,
            x="Count",
            y="cleaned_organization",
            orientation="h",
            labels={
                "Count": "Quantidade de Avaliaçõeses",
                "cleaned_organization": "Organização",
            },
            template="plotly_dark",  # Define um modelo escuro para o gráfico
            text_auto=True,
            color_discrete_sequence=["#94610B"],
        )

        # Customizar o gráfico
        fig_barras_organizacao.update_layout(
            xaxis_title="Quantidade de Avaliações",
            yaxis_title="Organização",
            plot_bgcolor="rgba(0,0,0,0)",  # Fundo transparente
            paper_bgcolor="rgba(0,0,0,0)",  # Fundo transparente
            legend=dict(
                yanchor="top",
                y=-0.3,
                xanchor="right",
                x=0,
                bgcolor="rgba(0,0,0,0)",  # Torna o fundo da legenda transparente
            ),
        )

        fig_barras_organizacao.update_traces(
            textfont_size=14,
            textangle=-0,
            textposition="outside",
            cliponaxis=False,
            hovertemplate="<b>%{y}</b><br>%{x}<br><extra></extra>",
        )

        # Mostrar o gráfico
        st.plotly_chart(fig_barras_organizacao)

        st.markdown("</div>", unsafe_allow_html=True)

    st.container(height=60, border=False)

    day_of_week_mapping = {
        0: "Segunda-Feira",
        1: "Terça-Feira",
        2: "Quarta-Feira",
        3: "Quinta-Feira",
        4: "Sexta-Feira",
        5: "Sábado",
    }

    tab_total, tab_ped = st.tabs(["Total", "Mensal"])

    with tab_total:
        calls_by_hour = df["Horas"].value_counts().sort_index()
        calls_by_hour_df = pd.DataFrame(
            {
                "Hora do Dia": calls_by_hour.index,
                "Número de Atendimentos": calls_by_hour.values,
            }
        )
        st.markdown(
            '<div class="title">DISTRIBUIÇÃO DE ATENDIMENTOS x HORA DO DIA</div>',
            unsafe_allow_html=True,
        )
        fig_horas_dia = px.bar(
            calls_by_hour_df,
            x="Hora do Dia",
            y="Número de Atendimentos",
            labels={
                "Hora do Dia": "Hora do Dia",
                "Número de Atendimentos": "Número de Atendimentos",
            },
            color="Número de Atendimentos",
            color_continuous_scale=["blue", "red"],
            text="Número de Atendimentos",
        )
        fig_horas_dia.update_traces(
            hovertemplate="<b>Hora: %{x}</b><br>Total de atendimentos: %{y}<br><extra></extra>",
            textfont_size=14,
            textangle=0,
            textposition="outside",
            cliponaxis=False,
        )

        fig_horas_dia.update_layout(
            coloraxis_colorbar=dict(title="Número de Atendimentos")
        )

        st.plotly_chart(fig_horas_dia)

        # Distribuição por Semana
        calls_by_day_of_week = df["Dia da Semana"].value_counts().sort_index()
        calls_by_day_of_week_df = pd.DataFrame(
            {
                "Dia da Semana": calls_by_day_of_week.index.map(day_of_week_mapping),
                "Número de Chamadas": calls_by_day_of_week.values,
            }
        )
        st.markdown(
            '<div class="title">DISTRIBUIÇÃO DE ATENDIMENTOS x DIA DA SEMANA</div>',
            unsafe_allow_html=True,
        )

        fig_day_of_week = px.bar(
            calls_by_day_of_week_df,
            x="Dia da Semana",
            y="Número de Chamadas",
            orientation="v",
            labels={
                "Dia da Semana": "Dia da Semana",
                "Número de Chamadas": "Número de Chamadas",
            },
            color="Número de Chamadas",
            color_continuous_scale=["blue", "red"],
            text="Número de Chamadas",
        )

        fig_day_of_week.update_traces(
            hovertemplate="<b>%{x}</b><br>%{y}<br><extra></extra>",
            textfont_size=14,
            textangle=-0,
            textposition="outside",
            cliponaxis=False,
        )
        # Usar Streamlit para mostrar o gráfico
        st.plotly_chart(fig_day_of_week)
    with tab_ped:
        lf, md, rt = st.columns([1, 4, 0.6521])
        mes_atual = pd.Timestamp.now().month
        mes_selectDia = lf.selectbox(
            "Selecione o mês", meses, index=mes_atual - 1, key="select-mes"
        )

        mes_numero2 = meses.index(mes_selectDia) + 1

        df_mes_selecionado = df[df["month"] == mes_numero2].copy()

        calls_by_hour_mes = df_mes_selecionado["Horas"].value_counts().sort_index()
        calls_by_hour_mes_df = pd.DataFrame(
            {
                "Hora do Dia": calls_by_hour_mes.index,
                "Número de Atendimentos": calls_by_hour_mes.values,
            }
        )
        st.markdown(
            '<div class="title">DISTRIBUIÇÃO DE ATENDIMENTOS x HORA DO DIA</div>',
            unsafe_allow_html=True,
        )
        fig_horas_dia_mes = px.bar(
            calls_by_hour_mes_df,
            x="Hora do Dia",
            y="Número de Atendimentos",
            labels={
                "Hora do Dia": "Hora do Dia",
                "Número de Atendimentos": "Número de Atendimentos",
            },
            color="Número de Atendimentos",
            color_continuous_scale=["blue", "red"],
            text="Número de Atendimentos",
        )
        fig_horas_dia_mes.update_traces(
            hovertemplate="<b>Hora: %{x}</b><br>Total de atendimentos: %{y}<br><extra></extra>",
            textfont_size=14,
            textangle=0,
            textposition="outside",
            cliponaxis=False,
        )

        fig_horas_dia_mes.update_layout(
            coloraxis_colorbar=dict(title="Número de Atendimentos")
        )

        st.plotly_chart(fig_horas_dia_mes)

        calls_by_day_of_week_mes = (
            df_mes_selecionado["Dia da Semana"].value_counts().sort_index()
        )
        calls_by_day_of_week_mes_df = pd.DataFrame(
            {
                "Dia da Semana": calls_by_day_of_week_mes.index.map(
                    day_of_week_mapping
                ),
                "Número de Chamadas": calls_by_day_of_week_mes.values,
            }
        )
        st.markdown(
            '<div class="title">DISTRIBUIÇÃO DE ATENDIMENTOS x DIA DA SEMANA</div>',
            unsafe_allow_html=True,
        )

        fig_day_of_week_mes = px.bar(
            calls_by_day_of_week_mes_df,
            x="Dia da Semana",
            y="Número de Chamadas",
            orientation="v",
            labels={
                "Dia da Semana": "Dia da Semana",
                "Número de Chamadas": "Número de Chamadas",
            },
            color="Número de Chamadas",
            color_continuous_scale=["blue", "red"],
            text="Número de Chamadas",
        )

        fig_day_of_week_mes.update_traces(
            hovertemplate="<b>%{x}</b><br>%{y}<br><extra></extra>",
            textfont_size=14,
            textangle=-0,
            textposition="outside",
            cliponaxis=False,
        )
        st.plotly_chart(fig_day_of_week_mes)

    tab1, tab2 = st.tabs(["Trimestre", "Mensal"])
    df["Trimestre"] = (
        df["createdDate"].dt.to_period("Q").astype(str).str.replace("Q", ".")
    )

    with tab1:
        st.markdown(
            '<div class="title">TOTAL DE ATENDIMENTOS POR CLIENTES (TRIMESTRE)</div>',
            unsafe_allow_html=True,
        )
        le, mi, ri = st.columns([1, 4, 0.6521])
        # color2 = ri.color_picker("","#0000ff", key='colorkey')
        trimestre = le.selectbox(
            "Selecione o mês", trimestres, index=trimestre_atual - 1
        )

        df_semestre_selecionado = df[df["Trimestre"] == trimestre]

        # Agrupar por organização limpa e contar
        org_atendimentos = (
            df_semestre_selecionado.groupby("clean_organization")
            .size()
            .reset_index(name="Count")
        )

        # Obter todas as organizações únicas limpas
        todas_organizacoes = pd.Series(df["clean_organization"].unique())

        # Criar DataFrame completo com todas as organizações
        orgs_completas = pd.DataFrame({"clean_organization": todas_organizacoes})
        org_atendimentos_completo = pd.merge(
            orgs_completas, org_atendimentos, on="clean_organization", how="left"
        ).fillna(0)

        # Agrupar novamente para garantir que não haja duplicatas
        org_atendimentos_completo = (
            org_atendimentos_completo.groupby("clean_organization").sum().reset_index()
        )

        fig_organizacao_atendimentos = px.bar(
            org_atendimentos_completo,
            x="clean_organization",
            y="Count",
            orientation="v",
            labels={
                "Count": "Quantidade de Atendimentos",
                "clean_organization": "Clientes",
            },
            template="plotly_dark",  # Define um modelo escuro para o gráfico
            text_auto=True,
            color_discrete_sequence=["#94610B"],
        )

        # Customizar o gráfico
        fig_organizacao_atendimentos.update_layout(
            xaxis_title="Quantidade de Atendimentos",
            yaxis_title="Clientes",
            plot_bgcolor="rgba(0,0,0,0)",  # Fundo transparente
            paper_bgcolor="rgba(0,0,0,0)",  # Fundo transparente
        )

        fig_organizacao_atendimentos.update_traces(
            hovertemplate="<b>%{x}</b><br>%{y}<br><extra></extra>",
            textfont_size=14,
            textangle=-0,
            textposition="outside",
            cliponaxis=False,
        )
        st.plotly_chart(fig_organizacao_atendimentos)
    with tab2:
        st.markdown(
            '<div class="title">TOTAL DE ATENDIMENTOS POR CLIENTES (MESES)</div>',
            unsafe_allow_html=True,
        )
        left, mid, right = st.columns([1, 4, 0.6521])
        # color1 = right.color_picker("","#0000ff")
        mes_selecionado = left.selectbox(
            "Selecione o mês", meses, index=mes_atual - 1, key="selectbox_mes"
        )

        mes_numero = meses.index(mes_selecionado) + 1

        df_mes_selecionado = df[df["month"] == mes_numero].copy()

        df_mes_selecionado["clean_organization"] = df_mes_selecionado[
            "organization"
        ].apply(clean_org_name)

        org_atendimentos_mes = (
            df_mes_selecionado.groupby("clean_organization")
            .size()
            .reset_index(name="Count")
        )

        orgs_completas_mes = pd.DataFrame({"clean_organization": todas_organizacoes})
        org_atendimentos_completo_mes = pd.merge(
            orgs_completas_mes,
            org_atendimentos_mes,
            on="clean_organization",
            how="left",
        ).fillna(0)
        org_atendimentos_completo_mes = (
            org_atendimentos_completo_mes.groupby("clean_organization")
            .sum()
            .reset_index()
        )

        fig_organizacao_atendimentos_mes = px.bar(
            org_atendimentos_completo_mes,
            x="clean_organization",
            y="Count",
            orientation="v",
            labels={
                "Count": "Quantidade de Atendimentos",
                "clean_organization": "Clientes",
            },
            template="plotly_dark",
            text_auto=True,
            color_discrete_sequence=["#94610B"],
        )

        fig_organizacao_atendimentos_mes.update_layout(
            xaxis_title="Clientes",
            yaxis_title="Quantidade de Atendimentos",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )

        fig_organizacao_atendimentos_mes.update_traces(
            hovertemplate="<b>%{x}</b><br>%{y}<br><extra></extra>",
            textfont_size=14,
            textangle=0,
            textposition="outside",
            cliponaxis=False,
        )

        st.plotly_chart(fig_organizacao_atendimentos_mes)
    st.divider()
