from typing import Optional, Dict

from requests import get

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


def grocery_search(query: str, offset: int, limit: int = 100) -> Optional[Dict]:
    grocery_url = f'{TESCO_API_URL}/grocery/products'
    params = {'query': query, 'offset': offset, 'limit': limit}
    return __make_request_to_tesco(grocery_url, params)


def product_data(gtin: Optional[str] = None, tpnb: Optional[str] = None,
                 tpnc: Optional[str] = None, catid: Optional[str] = None) -> Optional[Dict]:
    grocery_url = f'{TESCO_API_URL}/product'
    params = {'gtin': gtin, 'tpnb': tpnb, 'tpnc': tpnc, 'catid': catid}
    return __make_request_to_tesco(grocery_url, params)


def store_location(like: str, offset: int, limit: int = 100) -> Optional[Dict]:
    grocery_url = f'{TESCO_API_URL}/locations/search'
    params = {'like': f'name:{like}', 'offset': offset, 'limit': limit}
    return __make_request_to_tesco(grocery_url, params)


if __name__ == '__main__':
    print(grocery_search('milk', 0))
    print(product_data('4548736003446'))
    print(store_location('budapest', 0))
