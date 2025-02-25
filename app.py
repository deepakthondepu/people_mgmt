from flask import Flask, jsonify, request, abort
import json
import os

app = Flask(__name__)
DATA_FILE = 'people.json'

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as file:
        json.dump([], file)

def load_data():
    with open(DATA_FILE, 'r') as file:
        return json.load(file)

def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

# get all people #GET 
@app.route('/people', methods=['GET'])
def get_people():
    people = load_data()
    return jsonify(people), 200

# get a person by ID #GET
@app.route('/people/<int:person_id>', methods=['GET'])
def get_person(person_id):
    people = load_data()
    person = next((p for p in people if p['id'] == person_id), None)
    if person is None:
        abort(404, description="Person not found")
    return jsonify(person), 200

# add new person #POST
@app.route('/people', methods=['POST'])
def add_person():
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

    people = load_data()

    # check  duplicate ID
    if any(p['id'] == new_person['id'] for p in people):
        abort(400, description="Person with this ID already exists")

    people.append(new_person)
    save_data(people)
    return jsonify(new_person), 201

# update a Person #PUT
@app.route('/people/<int:person_id>', methods=['PUT'])
def update_person(person_id):
    if not request.json:
        abort(400, description="Invalid input")
    
    people = load_data()
    person = next((p for p in people if p['id'] == person_id), None)
    if person is None:
        abort(404, description="Person not found")

    person['name'] = request.json.get('name', person['name'])
    person['age'] = request.json.get('age', person['age'])
    person['email'] = request.json.get('email', person['email'])

    if person['age'] <= 0:
        abort(400, description="Age must be a positive number")
    if '@' not in person['email']:
        abort(400, description="check email address")

    save_data(people)
    return jsonify(person), 200

#  delete a Person #DELETE
@app.route('/people/<int:person_id>', methods=['DELETE'])
def delete_person(person_id):
    people = load_data()
    person = next((p for p in people if p['id'] == person_id), None)
    if person is None:
        abort(404, description="Person not found")

    people.remove(person)
    save_data(people)
    return jsonify({'result': True}), 200

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': str(error)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': str(error)}), 404

if __name__ == '__main__':
    app.run(debug=True)