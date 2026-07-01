import telebot
import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

def get_wb_search(query):

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept': '*/*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Referer': 'https://www.wildberries.ru/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
    }
    params = {
        'ab_testing': 'false',
        'appType': 1,
        'curr': 'rub',
        'dest': -1257786,
        'query': query,
        'resultset': 'catalog',
        'sort': 'popular',
        'spp': 27,
        'suppressSpellcheck': 'false',
        'ffeedbackpoints': 1
    }
    time.sleep(2)

    try:
        session = requests.Session()
        response = session.get(
            'https://search.wb.ru/exactmatch/ru/common/v4/search',
            params=params,
            headers=headers
        )

        if response.status_code != 200:
            print(f"Ошибка {response.status_code}: {response.text}")
            return None

        data = response.json()

        return data['data']['products']

    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return None

def make_product_image_url(product_id):
    vol = product_id // 100000
    part = product_id // 1000
    for i in range(int((vol + 364.60) / 171.35)-2, 24):
        if i == 0:
            continue
        basket = "0" + str(i) if i < 10 else str(i)
        image_url =  f"https://basket-{basket}.wbbasket.ru/vol{vol}/part{part}/{product_id}/images/c516x688/1.webp"
        response = requests.head(
            image_url,
            timeout=2,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        )

        if response.status_code == 200:
            if requests.get(image_url, timeout=3).status_code == 200:
                return image_url

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f'<i>Приветствую, <b>{message.from_user.first_name}</b>. Напишите запрос для WB: </i>', parse_mode='html')

@bot.message_handler(content_types=['text'])
def reply(message):
    products = get_wb_search(message.text)

    if not products:
        bot.send_message(message.chat.id, 'Товары не найдены :(\nПопробуйте другой запрос')
        return

    products.sort(key=lambda x: (x['feedbackPoints'] / x['salePriceU'] if x['salePriceU'] else 0), reverse=True)

    for product in products[:10]:

        price = product.get('salePriceU', product.get('priceU', 0)) // 100
        cashback = product.get('feedbackPoints', 0)
        url_img = make_product_image_url(product['id'])

        caption = (
            f'<b>{product.get("name", "Без названия")}</b>\n\n'
            f'🏷 <b>Цена: {price}</b>\n'
            f'💰 <b>Кешбек: {cashback}</b>\n\n'
            f'🔗 <a href="https://www.wildberries.ru/catalog/{product["id"]}/detail.aspx">Ссылка на товар</a>'
        )

        try:
            bot.send_photo(
                chat_id=message.chat.id,
                photo=url_img,
                caption=caption,
                parse_mode='html',
                timeout=10
            )
        except Exception as e:
            print(f"Ошибка: {e}")
            try:
                bot.send_message(
                    chat_id=message.chat.id,
                    text=caption,
                    parse_mode='HTML'
                )
            except Exception as e:
                print(f"Не удалось отправить товар: {e}")

        time.sleep(0.5)

if __name__ == '__main__':
    print('Бот запущен...')
    while True:
        try:
            bot.polling(none_stop=True)
        except KeyboardInterrupt:
            print("Бот остановлен")
        except Exception as e:
            print(f"Ошибка: {e}")

