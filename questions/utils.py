from django.conf import settings
from hashids import Hashids

# Initialize Hashids with the salt from settings.py
# The min_length parameter ensures the generated IDs are at least 6 characters long.
hashids = Hashids(salt=settings.HASHIDS_SALT, min_length=6)

def encode_id(id_number):
    """Encodes a single integer ID into a hashid string."""
    return hashids.encode(id_number)

def decode_id(hashed_id):
    """
    Decodes a hashid string into an integer ID.
    Returns the ID if successful, otherwise returns None.
    """
    decoded_tuple = hashids.decode(hashed_id)
    if decoded_tuple:
        return decoded_tuple[0]
    return None 