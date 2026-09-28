import sys

from argon2 import PasswordHasher


def main():
    ph = PasswordHasher()
    print("\n--- Admin Password Hash Generator ---")
    print("Enter the password you want to use for the admin panel.")
    print("The hash will be generated using Argon2.")
    print("-------------------------------------\n")

    password = input("Enter password: ").strip()
    if not password:
        print("Error: Password cannot be empty.")
        sys.exit(1)

    hash_value = ph.hash(password)

    print("\nSuccess! Copy the following hash into your .env file:\n")
    print(f"ADMIN_PASSWORD_HASH={hash_value}")
    print("\n")


if __name__ == "__main__":
    main()
