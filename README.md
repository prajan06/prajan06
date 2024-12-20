 import random
import string

def generate_password(length=12):
    # Define characters to use in the password
    all_characters = string.ascii_letters + string.digits + string.punctuation
    
    # Randomly select characters from the pool
    password = ''.join(random.choice(all_characters) for _ in range(length))
    
    return password

# Example usage
if __name__ == "__main__":
    password_length = 16  # You can specify any length you want
    generated_password = generate_password(password_length)
    print("Generated GitHub Password:", generated_password)
