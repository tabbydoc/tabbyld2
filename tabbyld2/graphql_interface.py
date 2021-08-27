import json
import requests
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.requests import RequestsHTTPTransport

# URL-адрес для получения токена
URL = "https://isdct.talisman.ispras.ru/auth/realms/demo/protocol/openid-connect/token"
# Параметры тела POST-запроса
PAYLOAD = "client_id=web-ui&grant_type=password&client_secret=039f8182-db0a-45d9-bc25-e1a979b06bfd&scope=openid&" \
          "username=test&password=ElephantMonocycleRally"
# Параметры заголовка POST-запроса
HEADERS = {"content-type": "application/x-www-form-urlencoded"}
# URL-адрес конечной точки GraphQL
GRAPHQL_ENDPOINT = "https://isdct.talisman.ispras.ru/graphql"
# Публичный ключ для авторизации
PUBLIC_KEY = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnRiAKiUSxZUSQYaVLB0p3jUgAkzE7A9l6WJR/UDekHWkTe/+4WIB23WywP" \
          "XBRR2FIDqH0oJPLciXTQX7HeofSCA3uKcCGlFwjTPgoGv5IZ8C0NrkurmefAEvlcjfHVo6I0FxE3Q9BAhFOn2F3MB5fDLgy77CLoJb" \
          "XdRbV7gDtGIC/t6OoY9xxfAnmA6fWmZfqgnyhraVM0xBLALpvoUz6VHPXpQqoQFbsFJVcTBkut+XtsUWBOjiQTsmtXSVHDz+UDPGII" \
          "qfVdPx+7tRm30DxhqYZtWcmHTJ88zZQlLRT3YAT7+PonsiYQCwXS6yrnuEDKWHn0R5hAWKwfLuy7d/pwIDAQAB"


def get_token():
    """
    Получение токена для доступа к GraphQL.
    :return: токен
    """
    access_token = None
    # POST-запрос на получение токена
    response = requests.request("POST", URL, data=PAYLOAD, headers=HEADERS)
    # Если данные с токеном есть
    if json.loads(response.text)["access_token"]:
        access_token = response.json().get("access_token")

    return access_token


def get_concept_types():
    """
    Получение списка типов концептов (классов) из БЗ Talisman.
    :return: список типов концептов
    """
    # Получение токена для доступа к GraphQL
    access_token = get_token()

    # Формирование заголовков запроса
    headers = {
        "x-api-key": PUBLIC_KEY,
        "Authorization": "Bearer " + access_token
    }
    # Подключение к конечной точке GraphQL в асинхронном режиме
    # transport = AIOHTTPTransport(url="https://demo.talisman.ispras.ru/", headers={"Authorization": access_token})
    # Подключение к конечной точке GraphQL в синхронном режиме
    transport = RequestsHTTPTransport(url=GRAPHQL_ENDPOINT, headers=headers, use_json=True)
    client = Client(transport=transport, fetch_schema_from_transport=True)
    # GraphQL-запрос
    query = gql(
        """
        query {
          listConceptType {
            id,
            name
          }
        }
        """
    )
    # Выполнение GraphQL-запроса
    response = client.execute(query)

    return response["listConceptType"]


def get_concept_link_types():
    """
    Получение списка типов связей (отношений между классами) из БЗ Talisman.
    :return: список типов связей
    """
    # Получение токена для доступа к GraphQL
    access_token = get_token()

    # Формирование заголовков запроса
    headers = {
        "x-api-key": PUBLIC_KEY,
        "Authorization": "Bearer " + access_token
    }
    # Подключение к конечной точке GraphQL в асинхронном режиме
    # transport = AIOHTTPTransport(url="https://demo.talisman.ispras.ru/", headers={"Authorization": access_token})
    # Подключение к конечной точке GraphQL в синхронном режиме
    transport = RequestsHTTPTransport(url=GRAPHQL_ENDPOINT, headers=headers, use_json=True)
    client = Client(transport=transport, fetch_schema_from_transport=True)
    # GraphQL-запрос
    query = gql(
        """
        query {
          listConceptLinkType {
            name
          }
        }
        """
    )
    # Выполнение GraphQL-запроса
    response = client.execute(query)

    # Формирование списка названий типов концептов (классов) из БЗ Talisman
    result = []
    if "listConceptLinkType" in response:
        for item in response["listConceptLinkType"]:
            result.append(item["name"])

    return result


def add_concept(name, concept_type_id):
    """
    Добавление нового концепта в базу знаний платформы TALISMAN.
    :param name: название концепта
    :param concept_type_id: идентификатор типа концепта
    :return: словарь с добавленным концептом
    """
    # Получение токена для доступа к GraphQL
    access_token = get_token()

    # Формирование заголовков запроса
    headers = {
        "x-api-key": PUBLIC_KEY,
        "Authorization": "Bearer " + access_token
    }
    # Подключение к конечной точке GraphQL в асинхронном режиме
    # transport = AIOHTTPTransport(url="https://demo.talisman.ispras.ru/", headers={"Authorization": access_token})
    # Подключение к конечной точке GraphQL в синхронном режиме
    transport = RequestsHTTPTransport(url=GRAPHQL_ENDPOINT, headers=headers, use_json=True)
    client = Client(transport=transport, fetch_schema_from_transport=True)
    # GraphQL-запрос
    query = gql(
        """
        mutation($name: String!, $conceptTypeId: ID!) {
          addConcept(form: {name: $name, conceptTypeId: $conceptTypeId}) {
            id,
            name
          }
        }
        """
    )
    params = {
        "name": name,
        "conceptTypeId": concept_type_id
    }
    # Выполнение GraphQL-запроса
    response = client.execute(query, variable_values=params)

    return response
