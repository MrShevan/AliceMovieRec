# coding: utf-8
# Импортирует поддержку UTF-8.
from __future__ import unicode_literals

# Импортируем модули для работы с JSON и логами.
import json
import logging

# Импортируем подмодули Flask для запуска веб-сервиса.
from flask import Flask, request
application = Flask(__name__)


logging.basicConfig(level=logging.DEBUG)

# Хранилище данных о сессиях.
sessionStorage = {}


def handle_dialog(event, context):
    translate_state = event.get('state', {}).get('session', {}).get('translate', {})
    last_phrase = event.get('state', {}).get('session', {}).get('last_phrase')
    intents = event.get('request', {}).get('nlu', {}).get('intents', {})
    command = event.get('request', {}).get('command')

    print(event)

    return {
        'version': event['version'],
        'session': event['session'],
        'response': {
            'text': "Test", 
            'end_session': False
        },
        'session_state': {'translate': translate_state, 'last_phrase': "last_phrase"}
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
