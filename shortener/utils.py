import string

BASE62_ALPHABET = string.ascii_letters + string.digits

def encode_base62(num):
    """
    Encode a number into a Base62 string.

    This is used to generate short keys from database IDs.

    Args:
        num (int): The integer to encode (e.g., database ID + offset).

    Returns:
        str: The Base62 encoded string.
    """
    if num == 0:
        return BASE62_ALPHABET[0]
    arr = []
    base = len(BASE62_ALPHABET)
    while num:
        num, rem = divmod(num, base)
        arr.append(BASE62_ALPHABET[rem])
    arr.reverse()
    return ''.join(arr)
