import requests
import pandas as pd
import time
import os


def check_ticket_evaluations():
    print("\n\n********Verificando avaliações de tickets********\n\n")

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
    survey_results = os.path.join(output_dir, "survey_results.csv")

    if not os.path.exists(survey_results):
        print("Arquivo CSV não encontrado.")
        return

    df = pd.read_csv(survey_results)
    
    
    # usar como padrão (valida mudança de nota por dia)
    current_date = time.strftime("%Y-%m-%d")
    # usar sempre no final do mês para validar todas as notas modificadas
    # current_date = '2025-07'

    df_today = df[df["createdDate"].str.startswith(current_date)]

    for index, row in df_today.iterrows():
        time.sleep(1.5)
        ticket_id = row["ticket_id"]
        current_type = row["type"]
        current_value = row["value"]
        analyst = row["analyst"]

        if current_type == "S/A" and current_value == "S/N":
            survey_url = f"https://api.movidesk.com/public/v1/survey/responses?token=62520dc9-f9ff-4e8a-9b77-8f378f93d22b&ticketId={ticket_id}"
            response = requests.get(survey_url)

            if response.status_code != 200:
                print(
                    f"❌ Falha ao buscar avaliação para o ticket {ticket_id}: {response.status_code}"
                )
                continue

            survey_data = response.json()
            items = survey_data.get("items", [])

            if items:
                df.loc[index, "type"] = items[0].get("type", "S/A")
                df.loc[index, "value"] = items[0].get("value", "S/N")
                print(f"Ticket {ticket_id} atualizado com sucesso. ✅")
            else:
                print(
                    f"ℹ️ Nenhuma avaliação encontrada para o ticket {ticket_id}. {analyst}"
                )
# mudar valor da nota minima
        elif current_type == "3" and int(current_value) < 6:
            time.sleep(2.5)
            survey_url = f"https://api.movidesk.com/public/v1/survey/responses?token=62520dc9-f9ff-4e8a-9b77-8f378f93d22b&ticketId={ticket_id}"
            response = requests.get(survey_url)

            if response.status_code != 200:
                print(
                    f"❌ Falha ao buscar reavaliação para o ticket {ticket_id}: {response.status_code}"
                )
                continue

            survey_data = response.json()
            items = survey_data.get("items", [])

            if items:
                new_value = str(items[0].get("value", "S/N"))

                # Se o valor mudou, atualize no CSV
                if new_value != current_value:
                    df.loc[index, "value"] = new_value
                    print(
                        f"✅ Nota do ticket {ticket_id} atualizada de {current_value} para {new_value}. {analyst} ✅"
                    )
                else:
                    print(
                        f"ℹ️ Ticket {ticket_id} já possui a nota mais recente: {current_value}. {analyst}."
                    )
            else:
                print(
                    f"❌ Nenhuma reavaliação encontrada para o ticket {ticket_id}. {analyst}"
                )

    # Salvar as mudanças no arquivo CSV
    df.to_csv(survey_results, index=False)
    print("✔️ Verificação de avaliações concluída.")
