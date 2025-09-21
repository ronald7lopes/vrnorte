import requests
import pandas as pd
import time
import os


def check_matriz_status():
    print("\n\n********Verificando tickets da Matriz********\n\n")

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
    tickets_data_csv = os.path.join(output_dir, "matriz_ids.csv")

    if not os.path.exists(tickets_data_csv):
        print("Arquivo CSV não encontrado.")
        return

    df = pd.read_csv(tickets_data_csv)

    statuses_in_progress = [
        "Em atendimento",
        "Aguardando resposta da Matriz",
        "Aguardando Retorno Cliente",
        "AGUARDANDO PRODUTO",
        "AGUARDANDO N2",
        "EM ANALISE N2",
        "Aguardando N2 - Fiscal",
        "Em Analise - Produto",
    ]

    df_in_progress = df[df["status"].isin(statuses_in_progress)]

    for index, row in df_in_progress.iterrows():
        time.sleep(1.5)
        ticket_id = row["ticket_id"]
        current_status = row["status"]
        analyst = row["analista"]

        ticket_url = f"https://api.movidesk.com/public/v1/tickets?token=62520dc9-f9ff-4e8a-9b77-8f378f93d22b&id={ticket_id}"
        response = requests.get(ticket_url)

        if response.status_code != 200:
            print(
                f"❌ Falha ao buscar status para o ticket {ticket_id}: {response.status_code}"
            )
            continue

        ticket_data = response.json()
        updated_status = ticket_data.get("status")

        if updated_status and updated_status != current_status:
            df.loc[index, "status"] = updated_status
            print(f"✅ Status do ticket {ticket_id} atualizado para {updated_status}.")
        else:
            print(
                f"ℹ️ O Ticket {ticket_id} do {analyst} continua com o status '{updated_status}'"
            )

    # Salva as mudanças de volta no arquivo CSV
    df.to_csv(tickets_data_csv, index=False)
    print("✔️ Verificação de status concluída.")
