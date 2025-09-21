"""
Arquivo principal contendo as funções necessárias para a extração dos dados da API
Para executar, basta executá-lo diretamente da pasta "API", e caso tenha internet
e o token esteja válido, iniciará a extração dos tickets.
"""

import datetime
import requests
import time
import pandas as pd
import schedule
import csv
import os
import json
import pprint as pp

from unidecode import unidecode
from check_survey import check_ticket_evaluations
from check_status import check_ticket_status
from check_matriz_survey import check_matriz_status


def extrair_informacoes(row):
    """
    Extrai informações sobre o analista e o time a partir de uma linha fornecida.

    A função tenta interpretar o conteúdo da `row` e extrair o nome do analista e
    o nome do time (organização). Lida com dois tipos de entrada:
      - String JSON: A função converte para objeto Python e extrai o primeiro item.
      - Lista de dicionários: Extrai o primeiro dicionário.

    Args:
        row: Linha da tabela que pode ser uma string no formato JSON ou uma lista.

    Returns:
        pd.Series: Uma série contendo duas informações:
            - [0]: Nome do analista (`businessName`).
            - [1]: Nome do time (`organization.businessName`).
            - Se a extração falhar, retorna [None, None].

    Exceções Tratadas:
        - json.JSONDecodeError: Quando a string JSON é inválida.
        - KeyError: Quando a chave não está presente no dicionário.
        - IndexError: Quando a lista fornecida está vazia ou incompleta.
    """
    try:
        if isinstance(row, str):
            client_info = json.loads(row.replace("'", '"'))[0]
        elif isinstance(row, list) and row:
            client_info = row[0]
        else:
            return pd.Series([None, None])

        # Garante valores padrão se as chaves não existirem
        analista = client_info.get("businessName", None)
        time = client_info.get("organization", {}).get("businessName", None)
        
        return pd.Series([analista, time])
    except (json.JSONDecodeError, KeyError, IndexError, TypeError) as e:
        return pd.Series([None, None])


def make_request(url):
    """
    Função responsável por criar uma comunicação com o URL 
    retornando a resposta da API,
    """
    response = requests.get(url)
    time.sleep(3)
    return response


def load_existing_ids_status(csv_file):
    """Carrega os IDs e status de tickets já registrados no CSV survey_results.csv.

    Args:
        csv_file: CSV survey_results.csv para executar as consultas.

    Returns:
        set: Conjunto de tuplas contendo (ticket_id, status) dos registros existentes.
    """
    if not os.path.exists(csv_file):
        return set()

    df = pd.read_csv(csv_file)
    return set(zip(df["ticket_id"], df["status"]))


def load_existing_ids(csv_file):
    """Carrega os IDs de tickets registrados na tabela `tickets_matriz`.

    Args:
        csv_file: CSV matriz_ids.csv para executar as consultas.

    Returns:
        set: Conjunto de IDs de tickets presentes na tabela `tickets_matriz`.
    """
    if not os.path.exists(csv_file) or os.stat(csv_file).st_size == 0:
        return set()
    try:
        df = pd.read_csv(csv_file)
        return set(df["ticket_id"])
    except pd.errors.EmptyDataError:
        return set()


def regex(text):
    """Remove acentos e caracteres especiais de uma string usando unidecode.

    Args:
        text (str): Texto contendo acentos e caracteres especiais.

    Returns:
        str: Texto normalizado, sem acentos ou caracteres especiais.
    """
    return unidecode(text) if text else ""


def fetch_and_process_tickets():
    """
    Função principal que busca, processa e armazena dados de tickets extraídos da API Movidesk.

    Esta função realiza as seguintes operações:
    1. **Busca de Tickets**:
        - Extrai tickets relacionados aos atendimentos dos clientes com os analistas de suporte.
        - Extrai tickets relacionados aos atendimentos dos analistas de suporte com a Matriz.

    2. **Verificação de Tickets**:
        - Compara os tickets extraídos com os já existentes no banco de dados.
        - Garante que apenas novos tickets sejam inseridos.

    3. **Avaliação de Tickets**:
        - Para cada ticket novo, realiza uma requisição à API de avaliações para obter a nota (se houver).
        - A avaliação inclui:
            - Tipo de avaliação (`type`), como "S/A" se não avaliado.
            - Valor da nota (`value`), como "S/N" se não houver nota registrada.
            - Um campo booleano (`emitido`) que indica se a avaliação é positiva (nota >= 7).

    4. **Armazenamento no Banco de Dados**:
        - Insere os dados dos tickets nos CSV's:
            - `matriz_ids.csv` (para tickets da matriz)
            - `survey_results.csv` (para todos os tickets com suas avaliações).

    5. **Verificações Finais**:
        - Executa funções auxiliares para verificar o status dos tickets e valores de avaliações.

    Exemplo de Dados Armazenados:
    - `ticket_id`: ID do ticket
    - `createdDate`: Data de criação do ticket (ajustada para UTC-3)
    - `status`: Status atual do ticket
    - `organization`: Nome da organização relacionada
    - `analyst`: Nome do analista responsável pelo ticket
    - `type`: Tipo da avaliação (ou 'S/A' se não avaliado)
    - `value`: Nota atribuída (ou 'S/N' se não houver avaliação)
    - `emitido`: Indica se a avaliação foi positiva (True ou False)

    Agendamento:
    - A função é executada a cada 3 minutos usando o módulo `schedule`.
    - O loop principal mantém o programa em execução contínua.

    Erros:
    - Em caso de falha na requisição à API, a função imprime o código de erro HTTP correspondente.

    """
    print("\n\n********Buscando novos Tickets********\n\n")
    
    intervals = [45, 15]
    """
    os valores dentro da lista "intervals" correspondem a uma subtração em número de dias
    com o dia atual. Cada valor dentro da lista é passado como step para o for loop.
    
    Exemplo: O primeiro valor da lista é 45. Nesse caso ele fará DIA_ATUAL - 45 DIAS.
    a API irá procurar os tickts dos últimos 45 dias.
    Após isso, passará para o próximo valor na lista, vamos supor "15"
    A API irá procurar os tickets dos ultimos 15 dias.
    
    Por que é feito dessa maneira? Por alguns motivos!
    
    1) A API só retorna por volta de 1000 tickets
    """

    for days_back in intervals:

        current_date = (
            datetime.datetime.now() - datetime.timedelta(days=days_back)
        ).strftime("%Y-%m-%d")
        # current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        # current_date = "2023-06-13"
        print(f"Puxando dados para a data {current_date}")
        output_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "data"
        )
        os.makedirs(output_dir, exist_ok=True)
        survey_results = os.path.join(output_dir, "survey_results.csv")
        matriz_csv_file = os.path.join(output_dir, "matriz_ids.csv")

        existing_ids_survey = load_existing_ids_status(survey_results)
        existing_ids_matriz = load_existing_ids(matriz_csv_file)

        belem_tickets = (
          # f"https://api.movidesk.com/public/v1/tickets/past?"
            f"https://api.movidesk.com/public/v1/tickets?"
            f"token=62520dc9-f9ff-4e8a-9b77-8f378f93d22b&"
            f"$select=statusHistories,lifeTimeWorkingTime,serviceThirdLevel,serviceSecondLevel,"
            f"serviceFirstLevel,chatTalkTime,chatWaitingTime,urgency,resolvedInFirstCall,category,createdDate,status,id&"
            f"$filter=((ownerTeam eq 'Suporte Bel\u00e9m') or (ownerTeam eq 'Supervis\u00e3o Bel\u00e9m') or (ownerTeam eq 'Suporte Bel\u00e9m ')) and "
            f"(origin eq Movidesk.Core.Data.Enums.TicketOrigin'5') and (createdDate gt {current_date})&"
            f"$expand=createdBy($select=businessName),owner($select=businessName),"
            f"clients($select=organization;$expand=organization($select=businessName))&$top=10000"
        )

        matriz_tickets = (
            f"https://api.movidesk.com/public/v1/tickets?"
            f"token=62520dc9-f9ff-4e8a-9b77-8f378f93d22b&$select"
            f"=serviceSecondLevel,serviceFirstLevel,urgency,category,status,ownerTeam,createdDate,id&$filter="
            f"((origin eq Movidesk.Core.Data.Enums.TicketOrigin'5') or (origin eq Movidesk.Core.Data.Enums.TicketOrigin'2')) and "
            f"(createdDate gt {current_date}T00:00:00.00z)"
            # f" and (clients/all(client: client/organization/businessName eq 'SKYONE  - Unidade Belem '))"
            f" and (clients/all(client: client/organization/businessName eq 'VRMAT - SKYONE  - Unidade Belem '))"
            f"&$expand=clients($select=businessName;$expand=organization($select=businessName)), "
            f"owner($select=id,businessName)&$top=10000"
        )

        response_ticket_API = make_request(belem_tickets)
        response_ticket_matriz_API = make_request(matriz_tickets)

        if (
            response_ticket_API.status_code != 200
            or response_ticket_matriz_API.status_code != 200
        ):
            print(f"Failed to fetch tickets: {response_ticket_API.status_code}")
            return

        parse_ticket_matriz_json = response_ticket_matriz_API.json()

        df_matriz = pd.json_normalize(parse_ticket_matriz_json)

        if not df_matriz.empty:
            df_matriz["clients"] = df_matriz["clients"].apply(
                lambda x: json.loads(x.replace("'", '"')) if isinstance(x, str) else x
            )            

            df_matriz[["analista", "time"]] = df_matriz["clients"].apply(extrair_informacoes)

            df_matriz["analista"] = df_matriz["analista"].where(df_matriz["analista"].notna(), "")

            df_matriz["analista"] = df_matriz.apply(
                lambda row: row["owner.businessName"] if pd.isna(row["analista"]) else row["analista"],
                axis=1,
            )

            df_matriz = df_matriz.drop(columns=["clients", "owner.id"])
            df_matriz = df_matriz[
                ~df_matriz["analista"].isin(["Suporte I", "Suporte II"])
            ]
            df_matriz = df_matriz[~df_matriz["ownerTeam"].isin(["Suporte Belém "])]

            # Filtra apenas os novos tickets que ainda não estão no CSV
            novos_tickets = df_matriz[~df_matriz["id"].isin(existing_ids_matriz)]

            if not novos_tickets.empty:
                # Adiciona os novos tickets ao CSV existente (modo append)
                novos_tickets.to_csv(
                    matriz_csv_file,
                    mode="a",
                    index=False,
                    header=not os.path.exists(matriz_csv_file),
                )
                print(f"{len(novos_tickets)} novos tickets adicionados.")
            else:
                print("Nenhum ticket da matriz encontrado.")

        parse_ticket_json = response_ticket_API.json()
        ticket_ids = []
        for ticket in parse_ticket_json:
            for client in ticket.get("clients", []):
                ticket_id = ticket.get("id", 0)
                status = regex(ticket.get("status", "Resolvido"))
                createdDate = ticket.get("createdDate", datetime.datetime.now())
                category = ticket.get("category", "Nao Informado")
                resolvedInFirstCall = ticket.get("resolvedInFirstCall", "Nao Informado")
                urgency = ticket.get("urgency", "Nao Informado")
                chatWaitingTime = ticket.get("chatWaitingTime", 0)
                chatTalkTime = ticket.get("chatTalkTime", 0)
                serviceFirstLevel = ticket.get("serviceFirstLevel", "Nao Informado")
                serviceSecondLevel = ticket.get("serviceSecondLevel", serviceFirstLevel)
                serviceThirdLevel = ticket.get("serviceThirdLevel", serviceSecondLevel)
                lifeTimeWorkingTime = ticket.get("lifeTimeWorkingTime", 0)
                owner = (
                    ticket["owner"]["businessName"]
                    if ticket.get("owner")
                    else ticket.get("ownerTeam", "Sem Nome")
                )
                client_name = (
                    client["organization"]["businessName"]
                    if client.get("organization")
                    else client.get("businessName", "Sem Nome")
                )
                createdBy = (
                    ticket["createdBy"]["businessName"]
                    if ticket.get("createdBy")
                    else "Sem Nome"
                )

                # Monta a tupla com exatamente 15 elementos
                ticket_tuple = (
                    ticket_id,
                    status,
                    createdDate,
                    category,
                    resolvedInFirstCall,
                    urgency,
                    chatWaitingTime,
                    chatTalkTime,
                    serviceFirstLevel,
                    serviceSecondLevel,
                    serviceThirdLevel,
                    lifeTimeWorkingTime,
                    client_name,
                    owner,
                    createdBy,
                )
                ticket_ids.append(ticket_tuple)

        # FOR LOOP
        ticket_data = []
        for (
            ticket_id,
            status,
            createdDate,
            category,
            resolvedInFirstCall,
            urgency,
            chatWaitingTime,
            chatTalkTime,
            serviceFirstLevel,
            serviceSecondLevel,
            serviceThirdLevel,
            lifeTimeWorkingTime,
            clients,
            owner,
            createdBy,
        ) in ticket_ids:
            if (ticket_id, status) in existing_ids_survey:
                continue

            survey_url = (
                f"https://api.movidesk.com/public/v1/survey/responses?token=62520dc9-f9ff-4e8a-9b77-8f378f93d22b&"
                f"ticketId={ticket_id}"
            )
            response_survey_API = make_request(survey_url)
            print(
                f"Ticket ID: {ticket_id}, Status Code: {response_survey_API.status_code}"
            )

            if response_survey_API.status_code != 200:
                print(
                    f"Failed to fetch survey responses for ticket {ticket_id}: {response_survey_API.status_code}"
                )
                continue

            parse_survey_json = response_survey_API.json()

            # Processa os itens da pesquisa
            items = parse_survey_json.get("items", [])
            if items:
                for item in items:
                    commentary = item.get("commentary", "")
                    commentary = (
                        commentary.replace("\n", ". ").strip() if commentary else ""
                    )
                    ticket_data.append(
                        {
                            "ticket_id": ticket_id,
                            "createdDate": createdDate,
                            "status": regex(status),
                            "category": regex(category),
                            "resolvedInFirstCall": resolvedInFirstCall,
                            "urgency": regex(urgency),
                            "chatWaitingTime": chatWaitingTime,
                            "chatTalkTime": round((chatTalkTime / 60),0) if chatTalkTime else 0,
                            "serviceFirstLevel": regex(serviceFirstLevel),
                            "serviceSecondLevel": regex(serviceSecondLevel),
                            "serviceThirdLevel": regex(serviceThirdLevel),
                            "lifeTimeWorkingTime": lifeTimeWorkingTime,
                            "organization": regex(clients),
                            "analyst": regex(owner),
                            "createdBy": regex(createdBy),
                            "type": item.get("type"),
                            "value": item.get("value"),
                            "comment": regex(commentary),
                        }
                    )
            else:
                ticket_data.append(
                    {
                        "ticket_id": ticket_id,
                        "createdDate": createdDate,
                        "status": regex(status),
                        "category": regex(category),
                        "resolvedInFirstCall": resolvedInFirstCall,
                        "urgency": regex(urgency),
                        "chatWaitingTime": chatWaitingTime,
                        "chatTalkTime": round((chatTalkTime / 60),0) if chatTalkTime else 0,
                        "serviceFirstLevel": regex(serviceFirstLevel),
                        "serviceSecondLevel": regex(serviceSecondLevel),
                        "serviceThirdLevel": regex(serviceThirdLevel),
                        "lifeTimeWorkingTime": lifeTimeWorkingTime,
                        "organization": regex(clients),
                        "analyst": regex(owner),
                        "createdBy": regex(createdBy),
                        "type": "S/A",
                        "value": "S/N",
                        "comment": "",
                    }
                )
        if ticket_data:
            with open(survey_results, "a", newline="") as csv_file:
                fieldnames = [
                    "ticket_id",
                    "createdDate",
                    "status",
                    "category",
                    "resolvedInFirstCall",
                    "urgency",
                    "chatWaitingTime",
                    "chatTalkTime",
                    "serviceFirstLevel",
                    "serviceSecondLevel",
                    "serviceThirdLevel",
                    "lifeTimeWorkingTime",
                    "organization",
                    "analyst",
                    "createdBy",
                    "type",
                    "value",
                    "comment",
                ]
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

                if os.stat(survey_results).st_size == 0:
                    writer.writeheader()
                writer.writerows(ticket_data)
            print(
                "Novos tickets adicionados com sucesso.",
                time.strftime("%d-%m-%Y - %H:%M:%S"),
            )
        else:
            print(
                "Nenhum ticket novo adicionado.", time.strftime("%d/%m/%Y - %H:%M:%S")
            )
    check_ticket_status()
    check_matriz_status()
    check_ticket_evaluations()


fetch_and_process_tickets()

schedule.every(2).minutes.do(fetch_and_process_tickets)

while True:
    schedule.run_pending()
    time.sleep(1)
