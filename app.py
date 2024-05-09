from flask import Flask, render_template, request, redirect, url_for
import numpy as np
from PIL import Image
from EmbeddingExtraction import logistic_map, generate_random_numbers, encrypt_message, embed_message_in_image, extract_message_from_image
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/embed', methods=['POST'])
def embed():
    # Get the text message and cover image from the formflask
    text_message = request.form['text_message']
    cover_image = request.files['cover_image']

    # Convert text message to bits
    message_bits = [int(bit) for bit in bin(int.from_bytes(text_message.encode(), 'big'))[2:]]

    # Generate random numbers using logistic map
    num_bits = len(message_bits)
    x_initial = 0.5
    u_initial = 3.9
    random_numbers = generate_random_numbers(num_bits, x_initial, u_initial)

    # Encrypt the message
    encrypted_message = encrypt_message(message_bits, random_numbers)

    # Embed the message in the image
    image = np.array(Image.open(cover_image))
    n_lsb = 2  # Example n value
    embedded_image = embed_message_in_image(image, encrypted_message, n_lsb)

    # Save the embedded image
    embedded_image_path = 'static/embedded_image.png'
    Image.fromarray(embedded_image).save(embedded_image_path)

    return render_template('EmbeddingResult.html', result='Embedding successful', image_path=embedded_image_path)

@app.route('/extract', methods=['POST'])
def extract():
    # Get the stego image from the form
    stego_image = request.files['stego_image']

    # Extract the message from the image
    image = np.array(Image.open(stego_image))
    n_lsb = 2  # Example n value
    x_initial = 0.5
    u_initial = 3.9
    extracted_message = extract_message_from_image(image, n_lsb, x_initial, u_initial)

    # Convert extracted message bits to text
    extracted_message_bytes = bytearray()
    for i in range(0, len(extracted_message), 8):
        byte = int(''.join(str(bit) for bit in extracted_message[i:i+8]), 2)
        extracted_message_bytes.append(byte)
    extracted_message_text = extracted_message_bytes.decode()

    return render_template('ExtractionResult.html', result='Extraction successful', extracted_message=extracted_message_text)

if __name__ == '__main__':
    app.run(debug=True)
    

