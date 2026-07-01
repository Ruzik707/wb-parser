import asyncio
import aiohttp
import tqdm
from tqdm.asyncio import tqdm_asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import time
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

if TOKEN is None:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

if CHANNEL_ID is None:
    raise RuntimeError("TELEGRAM_CHANNEL_ID is not set")

def load_sent_products():
    """ Загружает список отправленных товаров """
    with open('sent_products.txt', 'r') as file:
        return [f.strip() for f in file.readlines()]
        
def save_sent_products(ids):
    """ Сохраняет список отправленных товаров """
    with open('sent_products.txt', 'w') as f:
        f.write('\n'.join(ids))

def save_excel(products):
    df = pd.DataFrame(products).set_index('id')
    df.to_excel(f'Товары ({len(products)} штук).xlsx')

async def image_url(session, product_id):
    vol = product_id // 100000
    part = product_id // 1000
    baskets = [f"{i:02d}" for i in range(1, 30)]

    for basket in baskets:
        image_url = f"https://basket-{basket}.wbbasket.ru/vol{vol}/part{part}/{product_id}/images/c516x688/1.webp"
        try:
            async with session.head(
                image_url,
                timeout=aiohttp.ClientTimeout(total=2),
                headers={'User-Agent': 'Mozilla/5.0'}
            ) as response:
                if response.status == 200:
                    return image_url
        except (aiohttp.ClientError, asyncio.TimeoutError):
            continue

    return 'https://yt3.googleusercontent.com/ytc/AIdro_nJ5Hj93K904Ahd0EdGu2wVfhYs7zw_6oWKU-9aZtvrqXc=s900-c-k-c0x00ffffff-no-rj'

async def send_tg(session, product):
    try:
        im_url = await image_url(session, product['id'])
        end_price = product['price'] - product['cashback']
        caption = (
            f"\n<a href='{product['link']}'><b>{product['name']}</b></a>\n\n"
            f"<b>Цена:</b> {product['price']}₽ (Кешбек: {product['cashback']})\n"
            f"<b>Цена с кешбеком:</b> {end_price}🔥\n"
            f"<b>Рейтинг:</b> {product['rating']}⭐ ({product['feedback_count']} отзывов)\n\n"
            )
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        payload = {
            "chat_id": CHANNEL_ID,
            "photo": im_url,
            "caption": caption,
            "parse_mode": "HTML"
        }
        ### почему то ошибка 400 выходит
        async with session.post(url, json=payload, timeout=10) as response:
            response.raise_for_status()
            if response.status != 200:
                return f'Не получилось отправить товар {product["id"]}'
            
    except Exception as e:
        print(f'Ошибка в send_tg: {e}')

async def get_catalog(session):
    """ Получаем каталог товаров """
    url = 'https://static-basket-01.wbbasket.ru/vol0/data/main-menu-ru-ru-v3.json'
    try:
        async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15) as response:
            response.raise_for_status()
            return await response.json()
    except Exception as e:
        print(f'Ошибка в get_catalog: {e}')

async def category_urls(catalog):
    """ Извлекаем все URL из каталога """
    base_url = 'https://www.wildberries.ru'
    urls = []
    
    def process_item(item):
        """ Внутренняя функция для обработки элементов """
        if isinstance(item, dict):
            if item.get('url') and not item.get('childs'):
                urls.append(base_url + item['url'])
            
            if item.get('childs'):
                for child in item['childs']:
                    process_item(child)

        elif isinstance(item, list):
            for subitem in item:
                process_item(subitem)

    process_item(catalog)
    return urls[4:]

async def parse_page(session, shard, query, page, price_min, price_max, semaphore):
    """ Парсинг одной страницы категории """
    headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}
    url = (f'https://catalog.wb.ru/catalog/{shard}/v2/catalog?ab_testing=false'
           f'&appType=1&{query}&curr=rub&dest=-1257786&hide_dtype=10'
           f'&lang=ru&sort=popular&spp=30&page={page}&ffeedbackpoints=1')
    async with semaphore:
        try:
            async with session.get(url, headers=headers, timeout=15) as response:
                if response.status == 429:
                    return []
                if response.status == 200:
                    data = await response.json()
                    return data.get('data', {}).get('products', {})
                return []
        except Exception as e:
            print(f'Ошибка в parse_page: {e}')
        finally:
            await asyncio.sleep(0.1)

async def parse_category(session, url):
    """ Парсинг одной категории """
    try:
        catalog_data = await get_catalog()
        
        def f(catalog, url):
            url_path = url.replace('https://www.wildberries.ru', '')
            for item in catalog:
                if item.get('childs'):
                    child = f(item.get('childs'), url)      
                    if child:
                        return child
                if item.get('url') == url_path:
                    return item
            return None
            
        if not f(catalog_data, url):
            return []
            
        category_info = f(catalog_data, url)
        shard = category_info.get('shard', '')
        query = category_info.get('query', '')
        if not shard or not query:
            return 'shard или query не найден'

        prices = [
            (0, 50000),
            (50000, 100000),
            (100000, 200000),
            (200000, 500000),
            (500000, 1000000)
        ]

        semaphore = asyncio.Semaphore(20)
        products = []
        for price_min, price_max in prices:
            for page in range(1, 21):
                page_products = parse_page(session, shard, query, page, price_min, price_max, semaphore)
                if page_products: 
                    products.append(page_products)
        results = await asyncio.gather(*products)
        prods = []
        for p in results:
            if p:
                prods.extend(p)
    
        return [{
            'id': p.get('id'),
            'name': p.get('name'),
            'price': p.get('sizes')[0].get('price').get('product') // 100,
            'cashback': p.get('feedbackPoints', 0),
            'rating': p.get('reviewRating', 0),
            'feedback_count': p.get('feedbacks', 0),
            'link': f'https://www.wildberries.ru/catalog/{p.get("id")}/detail.aspx'
        } for p in prods]
    
    except Exception as e:
        print(f'Ошибка в parse_category: {e}')

async def main():
    """ Функция основного парсинга """
    start_time = time.time()
    cnt = 0
    new_products = []
    sent_products = load_sent_products()
    headers = {"User-Agent": "Mozilla/5.0"}
    connector = aiohttp.TCPConnector(limit=20)

    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        catalog = await get_catalog()
        urls = await category_urls(catalog)
        urls = urls[:100]
        sent_products = load_sent_products()
        
        print('Начинаем парсинг...')
        tasks = [parse_category(session, url) for url in urls]
        res = []
        for future in tqdm_asyncio.as_completed(tasks, desc='Обработка категорий'):
            res.extend(await future)
        for product in res:
            per = int(product['cashback']) / int(product['price']) * 100
            if per > 50 and str(product['id']) not in sent_products:
                new_products.append(product)  
    save_excel(new_products)
    print(f'Отправлено {cnt} новых товаров!')
    print(f'Время работы парсинга {(time.time() - start_time) / 60:.2f} минут')
