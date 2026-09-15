from auth import create_user
from database import initialize_database


initialize_database()

username = input("Enter admin username: ").strip()
password = input("Enter admin password: ")

if not username or not password:
    print("Username and password are required.")
    raise SystemExit(1)

result = create_user(
    username,
    password,
    "admin"
)

if result["success"]:
    print("Admin account created successfully.")
else:
    print(result["error"])