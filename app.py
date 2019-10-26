from flask import Flask, jsonify, render_template
from flask import request
import dao
import os

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html', title='JunctionX')


@app.route('/catalog/add', methods=['POST'])
def add():
    data = request.get_json()
    gtin = data['gtin']
    quantity = data['quantity']
    shop_id = data['shop_id']
    dao.add_catalog(gtin, quantity, shop_id)
    return jsonify(success=True)


@app.route('/catalog/all', methods=['GET'])
def get_all():
    return jsonify(dao.get_catalog_all())


@app.route('/catalog/<shop_id>', methods=['GET'])
def get_by_shop(shop_id: str):
    return jsonify(dao.get_catalog_by_shop(shop_id))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
