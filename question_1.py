import os

# Function: ensure_raw_file
# Purpose : Check whether raw_text.txt exists.
#           If it exists, ask the user whether to update it.
#           If it does not exist, create it using user input.

def ensure_raw_file():
    if os.path.exists("raw_text.txt"):
        while True:
            choice = input("raw_text.txt exists. Do you want to update it? (y/n): ").strip().lower()
            if choice == 'y':
                while True:
                    user_text = input("Enter text to encrypt: ").strip()
                    if user_text == "":
                        print("Text cannot be empty. Please enter some text.")
                    else:
                        break
                    
                with open("raw_text.txt", "w", encoding="utf-8") as file:
                    file.write(user_text)

                print("raw_text.txt updated.")
                break

            elif choice == 'n':
                print("Using existing raw_text.txt.")
                break

            else:
                print("Invalid input. Please enter y or n.")

    else:
        print("raw_text.txt does not exist.")

        while True:
            user_text = input("Enter text to create raw_text.txt: ").strip()
            if user_text == "":
                print("Text cannot be empty. Please enter some text.")
            else:
                break
        with open("raw_text.txt", "w", encoding="utf-8") as file:
            file.write(user_text)
        print("raw_text.txt created.")
# Function: shift_in_group
# Purpose : Shift a character inside a fixed group
#           of 13 letters only.
#           Example groups: a-m, n-z, A-M, N-Z
def shift_in_group(char, start_char, shift):
    group_size = 13
    return chr((ord(char) - ord(start_char) + shift) % group_size + ord(start_char))
# Function: encrypt_char
# Purpose : Encrypt one character according to the
#           given rules in the question.
def encrypt_char(char, shift1, shift2):
    # Lowercase first half: a-m
    if 'a' <= char <= 'm':
        return shift_in_group(char, 'a', shift1 * shift2)

    # Lowercase second half: n-z
    elif 'n' <= char <= 'z':
        return shift_in_group(char, 'n', -(shift1 + shift2))

    # Uppercase first half: A-M
    elif 'A' <= char <= 'M':
        return shift_in_group(char, 'A', -shift1)

    # Uppercase second half: N-Z
    elif 'N' <= char <= 'Z':
        return shift_in_group(char, 'N', shift2 ** 2)

    # Other characters remain unchanged
    else:
        return char
# Function: decrypt_char
# Purpose : Reverse the encryption rules for one
#           character.
def decrypt_char(char, shift1, shift2):
    # Lowercase first half: a-m
    if 'a' <= char <= 'm':
        return shift_in_group(char, 'a', -(shift1 * shift2))

    # Lowercase second half: n-z
    elif 'n' <= char <= 'z':
        return shift_in_group(char, 'n', shift1 + shift2)

    # Uppercase first half: A-M
    elif 'A' <= char <= 'M':
        return shift_in_group(char, 'A', shift1)

    # Uppercase second half: N-Z
    elif 'N' <= char <= 'Z':
        return shift_in_group(char, 'N', -(shift2 ** 2))

    # Other characters remain unchanged
    else:
        return char
# Function: encrypt_file
# Purpose : Read raw_text.txt, encrypt its content,
#           and write the result to encrypted_text.txt
def encrypt_file(shift1, shift2):
    with open("raw_text.txt", "r", encoding="utf-8") as file:
        original_text = file.read()

    encrypted_text = "".join(encrypt_char(char, shift1, shift2) for char in original_text)

    with open("encrypted_text.txt", "w", encoding="utf-8") as file:
        file.write(encrypted_text)

    print("Encryption completed successfully.")
# Function: decrypt_file
# Purpose : Read encrypted_text.txt, decrypt its
#           content, and write the result to
#           decrypted_text.txt
def decrypt_file(shift1, shift2):
    with open("encrypted_text.txt", "r", encoding="utf-8") as file:
        encrypted_text = file.read()

    decrypted_text = "".join(decrypt_char(char, shift1, shift2) for char in encrypted_text)

    with open("decrypted_text.txt", "w", encoding="utf-8") as file:
        file.write(decrypted_text)

    print("Decryption completed successfully.")

# Function: verify_decryption
# Purpose : Compare raw_text.txt and decrypted_text.txt
#           to check whether decryption was successful.

def verify_decryption():
    with open("raw_text.txt", "r", encoding="utf-8") as file1:
        original_text = file1.read()

    with open("decrypted_text.txt", "r", encoding="utf-8") as file2:
        decrypted_text = file2.read()

    if original_text == decrypted_text:
        print("Verification successful: decryption matches the original text.")
    else:
        print("Verification failed: decryption does not match the original text.")

# Function: main
# Purpose : Control the whole program.
#           1. Check input file
#           2. Take user input
#           3. Encrypt file
#           4. Decrypt file
#           5. Verify result

def main():
    ensure_raw_file()

    while True:
        try:
            shift1 = int(input("Enter shift1 value: "))
            break
        except ValueError:
            print("Please enter an integer.")
    while True:
        try:
            shift2 = int(input("Enter shift2 value: "))
            break
        except ValueError:
            print("Please enter an integer.")

    encrypt_file(shift1, shift2)
    decrypt_file(shift1, shift2)
    verify_decryption()


# Run the program
main()