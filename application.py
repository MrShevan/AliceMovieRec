# coding: utf-8
# Импортирует поддержку UTF-8.
from __future__ import unicode_literals

# Импортируем модули для работы с JSON и логами.
import json
import logging
import pandas as pd

# Импортируем подмодули Flask для запуска веб-сервиса.
from flask import Flask, request
application = Flask(__name__)

films_data = pd.read_csv("films.csv")


logging.basicConfig(level=logging.DEBUG)

# Хранилище данных о сессиях.
sessionStorage = {}


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
    response_text = "Привет! Я помогу тебе подобрать фильм. Какой жанр вам нравится?"

    if event["session"]["new"]:
        pass
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
