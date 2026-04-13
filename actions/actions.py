from typing import Any, Text, Dict, List
import requests
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

# Integração com a API pública do Open Library — sem autenticação necessária
BASE_URL = "https://openlibrary.org/search.json"


def formatar_livros(docs: list, limite: int = 5) -> str:
    """Organiza e retorna os livros encontrados pela API."""
    if not docs:
        return None

    saida = ""
    for i, doc in enumerate(docs[:limite]):
        nome_livro = doc.get("title", "Título não disponível")
        autores = ", ".join(doc.get("author_name", ["Autor não informado"]))
        ano = doc.get("first_publish_year", "Ano não disponível")
        saida += f"{i+1}. {nome_livro} — {autores} ({ano})\n"

    return saida


def extrair_termo(tracker: Tracker, slot: str) -> str:
    """
    Tenta obter o valor do slot. Se vazio, extrai a entidade diretamente
    da última mensagem. Se ainda vazio, usa o texto bruto como fallback.
    """
    # 1. Tenta pelo slot
    valor = tracker.get_slot(slot)
    if valor:
        return valor

    # 2. Tenta pela entidade na última mensagem
    entidades = tracker.latest_message.get("entities", [])
    for e in entidades:
        if e.get("entity") == slot:
            return e.get("value")

    # 3. Fallback: texto bruto digitado pelo usuário
    return tracker.latest_message.get("text")


class ActionBuscarPorTitulo(Action):

    def name(self) -> Text:
        return "action_buscar_por_titulo"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        titulo = extrair_termo(tracker, "titulo")

        if not titulo:
            dispatcher.utter_message(response="utter_perguntar_titulo")
            return []

        try:
            resposta = requests.get(BASE_URL, params={"title": titulo, "limit": 5})
            dados = resposta.json()
            docs = dados.get("docs", [])
            resultados = formatar_livros(docs)

            if resultados:
                mensagem = f"Localizei os seguintes títulos para \"{titulo}\":\n\n{resultados}"
            else:
                mensagem = f"Não encontrei nenhum livro com o título \"{titulo}\". Tente um título diferente."

        except Exception as e:
            print(f"Falha na consulta à API: {e}")
            mensagem = "Houve um problema ao realizar a pesquisa. Por favor, tente novamente."

        dispatcher.utter_message(text=mensagem)
        return [SlotSet("titulo", None)]


class ActionBuscarPorAutor(Action):

    def name(self) -> Text:
        return "action_buscar_por_autor"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        autor = extrair_termo(tracker, "autor")

        if not autor:
            dispatcher.utter_message(response="utter_perguntar_autor")
            return []

        try:
            resposta = requests.get(BASE_URL, params={"author": autor, "limit": 5})
            dados = resposta.json()
            docs = dados.get("docs", [])
            resultados = formatar_livros(docs)

            if resultados:
                mensagem = f"Encontrei as seguintes obras de \"{autor}\":\n\n{resultados}"
            else:
                mensagem = f"Não localizei nenhuma obra de \"{autor}\". Verifique o nome e tente novamente."

        except Exception as e:
            print(f"Falha na consulta à API: {e}")
            mensagem = "Houve um problema ao realizar a pesquisa. Por favor, tente novamente."

        dispatcher.utter_message(text=mensagem)
        return [SlotSet("autor", None)]


class ActionBuscarPorAssunto(Action):

    def name(self) -> Text:
        return "action_buscar_por_assunto"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        assunto = extrair_termo(tracker, "assunto")

        if not assunto:
            dispatcher.utter_message(response="utter_perguntar_assunto")
            return []

        try:
            resposta = requests.get(BASE_URL, params={"subject": assunto, "limit": 5})
            dados = resposta.json()
            docs = dados.get("docs", [])
            resultados = formatar_livros(docs)

            if resultados:
                mensagem = f"Veja os títulos que encontrei sobre \"{assunto}\":\n\n{resultados}"
            else:
                mensagem = f"Não encontrei livros relacionados a \"{assunto}\". Tente um assunto diferente."

        except Exception as e:
            print(f"Falha na consulta à API: {e}")
            mensagem = "Houve um problema ao realizar a pesquisa. Por favor, tente novamente."

        dispatcher.utter_message(text=mensagem)
        return [SlotSet("assunto", None)]