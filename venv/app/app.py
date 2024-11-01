from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import time
import timeit

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:toor@localhost/VENDAS'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model para Produto
class Product(db.Model):
    __tablename__ = 'produto'  # Nome da tabela no MySQL
    id = db.Column('ID', db.BigInteger, primary_key=True)
    name = db.Column('NOME', db.String(100), nullable=False)
    description = db.Column('DESCRICAO', db.String(255))
    price = db.Column('PRECO', db.Numeric(10, 2))
    sku = db.Column('SKU', db.String(20))
    date_added = db.Column('DATA_CADASTRO', db.Date)

# Model para Cliente
class Client(db.Model):
    __tablename__ = 'cliente'
    id = db.Column('ID', db.BigInteger, primary_key=True)
    name = db.Column('NOME', db.String(100), nullable=False)
    birthdate = db.Column('NASCIMENTO', db.Date)
    address = db.Column('ENDERECO', db.String(255))
    cpf = db.Column('CPF', db.String(11), unique=True)
    phone = db.Column('TELEFONE', db.String(15))
    email = db.Column('EMAIL', db.String(100), unique=True)
    date_added = db.Column('DATA_CADASTRO', db.Date)

# CRUD para Produto
@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{'id': p.id, 'name': p.name, 'description': p.description, 'price': float(p.price), 'sku': p.sku, 'date_added': p.date_added.isoformat() if p.date_added else None} for p in products])

@app.route('/api/products/create', methods=['POST'])
def create_product():
    data = request.get_json()
    new_product = Product(name=data['name'], description=data.get('description'), price=data['price'], sku=data.get('sku'), date_added=data.get('date_added'))
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'id': new_product.id, 'name': new_product.name, 'description': new_product.description, 'price': float(new_product.price), 'sku': new_product.sku, 'date_added': new_product.date_added})

@app.route('/api/products/<int:id>', methods=['PUT'])
def update_product(id):
    data = request.get_json()
    product = Product.query.get(id)
    if product is None:
        return jsonify({'message': 'Produto não encontrado!'}), 404

    product.name = data['name']
    product.description = data.get('description')
    product.price = data['price']
    product.sku = data.get('sku')
    product.date_added = data.get('date_added')
    db.session.commit()
    return jsonify({'id': product.id, 'name': product.name, 'description': product.description, 'price': float(product.price), 'sku': product.sku, 'date_added': product.date_added})

@app.route('/api/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    if product is None:
        return jsonify({'message': 'Produto não encontrado!'}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Produto deletado com sucesso!'})

# CRUD para Cliente
@app.route('/api/clients', methods=['GET'])
def get_clients():
    clients = Client.query.all()
    return jsonify([{'id': c.id, 'name': c.name, 'birthdate': c.birthdate.isoformat() if c.birthdate else None, 'address': c.address, 'cpf': c.cpf, 'phone': c.phone, 'email': c.email, 'date_added': c.date_added.isoformat() if c.date_added else None} for c in clients])

@app.route('/api/clients/create', methods=['POST'])
def create_client():
    data = request.get_json()
    new_client = Client(name=data['name'], birthdate=data.get('birthdate'), address=data.get('address'), cpf=data['cpf'], phone=data['phone'], email=data['email'], date_added=data.get('date_added'))
    db.session.add(new_client)
    db.session.commit()
    return jsonify({'id': new_client.id, 'name': new_client.name, 'birthdate': new_client.birthdate, 'address': new_client.address, 'cpf': new_client.cpf, 'phone': new_client.phone, 'email': new_client.email, 'date_added': new_client.date_added})

@app.route('/api/clients/<int:id>', methods=['PUT'])
def update_client(id):
    data = request.get_json()
    client = Client.query.get(id)
    if client is None:
        return jsonify({'message': 'Cliente não encontrado!'}), 404

    client.name = data['name']
    client.birthdate = data.get('birthdate')
    client.address = data.get('address')
    client.cpf = data['cpf']
    client.phone = data['phone']
    client.email = data['email']
    client.date_added = data.get('date_added')
    db.session.commit()
    return jsonify({'id': client.id, 'name': client.name, 'birthdate': client.birthdate, 'address': client.address, 'cpf': client.cpf, 'phone': client.phone, 'email': client.email, 'date_added': client.date_added})

@app.route('/api/clients/<int:id>', methods=['DELETE'])
def delete_client(id):
    client = Client.query.get(id)
    if client is None:
        return jsonify({'message': 'Cliente não encontrado!'}), 404

    db.session.delete(client)
    db.session.commit()
    return jsonify({'message': 'Cliente deletado com sucesso!'})

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

# Rota para medir o tempo de requisição
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
        db.create_all()
    app.run(debug=True)
