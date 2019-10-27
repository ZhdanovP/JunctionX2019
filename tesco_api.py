import random
from collections import defaultdict
from typing import Optional, Dict, List

from requests import get

from dao import ORM

TESCO_API_KEY = '438ec90168ae495ca1dd9993f594e957'
TESCO_API_URL = 'https://dev.tescolabs.com'


# === BASE TESCO API ===

def __make_request_to_tesco(url: str, params: Dict) -> Optional[Dict]:
    """
    A common method to get response by tesco api
    """
    headers = {'Ocp-Apim-Subscription-Key': TESCO_API_KEY}
    try:
        response = get(url, params=params, headers=headers)
        if response.ok:
            return response.json()
        print(f'Cannot get response from {url} with params {params}. Returned code: {response.status_code}')
    except Exception as e:
        print(e)


def grocery_search(query: str, offset: int = 0, limit: int = 20) -> Optional[Dict]:
    grocery_url = f'{TESCO_API_URL}/grocery/products'
    params = {'query': query, 'offset': offset, 'limit': limit}
    return __make_request_to_tesco(grocery_url, params)


def product_data(gtin: Optional[str] = None, tpnb: Optional[str] = None,
                 tpnc: Optional[str] = None, catid: Optional[str] = None) -> Optional[Dict]:
    grocery_url = f'{TESCO_API_URL}/product'
    params = {'gtin': gtin, 'tpnb': tpnb, 'tpnc': tpnc, 'catid': catid}
    return __make_request_to_tesco(grocery_url, params)


def store_location(near: str = 'Budapest', like: Optional[str] = None,
                   offset: int = 0, limit: int = 100) -> Optional[Dict]:
    grocery_url = f'{TESCO_API_URL}/locations/search'
    params = {'offset': offset, 'limit': limit}
    if near:
        params['sort'] = f'near:{near}'
    if like:
        params['like'] = f'name:{like}'
    return __make_request_to_tesco(grocery_url, params)


# === COMPLEX FUNCTIONS FOR DATA PROCESSING ===

def get_product_data(gtin):
    db = ORM()

    product = db.get_cache(gtin)

    if product:
        return product[0]

    prod = product_data(gtin)
    prod = prod.get('products', [])
    if not prod:
        print(f'There is not products with gtin {gtin}')
        return None
    descr = prod[0].get('description')
    first_word_of_descr = descr.split(' ')[0]
    tpnc = prod[0].get('tpnc')

    offset = 0
    glosery = grocery_search(descr, offset)
    product = get_necessary_data_from_grocery_search(glosery, tpnc)

    while not product and offset < 10:
        offset += 1
        glosery = grocery_search(first_word_of_descr, offset)
        product = get_necessary_data_from_grocery_search(glosery, tpnc)

    if product:
        db.add_cache(gtin, **product)

    return product


def get_necessary_data_from_grocery_search(grocery_search: Dict, tpnc: str) -> Optional[Dict]:
    """
    Extracts necessary info from product json.
    Returns: 'image', 'name' and 'description'
    """
    products_list = grocery_search.get('uk', {}).get('ghs', {}).get('products', {}).get('results', [])
    if not products_list:
        print('There are no products')
        return None
    results = [result for result in products_list if str(result.get('id')) == tpnc]
    if not results:
        print(f'There are no results with tpnc {tpnc}')
        return {}
    result = results[0]
    description = result.get('description')[0] if result.get('description') else ''
    return {'image': result.get('image'), 'name': result.get('name'), 'description': description,
            'department': result.get('department'), 'weight': result.get('AverageSellingUnitWeight'),
            'price': result.get('price')}


def get_all_products_from_grocery_search(grocery_search: Dict) -> Optional[List[Dict]]:
    products_list = grocery_search.get('uk', {}).get('ghs', {}).get('products', {}).get('results', [])
    if not products_list:
        print('There are no products')
        return None
    products = []
    for product in products_list:
        prod = product_data(tpnc=product.get('id'))
        gtin = prod.get('products')[0].get('gtin')
        description = product.get('description')[0] if product.get('description') else ''
        products.append({'image': product.get('image'), 'name': product.get('name'), 'description': description,
                         'department': product.get('department'), 'weight': product.get('AverageSellingUnitWeight'),
                         'price': product.get('price'), 'gtin': gtin})
    return products


# === DATA FOR FRONTEND ===

def get_shop_list() -> List[Dict]:
    orm = ORM()
    shops = orm.get_shops()
    return shops


def get_goods_list(shops: List[Dict]) -> List[Dict]:
    orm = ORM()

    goods_list = []
    _cashes = orm.get_caches()
    cashes = {cache.get('gtin'): cache for cache in _cashes}
    _catalog = orm.get_catalog_all()
    catalog = defaultdict(list)
    for product in _catalog:
        catalog[product.get('shop_id')].append(product)

    for shop in shops:
        goods = []
        shop_catalog = catalog.get(shop.get('id'))
        if not shop_catalog:
            shop.update({'count': 0})
            goods_list.append({'id': shop.get('id'), 'goods': goods})
            continue

        categories_dict = defaultdict(list)
        already_checked_products = set()
        for current_product in shop_catalog:
            product = cashes.get(current_product.get('gtin'))
            if not product:
                continue
            qtt = sum([_product['quantity'] for _product in shop_catalog
                       if _product.get('gtin') == product.get('gtin')])

            if product.get('image') not in already_checked_products:
                categories_dict[product.get('department')].append({'image': product.get('image'),
                                                                   'name': product.get('name'),
                                                                   'description': product.get('description'),
                                                                   'qtt': qtt})
                already_checked_products.add(product.get('image'))

        shop.update({'count': len(already_checked_products)})

        for category, products in categories_dict.items():
            goods.append({'category': category, 'products': products})

        goods_list.append({'id': shop.get('id'), 'goods': goods})

    return goods_list


# === FILL THE TABLES ===

def extract_stores_from_results(stores: Dict, filter_town: Optional[str] = 'Budapest'):
    """
    The function is used only one time to fill `Shop` table by values.
    :param stores: Result of store_location() function works
    :param filter_town: A town name to filter stores for
    :return: Nothing, just placed target stores to the DB
    """
    all_stores = stores.get('results', [])
    target_stores = []
    for store in all_stores:
        store_data = store.get('location', {})
        coords = store_data.get('geo', {}).get('coordinates', {})
        address = store_data.get('contact', {}).get('address')
        if filter_town and filter_town not in address.get('town'):
            continue
        street = address.get('lines', [{}])[0].get('text')
        target_stores.append({'_id': store_data.get('id'),
                              'address': street,
                              'lon': coords.get('longitude'),
                              'lat': coords.get('latitude'),
                              '_type': store_data.get('classification', {}).get('type'),
                              'name': store_data.get('name')})

    orm = ORM()
    for store in target_stores:
        orm.add_shop(**store)


def fill_cache_table():
    """
    The function is used only for filling cache table
    """
    products = []
    for query in ['bread', 'milk', 'rice']:
        grocery = grocery_search(query)
        products += get_all_products_from_grocery_search(grocery)

    orm = ORM()
    for product in products:
        orm.add_cache(**product)


def fill_catalog_table():
    orm = ORM()

    caches = orm.get_caches()
    shops = orm.get_shops()

    for shop in shops:
        for items in range(1, random.randrange(3, 8)):
            for index in range(random.randrange(0, len(caches))):
                gtin = caches[index].get('gtin')
                orm.add_catalog(gtin, random.randint(1, 6), shop.get('id'))


if __name__ == '__main__':
    # Tests
    # glosery = grocery_search('Tescobritish', 0)
    # print(get_necessary_data_from_grocery_search(glosery, 254656543))
    # print(product_data('4548736003446'))
    # stores = store_location()
    # extract_stores_from_results(stores)
    # print(get_product_data('05010003000131'))
    # fill_cache_table()
    fill_catalog_table()
