import requests
import json
import time
import csv

current_date = "2025-01-16"


# Função para fazer requisições à API do Movidesk com controle de taxa
def make_request(url):
    response = requests.get(url)
    return response


ticket_id = "2125571"

# URL da primeira requisição para obter tickets
tickets_url = (f"https://api.movidesk.com/public/v1/tickets/past?token=62520dc9-f9ff-4e8a-9b77-8f378f93d22b&id={ticket_id}")
# tickets_url = (f'https://api.movidesk.com/public/v1/survey/responses?token=fb22fdd3-b6a4-48c9-be02-50c7c3c800b5&ticketId={ticket_id}')

# tickets_url = (
#     f"https://api.movidesk.com/public/v1/tickets?"
#     f"token=62520dc9-f9ff-4e8a-9b77-8f378f93d22b&"
#     f"$select=statusHistories,lifeTimeWorkingTime,serviceThirdLevel,serviceSecondLevel,"
#     f"serviceFirstLevel,chatTalkTime,chatWaitingTime,urgency,resolvedInFirstCall,category,createdDate,status,origin,id&"
#     f"$filter=((ownerTeam eq 'Suporte Bel\u00e9m') or (ownerTeam eq 'Supervis\u00e3o Bel\u00e9m') or (ownerTeam eq 'Suporte Bel\u00e9m ')) and "
#     f"(createdDate gt {current_date})&"
#     f"$expand=createdBy($select=businessName),owner($select=businessName),"
#     f"clients($select=organization;$expand=organization($select=businessName))&$top=10000"
# )


# tickets_url = f"https://api.movidesk.com/public/v1/tickets?token=fb22fdd3-b6a4-48c9-be02-50c7c3c800b5&$select=status,origin,ownerTeam,createdDate,id&$filter=((ownerTeam eq 'Suporte Bel\u00e9m') or (ownerTeam eq 'Supervis\u00e3o Bel\u00e9m')) and (origin eq Movidesk.Core.Data.Enums.TicketOrigin'5') and (createdDate gt {current_date}T00:00:00.00z)&$expand=clients($select=businessName;$expand=organization($select=businessName)), owner($select=id,businessName)"
# matriz_tick = f"https://api.movidesk.com/public/v1/tickets?token=fb22fdd3-b6a4-48c9-be02-50c7c3c800b5&$select=status,origin,ownerTeam,createdDate,id&$filter=(ownerTeam eq 'PDV - Matriz') and (origin eq Movidesk.Core.Data.Enums.TicketOrigin'5') and (createdDate gt 2024-06-01T00:00:00.00z)&$expand=clients($select=businessName;$expand=organization($select=businessName)), owner($select=id,businessName)"


response_ticket_API = make_request(tickets_url)
print(response_ticket_API.status_code)
data2 = response_ticket_API.text
parse_ticket_json = json.loads(data2)

file_name2 = "ticket_data.json"
with open(file_name2, "w") as json_file:
    json.dump(parse_ticket_json, json_file, indent=4)


print("Processo completo.")
