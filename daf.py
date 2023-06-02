
from flask import Flask, render_template,jsonify, request
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medical_services.db'
db = SQLAlchemy(app)


#Модели
class MedicalService(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"MedicalService(name='{self.name}', price={self.price}, duration={self.duration})"

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

@app.route('/services', methods=['POST'])
def add_service():
    """
    Добавление новой врачебной услуги.
    ---
    tags:
      - services
    parameters:
      - name: name
        in: formData
        description: Название услуги.
        required: true
        type: string
      - name: description
        in: formData
        description: Описание услуги.
        required: false
        type: string
      - name: price
        in: formData
        description: Цена услуги.
        required: true
        type: number
      - name: duration
        in: formData
        description: Продолжительность услуги (в минутах).
        required: true
        type: integer
    responses:
      201:
        description: Успешное добавление новой врачебной услуги.
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

    new_service = MedicalService(name=name, description=description, price=price, duration=duration)
    db.session.add(new_service)
    db.session.commit()
    print(name)
    return jsonify({'message': 'New medical service added successfully'}), 201

@app.route('/services/<int:service_id>', methods=['DELETE'])
def delete_service(service_id):
    """
    Удаление врачебной услуги по ID.
    ---
    tags:
      - services
    parameters:
      - name: service_id
        in: path
        description: ID врачебной услуги для удаления.
        required: true
        type: integer
    responses:
      204:
        description: Успешное удаление врачебной услуги.
      404:
        description: Врачебная услуга с указанным ID не найдена.
    """
    service = MedicalService.query.get(service_id)

    if not service:
        return jsonify({'error': 'Medical service not found'}), 404

    db.session.delete(service)
    db.session.commit()

    return '', 204

@app.route('/services', methods=['GET'])
def filter_services():
    """
       Получение фильтрованного списка медицинских услуг.
       ---
       tags:
         - services
       parameters:
         - name: name
           in: query
           description: Название услуги для фильтрации (поиск по частичному совпадению).
           required: false
           type: string
         - name: min_price
           in: query
           description: Минимальная цена услуги для фильтрации.
           required: false
           type: number
         - name: max_price
           in: query
           description: Максимальная цена услуги для фильтрации.
           required: false
           type: number
         - name: min_duration
           in: query
           description: Минимальная продолжительность услуги (в минутах) для фильтрации.
           required: false
           type: integer
         - name: max_duration
           in: query
           description: Максимальная продолжительность услуги (в минутах) для фильтрации.
           required: false
           type: integer
       responses:
         200:
           description: Успешное получение списка медицинских услуг.
       """
    name = request.args.get('name')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    min_duration = request.args.get('min_duration')
    max_duration = request.args.get('max_duration')

    query = MedicalService.query

    if name:
        query = query.filter(MedicalService.name.ilike(f'%{name}%'))

    if min_price:
        query = query.filter(MedicalService.price >= float(min_price))

    if max_price:
        query = query.filter(MedicalService.price <= float(max_price))

    if min_duration:
        query = query.filter(MedicalService.duration >= int(min_duration))

    if max_duration:
        query = query.filter(MedicalService.duration <= int(max_duration))

    services = query.all()

    return jsonify([{
        'id': service.id,
        'name': service.name,
        'description': service.description,
        'price': service.price,
        'duration': service.duration
    } for service in services])

@app.route('/services/<int:service_id>', methods=['PUT'])
def update_service(service_id):
    """
    Обновление врачебной услуги по ID.
    ---
    tags:
      - services
    parameters:
      - name: service_id
        in: path
        description: ID врачебной услуги для обновления.
        required: true
        type: integer
      - name: name
        in: formData
        description: Новое название услуги.
        required: false
        type: string
      - name: description
        in: formData
        description: Новое описание услуги.
        required: false
        type: string
      - name: price
        in: formData
        description: Новая цена услуги.
        required: false
        type: number
      - name: duration
        in: formData
        description: Новая продолжительность услуги (в минутах).
        required: false
        type: integer
    responses:
      200:
        description: Успешное обновление врачебной услуги.
      400:
        description: Ошибка валидации данных.
      404:
        description: Врачебная услуга с указанным ID не найдена.
    """
    service = MedicalService.query.get(service_id)

    if not service:
        return jsonify({'error': 'Medical service not found'}), 404

    # Обновление полей услуги, если они указаны
    if 'name' in request.form:
        service.name = request.form['name']

    if 'description' in request.form:
        service.description = request.form['description']

    if 'price' in request.form:
        try:
            service.price = float(request.form['price'])
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid data type for price'}), 400

    if 'duration' in request.form:
        try:
            service.duration = int(request.form['duration'])
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid data type for duration'}), 400

    db.session.commit()

    return jsonify({'message': 'Medical service updated successfully'}), 200
@app.route('/services/average_price', methods=['GET'])
def get_average_price():
    """
    Получение средней цены врачебных услуг.
    ---
    tags:
      - services
    responses:
      200:
        description: Успешное получение средней цены.
    """
    average_price = db.session.query(func.avg(MedicalService.price)).scalar()
    return jsonify({'average_price': average_price})
@app.route('/services/max_duration', methods=['GET'])
def get_max_duration():
    """
    Получение максимальной продолжительности врачебных услуг.
    ---
    tags:
      - services
    responses:
      200:
        description: Успешное получение максимальной продолжительности.
    """
    max_duration = db.session.query(func.max(MedicalService.duration)).scalar()
    return jsonify({'max_duration': max_duration})


@app.route('/services/min_duration', methods=['GET'])
def get_min_duration():
    """
    Получение минимальной продолжительности врачебных услуг.
    ---
    tags:
      - services
    responses:
      200:
        description: Успешное получение минимальной продолжительности.
    """
    min_duration = db.session.query(func.min(MedicalService.duration)).scalar()
    return jsonify({'min_duration': min_duration})

@app.cli.command()
def create_tables():
    with app.app_context():
        db.create_all()
        print('Tables created successfully')

if __name__ == "__main__":
    app.run()