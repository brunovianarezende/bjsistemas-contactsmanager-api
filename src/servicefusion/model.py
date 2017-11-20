from copy import deepcopy

class Contact:
    def __init__(self, contact_id=None, firstname=None, lastname=None, emails=[], phone_numbers=[], addresses=[]):
        self.contact_id = contact_id
        self.firstname = firstname
        self.lastname = lastname
        self.emails = emails
        self.phone_numbers = phone_numbers
        self.addresses = addresses

    def __eq__(self, other):
        if other is None:
            return False
        else:
            return all(getattr(self, attr) == getattr(other, attr)
                       for attr in ('contact_id', 'firstname', 'lastname', 'emails', 'phone_numbers', 'addresses'))

    def __repr__(self):
        return 'Contact(%s)' % ({k: getattr(self, k) for k in ('contact_id', 'firstname', 'lastname', 'emails', 'phone_numbers', 'addresses')},)

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
        self.contacts = [c for c in self.contacts if c.contact_id != contact_id]

    def update_contact(self, contact):
        index = next((index for index, c in enumerate(self.contacts) if c.contact_id == contact.contact_id), -1)
        if index != -1:
            self.contacts[index] = contact

    def get_contact(self, contact_id):
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