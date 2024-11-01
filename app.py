from flask import Flask, request, render_template, send_file, flash, redirect, url_for
import Dehaze
import cv2
import numpy as np
import io
from PIL import Image
import base64

# Create a Flask application instance
app = Flask(__name__)
app.secret_key = "supersecretkey12345"  # Needed for flashing messages

# Define a route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Define a route to handle the image upload
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        flash("No file part in the request")
        return redirect(url_for('home'))

    file = request.files['image']
    if file.filename == '':
        flash("No file selected")
        return redirect(url_for('home'))

    try:
        # Read the uploaded image as a byte stream
        file_bytes = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        # Check if OpenCV successfully read the image
        if img is None:
            flash("Unsupported image format! Please upload a valid image file.")
            return redirect(url_for('home'))

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
        return render_template('result.html', original_image=f"data:image/jpeg;base64,{original_image_str}", dehazed_image=f"data:image/jpeg;base64,{dehazed_image_str}")

    except Exception as e:
        flash("An error occurred while processing the image. Please try again.")
        # Log the exception if needed
        print(f"Error: {e}")
        return redirect(url_for('home'))

# Define a route to handle the download request
@app.route('/download_dehazed')
def download_dehazed():
    try:
        global dehazed_image_buffer
        return send_file(io.BytesIO(dehazed_image_buffer), mimetype='image/jpeg', as_attachment=True, download_name='dehazed_image.jpg')
    except Exception as e:
        flash("Error downloading the image. Please try again.")
        print(f"Error: {e}")
        return redirect(url_for('home'))


# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)  # Set debug=False in production
