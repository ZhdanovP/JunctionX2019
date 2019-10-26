from typing import Optional, Dict, List

from requests import get

from dao import ORM

TESCO_API_KEY = '438ec90168ae495ca1dd9993f594e957'
TESCO_API_URL = 'https://dev.tescolabs.com'


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


def grocery_search(query: str, offset: int = 0, limit: int = 10) -> Optional[Dict]:
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
        target_stores.append({'_id': store_data.get('id'),
                              'address': store_data.get('contact', {}).get('address').get('town'),
                              'lon': coords.get('longitude'),
                              'lat': coords.get('latitude'),
                              '_type': store_data.get('classification', {}).get('type'),
                              'name': store_data.get('name')})

    if filter_town:
        target_stores = [store for store in target_stores if filter_town in store.get('address')]

    orm = ORM()
    for store in target_stores:
        orm.add_shop(**store)


def get_shop_list() -> List[Dict]:
    orm = ORM()
    shops = orm.get_shops()

    shop_list = [shop.update({'count': 0}) for shop in shops]

    return shop_list

if __name__ == '__main__':
    # Tests
    # glosery = grocery_search('Tescobritish', 0)
    # print(get_necessary_data_from_grocery_search(glosery, 254656543))
    # print(product_data('4548736003446'))
    # stores = store_location()
    # extract_stores_from_results(stores)
    print(get_product_data('05010003000131'))
