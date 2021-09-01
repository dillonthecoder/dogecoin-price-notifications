from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import requests
import json
import time
from datetime import datetime

DOGECOIN_PRICE_THRESHOLD = 0.29
IFTTT_WEBHOOKS_URL = 'https://maker.ifttt.com/trigger/{event}/with/key/{yourkey}'
DOGECOIN_API_URL = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

parameters = {
    'slug': 'dogecoin',
    'convert': 'USD'
}
headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': 'your_api_key_here',
}

session = Session()
session.headers.update(headers)


def get_latest_dogecoin_price():
    try:
        # might need to try global
        response = session.get(DOGECOIN_API_URL, params=parameters)
        data = json.loads(response.text)
        return data['data']['74']['quote']['USD']['price']
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)


def post_ifttt_webhook(event, value):
    data = {'value1': value}
    ifttt_event_url = IFTTT_WEBHOOKS_URL.format(event=event)
    requests.post(ifttt_event_url, json=data)


def format_dogecoin_history(dogecoin_history):
    rows = []
    for dogecoin_price in dogecoin_history:
        date = dogecoin_price['date'].strftime('%d.%m.%Y %H:%M')
        price = dogecoin_price['price']
        row = '{}: $<b>{}</b>'.format(date, price)
        rows.append(row)

    return '<br>'.join(rows)


def main():
    dogecoin_history = []
    while True:
        price = get_latest_dogecoin_price()
        date = datetime.now()
        dogecoin_history.append({'date': date, 'price': price})
        print('Working so far')
        print(get_latest_dogecoin_price())

        if price < DOGECOIN_PRICE_THRESHOLD:
            post_ifttt_webhook('dogecoin_price_emergency', price)

        if len(dogecoin_history) == 5:
            post_ifttt_webhook('dogecoin_price_update', format_dogecoin_history(dogecoin_history))
            dogecoin_history = []

        time.sleep(5 * 60)


if __name__ == '__main__':
    main()
