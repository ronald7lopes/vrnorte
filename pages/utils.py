import json
import datetime
import pdfkit
import os


def load_previous_data():
    try:
        with open("ticket_count.json", "r") as file:
            data = json.load(file)
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_data(total, delta):
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    previous_data = load_previous_data()

    if previous_data is None or previous_data.get("date") != today_date:
        data = {"date": today_date, "total": int(total), "delta": delta}
        with open("ticket_count.json", "w") as file:
            json.dump(data, file)


def gerar_relatorio_html(daily_stats, daily_stats_analyst_matriz, daily_stats_analyst, data):



# ------------------------------------------------------------------------------------------------


    total_atendimentos_por_dia = daily_stats["total_atendimentos"].sum()
    media_atendimentos_por_dia = round(daily_stats["total_atendimentos"].mean(), 2)
    desvio_padrao_atendimentos_por_dia = round(
        daily_stats["total_atendimentos"].std(), 2
    )
    maximo_atendimentos_por_dia = round(daily_stats["total_atendimentos"].max(), 2)
    minimo_atendimentos_por_dia = round(daily_stats["total_atendimentos"].min(), 2)


#------------------------------------------------------------------------------------------------------


    total_atendimentos_por_dia_matriz = daily_stats_analyst_matriz["total_atendimentos"].sum()
    porcentagem_atendimentos_por_dia_matriz = round(
        (total_atendimentos_por_dia_matriz / total_atendimentos_por_dia)
        * 100,
        2,
    )
    media_atendimentos_por_dia_matriz = round(daily_stats_analyst_matriz["total_atendimentos"].mean(), 2)
    desvio_padrao_atendimentos_por_dia_matriz = round(daily_stats_analyst_matriz["total_atendimentos"].std(), 2)
    maximo_atendimentos_por_dia_matriz = round(daily_stats_analyst_matriz["total_atendimentos"].max(), 2)
    minimo_atendimentos_por_dia_matriz = round(daily_stats_analyst_matriz["total_atendimentos"].min(), 2)


# ------------------------------------------------------------------------------------------------


    total_convertidos_por_dia = daily_stats["total_convertido_por_dia"].sum()
    porcentagem_convertidos_por_dia = round(
        (daily_stats["total_convertido_por_dia"].sum() / total_atendimentos_por_dia)
        * 100,
        2,
    )
    media_convertidos_por_dia = round(daily_stats["total_convertido_por_dia"].mean(), 2)
    desvio_padrao_convertidos_por_dia = round(
        daily_stats["total_convertido_por_dia"].std(), 2
    )
    maximo_convertido_por_dia = round(daily_stats["total_convertido_por_dia"].max(), 2)
    minimo_convertido_por_dia = round(daily_stats["total_convertido_por_dia"].min(), 2)


# ------------------------------------------------------------------------------------------------


    total_nao_convertido_por_dia = daily_stats["total_nao_convertido_por_dia"].sum()
    porcentagem_nao_convertido_por_dia = round(
        (daily_stats["total_nao_convertido_por_dia"].sum() / total_atendimentos_por_dia)
        * 100,
        2,
    )
    minimo_nao_convertido_por_dia = round(
        daily_stats["total_nao_convertido_por_dia"].min(), 2
    )
    media_nao_convertido_por_dia = round(
        daily_stats["total_nao_convertido_por_dia"].mean(), 2
    )
    desvio_padrao_nao_convertido_por_dia = round(
        daily_stats["total_nao_convertido_por_dia"].std(), 2
    )
    maximo_nao_convertido_por_dia = round(
        daily_stats["total_nao_convertido_por_dia"].max(), 2
    )


# ------------------------------------------------------------------------------------------------


    total_resolvidos_na_hora = daily_stats["total_resolvidos_na_hora"].sum()
    porcentagem_resolvidos_na_hora = round(
        (daily_stats["total_resolvidos_na_hora"].sum() / total_atendimentos_por_dia)
        * 100,
        2,
    )
    media_resolvidos_na_hora = round(daily_stats["total_resolvidos_na_hora"].mean(), 2)
    desvio_padrao_resolvidos_na_hora = round(
        daily_stats["total_resolvidos_na_hora"].std(), 2
    )
    maximo_resolvidos_na_hora = round(daily_stats["total_resolvidos_na_hora"].max(), 2)
    minimo_resolvidos_na_hora = round(daily_stats["total_resolvidos_na_hora"].min(), 2)


# ------------------------------------------------------------------------------------------------


    total_resolvidos_depois = daily_stats["total_resolvidos_depois"].sum()
    porcentagem_resolvidos_depois = round(
        (daily_stats["total_resolvidos_depois"].sum() / total_atendimentos_por_dia)
        * 100,
        2,
    )
    media_resolvidos_depois = round(daily_stats["total_resolvidos_depois"].mean(), 2)
    desvio_resolvidos_depois = round(daily_stats["total_resolvidos_depois"].std(), 2)
    maximo_resolvidos_depois = round(daily_stats["total_resolvidos_depois"].max(), 2)
    minimo_resolvidos_depois = round(daily_stats["total_resolvidos_depois"].min(), 2)


# ------------------------------------------------------------------------------------------------


    total_notas_promotoras = daily_stats["notas_positivas"].sum()
    porcentagem_notas_promotoras = round(
        (daily_stats["notas_positivas"].sum() / total_atendimentos_por_dia) * 100, 2
    )
    media_notas_promotoras = round(daily_stats["notas_positivas"].mean(), 2)
    desvio_padrao_notas_promotoras = round(daily_stats["notas_positivas"].std(), 2)
    maximo_notas_promotoras = round(daily_stats["notas_positivas"].max(), 2)
    minimo_notas_promotoras = round(daily_stats["notas_positivas"].min(), 2)


# ------------------------------------------------------------------------------------------------


    total_notas_detratoras = daily_stats["notas_negativas"].sum()
    porcentagem_notas_detratoras = round(
        (daily_stats["notas_negativas"].sum() / total_atendimentos_por_dia) * 100, 2
    )
    media_notas_detratoras = round(daily_stats["notas_negativas"].mean(), 2)
    desvio_padrao_notas_detratoras = round(daily_stats["notas_negativas"].std(), 2)
    maximo_notas_detratoras = round(daily_stats["notas_negativas"].max(), 2)
    minimo_notas_detratoras = round(daily_stats["notas_negativas"].min(), 2)


# ------------------------------------------------------------------------------------------------


    satisfacao_geral = round(
        (
            daily_stats["notas_positivas"].sum()
            / (
                daily_stats["notas_positivas"].sum()
                + daily_stats["notas_negativas"].sum()
            )
        )
        * 100,
        2,
    )
    conversão_geral = round(
        (
            (
                daily_stats["notas_positivas"].sum()
                + daily_stats["notas_negativas"].sum()
            )
            / total_atendimentos_por_dia
        )
        * 100,
        2,
    )



    html = f"""
<!DOCTYPE html>
<html>
    <head>
    <meta charset="UTF-8">

    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            line-height: 1.6;
        }}

        hr {{
            height: 2px;
            border-width: 0;
            color: gray;
            background-color: gray;
        }}

        h1, 
        h2 {{
            text-align: center;
            color: #333;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}

        th,
        td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}

        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        
        .main-header {{
            padding-right: 100px;
        }}

        .legend {{
            text-align: center; /* Centraliza os itens na div */
            font-size: 0.8em; /* Reduz o tamanho das legendas */
            color: gray;
        }}

        .legend  p {{
            display: inline-block; /* Coloca os elementos lado a lado */
            margin: 0 10px; /* Espaçamento horizontal entre os itens */
            font-size: 0.9em; /* Ajusta o tamanho das legendas individualmente */
            white-space: nowrap; /* Evita quebra de linha nos textos */
        }}

        .footer {{
            margin-top: 30px;
            text-align: center;
            font-size: 0.8em;
            color: gray;
            margin-top: 370px;
        }}

    </style>
</head>

<body>
    <h1>Relatório de Desempenho</h1>
    <h2>Relatório geral</h2>
    <p><strong>Data:</strong> {data}</p>
    <p><strong>Responsável:</strong> Ronald Lopes </p>
    
    <hr>
    
    <p><strong>Atendimentos do mês:</strong> {total_atendimentos_por_dia}</p>
    <p><strong>Atendimentos com a Matriz do mês:</strong> {total_atendimentos_por_dia_matriz}</p>
    <p><strong>Satisfação geral do mês:</strong> {satisfacao_geral}%</p>
    <p><strong>Conversão geral do mês:</strong> {conversão_geral}%</p>
    
    <hr>
    
    <h2>Estatísticas</h2>
    <table>
        <tr>
            <th class="main-header">Métrica</th> <!-- Métricas -->
            <th>Total</th> <!-- Total Geral -->
            <th>%</th> <!-- Porcentagem em relação ao Total-->
            <th>xMédia</th> <!-- Média -->
            <th>Desvio Padrão</th> <!-- Desvio Padrão -->
            <th>Máximo</th> <!-- Máximo dos valores -->
            <th>Mínimo</th> <!-- Mínimo dos valores -->
        </tr>
        <tr>
            <td>Atendimentos por dia</td> <!-- Métricas: Satisfação -->
            <td>{total_atendimentos_por_dia}</td>
            <td>---</td> <!-- Porcentagem em relação ao Total-->
            <td>{media_atendimentos_por_dia}</td> <!-- Média -->
            <td>{desvio_padrao_atendimentos_por_dia}</td> <!-- Desvio Padrão -->
            <td>{maximo_atendimentos_por_dia}</td> <!-- Máximo -->
            <td>{minimo_atendimentos_por_dia} </td> <!-- Mínimo -->
        </tr>
        <tr>
            <td>Convertidos por dia</td> <!-- Métricas: Satisfação -->
            <td>{total_convertidos_por_dia}</td>
            <td>{porcentagem_convertidos_por_dia}%</td> <!-- Porcentagem em relação ao Total-->
            <td>{media_convertidos_por_dia}</td> <!-- Média -->
            <td>{desvio_padrao_convertidos_por_dia}</td> <!-- Desvio Padrão -->
            <td>{maximo_convertido_por_dia}</td> <!-- Máximo -->
            <td>{minimo_convertido_por_dia} </td> <!-- Mínimo -->
        </tr>
        <tr>
            <td>Atendimentos com a matriz</td> <!-- Métricas: Satisfação -->
            <td>{total_atendimentos_por_dia_matriz}</td>
            <td>{porcentagem_atendimentos_por_dia_matriz}%</td> <!-- Porcentagem em relação ao Total-->
            <td>{media_atendimentos_por_dia_matriz}</td> <!-- Média -->
            <td>{desvio_padrao_atendimentos_por_dia_matriz}</td> <!-- Desvio Padrão -->
            <td>{maximo_atendimentos_por_dia_matriz}</td> <!-- Máximo -->
            <td>{minimo_atendimentos_por_dia_matriz} </td> <!-- Mínimo -->
        </tr>
        <tr>
            <td>Não convertidos por dia </td> <!-- Métricas: Conversão -->
            <td>{total_nao_convertido_por_dia}</td> <!-- Total Geral -->
            <td>{porcentagem_nao_convertido_por_dia}%</td> <!-- Porcentagem em relação ao Total-->
            <td>{media_nao_convertido_por_dia}</td> <!-- Média -->
            <td>{desvio_padrao_nao_convertido_por_dia}</td> <!-- Desvio Padrão -->
            <td>{maximo_nao_convertido_por_dia}</td> <!-- Máximo dos valores -->
            <td>{minimo_nao_convertido_por_dia}</td> <!-- Mínimo dos valores -->
        </tr>
        <tr>
            <td>Resolvidos no mesmo dia</td> <!-- Métricas: Acessos com a Matriz -->
            <td>{total_resolvidos_na_hora}</td> <!-- Total Geral -->
            <td>{porcentagem_resolvidos_na_hora}%</td> <!-- Porcentagem em relação ao Total-->
            <td>{media_resolvidos_na_hora}</td> <!-- Média -->
            <td>{desvio_padrao_resolvidos_na_hora}</td> <!-- Desvio Padrão -->
            <td>{maximo_resolvidos_na_hora}</td> <!-- Máximo dos valores -->
            <td>{minimo_resolvidos_na_hora}</td> <!-- Mínimo dos valores -->
        </tr>
            <td>Resolvidos depois</td> <!-- Métricas: Acessos com a Matriz -->
            <td>{total_resolvidos_depois}</td> <!-- Total Geral -->
            <td>{porcentagem_resolvidos_depois}%</td> <!-- Porcentagem em relação ao Total-->
            <td>{media_resolvidos_depois}</td> <!-- Média -->
            <td>{desvio_resolvidos_depois}</td> <!-- Desvio Padrão -->
            <td>{maximo_resolvidos_depois}</td> <!-- Máximo dos valores -->
            <td>{minimo_resolvidos_depois}</td> <!-- Mínimo dos valores -->
        </tr>
        <tr>
            <td>Notas promotoras</td> <!-- Métricas: Acessos com a Matriz -->
            <td>{total_notas_promotoras}</td> <!-- Total Geral -->
            <td>{porcentagem_notas_promotoras}%</td> <!-- Porcentagem em relação ao Total-->
            <td>{media_notas_promotoras}</td> <!-- Média -->
            <td>{desvio_padrao_notas_promotoras}</td> <!-- Desvio Padrão -->
            <td>{maximo_notas_promotoras}</td> <!-- Máximo dos valores -->
            <td>{minimo_notas_promotoras}</td> <!-- Mínimo dos valores -->
        </tr>
        <tr>
            <td>Notas detratoras</td> <!-- Métricas: Acessos com a Matriz -->
            <td>{total_notas_detratoras}</td> <!-- Total Geral -->
            <td>{porcentagem_notas_detratoras}%</td> <!-- Porcentagem em relação ao Total-->
            <td>{media_notas_detratoras}</td> <!-- Média -->
            <td>{desvio_padrao_notas_detratoras}</td> <!-- Desvio Padrão -->
            <td>{maximo_notas_detratoras}</td> <!-- Máximo dos valores -->
            <td>{minimo_notas_detratoras}</td> <!-- Mínimo dos valores -->
        </tr>
    </table>
    
    <div class="legend">
        <p><strong>%:</strong> Percentual em relação ao total</p>
    </div>
    
    <div class="footer">
        <p>Em caso de duvidas, consultar o setor de desenvolvimento.</p>
    </div>
    
    <div style="page-break-before: always;"></div>
"""

#------------------------------------ ANALISTA ---------------------------------------
#------------------------------------ ANALISTA ---------------------------------------
#------------------------------------ ANALISTA ---------------------------------------
#------------------------------------ ANALISTA ---------------------------------------
#------------------------------------ ANALISTA ---------------------------------------


    for analista in daily_stats_analyst['analyst'].unique():
        analista_data = daily_stats_analyst[daily_stats_analyst['analyst'] == analista]
        
        analista_data_matriz = daily_stats_analyst_matriz[daily_stats_analyst_matriz['analista'] == analista] 


#-------------------------------------------------------------------------------------------------

        analista_total_atendimentos_por_dia = analista_data["total_atendimentos"].sum()
        analista_media_atendimentos_por_dia = round(analista_data["total_atendimentos"].mean(), 2)
        analista_desvio_padrao_atendimentos_por_dia = round(
            analista_data["total_atendimentos"].std(), 2
        )
        analista_maximo_atendimentos_por_dia = round(analista_data["total_atendimentos"].max(), 2)
        analista_minimo_atendimentos_por_dia = round(analista_data["total_atendimentos"].min(), 2)

# ------------------------------------------------------------------------------------------------


        analista_total_atendimentos_por_dia_matriz = analista_data_matriz["total_atendimentos"].sum()
        analista_porcentagem_atendimentos_por_dia_matriz = round(
            (analista_total_atendimentos_por_dia_matriz / analista_total_atendimentos_por_dia)
            * 100,
            2,
        )
        analista_media_atendimentos_por_dia_matriz = round(analista_data_matriz["total_atendimentos"].mean(), 2)
        analista_desvio_padrao_atendimentos_por_dia_matriz = round(analista_data_matriz["total_atendimentos"].std(), 2)
        analista_maximo_atendimentos_por_dia_matriz = round(analista_data_matriz["total_atendimentos"].max(), 2)
        analista_minimo_atendimentos_por_dia_matriz = round(analista_data_matriz["total_atendimentos"].min(), 2)

# ------------------------------------------------------------------------------------------------

        analista_total_convertidos_por_dia = analista_data["total_convertido_por_dia"].sum()
        analista_porcentagem_convertidos_por_dia = round(
            (analista_data["total_convertido_por_dia"].sum() / analista_total_atendimentos_por_dia)
            * 100,
            2,
        )
        analista_media_convertidos_por_dia = round(analista_data["total_convertido_por_dia"].mean(), 2)
        analista_desvio_padrao_convertidos_por_dia = round(
            analista_data["total_convertido_por_dia"].std(), 2
        )
        analista_maximo_convertido_por_dia = round(analista_data["total_convertido_por_dia"].max(), 2)
        analista_minimo_convertido_por_dia = round(analista_data["total_convertido_por_dia"].min(), 2)

# ------------------------------------------------------------------------------------------------

        analista_total_nao_convertido_por_dia = analista_data["total_nao_convertido_por_dia"].sum()
        analista_porcentagem_nao_convertido_por_dia = round(
            (analista_data["total_nao_convertido_por_dia"].sum() / analista_total_atendimentos_por_dia)
            * 100,
            2,
        )
        analista_minimo_nao_convertido_por_dia = round(
            analista_data["total_nao_convertido_por_dia"].min(), 2
        )
        analista_media_nao_convertido_por_dia = round(
            analista_data["total_nao_convertido_por_dia"].mean(), 2
        )
        analista_desvio_padrao_nao_convertido_por_dia = round(
            analista_data["total_nao_convertido_por_dia"].std(), 2
        )
        analista_maximo_nao_convertido_por_dia = round(
            analista_data["total_nao_convertido_por_dia"].max(), 2
        )

# ------------------------------------------------------------------------------------------------

        analista_total_resolvidos_na_hora = analista_data["total_resolvidos_na_hora"].sum()
        analista_porcentagem_resolvidos_na_hora = round(
            (analista_data["total_resolvidos_na_hora"].sum() / analista_total_atendimentos_por_dia)
            * 100,
            2,
        )
        analista_media_resolvidos_na_hora = round(analista_data["total_resolvidos_na_hora"].mean(), 2)
        analista_desvio_padrao_resolvidos_na_hora = round(
            analista_data["total_resolvidos_na_hora"].std(), 2
        )
        analista_maximo_resolvidos_na_hora = round(analista_data["total_resolvidos_na_hora"].max(), 2)
        analista_minimo_resolvidos_na_hora = round(analista_data["total_resolvidos_na_hora"].min(), 2)

# ------------------------------------------------------------------------------------------------

        analista_total_resolvidos_depois = analista_data["total_resolvidos_depois"].sum()
        analista_porcentagem_resolvidos_depois = round(
            (analista_data["total_resolvidos_depois"].sum() / analista_total_atendimentos_por_dia)
            * 100,
            2,
        )
        analista_media_resolvidos_depois = round(analista_data["total_resolvidos_depois"].mean(), 2)
        analista_desvio_resolvidos_depois = round(analista_data["total_resolvidos_depois"].std(), 2)
        analista_maximo_resolvidos_depois = round(analista_data["total_resolvidos_depois"].max(), 2)
        analista_minimo_resolvidos_depois = round(analista_data["total_resolvidos_depois"].min(), 2)

# ------------------------------------------------------------------------------------------------

        analista_total_notas_promotoras = analista_data["notas_positivas"].sum()
        analista_porcentagem_notas_promotoras = round(
            (analista_data["notas_positivas"].sum() / analista_total_atendimentos_por_dia) * 100, 2
        )
        analista_media_notas_promotoras = round(analista_data["notas_positivas"].mean(), 2)
        analista_desvio_padrao_notas_promotoras = round(analista_data["notas_positivas"].std(), 2)
        analista_maximo_notas_promotoras = round(analista_data["notas_positivas"].max(), 2)
        analista_minimo_notas_promotoras = round(analista_data["notas_positivas"].min(), 2)

# ------------------------------------------------------------------------------------------------

        analista_total_notas_detratoras = analista_data["notas_negativas"].sum()
        analista_porcentagem_notas_detratoras = round(
            (analista_data["notas_negativas"].sum() / analista_total_atendimentos_por_dia) * 100, 2
        )
        analista_media_notas_detratoras = round(analista_data["notas_negativas"].mean(), 2)
        analista_desvio_padrao_notas_detratoras = round(analista_data["notas_negativas"].std(), 2)
        analista_maximo_notas_detratoras = round(analista_data["notas_negativas"].max(), 2)
        analista_minimo_notas_detratoras = round(analista_data["notas_negativas"].min(), 2)

# ------------------------------------------------------------------------------------------------

        analista_satisfacao_geral = round(
            (
                analista_data["notas_positivas"].sum()
                / (
                    analista_data["notas_positivas"].sum()
                    + analista_data["notas_negativas"].sum()
                )
            )
            * 100,
            2,
        )
        analista_conversão_geral = round(
            (
                (
                    analista_data["notas_positivas"].sum()
                    + analista_data["notas_negativas"].sum()
                )
                / analista_total_atendimentos_por_dia
            )
            * 100,
            2,
        )

        html_analista = f"""
        
        <h1>Relatório de Desempenho</h1>
        <h2>Relatório Individual dos Analistas de Suporte</h2>
        
        <hr>
    
            <p><strong>Data:</strong> {data} </p>
            <p><strong>Analista:</strong> {analista} </p>
            <p><strong>Atendimentos do mês:</strong> {analista_total_atendimentos_por_dia}</p>
            <p><strong>Atendimentos com a Matriz do mês:</strong> {analista_total_atendimentos_por_dia_matriz}</p>
            <p><strong>Satisfação geral do mês:</strong> {analista_satisfacao_geral}%</p>
            <p><strong>Conversão geral do mês:</strong> {analista_conversão_geral}%</p>
            
        <hr>
        
        <h2>Estatísticas</h2>
        
        <table>
            <tr>
                <th class="main-header">Métrica</th> <!-- Métricas -->
                <th>Total</th> <!-- Total Geral -->
                <th>%</th> <!-- Porcentagem em relação ao Total-->
                <th>xMédia</th> <!-- Média -->
                <th>Desvio Padrão</th> <!-- Desvio Padrão -->
                <th>Maxímo</th> <!-- Máximo dos valores -->
                <th>Mínimo</th> <!-- Mínimo dos valores -->
            </tr>
            <tr>
                <td>Atendimentos</td> <!-- Métricas: Satisfação -->
                <td>{analista_total_atendimentos_por_dia}</td>
                <td>---</td> <!-- Porcentagem em relação ao Total-->
                <td>{analista_media_atendimentos_por_dia}</td> <!-- Média -->
                <td>{analista_desvio_padrao_atendimentos_por_dia}</td> <!-- Desvio Padrão -->
                <td>{analista_maximo_atendimentos_por_dia}</td> <!-- Máximo -->
                <td>{analista_minimo_atendimentos_por_dia} </td> <!-- Mínimo -->
            </tr>
            <tr>
                <td>Conversão</td> <!-- Métricas: Satisfação -->
                <td>{analista_total_convertidos_por_dia}</td>
                <td>{analista_porcentagem_convertidos_por_dia}%</td> <!-- Porcentagem em relação ao Total-->
                <td>{analista_media_convertidos_por_dia}</td> <!-- Média -->
                <td>{analista_desvio_padrao_convertidos_por_dia}</td> <!-- Desvio Padrão -->
                <td>{analista_maximo_convertido_por_dia}</td> <!-- Máximo -->
                <td>{analista_minimo_convertido_por_dia} </td> <!-- Mínimo -->
            </tr>
            <tr>
                <td>Atendimentos com a matriz</td> <!-- Métricas: Satisfação -->
                <td>{analista_total_atendimentos_por_dia_matriz}</td>
                <td>{analista_porcentagem_atendimentos_por_dia_matriz}%</td> <!-- Porcentagem em relação ao Total-->
                <td>{analista_media_atendimentos_por_dia_matriz}</td> <!-- Média -->
                <td>{analista_desvio_padrao_atendimentos_por_dia_matriz}</td> <!-- Desvio Padrão -->
                <td>{analista_maximo_atendimentos_por_dia_matriz}</td> <!-- Máximo -->
                <td>{analista_minimo_atendimentos_por_dia_matriz} </td> <!-- Mínimo -->
            </tr>
            <tr>
                <td>Não convertidos</td> <!-- Métricas: Conversão -->
                <td>{analista_total_nao_convertido_por_dia}</td> <!-- Total Geral -->
                <td>{analista_porcentagem_nao_convertido_por_dia}%</td> <!-- Porcentagem em relação ao Total-->
                <td>{analista_media_nao_convertido_por_dia}</td> <!-- Média -->
                <td>{analista_desvio_padrao_nao_convertido_por_dia}</td> <!-- Desvio Padrão -->
                <td>{analista_maximo_nao_convertido_por_dia}</td> <!-- Máximo dos valores -->
                <td>{analista_minimo_nao_convertido_por_dia}</td> <!-- Mínimo dos valores -->
            </tr>
            <tr>
                <td>Resolvidos no mesmo dia</td> <!-- Métricas: Acessos com a Matriz -->
                <td>{analista_total_resolvidos_na_hora}</td> <!-- Total Geral -->
                <td>{analista_porcentagem_resolvidos_na_hora}%</td> <!-- Porcentagem em relação ao Total-->
                <td>{analista_media_resolvidos_na_hora}</td> <!-- Média -->
                <td>{analista_desvio_padrao_resolvidos_na_hora}</td> <!-- Desvio Padrão -->
                <td>{analista_maximo_resolvidos_na_hora}</td> <!-- Máximo dos valores -->
                <td>{analista_minimo_resolvidos_na_hora}</td> <!-- Mínimo dos valores -->
            </tr>
                <td>Resolvidos depois</td> <!-- Métricas: Acessos com a Matriz -->
                <td>{analista_total_resolvidos_depois}</td> <!-- Total Geral -->
                <td>{analista_porcentagem_resolvidos_depois}%</td> <!-- Porcentagem em relação ao Total-->
                <td>{analista_media_resolvidos_depois}</td> <!-- Média -->
                <td>{analista_desvio_resolvidos_depois}</td> <!-- Desvio Padrão -->
                <td>{analista_maximo_resolvidos_depois}</td> <!-- Máximo dos valores -->
                <td>{analista_minimo_resolvidos_depois}</td> <!-- Mínimo dos valores -->
            </tr>
            <tr>
                <td>Notas promotoras</td> <!-- Métricas: Acessos com a Matriz -->
                <td>{analista_total_notas_promotoras}</td> <!-- Total Geral -->
                <td>{analista_porcentagem_notas_promotoras}%</td> <!-- Porcentagem em relação ao Total-->
                <td>{analista_media_notas_promotoras}</td> <!-- Média -->
                <td>{analista_desvio_padrao_notas_promotoras}</td> <!-- Desvio Padrão -->
                <td>{analista_maximo_notas_promotoras}</td> <!-- Máximo dos valores -->
                <td>{analista_minimo_notas_promotoras}</td> <!-- Mínimo dos valores -->
            </tr>
            <tr>
                <td>Notas detratoras</td> <!-- Métricas: Acessos com a Matriz -->
                <td>{analista_total_notas_detratoras}</td> <!-- Total Geral -->
                <td>{analista_porcentagem_notas_detratoras}%</td> <!-- Porcentagem em relação ao Total-->
                <td>{analista_media_notas_detratoras}</td> <!-- Média -->
                <td>{analista_desvio_padrao_notas_detratoras}</td> <!-- Desvio Padrão -->
                <td>{analista_maximo_notas_detratoras}</td> <!-- Máximo dos valores -->
                <td>{analista_minimo_notas_detratoras}</td> <!-- Mínimo dos valores -->
            </tr>
        </table>
        
        <div class="legend">
            <p>%: Percentual em relação ao total</p>
        </div>
        

        <div class="footer">
            <p>Em caso de duvidas, consultar o setor de desenvolvimento.</p>
        </div>
        

        <div style="page-break-before: always;"></div>
        
        """
            
        html += html_analista
    
    html += f"""
    
        </body>

        </html>
    """
    return html

def exportar_pdf(html, filename="relatorio.pdf"):
    pdfkit.from_string(html, filename)
    with open(filename, "rb") as pdf_file:
        pdf_data = pdf_file.read()
    os.remove(filename)  
    return pdf_data
