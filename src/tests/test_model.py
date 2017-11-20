import unittest
from copy import deepcopy
from servicefusion.model import Contact, InMemoryBackend


class InMemoryTest(unittest.TestCase):
    def test_add_contact(self):
        contact = Contact(firstname='First', lastname='Last', emails=['bruno@bruno.com'],
                         phone_numbers=['55-31-1234-4321'], addresses=[])
        backend = InMemoryBackend()
        new_id = backend.add_contact(contact)
        self.assertEqual(new_id, backend.contacts[0].contact_id)
        self.assertIsNone(contact.contact_id)
        contact.contact_id = new_id
        self.assertEqual(backend.contacts, [contact])

    def test_delete_contact(self):
        contact = Contact(firstname='First', lastname='Last', emails=['bruno@bruno.com'],
                         phone_numbers=['55-31-1234-4321'], addresses=[])
        backend = InMemoryBackend()
        new_id = backend.add_contact(contact)
        self.assertEqual(len(backend.contacts), 1)
        backend.delete_contact(new_id)
        self.assertEqual(len(backend.contacts), 0)

    def test_update_contact(self):
        contact = Contact(firstname='First', lastname='Last', emails=['bruno@bruno.com'],
                         phone_numbers=['55-31-1234-4321'], addresses=[])
        backend = InMemoryBackend()
        new_id = backend.add_contact(contact)
        contact.contact_id = new_id
        contact.firstname = 'NewFirst'
        self.assertNotEqual(backend.contacts, [contact])
        backend.update_contact(contact)
        self.assertEqual(backend.contacts, [contact])

    def test_update_contact_not_available(self):
        contact = Contact(firstname='First', lastname='Last', emails=['bruno@bruno.com'],
                         phone_numbers=['55-31-1234-4321'], addresses=[])
        backend = InMemoryBackend()
        new_id = backend.add_contact(contact)
        contact.contact_id = new_id
        old_contact = deepcopy(contact)
        contact.contact_id = 10000
        contact.firstname = 'NewFirst'
        self.assertNotEqual(backend.contacts, [contact])
        backend.update_contact(contact)
        self.assertEqual(backend.contacts, [old_contact])
        self.assertNotEqual(backend.contacts, [contact])

    def test_get_contact(self):
        contact = Contact(firstname='First', lastname='Last', emails=['bruno@bruno.com'],
                         phone_numbers=['55-31-1234-4321'], addresses=[])
        backend = InMemoryBackend()
        new_id = backend.add_contact(contact)
        contact.contact_id = new_id
        self.assertEqual(contact, backend.get_contact(new_id))

    def test_get_contact_not_available(self):
        backend = InMemoryBackend()
        self.assertIsNone(backend.get_contact(100))


class InMemorySearchTest(unittest.TestCase):
    def setUp(self):
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
        backend = InMemoryBackend()
        for contact in data:
            new_id = backend.add_contact(contact)
            contact.contact_id = new_id
        self.backend = backend

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
