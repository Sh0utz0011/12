
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint
from sqlalchemy import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///drinks.db'
db = SQLAlchemy(app)


#Модели
class DrinkService(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"DrinkService(name='{self.name}', price={self.price}, duration={self.duration})"

#Сваггер
@app.route('/swagger')
def swagger_spec():
    swag = swagger(app)
    swag['info']['title'] = 'Your API Title'
    swag['info']['version'] = '1.0'
    return jsonify(swag)

SWAGGER_URL = '/api/docs'  # URL Swagger UI
API_URL = '/swagger'  # URL спецификации Swagger

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Your API Name"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

@app.route('/drinks', methods=['POST'])
def add_drink():
    """
    Добавление нового напитка для продажи.
    ---
    tags:
      - drinks
    parameters:
      - name: name
        in: formData
        description: Название напитка.
        required: true
        type: string
      - name: description
        in: formData
        description: Описание напитка.
        required: false
        type: string
      - name: price
        in: formData
        description: Цена напитка.
        required: true
        type: number
      - name: duration
        in: formData
        description: Продолжительность приготовления.
        required: true
        type: integer
    responses:
      201:
        description: Успешное добавление нового напитка.
      400:
        description: Ошибка валидации данных.
    """
    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    duration = request.form.get('duration')

    # Валидация данных
    if not name or not price or not duration:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        price = float(price)
        duration = int(duration)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid data types for price or duration'}), 400

    new_drink = DrinkService(name=name, description=description, price=price, duration=duration)
    db.session.add(new_drink)
    db.session.commit()

    return jsonify({'message': 'New drink added successfully'}), 201

@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
def delete_drink(drink_id):
    """
    Удаление напитка по ID.
    ---
    tags:
      - drinks
    parameters:
      - name: drink_id
        in: path
        description: ID напитка для удаления.
        required: true
        type: integer
    responses:
      204:
        description: Успешное удаление напитка.
      404:
        description: Напиток с указанным ID не найдена.
    """
    drink = DrinkService.query.get(drink_id)

    if not drink:
        return jsonify({'error': 'Drink not found'}), 404

    db.session.delete(drink)
    db.session.commit()

    return '', 204

@app.route('/drinks', methods=['GET'])
def filter_drinks():
    """
       Получение фильтрованного списка напитков.
       ---
       tags:
         - drinks
       parameters:
         - name: name
           in: query
           description: Название напитка для фильтрации (поиск по частичному совпадению).
           required: false
           type: string
         - name: min_price
           in: query
           description: Минимальная цена напитка для фильтрации.
           required: false
           type: number
         - name: max_price
           in: query
           description: Максимальная цена напитка для фильтрации.
           required: false
           type: number
         - name: min_duration
           in: query
           description: Минимальная продолжительность приготовления напитка для фильтрации.
           required: false
           type: integer
         - name: max_duration
           in: query
           description: Максимальная продолжительность приготовления напитка для фильтрации.
           required: false
           type: integer
       responses:
         200:
           description: Успешное получение списка напитков.
       """
    name = request.args.get('name')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    min_duration = request.args.get('min_duration')
    max_duration = request.args.get('max_duration')

    query = DrinkService.query

    if name:
        query = query.filter(DrinkService.name.ilike(f'%{name}%'))

    if min_price:
        query = query.filter(DrinkService.price >= float(min_price))

    if max_price:
        query = query.filter(DrinkService.price <= float(max_price))

    if min_duration:
        query = query.filter(DrinkService.duration >= int(min_duration))

    if max_duration:
        query = query.filter(DrinkService.duration <= int(max_duration))

    drinks = query.all()

    return jsonify([{
        'id': drink.id,
        'name': drink.name,
        'description': drink.description,
        'price': drink.price,
        'duration': drink.duration
    } for drink in drinks])
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
def increase_price(drink_id):
    """
    Повышение цены напитка по ее идентификатору.
    ---
    tags:
      - drinks
    parameters:
      - name: drink_id
        in: path
        description: Идентификатор напитка.
        required: true
        type: integer
      - name: price
        in: formData
        description: Новая цена напитка.
        required: true
        type: number
    responses:
      200:
        description: Успешное повышение цены напитка.
      404:
        description: Напиток не найден.
    """
    drink = DrinkService.query.get(drink_id)

    if drink:
        new_price = request.form.get('price')
        drink.price = int(new_price)
        db.session.commit()
        return jsonify({'message': 'Price updated successfully'})
    else:
        return jsonify({'error': 'Drink not found'}), 404

@app.route('/drinks/<int:drink_id>', methods=['PUT'])
def update_drink(drink_id):
    """
    Обновление напитка по ID.
    ---
    tags:
      - drinks
    parameters:
      - name: drink_id
        in: path
        description: ID напитка для обновления.
        required: true
        type: integer
      - name: name
        in: formData
        description: Новое название напитка.
        required: false
        type: string
      - name: description
        in: formData
        description: Новое описание напитка.
        required: false
        type: string
      - name: price
        in: formData
        description: Новая цена напитка.
        required: false
        type: number
      - name: duration
        in: formData
        description: Новая продолжительность приготовления напитка.
        required: false
        type: integer
    responses:
      200:
        description: Успешное обновление напитка.
      400:
        description: Ошибка валидации данных.
      404:
        description: Напиток с указанным ID не найдена.
    """
    drink = DrinkService.query.get(drink_id)

    if not drink:
        return jsonify({'error': 'Drink not found'}), 404

    # Обновление полей услуги, если они указаны
    if 'name' in request.form:
        drink.name = request.form['name']

    if 'description' in request.form:
        drink.description = request.form['description']

    if 'price' in request.form:
        try:
            drink.price = float(request.form['price'])
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid data type for price'}), 400

    if 'duration' in request.form:
        try:
            drink.duration = int(request.form['duration'])
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid data type for duration'}), 400

    db.session.commit()

    return jsonify({'message': 'Drink updated successfully'}), 200
@app.route('/drinks/average_price', methods=['GET'])
def get_average_price():
    """
    Получение средней цены напитков.
    ---
    tags:
      - drinks
    responses:
      200:
        description: Успешное получение средней цены.
    """
    average_price = db.session.query(func.avg(DrinkService.price)).scalar()
    return jsonify({'average_price': average_price})


@app.route('/drinks/max_duration', methods=['GET'])
def get_max_duration():
    """
    Получение максимальной продолжительности напитков и их названия.
    ---
    tags:
      - drinks
    responses:
      200:
        description: Успешное получение максимальной продолжительности и названия напитка.
    """
    max_duration = db.session.query(func.max(DrinkService.duration)).scalar()
    drink = db.session.query(DrinkService).filter_by(duration=max_duration).first()

    if drink:
        return jsonify({'max_duration': max_duration, 'drink_name': drink.name})
    else:
        return jsonify({'message': 'No drinks found'})


@app.route('/drinks/min_duration', methods=['GET'])
def get_min_duration():
    """
    Получение минимальной продолжительности приготовления напитка.
    ---
    tags:
      - drinks
    responses:
      200:
        description: Успешное получение минимальной продолжительности.
    """
    min_duration = db.session.query(func.min(DrinkService.duration)).scalar()
    return jsonify({'min_duration': min_duration})


if __name__ == "__main__":

    app.run()