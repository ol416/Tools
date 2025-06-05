from flask import Flask, request, send_file
import qrcode
from io import BytesIO

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    """
    Displays usage instructions for the QR code generator.
    """
    return """
    <h1>QR Code Generator API</h1>
    <p>This API generates QR codes from provided data.</p>
    <h2>Usage</h2>
    <p>To generate a QR code, send a GET request to the <code>/generate_qrcode</code> endpoint with the <code>data</code> parameter.</p>
    <p>Example:</p>
    <pre>/generate_qrcode?data=your_data_here</pre>
    <p>Replace <code>your_data_here</code> with the data you want to encode in the QR code.</p>
    """


@app.route('/generate_qrcode', methods=['GET'])
def generate_qrcode():
    """
    Generates a QR code from the provided data.
    """
    data = request.args.get('data', '')
    if not data:
        return "No data provided. Please use the 'data' parameter in the URL, e.g., /generate_qrcode?data=your_data", 400

    # Generate QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Save to a buffer
    img_buffer = BytesIO()
    img.save(img_buffer, 'PNG') # Specify the format explicitly
    img_buffer.seek(0)

    return send_file(img_buffer, mimetype='image/png')

if __name__ == '__main__':
    # Use the following line for development with a test certificate.
    #  Remove for production, and handle SSL appropriately for your deployment.
    app.run(ssl_context=(r'D:\Tools\mkcert\localhost+2.pem', r'D:\Tools\mkcert\localhost+2-key.pem'), debug=True)
    # For a production deployment, use a proper WSGI server and configure SSL properly.
    # Example:
    # from waitress import serve
    # serve(app, host='0.0.0.0', port=5000, url_scheme='https', ssl_pem='path/to/certificate.pem', ssl_key='path/to/key.pem')
