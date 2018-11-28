import requests
import csv
import time
from bs4 import BeautifulSoup
from multiprocessing.pool import ThreadPool

URLS = [
	'https://ru.autoplius.lt/objavlenija/b-u-avtomobili?make_date_from=2011&sell_price_to=15000&fuel_id=32&make_id_list=67&make_id%5B67%5D=682&slist=636345659&order_by=3&order_direction=DESC'
]

RESULT_FILENAME = 'result.csv'

DELIMITER = ';'

THREADS = 2

PAUSE = 0

DOMAIN = 'https://ru.autoplius.lt'

HEADERS = {
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
	'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'
}

CSV_HEADERS = [
	('ID', 'id'),
	('Марка', 'brand'),
	('Модель', 'model'),
	('Дата выпуска', 'release_date'),
	('Объем двигателя', 'engine_capacity'),
	('Тип топлива', 'fuel_type'),
	('Коробка передач', 'transmission_type'),
	('Мощность (кВт)', 'engine_power'),
	('Тип кузова', 'body_type'),
	('Пробег (км)', 'mileage'),
	('Страна первичной регистрации', 'initial_registration_country'),
	('Стоимость', 'price'),
	('Телефон продавца', 'phone'),
	('Местонахождение', 'location'),
	('Ссылка', 'url'),
]

def get_full_url(url):
	if not url.startswith(('http://', 'https://')):
		if url.startswith('//'):
			return 'http:' + url
		if url.startswith('/'):
			return DOMAIN + url
		return '%s/%s' % (DOMAIN, url)
	return url

def get_soup(url):
	r = requests.get(get_full_url(url), headers=HEADERS)
	return BeautifulSoup(r.content, 'html.parser')

def get_table_data(item_page):
	rows = item_page.select('.col-5 .parameter-row')
	data = {}
	for row in rows:
		key = row.find('div', class_='parameter-label')
		if not key:
			continue
		value = row.find('div', class_='parameter-value')
		if not value:
			continue
		data[key.text.strip()] = value.text.strip()
	return data

def get_item_id(item_url):
	return int(item_url[:-5].rsplit('-', 1)[-1])

def get_price(item):
	price = item.select_one('.announcement-pricing-info strong')
	if price:
		price = price.text.strip().split(' ')
		return ''.join(price[:-1])
	return ''

def get_engine_power(item):
	engine_power = item.find('span', attrs={'title': 'Мощность'})
	if engine_power:
		return engine_power.text.strip().split(' ')[0]
	return ''

def get_mileage(table_data):
	mileage = table_data.get('Пробег', '').strip().split(' ')
	return ''.join(mileage[:-1])

def get_phone(item_page):
	phone = item_page.find('a', class_='seller-phone-number')
	if phone:
		return phone.text.strip()
	return ''

def get_location(item_page):
	location = item_page.find('div', class_='seller-contact-location')
	if location:
		return location.text.strip()
	return ''

def get_brand_and_model(item_page):
	bc = item_page.select('.breadcrumbs a')
	return bc[-2].text.strip(), bc[-1].text.strip()

def get_body_type_and_engine_capacity(item_page):
	title = item_page.select_one('.page-title h1').text.strip().split(', ')
	if len(title) == 3:
		engine_cap = title[1].split(' ')[0]
	else:
		engine_cap = ''
	return title[-1], engine_cap

def process_item(item):
	data = {}
	data['url'] = get_full_url(item.get('href'))
	data['id'] = get_item_id(data['url'])
	item_page = get_soup(data['url'])
	data['brand'], data['model'] = get_brand_and_model(item_page)
	data['body_type'], data['engine_capacity'] = get_body_type_and_engine_capacity(item_page)
	table_data = get_table_data(item_page)
	data['release_date'] = table_data.get('Дата выпуска', '').strip()
	data['fuel_type'] = table_data.get('Тип топлива', '').strip()
	data['transmission_type'] = table_data.get('Коробка передач', '').strip()
	data['engine_power'] = get_engine_power(item)
	data['mileage'] = get_mileage(table_data)
	data['initial_registration_country'] = table_data.get('Страна первичной регистрации', '').strip()
	data['price'] = get_price(item)
	data['phone'] = get_phone(item_page)
	data['location'] = get_location(item_page)
	return data

def get_last_id():
	try:
		with open(RESULT_FILENAME, 'r') as f:
			reader = csv.reader(f, delimiter=DELIMITER)
			next(reader)
			return int(next(reader)[0])
	except (IOError, ValueError, StopIteration):
		return 0

def has_new_items(results):
	return results and results[0]['id'] > get_last_id()

def main():
	pool = ThreadPool(THREADS)
	results = []

	for page_url in URLS:
		while page_url:
			page = get_soup(page_url)
			items = page.select('.auto-lists .announcement-item')

			for result in pool.imap_unordered(process_item, items):
				results.append(result)

			next_page_a = page.select_one('.pagination a.next')
			if next_page_a:
				page_url = next_page_a.get('href')
				time.sleep(PAUSE)
			else:
				page_url = None

	results.sort(key=lambda x: x['id'], reverse=True)

	if has_new_items(results):
		print('New items appeared')

	with open(RESULT_FILENAME, 'w', encoding='utf-8') as f:
		f.write('\ufeff')
		writer = csv.writer(f, delimiter=DELIMITER)
		writer.writerow(h for h, k in CSV_HEADERS)

		for result in results:
			writer.writerow(result[k] for h, k in CSV_HEADERS)

if __name__ == '__main__':
	main()