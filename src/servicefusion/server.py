from flask import Flask, request, make_response, json

import jsonpickle
from json.decoder import JSONDecodeError

from .model import Contact
from .validation import validate_contact, ValidationError

app = Flask(__name__)

_db = lambda: app.config['BACKEND']
dumps = lambda o: jsonpickle.dumps(o, unpicklable=False)

@app.route('/search/contacts/', methods=['GET'])
def search_contacts():
    firstname = request.args.get('firstname', '')
    lastname= request.args.get('lastname', '')
    return make_response(dumps(_db().search_contacts(firstname, lastname)))

@app.route('/contacts/', methods=['POST'])
def add_contact():
    try:
        new_contact_raw = json.loads(request.data)
    except JSONDecodeError:
        return make_response(dumps(dict(error='invalid input - not json')), 400)
    try:
        new_contact = Contact.from_raw_dict(**new_contact_raw)
    except TypeError as e:
        return make_response(dumps(dict(error='invalid input - invalid fields %s' % e)), 400)
    try:
        validate_contact(new_contact)
    except ValidationError:
        return make_response(dumps(dict(error='invalid input - validation error')), 400)

    new_id = _db().add_contact(new_contact)
    return make_response(dumps(new_id))

@app.route('/contacts/<contact_id>/', methods=['PUT'])
def edit_contact(contact_id):
    try:
        new_contact_raw = json.loads(request.data)
    except JSONDecodeError:
        return make_response(dumps(dict(error='invalid input - not a json')), 400)
    try:
        new_contact = Contact.from_raw_dict(**new_contact_raw)
    except TypeError:
        return make_response(dumps(dict(error='invalid input - invalid fields')), 400)
    try:
        if contact_id != str(new_contact.contact_id):
            raise ValidationError("Invalid id")
        validate_contact(new_contact)
    except ValidationError:
        return make_response(dumps(dict(error='invalid input - validation error')), 400)
    db = _db()
    if db.get_contact(contact_id):
        db.update_contact(new_contact)
        return make_response(dumps({'ok': True}))
    else:
        return make_response(dumps({'ok': False}), 404)

@app.route('/contacts/<contact_id>/', methods=['DELETE'])
def delete_contact(contact_id):
    db = _db()
    if db.get_contact(contact_id):
        db.delete_contact(contact_id)
        return make_response(dumps({'ok': True}))
    else:
        return make_response(dumps({'ok': False}), 404)
