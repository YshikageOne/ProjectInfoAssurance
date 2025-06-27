import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'LaundryItems.db')

JWT_SECRET = 'supersecretkey'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 3600
