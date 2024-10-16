from flask import Flask, request, render_template, send_file
import Dehaze
import cv2
import numpy as np
import io
from PIL import Image
import base64

# Create a Flask application instance
app = Flask(__name__)

# Define a route for the home page


@app.route('/')
def home():
    return render_template('index.html')

# Define a route to handle the image upload


@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return "No file part"

    file = request.files['image']

    if file.filename == '':
        return "No selected file"

    if file:
        # Read the image file
        img = Image.open(file.stream)
        img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        # Apply the dehazing function
        dehazed_img = Dehaze.dhazei(img, 0)

        # Convert images to base64 strings
        _, buffer = cv2.imencode('.jpg', img)
        original_image_str = base64.b64encode(buffer).decode('utf-8')

        _, buffer = cv2.imencode('.jpg', dehazed_img)
        dehazed_image_str = base64.b64encode(buffer).decode('utf-8')

        # Store the dehazed image in a global variable for download
        global dehazed_image_buffer
        dehazed_image_buffer = buffer

        # Render the result template with the images
        return render_template('result.html',
                               original_image=f"data:image/jpeg;base64,{
                                   original_image_str}",
                               dehazed_image=f"data:image/jpeg;base64,{dehazed_image_str}")

# Define a route to handle the download request


@app.route('/download_dehazed')
def download_dehazed():
    global dehazed_image_buffer
    return send_file(io.BytesIO(dehazed_image_buffer), mimetype='image/jpeg', as_attachment=True, download_name='dehazed_image.jpg')


# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)