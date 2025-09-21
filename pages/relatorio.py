import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
import datetime as dt
import time


def run():
    # Leitura dos dados
    df = pd.read_csv(".\\data\\survey_results.csv")
    df = df.drop_duplicates(subset=["ticket_id", "status"])
    df = df.sort_values(by=["ticket_id"]).drop_duplicates(subset=["ticket_id"], keep="last")

    df = df[df["type"] != "2"]
    df["createdDate"] = pd.to_datetime(df["createdDate"])
    df["dia da semana"] = df["createdDate"].dt.dayofweek
    df["dia"] = df["createdDate"].dt.day
    df["horas"] = df["createdDate"].dt.hour
    df["mes"] = df["createdDate"].dt.month
    df["ano"] = df["createdDate"].dt.year

    df_matriz = pd.read_csv(".\\data\\matriz_ids.csv")
    df_matriz = df_matriz.drop_duplicates(subset=["ticket_id", "status"])
    df_matriz = df_matriz.sort_values(by=["ticket_id"]).drop_duplicates(
        subset=["ticket_id"], keep="last"
    )

    df_matriz["createdDate"] = pd.to_datetime(df_matriz["createdDate"])
    df_matriz["dia da semana"] = df_matriz["createdDate"].dt.dayofweek
    df_matriz["dia"] = df_matriz["createdDate"].dt.day
    df_matriz["horas"] = df_matriz["createdDate"].dt.hour
    df_matriz["mes"] = df_matriz["createdDate"].dt.month
    df_matriz["ano"] = df_matriz["createdDate"].dt.year

    left, mid = st.columns([1.5, 6])
    with left.container(border=True):
        data_atual = dt.datetime.now()
        mes_atual = data_atual.month
        ano_atual = data_atual.year

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

        # Garantir que existam anos válidos
        anos_disponiveis = sorted(df["ano"].unique(), reverse=True)
        if len(anos_disponiveis) == 0:
            st.error("Não há anos disponíveis no CSV.")
            return

        # Se ano atual existir, usar ele. Caso contrário, usar o mais recente disponível
        if ano_atual in anos_disponiveis:
            default_ano_index = anos_disponiveis.index(ano_atual)
        else:
            default_ano_index = 0  # mais recente

        ano_selecionado = st.selectbox("Selecione o ano", anos_disponiveis, index=default_ano_index)

        df_ano_selecionado = df[df["ano"] == ano_selecionado]

        # Garantir meses disponíveis
        meses_disponiveis = sorted(df_ano_selecionado["mes"].unique())
        if len(meses_disponiveis) == 0:
            st.error(f"Não há meses disponíveis para o ano {ano_selecionado}.")
            return

        meses_disponiveis_nomes = [meses[mes - 1] for mes in meses_disponiveis]

        # Se mês atual existir no ano filtrado, usar ele. Senão, usar o último disponível
        if mes_atual in meses_disponiveis:
            default_mes_index = meses_disponiveis.index(mes_atual)
        else:
            default_mes_index = len(meses_disponiveis) - 1

        mes_selecionado_nome = st.selectbox(
            "Selecione o mês", meses_disponiveis_nomes, index=default_mes_index
        )

        # Mapear o nome do mês para seu número correspondente
        mes_numero = meses.index(mes_selecionado_nome) + 1

        df_mes_selecionado = df[(df["ano"] == ano_selecionado) & (df["mes"] == mes_numero)]
        df_mes_selecionado_matriz = df_matriz[
            (df_matriz["ano"] == ano_selecionado) & (df_matriz["mes"] == mes_numero)
        ]

        analistas_disponiveis = sorted(df_mes_selecionado["analyst"].unique())
        if len(analistas_disponiveis) == 0:
            st.warning("Nenhum analista disponível para esse período.")
            return

        analista_selecionado = st.selectbox("Selecione o Analista", analistas_disponiveis)

        df_analista_selecionado = df[
            (df["ano"] == ano_selecionado)
            & (df["mes"] == mes_numero)
            & (df["analyst"] == analista_selecionado)
        ]

        df_analista_matriz = df_matriz[
            (df_matriz["ano"] == ano_selecionado)
            & (df_matriz["mes"] == mes_numero)
            & (df_matriz["analista"] == analista_selecionado)
        ]

        avaliados_mes = df_analista_selecionado[df_analista_selecionado["value"] != "S/N"]
        avaliados_mes.loc[:, "value"] = avaliados_mes["value"].astype(int)

        avaliados = df[df["value"] != "S/N"]
        avaliados.loc[:, "value"] = avaliados["value"].astype(int)

        # Métricas principais
        total_atendimentos = len(df_analista_selecionado)
        total_avaliados = len(avaliados_mes)
        positivas = avaliados_mes[avaliados_mes["value"] >= 7]
        total_positivas = len(positivas)
        total_negativas = total_avaliados - total_positivas

        if total_avaliados > 0:
            percent_positivas = round((total_positivas / total_avaliados) * 100, 2)
            percent_negativas = round(100 - percent_positivas, 2)
        else:
            percent_positivas = 100
            percent_negativas = 0

        total_respondidos = total_avaliados
        if total_atendimentos > 0:
            percent_respondidos = round((total_respondidos / total_atendimentos) * 100, 2)
        else:
            percent_respondidos = 100

        total_matriz_count = len(df_analista_matriz)
        if total_atendimentos > 0:
            percent_acesso_matriz = round((total_matriz_count / total_atendimentos) * 100, 2)
        else:
            percent_acesso_matriz = 0

        total_first_call = len(df_analista_selecionado[df["resolvedInFirstCall"] == True])
        if total_atendimentos > 0:
            percent_first_call = round((total_first_call / total_atendimentos) * 100, 2)
        else:
            percent_first_call = 0

        st.write("---")
        st.header("Métricas")
        st.metric(label="Total de Atendimentos", value=f"{total_atendimentos}")
        st.metric(label="Conversão", value=f"{total_respondidos} - ({percent_respondidos}%)")
        st.metric(label="Promotoras", value=f"{total_positivas} - ({percent_positivas}%)")
        st.metric(label="Detratoras", value=f"{total_negativas} - ({percent_negativas}%)")
        st.metric(label="Resolvido de Primeira", value=f"{total_first_call} - ({percent_first_call}%)")
        st.metric(label="Matriz", value=f"{total_matriz_count} - ({percent_acesso_matriz}%)")

        # Agrupamentos
        df_total_atendimentos = (
            df_analista_selecionado.groupby("dia").size().reset_index(name="ticket_count")
        )
        df_notas_avaliadas = (
            df_analista_selecionado.groupby("value").size().reset_index(name="value_count")
        )
        df_media_tempo = (
            df_analista_selecionado.groupby("dia")["chatTalkTime"]
            .mean()
            .reset_index(name="mean_value")
        )

    # --- Aba direita (gráficos)
    with mid.container(border=True):
        tab1, tab2, tab3 = st.tabs(["Atendimentos", "Notas Negativas", "Assunto"])

        with tab1:
            col1, col2 = st.columns(2)
            fig = px.bar(
                df_notas_avaliadas,
                x="value",
                y="value_count",
                template="ggplot2",
                text="value_count",
            )
            fig.update_traces(texttemplate="%{text:.0f}", textposition="outside")
            fig.update_layout(xaxis={"categoryorder": "total ascending"})
            col1.plotly_chart(fig)

            fig2 = px.line(
                df_total_atendimentos,
                x="dia",
                y="ticket_count",
                title="Número de Atendimentos",
                markers=True,
                template="ggplot2",
                text="ticket_count",
            )
            fig2.update_traces(texttemplate="%{text:.0f}", textposition="top center")
            fig2.update_layout(hovermode="x")
            col2.plotly_chart(fig2)

            fig3 = px.line(
                df_media_tempo,
                x="dia",
                y="mean_value",
                title="Média de tempo de conversa",
                text="mean_value",
                markers=True,
                template="ggplot2",
            )
            fig3.update_traces(texttemplate="%{text:.0f}", textposition="top right")
            fig3.update_layout(hovermode="x")
            st.plotly_chart(fig3)

        with tab2:
            negativas = avaliados_mes[avaliados_mes["value"] < 7].copy()
            drop_list = [
                "analyst", "type", "dia da semana", "dia", "horas", "mes", "ano",
                "chatWaitingTime", "urgency", "chatTalkTime"
            ]
            rename = {
                "createdDate": "Data",
                "ticket_id": "Ticket",
                "status": "Status",
                "category": "Categoria",
                "resolvedInFirstCall": "Resolvido Rapido",
                "serviceFirstLevel": "Tipo1",
                "serviceSecondLevel": "Tipo2",
                "serviceThirdLevel": "Tipo3",
                "lifeTimeWorkingTime": "Tempo de Vida do Ticket",
                "organization": "Cliente",
                "createdBy": "Solicitante",
                "value": "Nota",
                "comment": "Comentário",
            }
            negativas = negativas.drop(axis=1, labels=drop_list)
            negativas = negativas.rename(columns=rename)
            if not negativas.empty:
                st.dataframe(negativas, use_container_width=True, hide_index=True)
            else:
                st.header("Não há notas negativas")

        with tab3:
            coll1, coll2 = st.columns(2)
            df_first_level = (
                avaliados_mes.groupby("serviceFirstLevel")
                .agg(Quantidade=("serviceFirstLevel", "size"), Media_Avaliacao=("value", "mean"))
                .reset_index()
            )
            df_first_filtered = df_first_level[df_first_level["Quantidade"] > 5].sort_values(
                by="Quantidade", ascending=True
            )
            fig_first_level = px.bar(df_first_filtered, x="Quantidade", y="serviceFirstLevel", orientation="h")
            fig_first_level.add_trace(
                go.Scatter(
                    x=df_first_filtered["Media_Avaliacao"],
                    y=df_first_filtered["serviceFirstLevel"],
                    mode="lines+markers",
                    name="Média de Avaliação",
                    line=dict(color="firebrick", width=2),
                )
            )
            coll1.plotly_chart(fig_first_level)

            df_second_level = (
                avaliados_mes.groupby("serviceSecondLevel")
                .agg(Quantidade=("serviceSecondLevel", "size"), Media_Avaliacao=("value", "mean"))
                .reset_index()
            )
            df_second_filtered = df_second_level[df_second_level["Quantidade"] > 5].sort_values(
                by="Quantidade", ascending=True
            )
            fig_second_level = px.bar(df_second_filtered, x="Quantidade", y="serviceSecondLevel", orientation="h")
            fig_second_level.add_trace(
                go.Scatter(
                    x=df_second_filtered["Media_Avaliacao"],
                    y=df_second_filtered["serviceSecondLevel"],
                    mode="lines+markers",
                    name="Média de Avaliação",
                    line=dict(color="firebrick", width=2),
                )
            )
            coll2.plotly_chart(fig_second_level)

            df_third_level = (
                avaliados_mes.groupby("serviceThirdLevel")
                .agg(Quantidade=("serviceThirdLevel", "size"), Media_Avaliacao=("value", "mean"))
                .reset_index()
            )
            df_third_filtered = df_third_level[df_third_level["Quantidade"] > 10].sort_values(
                by="Quantidade", ascending=True
            )
            fig_third_level = px.bar(df_third_filtered, x="Quantidade", y="serviceThirdLevel", orientation="h")
            fig_third_level.add_trace(
                go.Scatter(
                    x=df_third_filtered["Media_Avaliacao"],
                    y=df_third_filtered["serviceThirdLevel"],
                    mode="lines+markers",
                    name="Média de Avaliação",
                    line=dict(color="firebrick", width=2),
                )
            )
            coll2.plotly_chart(fig_third_level)