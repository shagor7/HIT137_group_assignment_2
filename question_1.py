#encryption
# ope
def encryption(shift1: int, shift2: int):
    text = open("raw_text.txt", 'r').read()
    text1 = []
    for char in text:
        if char >= 'a' and char <= 'm':
            char = chr((ord(char) - ord('a') + (shift1 * shift2)) % 26 + ord('a'))
            text1.append(char)
        elif char >= 'n' and char <= 'z':
            char = chr((ord(char) - ord('a') + (shift1 + shift2)) % 26 + ord('n'))
            text1.append(char)
        if char >= 'A' and char <= 'M':
            char = chr((ord(char) - ord('A') + shift1 ) % 26 + ord('A'))
            text1.append(char)
        elif char >= 'N' and char <= 'Z':
            char = chr((ord(char) - ord('A') + (shift2 * shift2)) % 26 + ord('N'))
            text1.append(char)
    open("encrypted_text.txt", 'w').write(''.join(text1))
    return ''.join(text1)
x = int(input("Enter the first shift value: "))
y = int(input("Enter the second shift value: "))
encryption(x, y)
