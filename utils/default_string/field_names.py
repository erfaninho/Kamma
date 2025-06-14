"""
    All Field Names
"""

from .db_names import D


class S(D):
    
    """
        Procuts App
    """
    ID = "id"
    NAME = "name"
    COLORS = "colors"
    MATERIALS = "materials"
    GENDER = "gender"
    RATE = "rate"
    PRICE = "price"
    DESCRIPTION = "description"
    IMAGE = "image"
    FILE = "file"
    STOCK = "stock"
    P_ID = "p_id"
    
    """
        Users App
    """
    EMAIL = "email"
    PHONE_NUMBER = "phone_number"
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"
    USERNAME = "username"
    VERIFIED_EMAIL = "verified_email"
    VERIFIED_PHONE_NUMBER = "verified_phone_number"
    ADDRESS = "address"
    BIRTH_DATE = "birth_date"
    PASSWORD = "password"
    USER = "user"
    TITLE = "title"
    POST_CODE = "post_code"
    STATE = "state"
    CITY = "city"
    LATITUDE = "latitude"
    LONGITUDE = "longitude"
    POSTAL_ADDRESS = "postal_address"
    IS_DEFAULT = "is_default"
    NUMBER = "number"
    IS_ACTIVE = "is_active"
    TOTAL_AMOUNT = "total_amount"
    CART = "cart"
    COUNT = "count"
    PRODUCT_INSTANCE = "product_instace"

    """
        Order App
    """
    ORDER = "order"
    ORDER_STATUS = "order_status"
    SHIPPING_ADDRESS = "shipping_address"
