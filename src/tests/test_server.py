import unittest
from copy import deepcopy

from flask import json
import jsonpickle

from servicefusion.server import app
from servicefusion.model import InMemoryBackend, Contact, Address

dumps = lambda o: jsonpickle.dumps(o, unpicklable=False)
to_dict = lambda o: deepcopy(json.loads(dumps(o)))

class TestServer(unittest.TestCase):
    def setUp(self):
        app.config['BACKEND'] = InMemoryBackend()
        app.testing = True
        self.app = app.test_client()

        def contact(firstname, lastname):
            return Contact(firstname=firstname, lastname=lastname,
                           emails=['bruno@bruno.com'], phone_numbers=['55-31-1234-4321'],
                           birthdate='1975-11-02',
                           addresses=[Address('street', 'city', 'AL', '12345')])

        self.first = contact('First', 'Contact')
        self.random = contact('Someone', 'Random')
        self.not_random = contact('Someone', 'Notrandom')
        self.fourth = contact('Fourth', 'Contact')

        self.contacts = [self.first, self.random, self.not_random, self.fourth]

    def test_search_no_contacts(self):
        response = self.app.get('/search/contacts/')
        self.assertEqual(response.status_code, 200)
        contacts = json.loads(response.data)
        self.assertEqual(contacts, [])

    def test_search_with_contacts(self):
        for contact in self.contacts:
            new_id = app.config['BACKEND'].add_contact(contact)
            contact.contact_id = new_id

        response = self.app.get('/search/contacts/')
        self.assertEqual(response.status_code, 200)

        contacts = json.loads(response.data)
        n = lambda c: json.loads(dumps(c))
        self.assertEqual(contacts, n([self.first, self.fourth, self.not_random, self.random]))

    def test_search_with_filters(self):
        for contact in self.contacts:
            new_id = app.config['BACKEND'].add_contact(contact)
            contact.contact_id = new_id

        def search(firstname='', lastname=''):
            query_string = {}
            if firstname:
                query_string['firstname'] = firstname
            if lastname:
                query_string['lastname'] = lastname
            response = self.app.get('/search/contacts/', query_string=query_string)
            self.assertEqual(response.status_code, 200)
            return json.loads(response.data)

        n = lambda c: json.loads(dumps(c))

        contacts = search('f', 'c')
        self.assertEqual(contacts, n([self.first, self.fourth]))

        contacts = search('fo', 'c')
        self.assertEqual(contacts, n([self.fourth]))

    def test_add_contact(self):
        response = self.app.post('/contacts/', data=dumps(self.first))
        content = json.loads(response.data)
        self.first.contact_id = content
        self.assertEqual(response.status_code, 200)
        self.assertEqual([self.first], app.config['BACKEND'].search_contacts())

    def test_add_invalid_contact_invalid_key(self):
        first = to_dict(self.first)
        first['invalid_key'] = 'anything'
        response = self.app.post('/contacts/', data=dumps(first))
        self.assertEqual(response.status_code, 400)

    def test_add_invalid_contact_not_a_json(self):
        response = self.app.post('/contacts/', data="I'm not a json")
        self.assertEqual(response.status_code, 400)

    def test_add_invalid_contact_wrong_validation(self):
        # for more validations, see test_validation.py
        first = to_dict(self.first)
        first.pop('firstname')
        response = self.app.post('/contacts/', data=dumps(first))
        self.assertEqual(response.status_code, 400)

    def test_add_invalid_contact_invalid_address_key(self):
        first = to_dict(self.first)
        first['addresses'][0]['invalid_key'] = 'invalid'
        response = self.app.post('/contacts/', data=dumps(first))
        self.assertEqual(response.status_code, 400)

    def test_add_invalid_contact_missing_address_field(self):
        first = to_dict(self.first)
        first['addresses'][0]['street'] = ''
        response = self.app.post('/contacts/', data=dumps(first))
        self.assertEqual(response.status_code, 400)
