import json
import requests

URL = ""


def init(port=9274):
    """
    Изменение порта для запуска сервиса DBpedia Lookup.
    :param port: номер порта (при импорте библиотеки порт 9274 задаётся по умолчанию)
    :return: URL с новым портом
    """
    global URL
    URL = f"http://localhost:{port}/lookup-application/api/search"


def get_entities(query: str, max_results: int = None, min_relevance: int = None, short_name: bool = False) -> list:
    """
    Получение набора (списка) сущностей кандидатов по строковому запросу.
    :param query: строка запроса
    :param max_results: максимальное количество сущностей кандидатов, возвращаемых за один поиск
    :param min_relevance: минимальная оценка релевантности запроса
    :param short_name: режим отображения короткого наименования сущности (без полного URI)
    :return: список найденных сущностей кандидатов
    """
    result_list = []

    parameters = {"query": query, "format": "JSON"}
    if max_results:
        parameters["maxResults"] = max_results
    if min_relevance:
        parameters["minRelevance"] = min_relevance

    try:
        response = requests.get(url=URL, params=parameters)

        if response.status_code == 200:
            json_response = json.loads(response.text)
            for doc in json_response["docs"]:
                if short_name:
                    result_list.append(doc["resource"][0].replace("http://dbpedia.org/resource/", ""))
                else:
                    result_list.append(doc["resource"][0])
            return result_list
        # else:
        #     raise requests.exceptions.ConnectionError(f"{response.status_code}")
    except requests.exceptions.RequestException as e:
        return result_list


init()
