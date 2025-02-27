from flask import Flask, jsonify, request, abort
import json
import os

app = Flask(__name__)
DATA_FILE = 'people.json'
USERS_FILE = 'users.json'

for file_name in [DATA_FILE, USERS_FILE]:
    if not os.path.exists(file_name):
        with open(file_name, 'w') as file:
            json.dump([], file)

def load_data(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def save_data(data, file_name):
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)

def authenticate(username, password):
    users = load_data(USERS_FILE)
    user = next((u for u in users if u['username'] == username and u['password'] == password), None)
    
    if not user:
        abort(401, description="Authentication failed. Invalid username or password.")
    
    return user

def initialize_users():
    users = load_data(USERS_FILE)
    if not users:
        default_users = [
            {'username': 'admin', 'password': 'admin123', 'role': 'admin'},
            {'username': 'viewer', 'password': 'viewer123', 'role': 'viewer'}
        ]
        save_data(default_users, USERS_FILE)

initialize_users()

# all people (Admin and Viewer)
@app.route('/people', methods=['GET'])
def get_people():
    username = request.headers.get('username')
    password = request.headers.get('password')
    
    authenticate(username, password)
    people = load_data(DATA_FILE)
    return jsonify(people), 200

# person by ID (Admin and Viewer)
@app.route('/people/<int:person_id>', methods=['GET'])
def get_person(person_id):
    username = request.headers.get('username')
    password = request.headers.get('password')
    
    authenticate(username, password)
    people = load_data(DATA_FILE)
    person = next((p for p in people if p['id'] == person_id), None)
    if person is None:
        abort(404, description="Person not found")
    return jsonify(person), 200

# update  person (Admin only)
@app.route('/people/<int:person_id>', methods=['PUT'])
def update_person(person_id):
    username = request.headers.get('username')
    password = request.headers.get('password')
    
    user = authenticate(username, password)
    
    if user['role'] == 'viewer':
        print("As a viewer, you cannot update the details, upgrade to admin.")
        abort(403, description="As a viewer, you cannot update the details, upgrade to admin.")
    
    if not request.json:
        abort(400, description="Invalid input")
    
    people = load_data(DATA_FILE)
    person = next((p for p in people if p['id'] == person_id), None)
    if person is None:
        abort(404, description="Person not found")

    person['name'] = request.json.get('name', person['name'])
    person['age'] = request.json.get('age', person['age'])
    person['email'] = request.json.get('email', person['email'])

    if person['age'] <= 0:
        abort(400, description="Age must be a positive integer")
    if '@' not in person['email']:
        abort(400, description="Invalid email address")

    save_data(people, DATA_FILE)
    return jsonify(person), 200

# add or update person (Admin only)
@app.route('/people', methods=['POST'])
def add_or_update_person():
    username = request.headers.get('username')
    password = request.headers.get('password')
    
    user = authenticate(username, password)
    
    if user['role'] == 'viewer':
        print("As a viewer, you can't add new people, upgrade to admin.")
        abort(403, description="As a viewer, you can't add new people, upgrade to admin.")
    
    if not request.json or 'id' not in request.json:
        abort(400, description="Invalid input")
    
    new_person = {
        'id': request.json['id'],
        'name': request.json.get('name', ""),
        'age': request.json.get('age', 0),
        'email': request.json.get('email', "")
    }
    
    if new_person['age'] <= 0:
        abort(400, description="Age must be a positive integer")
    if '@' not in new_person['email']:
        abort(400, description="Invalid email address")
    
    people = load_data(DATA_FILE)
    existing_person = next((p for p in people if p['id'] == new_person['id']), None)
    if existing_person:
        existing_person.update(new_person)
    else:
        people.append(new_person)
    save_data(people, DATA_FILE)
    return jsonify(new_person), 201

# delete person (Admin only)
@app.route('/people/<int:person_id>', methods=['DELETE'])
def delete_person(person_id):
    username = request.headers.get('username')
    password = request.headers.get('password')
    
    user = authenticate(username, password)
    
    if user['role'] == 'viewer':
        print("As a viewer, you can't delete people, upgrade to admin.")
        abort(403, description="As a viewer, you can't delete people, upgrade to admin.")
    
    people = load_data(DATA_FILE)
    person = next((p for p in people if p['id'] == person_id), None)
    if person is None:
        abort(404, description="Person not found")
    
    people.remove(person)
    save_data(people, DATA_FILE)
    return jsonify({'message': 'Person deleted successfully'}), 200

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': str(error)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': str(error)}), 404

if __name__ == '__main__':
    app.run(debug=True)
