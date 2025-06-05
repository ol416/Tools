from flask import Flask, request, send_file
import qrcode
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from PIL import Image, ImageDraw

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    """
    Displays usage instructions for the QR code generator.
    """
    return """
    <h1>QR Code Generator</h1>
    <p>Enter text to generate a QR code:</p>
    <form action="/generate_qrcode" method="get">
        <label for="data">Data:</label>
        <input type="text" id="data" name="data"><br><br>
        <input type="submit" value="Generate QR Code">
    </form>
    <h2>API Usage</h2>
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
    qr_img = qr.make_image(fill_color="black", back_color="white")

   # Generate Barcode
    try:
        ean = barcode.get('ean13', data, writer=ImageWriter())
        barcode_img_buffer = BytesIO()
        ean.write(barcode_img_buffer)
        barcode_img_buffer.seek(0)
        barcode_img = Image.open(barcode_img_buffer)
    except Exception as e:
        try:
            code128 = barcode.get('code128', data, writer=ImageWriter())
            barcode_img_buffer = BytesIO()
            code128.write(barcode_img_buffer)
            barcode_img_buffer.seek(0)
            barcode_img = Image.open(barcode_img_buffer)
        except Exception as e:
            return f"Error generating barcode: {str(e)}", 500

    # Combine images
    qr_width, qr_height = qr_img.size
    barcode_width, barcode_height = barcode_img.size
    combined_width = max(qr_width, barcode_width)
    combined_height = qr_height + barcode_height
    combined_img = Image.new("RGB", (combined_width, combined_height), "white")
    combined_img.paste(qr_img, (int((combined_width - qr_width) / 2), 0))
    combined_img.paste(barcode_img, (int((combined_width - barcode_width) / 2), qr_height))

    img_buffer = BytesIO()
    combined_img.save(img_buffer, 'PNG')
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
