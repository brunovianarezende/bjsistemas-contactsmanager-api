import unittest
from copy import deepcopy

from pymongo import MongoClient
from bson.objectid import ObjectId

from servicefusion.model import Contact, Address, InMemoryBackend, MongoBackend


class ContactTest(unittest.TestCase):
    def test_from_raw_dict(self):
        contact = Contact.from_raw_dict(firstname='firstname', lastname='lastname',
            emails=['bruno@bruno.com'], phone_numbers=['55-31-1234-4321'],
            birthdate='1975-11-02',
            addresses=[{'street': 'street', 'city': 'city', 'state': 'AL', 'zipcode': '12345'}])
        expected = Contact(firstname='firstname', lastname='lastname',
            emails=['bruno@bruno.com'], phone_numbers=['55-31-1234-4321'],
            birthdate='1975-11-02',
            addresses=[Address('street', 'city', 'AL', '12345')])
        self.assertEqual(expected, contact)

class BaseTests:
    def test_add_contact(self):
        contact = Contact(firstname='First', lastname='Last', emails=['bruno@bruno.com'],
                         phone_numbers=['55-31-1234-4321'], addresses=[])
        new_id = self._backend.add_contact(contact)
        self.assertEqual(new_id, self._contacts[0].contact_id)
        self.assertIsNone(contact.contact_id)
        contact.contact_id = new_id
        self.assertEqual(self._contacts, [contact])

    def test_delete_contact(self):
        contact = Contact(firstname='First', lastname='Last', emails=['bruno@bruno.com'],
                         phone_numbers=['55-31-1234-4321'], addresses=[])
        new_id = self._backend.add_contact(contact)
        self.assertEqual(len(self._contacts), 1)
        self._backend.delete_contact(new_id)
        self.assertEqual(len(self._contacts), 0)

    def test_update_contact(self):
        contact = Contact(firstname='First', lastname='Last', emails=['bruno@bruno.com'],
                         phone_numbers=['55-31-1234-4321'], addresses=[])
        new_id = self._backend.add_contact(contact)
        contact.contact_id = new_id
        contact.firstname = 'NewFirst'
        self.assertNotEqual(self._contacts, [contact])
        self._backend.update_contact(contact)
        self.assertEqual(self._contacts, [contact])

    def test_update_contact_not_available(self):
        contact = Contact(firstname='First', lastname='Last', emails=['bruno@bruno.com'],
                         phone_numbers=['55-31-1234-4321'], addresses=[])
        new_id = self._backend.add_contact(contact)
        contact.contact_id = new_id
        old_contact = deepcopy(contact)
        contact.contact_id = self._unavailable_id
        contact.firstname = 'NewFirst'
        self.assertNotEqual(self._contacts, [contact])
        self._backend.update_contact(contact)
        self.assertEqual(self._contacts, [old_contact])
        self.assertNotEqual(self._contacts, [contact])

    def test_get_contact(self):
        contact = Contact(firstname='First', lastname='Last', emails=['bruno@bruno.com'],
                         phone_numbers=['55-31-1234-4321'], addresses=[])
        new_id = self._backend.add_contact(contact)
        contact.contact_id = new_id
        self.assertEqual(contact, self._backend.get_contact(new_id))

    def test_get_contact_not_available(self):
        self.assertIsNone(self._backend.get_contact(self._unavailable_id))

class BaseSearchTests:
    def baseSearchSetUp(self, backend):
        self.backend = backend
        self.first = Contact(firstname='First', lastname='Contact', emails=['bruno@bruno.com'],
                        phone_numbers=['55-31-1234-4321'], addresses=[])
        self.random = Contact(firstname='Someone', lastname='Random', emails=['bruno@bruno.com'],
                                 phone_numbers=['55-31-1234-4321'], addresses=[])
        self.not_random = Contact(firstname='Someone', lastname='Notrandom', emails=['bruno@bruno.com'],
                             phone_numbers=['55-31-1234-4321'], addresses=[])
        self.fourth = Contact(firstname='Fourth', lastname='Contact', emails=['bruno@bruno.com'],
                        phone_numbers=['55-31-1234-4321'], addresses=[])

        data = [
            self.first,
            self.random,
            self.not_random,
            self.fourth,
        ]
        for contact in data:
            new_id = self.backend.add_contact(contact)
            contact.contact_id = new_id

    def test_no_filter(self):
        # results are ordered by firstname and then lastname
        self.assertEqual([self.first, self.fourth, self.not_random, self.random], self.backend.search_contacts())

    def test_filter_by_firstname(self):
        self.assertEqual([self.not_random, self.random], self.backend.search_contacts('someone'))
        self.assertEqual([self.first, self.fourth], self.backend.search_contacts('f'))
        self.assertEqual([self.first], self.backend.search_contacts('FIRST'))
        self.assertEqual([], self.backend.search_contacts('FIRSTONE'))

    def test_filter_by_lastname(self):
        self.assertEqual([self.first, self.fourth], self.backend.search_contacts(lastname='contact'))
        self.assertEqual([self.first, self.fourth], self.backend.search_contacts(lastname='CON'))
        self.assertEqual([], self.backend.search_contacts(lastname='contact1'))

    def test_filter_by_both(self):
        self.assertEqual([self.first, self.fourth], self.backend.search_contacts(firstname='f', lastname='c'))
        self.assertEqual([self.fourth], self.backend.search_contacts(firstname='fourth', lastname='contact'))
        self.assertEqual([], self.backend.search_contacts(firstname='f', lastname='contact1'))

class InMemoryTest(unittest.TestCase, BaseTests):
    def setUp(self):
        self._backend = InMemoryBackend()

    @property
    def _contacts(self):
        return self._backend.contacts

    @property
    def _unavailable_id(self):
        return 10000

class InMemorySearchTest(unittest.TestCase, BaseSearchTests):
    def setUp(self):
        self.baseSearchSetUp(InMemoryBackend())

class MongoBackendTest(unittest.TestCase, BaseTests):
    def setUp(self):
        self._mongo = MongoClient('mongodb://127.0.0.1:27017')
        self._backend = MongoBackend(self._mongo.servicefusion_test)

    def tearDown(self):
        self._mongo.drop_database('servicefusion_test')
        self._mongo.close()

    @property
    def _unavailable_id(self):
        return ObjectId(b'123456789012')

    @property
    def _contacts(self):
        return self._backend.all_contacts()

class MongoBackendSearchTest(unittest.TestCase, BaseSearchTests):
    def setUp(self):
        self._mongo = MongoClient('mongodb://127.0.0.1:27017')
        self.baseSearchSetUp(MongoBackend(self._mongo.servicefusion_test))

    def tearDown(self):
        self._mongo.drop_database('servicefusion_test')
        self._mongo.close()
