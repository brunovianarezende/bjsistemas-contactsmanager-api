from pyisemail import is_email

def validate_contact(contact):
    validate_firstname(contact.firstname)
    validate_lastname(contact.lastname)
    validate_emails(contact.emails)
    validate_phone_numbers(contact.phone_numbers)
    validate_addresses(contact.addresses)

def validate_firstname(firstname):
    if not isinstance(firstname, str):
        raise ValidationError('invalid firstname type')
    if not firstname:
        raise ValidationError('firstname is required')

def validate_lastname(lastname):
    if not isinstance(lastname, str):
        raise ValidationError('invalid lastname type')
    if not lastname:
        raise ValidationError('lastname is required')

def validate_emails(emails):
    if not isinstance(emails, list):
        raise ValidationError('emails must be a list')
    if not emails:
        raise ValidationError('emails is required')
        
    for email in emails:
        validate_email(email)

def validate_email(email):
    if not isinstance(email, str):
        raise ValidationError('invalid email %s' % email)
    if not email:
        raise ValidationError('email is required')
    if not is_email(email):
        raise ValidationError('invalid email %s' % email)

def validate_phone_numbers(numbers):
    if not isinstance(numbers, list):
        raise ValidationError('phone numbers must be a list')
    if not numbers:
        raise ValidationError('phone numbers is required')
        
    for number in numbers:
        validate_phone_number(number)

def validate_phone_number(number):
    if not isinstance(number, str):
        raise ValidationError('invalid phone number %s' % number)
    if not number:
        raise ValidationError('phone number is required')

def validate_addresses(addresses):
    if not isinstance(addresses, list):
        raise ValidationError('addresses must be a list')
        
    for address in addresses:
        validate_address(address)

def validate_address(address):
    validate_street(address.street)
    validate_city(address.city)

def validate_street(street):
    if not isinstance(street, str):
        raise ValidationError('invalid street type')
    if not street:
        raise ValidationError('street is required')

def validate_city(city):
    if not isinstance(city, str):
        raise ValidationError('invalid city type')
    if not city:
        raise ValidationError('city is required')

class ValidationError(Exception):
    pass
