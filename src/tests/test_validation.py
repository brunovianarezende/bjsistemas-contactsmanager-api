import unittest
from copy import deepcopy

from flask import json
import jsonpickle

from servicefusion.model import Contact, Address
from servicefusion.validation import validate_contact, ValidationError, validate_address

dumps = lambda o: jsonpickle.dumps(o, unpicklable=False)
to_dict = lambda o: deepcopy(json.loads(dumps(o)))

class TestValidation(unittest.TestCase):
    def setUp(self):
        self.contact = Contact(firstname='Firstname', lastname='Lastname',
                           emails=['bruno@bruno.com'], phone_numbers=['55-31-1234-4321'],
                           birthdate='1975-11-02', addresses=[])
        self.contact_with_addresses = Contact(firstname='Firstname', lastname='Lastname',
            emails=['bruno@bruno.com'], phone_numbers=['55-31-1234-4321'], birthdate='1975-11-02',
            addresses=[Address('street', 'city', 'AL', '12345'), Address('street', 'city', 'AL')])

    def test_is_valid(self):
        validate_contact(self.contact)
        validate_contact(self.contact_with_addresses)

    def test_firstname_validation(self):
        for invalid_value in ['', None, 0, 1, [1], {1: 2}]:
            with self.assertRaises(ValidationError, msg='invalid value %s' % invalid_value):
                self.contact.firstname = invalid_value 
                validate_contact(self.contact)

    def test_lastname_validation(self):
        for invalid_value in ['', None, 0, 1, [1], {1: 2}]:
            with self.assertRaises(ValidationError, msg='invalid value %s' % invalid_value):
                self.contact.lastname = invalid_value 
                validate_contact(self.contact)

    def test_emails_validation(self):
        for invalid_value in [[], '[]', 1, ['invalid']]:
            with self.assertRaises(ValidationError, msg='invalid value %s' % invalid_value):
                self.contact.emails = invalid_value 
                validate_contact(self.contact)

    def test_phone_numbers_validation(self):
        for invalid_value in [[], '[]', 1, ['']]:
            with self.assertRaises(ValidationError, msg='invalid value %s' % invalid_value):
                self.contact.phone_numbers = invalid_value 
                validate_contact(self.contact)

    def test_addresses_validation(self):
        for invalid_value in [{}, '[]', 'bla', [Address()]]:
            with self.assertRaises(ValidationError, msg='invalid value %s' % invalid_value):
                self.contact.addresses = invalid_value 
                validate_contact(self.contact)

    def test_address_street_validation(self):
        address = Address(street='street', city='city', state='state', zipcode='12345')
        for invalid_value in ['', {1: 2}, [1], 1]:
            with self.assertRaises(ValidationError, msg='invalid value %s' % invalid_value):
                address.street = invalid_value
                validate_address(address)

    def test_address_city_validation(self):
        address = Address(street='street', city='city', state='state', zipcode='12345')
        for invalid_value in ['', {1: 2}, [1], 1]:
            with self.assertRaises(ValidationError, msg='invalid value %s' % invalid_value):
                address.city = invalid_value
                validate_address(address)
