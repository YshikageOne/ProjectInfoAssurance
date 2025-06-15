import os

DB_PATH = 'LaundryItems.db'

JWT_SECRET = 'supersecretkey'  # 🔐 Replace this in production
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 20  # 20 secc token validity
