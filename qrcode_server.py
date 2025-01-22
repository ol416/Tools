from flask import Flask, request, send_file
import qrcode
from io import BytesIO

app = Flask(__name__)

@app.route('/generate_qrcode', methods=['GET'])
def generate_qrcode():
    data = request.args.get('data', '')
    if not data:
        return "No data provided", 400

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
    img.save(img_buffer)
    img_buffer.seek(0)

    return send_file(img_buffer, mimetype='image/png')

if __name__ == '__main__':
        app.run(ssl_context=(r'D:\Tools\mkcert\localhost+2.pem', r'D:\Tools\mkcert\localhost+2-key.pem'), debug=True)

