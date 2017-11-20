from flask import Flask, request

app = Flask(__name__)

@app.route('/search/contacts/', methods=['GET'])
def search_contacts():
    return 'Hello, World! %s' % request.args

@app.route('/contacts/', methods=['POST'])
def add_contact():
    return 'Hello, World! '

@app.route('/contacts/<id>', methods=['PUT'])
def edit_contact(contact_id):
    return 'Hello, World! - %s' % contact_id

@app.route('/contacts/<id>', methods=['DELETE'])
def delete_contact(contact_id):
    return 'Hello, World! - %s' % contact_id
