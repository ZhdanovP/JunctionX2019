from flask import Flask, jsonify, render_template
from flask import request
from dao import ORM
import os

app = Flask(__name__)
app._static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")


shop_list = [
    {
        'value': 3245,
        'counter': 10,
        'address': 'Pushkina, 27'
    },
    {
        'value': 6343,
        'counter': 6,
        'address': 'Tolstogo, 230a'
    },
    {
        'value': 97687,
        'counter': 43,
        'address': 'Budabuda street, 12'
    },
    {
        'value': 2452,
        'counter': 0,
        'address': 'Lorem ipsum, 117'
    }
]

@app.route('/')
def hello_world():
    shop_list_sorted = sorted(shop_list, key=lambda x: x['counter'], reverse=True)
    return render_template('index.html', title='JunctionX', shop_list=shop_list_sorted)


@app.route('/catalog/add', methods=['POST'])
def add():
    data = request.get_json()
    gtin = data['gtin']
    quantity = data['quantity']
    shop_id = data['shop_id']
    orm = ORM()
    orm.add_catalog(gtin, quantity, shop_id)
    return jsonify(success=True)


@app.route('/catalog/all', methods=['GET'])
def get_all():
    orm = ORM()
    return jsonify(orm.get_catalog_all())


@app.route('/catalog/<shop_id>', methods=['GET'])
def get_by_shop(shop_id: str):
    orm = ORM()
    return jsonify(orm.get_catalog_by_shop(shop_id))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
