from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import time
import timeit

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
db = SQLAlchemy(app)

# Definindo model para produto com os campos de id, nome e preço.
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)

# Rota getAll para obter todos os produtos
@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{'id': p.id, 'name': p.name, 'price': p.price} for p in products])

# Rota create para produto
@app.route('/api/products/create', methods=['POST'])
def create_product():
    data = request.get_json()
    new_product = Product(name=data['name'], price=data['price'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'id': new_product.id, 'name': new_product.name, 'price': new_product.price})

# Rota update para produto
@app.route('/api/products/<int:id>', methods=['PUT'])
def update_product(id):
    data = request.get_json()
    product = Product.query.get(id)
    if product is None:
        return jsonify({'message': 'Produto não encontrado!'}), 404

    product.name = data['name']
    product.price = data['price']
    db.session.commit()
    return jsonify({'id': product.id, 'name': product.name, 'price': product.price})

# Delete
@app.route('/api/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    if product is None:
        return jsonify({'message': 'Produto não encontrado!'}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Produto deletado com sucesso!'})

# Rota para testar a performance
@app.route('/api/test_performance', methods=['GET'])
def test_performance():
    setup_code = """
from app import app, db, Product
from flask import json
client = app.test_client()
    """
    
    test_code = """
response = client.get('/api/products')
    """
    
    execution_time = timeit.timeit(stmt=test_code, setup=setup_code, number=100)
    return jsonify({"execution_time": execution_time})

# Rota get que mede o tempo de requisição.
@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    diff = time.time() - request.start_time
    print(f"Request processing time: {diff:.5f} seconds")
    return response

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Criqção de tabelas no bd
    app.run(debug=True)
