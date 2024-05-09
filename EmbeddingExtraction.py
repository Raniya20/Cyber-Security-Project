import numpy as np
from PIL import Image


def logistic_map(x, u):
    x = u * x * (1 - x)
    if x == float('inf') or x == float('-inf') or abs(x) > 1e10:
        x = 0.5  # Reset x to a reasonable value
    return x

def generate_random_numbers(num_bits, x, u):
    random_numbers = []
    for _ in range(num_bits):
        x = logistic_map(x, u)
        random_number = int(x * 10)  # Multiply by 10 and convert to integer
        random_numbers.append(random_number)
    return random_numbers

def encrypt_message(original_message, random_numbers):
    encrypted_message = [bit ^ random_numbers[i] for i, bit in enumerate(original_message)]
    return encrypted_message

def embed_message_in_image(image, encrypted_message, n):
    height, width, _ = image.shape
    message_index = 0
    for y in range(height):
        for x in range(width):
            pixel = image[y, x]
            for i in range(3):  # R, G, B channels
                for j in range(n):  # n least significant bits
                    if message_index < len(encrypted_message):
                        pixel[i] = (pixel[i] & ~(1 << j)) | ((encrypted_message[message_index] & 1) << j)
                        message_index += 1
            image[y, x] = pixel
    return image

# Example Usage
message_bits = [0, 1, 0, 1, 1, 0, 1, 0]  # Example message bits
num_bits = len(message_bits)
x_initial = 0.5
u_initial = 3.9
random_numbers = generate_random_numbers(num_bits, x_initial, u_initial)
encrypted_message = encrypt_message(message_bits, random_numbers)

# Assuming you have a 24-bit RGB image as a numpy array
image = np.random.randint(0, 256, size=(100, 100, 3), dtype=np.uint8)  # Example random image
n_lsb = 2  # Example n value

embedded_image = embed_message_in_image(image, encrypted_message, n_lsb)


def extract_message_from_image(image, n, x, u):
    height, width, _ = image.shape
    extracted_message = []
    random_numbers = []
    total_bits = height * width * 3 * n  # Total number of bits to extract
    bit_count = 0  # Counter for extracted bits

    for y in range(height):
        for x in range(width):
            pixel = image[y, x]
            for i in range(3):  # R, G, B channels
                for j in range(n):  # n least significant bits
                    if bit_count >= total_bits:
                        break
                    extracted_bit = (pixel[i] >> j) & 1
                    extracted_message.append(extracted_bit)
                    bit_count += 1
                if bit_count >= total_bits:
                    break
            if bit_count >= total_bits:
                break
        if bit_count >= total_bits:
            break
    
    for _ in range(len(extracted_message)):
        x = logistic_map(x, u)
        random_number = int(x * 10)  # Multiply by 10 and convert to integer
        random_numbers.append(random_number)
    
    # Convert extracted message bits to text
    extracted_message_bytes = bytearray()
    for i in range(0, len(extracted_message), 8):
        byte_str = ''.join(str(bit) for bit in extracted_message[i:i+8])
        try:
            byte = int(byte_str, 2)
            extracted_message_bytes.append(byte)
        except ValueError:
            print(f"Error converting binary string '{byte_str}' to integer.")

    original_message = ""
    for i, byte in enumerate(extracted_message_bytes):
        # Handle large integers
        try:
            character = chr((byte ^ random_numbers[i]) % 256)  # Limit to 0-255 range
            original_message += character
        except OverflowError:
            # Replace with a placeholder character
            original_message += "?"

    return original_message
# Example Usage
stego_image = embedded_image  # Assuming you have the stego image from the embedding algorithm
n_lsb = 2  # Example n value
x_initial = 0.5
u_initial = 3.9

extracted_message = extract_message_from_image(stego_image, n_lsb, x_initial, u_initial)
print("Extracted Message:", extracted_message)
