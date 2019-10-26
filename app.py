from flask import Flask, jsonify, render_template
from flask import request
import dao
import os

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html', title='JunctionX')


@app.route('/add', methods=['POST'])
def add():
    data = request.get_json()
    gtin = data['gtin']
    quantity = data['quantity']
    shop_id = data['shop_id']
    dao.add_catalog(gtin, quantity, shop_id)
    return jsonify(success=True)


@app.route('/all')
def get_all():
    return jsonify(dao.get_all())


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
