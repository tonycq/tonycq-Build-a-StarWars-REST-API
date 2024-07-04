import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from models import db, User, Planet, People, Favorite
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

# Configuración de la base de datos
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

# Endpoints

# Listar todos los personajes
@app.route('/people', methods=['GET'])
def get_people():
    characters = People.query.all()
    return jsonify([char.serialize() for char in characters]), 200

# Obtener un personaje por ID
@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    character = People.query.get(people_id)
    if character is None:
        return jsonify({"msg": "Character not found"}), 404
    return jsonify(character.serialize()), 200

# Crear un nuevo personaje
@app.route('/people', methods=['POST'])
def create_person():
    data = request.json
    name = data.get('name')
    gender = data.get('gender')
    birth_year = data.get('birth_year')

    if not name or not gender or not birth_year:
        return jsonify({"msg": "Name, gender, and birth year are required"}), 400

    new_person = People(name=name, gender=gender, birth_year=birth_year)
    db.session.add(new_person)
    db.session.commit()

    return jsonify(new_person.serialize()), 201

# Modificar un personaje existente
@app.route('/people/<int:people_id>', methods=['PUT'])
def update_person(people_id):
    data = request.json
    person = People.query.get(people_id)
    
    if person is None:
        return jsonify({"msg": "Character not found"}), 404

    person.name = data.get('name', person.name)
    person.gender = data.get('gender', person.gender)
    person.birth_year = data.get('birth_year', person.birth_year)

    db.session.commit()
    
    return jsonify(person.serialize()), 200

# Eliminar un personaje existente
@app.route('/people/<int:people_id>', methods=['DELETE'])
def delete_person(people_id):
    person = People.query.get(people_id)
    if person is None:
        return jsonify({"msg": "Character not found"}), 404
    
    db.session.delete(person)
    db.session.commit()
    
    return jsonify({"msg": "Character deleted"}), 200

# Listar todos los planetas
@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200

# Obtener un planeta por ID
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"msg": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200

# Crear un nuevo planeta
@app.route('/planets', methods=['POST'])
def create_planet():
    data = request.json
    name = data.get('name')
    climate = data.get('climate')
    terrain = data.get('terrain')

    if not name or not climate or not terrain:
        return jsonify({"msg": "Name, climate and terrain are required"}), 400

    new_planet = Planet(name=name, climate=climate, terrain=terrain)
    db.session.add(new_planet)
    db.session.commit()

    return jsonify(new_planet.serialize()), 201

# Modificar un planeta existente
@app.route('/planets/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    data = request.json
    planet = Planet.query.get(planet_id)
    
    if planet is None:
        return jsonify({"msg": "Planet not found"}), 404

    planet.name = data.get('name', planet.name)
    planet.climate = data.get('climate', planet.climate)
    planet.terrain = data.get('terrain', planet.terrain)

    db.session.commit()
    
    return jsonify(planet.serialize()), 200

# Eliminar un planeta existente
@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"msg": "Planet not found"}), 404
    
    db.session.delete(planet)
    db.session.commit()
    
    return jsonify({"msg": "Planet deleted"}), 200

# Listar todos los usuarios
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

# Crear un nuevo usuario
@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    is_active = data.get('is_active', True)  # Default to True if not provided

    if not email or not password:
        return jsonify({"msg": "Email and password are required"}), 400
    
    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"msg": "User already exists"}), 400

    # Create new user
    new_user = User(email=email, password=password, is_active=is_active)
    db.session.add(new_user)
    db.session.commit()

    return jsonify(new_user.serialize()), 201

# Listar los favoritos del usuario actual
@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"msg": "User not found"}), 404
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    return jsonify([favorite.serialize() for favorite in favorites]), 200

# Añadir un nuevo planeta favorito
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = request.json.get('user_id')
    user = User.query.get(user_id)
    planet = Planet.query.get(planet_id)
    if user is None or planet is None:
        return jsonify({"msg": "User or Planet not found"}), 404
    favorite = Favorite(user_id=user_id, planet_id=planet_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 201

# Añadir un nuevo personaje favorito
@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_person(people_id):
    user_id = request.json.get('user_id')
    user = User.query.get(user_id)
    person = People.query.get(people_id)
    if user is None or person is None:
        return jsonify({"msg": "User or Character not found"}), 404
    favorite = Favorite(user_id=user_id, people_id=people_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 201

# Eliminar un planeta favorito
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = request.json.get('user_id')
    favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if favorite is None:
        return jsonify({"msg": "Favorite not found"}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": "Favorite deleted"}), 200

# Eliminar un personaje favorito
@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_person(people_id):
    user_id = request.json.get('user_id')
    favorite = Favorite.query.filter_by(user_id=user_id, people_id=people_id).first()
    if favorite is None:
        return jsonify({"msg": "Favorite not found"}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": "Favorite deleted"}), 200

if __name__ == '__main__':
    app.run(debug=True)
