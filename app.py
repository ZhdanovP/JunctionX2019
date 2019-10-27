import os

from flask import Flask, jsonify, render_template
from flask import request

from dao import ORM
from tesco_api import get_shop_list, get_goods_list

import prediction.prediction as ml
import tesco_api as api

app = Flask(__name__)
app._static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")


@app.route('/')
def hello_world():
    shops = get_shop_list()
    return render_template('index.html', title='JunctionX', shop_list=shops, good_list=get_goods_list(shops))


@app.route('/barcode', methods=['POST'])
def barcode_processing():
    data = request.get_json()
    gtin = data['gtin']
    shop_id = data['shop_id']
    product = api.get_product_data(gtin)

    how_much_will_be_waist = ml.predict(product)
    # TODO: Send how_much_will_be_waist to mobile

    orm = ORM()
    orm.add_catalog(gtin, how_much_will_be_waist, shop_id)
    return jsonify({'how_much_will_be_waist': how_much_will_be_waist})


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


@app.route('/shop/all', methods=['GET'])
def get_shop_all():
    return jsonify(get_shop_list)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
