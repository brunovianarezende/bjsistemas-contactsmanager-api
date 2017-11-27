import json
from copy import deepcopy

import pymongo
from bson.objectid import ObjectId

import jsonpickle

class Contact:
    def __init__(self, contact_id=None, firstname=None, lastname=None, birthdate=None, emails=[], phone_numbers=[], addresses=[]):
        self.contact_id = contact_id
        self.firstname = firstname
        self.lastname = lastname
        self.birthdate = birthdate
        self.emails = emails
        self.phone_numbers = phone_numbers
        self.addresses = addresses

    @classmethod
    def from_raw_dict(cls, **kwargs):
        params = dict(**kwargs)
        addresses = [Address(**a) for a in params.pop('addresses', [])]
        params['addresses'] = addresses
        result = cls(**params)
        return result

    def __eq__(self, other):
        if other is None:
            return False
        else:
            return all(getattr(self, attr) == getattr(other, attr)
                       for attr in ('contact_id', 'firstname', 'lastname', 'emails', 'phone_numbers', 'addresses'))

    def __repr__(self):
        return 'Contact(%s)' % ({k: getattr(self, k) for k in ('contact_id', 'firstname', 'lastname', 'emails', 'phone_numbers', 'addresses')},)

class Address:
    def __init__(self, street='', city='', state='', zipcode=''):
        self.street = street
        self.city = city
        self.state = state
        self.zipcode = zipcode

    def __eq__(self, other):
        if other is None:
            return False
        else:
            return all(getattr(self, attr) == getattr(other, attr)
                       for attr in ('street', 'city', 'state', 'zipcode'))

    def __repr__(self):
        return 'Address(%s)' % ({k: getattr(self, k) for k in ('street', 'city', 'state', 'zipcode')},)

class Backend:
    def get_contact(self, contact_id):
        pass

    def update_contact(self, contact):
        pass

    def add_contact(self, contact):
        pass

    def delete_contact(self, contact_id):
        pass

    def search_contacts(self, firstname='', lastname=''):
        pass

class InMemoryBackend(Backend):
    def __init__(self):
        self.next_id = 1
        self.contacts = []

    def add_contact(self, contact):
        new_contact = deepcopy(contact)
        new_contact.contact_id = self.next_id
        self.next_id += 1
        self.contacts.append(new_contact)
        return new_contact.contact_id

    def delete_contact(self, contact_id):
        try:
            contact_id = int(contact_id)
        except:
            return None
        self.contacts = [c for c in self.contacts if c.contact_id != contact_id]

    def update_contact(self, contact):
        try:
            contact_id = int(contact.contact_id)
        except:
            return None
        contact = deepcopy(contact)
        index = next((index for index, c in enumerate(self.contacts) if c.contact_id == contact_id), -1)
        if index != -1:
            self.contacts[index] = contact

    def get_contact(self, contact_id):
        try:
            contact_id = int(contact_id)
        except:
            return None
        index = next((index for index, c in enumerate(self.contacts) if c.contact_id == contact_id), -1)
        if index != -1:
            return self.contacts[index]
        else:
            return None

    def search_contacts(self, firstname='', lastname=''):
        n = lambda s: s.lower()
        
        def f(contact):
            return n(contact.firstname).startswith(n(firstname))\
                and n(contact.lastname).startswith(n(lastname))

        k = lambda c: (n(c.firstname), n(c.lastname))

        return sorted([
            c for c in self.contacts if f(c)
        ], key=k)

class MongoBackend(Backend):
    def __init__(self, db):
        self._db= db
        self._collection = self._db.contacts

    def _to_dict(self, contact):
        if contact.contact_id is not None:
            contact.contact_id = str(contact.contact_id)
        result = json.loads(jsonpickle.dumps(contact, unpicklable=False))
        result['firstname_lower'] = result['firstname'].lower()
        result['lastname_lower'] = result['lastname'].lower()
        return result

    def _map_contact(self, contact):
        contact['contact_id'] = str(contact.pop('_id'))
        contact.pop('firstname_lower', '')
        contact.pop('lastname_lower', '')
        return Contact.from_raw_dict(**contact)

    def all_contacts(self):
        return [self._map_contact(c) for c in self._collection.find({})]

    def add_contact(self, contact):
        dict_repr = self._to_dict(contact)
        contact_id = self._collection.insert_one(dict_repr).inserted_id
        return str(contact_id)

    def delete_contact(self, contact_id):
        try:
            contact_id = ObjectId(contact_id)
        except:
            return None
        self._collection.delete_one({'_id': contact_id})

    def get_contact(self, contact_id):
        try:
            contact_id = ObjectId(contact_id)
        except:
            return None
        result = self._collection.find_one({'_id': contact_id})
        if result is not None:
            return self._map_contact(result)
        else:
            return None

    def update_contact(self, contact):
        dict_repr = self._to_dict(contact)
        try:
            contact_id = ObjectId(dict_repr.pop('contact_id'))
        except:
            return None
        self._collection.find_one_and_replace({'_id': contact_id}, dict_repr)

    def search_contacts(self, firstname='', lastname=''):
        # reason to use firstname_lower and lastname_lower:
        # https://docs.mongodb.com/manual/reference/operator/query/regex/
        # "Case insensitive regular expression queries generally cannot use indexes effectively.
        # The $regex implementation is not collation-aware and is unable to utilize case-insensitive
        # indexes."
        query = {}
        if firstname:
            query['firstname_lower'] = { '$regex': '^%s' % firstname.lower() }
        if lastname:
            query['lastname_lower'] = { '$regex': '^%s' % lastname.lower() }
        return [self._map_contact(c) for c in self._collection.find(query).sort([("firstname_lower", pymongo.ASCENDING), ("lastname_lower", pymongo.ASCENDING)])]
