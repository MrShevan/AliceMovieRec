# coding: utf-8
# Импортирует поддержку UTF-8.
from __future__ import unicode_literals

# Импортируем модули для работы с JSON и логами.
import json
import logging
import pandas as pd
import pymorphy2


# Импортируем подмодули Flask для запуска веб-сервиса.
from flask import Flask, request
application = Flask(__name__)

films_data = pd.read_csv("films.csv")

morph = pymorphy2.MorphAnalyzer()

logging.basicConfig(level=logging.DEBUG)

# Хранилище данных о сессиях.
sessionStorage = {}

from tmdbv3api import TMDb, Movie

tmdb = TMDb()
tmdb.api_key = 'e1783cc13e6f2086cc492c5da6921749'
tmdb.language = 'ru'

movie = Movie()


def get_movie_id_by_name(name):
    search = movie.search(name)
    if search:
        first = search[0]
        return first.id
    return None


def get_similar_by_id(id_, topn=3):
    recommendations = movie.recommendations(movie_id=id_)
    if recommendations:
        return recommendations[:topn]


def get_film(genre, freshness):
    print(genre, freshness)
    threshold = "2010"
    if freshness == "new":
        films_data_tmp = films_data[(films_data["genre"] == genre) & (films_data["year"].astype(str) >= threshold)]
    else:
        films_data_tmp = films_data[(films_data["genre"] == genre) & (films_data["year"].astype(str) < threshold)]

    print(films_data_tmp)

    if len(films_data_tmp) > 0:
        films_data_tmp.sample(frac=1)
        film_name = films_data_tmp.iloc[0]["name"]
        return film_name
    return "Властелин Колец"


def handle_dialog(event, context):
    genre_phrase = event.get('state', {}).get('session', {}).get('genre', "")
    year_phrase = event.get('state', {}).get('session', {}).get('year', "")
    intents = event.get('request', {}).get('nlu', {}).get('intents', {})

    end_session = False
    new_state = None
    response_text = "Привет! Я помогу тебе подобрать фильм." \
                    " Я могу посоветовать Вам комедию, боевик, триллер, драму или фильм ужасов. Что Вас интересует?"

    if event["session"]["new"]:
        pass

    elif "help" in intents:
        response_text = """
            Я могу рекомендовать фильмы по жанру, найти похожий фильм или найти фильм с вашими любимыми актерами
            """
    elif "genre" in intents:
        genre_phrase = list(intents["genre"]["slots"].keys())[0]
        new_state = {'genre': genre_phrase}
        response_text = "Хотите посмотреть новинку или классику?"

        # добавить проверку - есть ли у нас такой жанр или нет

    elif "year" in intents:
        year_phrase = list(intents["year"]["slots"].keys())[0]
        if genre_phrase == "":
            pass
        new_state = {"year": year_phrase, "genre": genre_phrase}

        film_name = get_film(new_state["genre"], new_state["year"])
        response_text = f"Посмотри {film_name}"
        end_session = True

    elif "similar" in intents:
        print("TESTTTTTTT")
        print(intents)
        film_name = intents["similar"]["slots"]["film"]["value"]
        print(film_name)
        film_name = morph.parse(film_name)[0]
        norm_form = film_name.normal_form
        print(norm_form)

        mid = get_movie_id_by_name(norm_form)
        response_text = "Не нашла похожие фильмы"
        if mid:
            similar_names = get_similar_by_id(mid, topn=3)
            response_text = f"Похожие фильмы - {' '.join([sim.title for sim in similar_names])}"

        print(response_text)
    else:
        response_text = "Вы молодец"

    print(event)
    print("\n\n\n\n")

    return {
        'version': event['version'],
        'session': event['session'],
        'response': {
            'text': response_text,
            'end_session': end_session
        },
        'session_state': new_state
    }


@application.route('/', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)

    response = {
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {
            "end_session": False
        }
    }

    response = handle_dialog(request.json, response)

    logging.info('Response: %r', response)

    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2
    )


if __name__ == '__main__':
    application.run(host="0.0.0.0", port=5000)
