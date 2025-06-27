from werkzeug.security import generate_password_hash

# Force pbkdf2:sha256 format
print(generate_password_hash("admin123", method="pbkdf2:sha256"))
