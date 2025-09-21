import requests
import pandas as pd
import time
import os


def check_ticket_status():
    print("\n\n********Verificando status dos tickets...********\n\n")

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
    tickets_data_csv = os.path.join(output_dir, "survey_results.csv")

    if not os.path.exists(tickets_data_csv):
        print("⛔ Arquivo CSV não encontrado.")
        return

    df = pd.read_csv(tickets_data_csv)

    df_in_progress = df[
        (df["status"] == "Em atendimento")
        | (df["status"] == "Aguardando resposta da Matriz")
    ]

    for index, row in df_in_progress.iterrows():
        time.sleep(1.5)
        ticket_id = row["ticket_id"]
        current_status = row["status"]
        analyst = row["analyst"]
        organization = row['organization']
        createdBy = row['createdBy']

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
            print(
                f"✅ Status do ticket {ticket_id} do {analyst} foi atualizado para {updated_status}."
            )
        else:
            print(f"ℹ️ Ticket continua em 'Em atendimento': {ticket_id } - {organization}({createdBy}), {analyst}")

    # Salva as mudanças de volta no arquivo CSV
    df.to_csv(tickets_data_csv, index=False)
    print("✔️ Verificação de status concluída.")
