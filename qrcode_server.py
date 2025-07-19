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
    <head>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                background-color: #f4f4f4;
            }
            form {
                display: flex;
                flex-direction: column;
                align-items: flex-start;
                margin-bottom: 20px;
                padding: 20px;
                background-color: #fff;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            label {
                margin-bottom: 5px;
                font-weight: bold;
            }
            textarea {
                padding: 8px;
                margin-bottom: 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                width: 100%;
                height: 100px;
            }
            select {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                cursor: pointer;
            }
            select:hover {
                border-color: #aaa;
            }
            .options {
                display: flex;
                align-items: center;
            }
            .options > div {
                margin-right: 20px;
            }
            input[type="radio"] {
                margin-right: 5px;
                cursor: pointer;
            }
            input[type="radio"]:hover + label {
                text-decoration: underline;
            }
            img {
                max-width: 300px;
                border: 1px solid #ccc;
                border-radius: 4px;
                margin-top: 20px;
            }
        </style>
    </head>
    <h1>QR Code Generator</h1>
    <p>Enter text to generate a QR code:</p>
    <form action="/generate_qrcode" method="get">
        <label for="data">Data:</label>
        <textarea id="data" name="data" rows="4" cols="50"></textarea>
        <label for="autoReset">Auto Reset Data:<input type="checkbox" id="autoReset" name="autoReset"></label>

        <div class="options">
            <div style="margin-right: 20px;">
                <label for="mode">Mode:</label>
                <select id="mode" name="mode">
                    <option value="qr">QR Code</option>
                    <option value="barcode">Barcode</option>
                    <option value="both">Both</option>
                </select>
            </div>
            <div>
                <label>Position:</label>
                <input type="radio" id="leftRight" name="position" value="leftRight">
                <label for="leftRight">Left/Right</label>
                <input type="radio" id="topBottom" name="position" value="topBottom">
                <label for="topBottom">Top/Bottom</label>
            </div>
        </div>

        <div>
            <label for="error_correction">Error Correction:</label>
            <select id="error_correction" name="error_correction" id="error_correction">
                <option value="L">L</option>
                <option value="M">M</option>
                <option value="Q">Q</option>
                <option value="H">H</option>
            </select>
        </div>

        <div>
            <label for="size">Size:</label>
            <input type="number" id="size" name="size" value="10" min="1" id="size">
        </div>

        <div>
            <label for="padding">Padding:</label>
            <input type="number" id="padding" name="padding" value="4" min="0" id="padding">
        </div>
    </form>

    <img id="qrcodeImage" src="" alt="Generated QR Code"><br><br>

    <h2>API Usage</h2>
    <p>To generate a QR code, send a GET request to the <code>/generate_qrcode</code> endpoint with the <code>data</code> parameter.</p>
    <p>Examples:</p>
    <ul style="list-style-type: disc; padding-left: 20px;">
        <li><code>/generate_qrcode?data=your_data_here</code> (Default: Both QR & Barcode, Top/Bottom, Error Correction L, Size 10, Padding 4)</li>
        <li><code>/generate_qrcode?data=your_data_here&mode=qr</code> (QR code only)</li>
        <li><code>/generate_qrcode?data=your_data_here&mode=barcode</code> (Barcode only)</li>
        <li><code>/generate_qrcode?data=your_data_here&mode=both&position=leftRight</code> (Both QR & Barcode, Left/Right)</li>
        <li><code>/generate_qrcode?data=your_data_here&mode=both&position=topBottom</code> (Both QR & Barcode, Top/Bottom)</li>
        <li><code>/generate_qrcode?data=your_data_here&mode=qr&error_correction=H&size=12&padding=2</code> (QR code with High error correction, size 12, padding 2)</li>
        <li><code>/generate_qrcode?data=your_data_here&mode=barcode&size=15&padding=5</code> (Barcode with size 15 (affects module width), padding 5)</li>
        <li><code>/generate_qrcode?data=your_data_here&mode=both&position=leftRight&error_correction=M&size=8&padding=1</code> (Both, Left/Right, QR Error Correction M, Size 8, Padding 1)</li>
    </ul>
    <p>Replace <code>your_data_here</code> with the data you want to encode.</p>

    <script>
        const modeSelect = document.getElementById('mode');
        const positionOptions = document.getElementById('positionOptions');
        const leftRightRadio = document.getElementById('leftRight');
        const topBottomRadio = document.getElementById('topBottom');
        const dataInput = document.getElementById('data');
        const qrcodeImage = document.getElementById('qrcodeImage');
        const form = document.querySelector('form');
        const autoResetCheckbox = document.getElementById('autoReset');
        const errorCorrectionSelect = document.getElementById('error_correction');
        const sizeInput = document.getElementById('size');
        const paddingInput = document.getElementById('padding');

        // Load saved settings
        const savedMode = localStorage.getItem('mode');
        const savedPosition = localStorage.getItem('position');
        const savedAutoReset = localStorage.getItem('autoReset');
        const savedErrorCorrection = localStorage.getItem('error_correction');
        const savedSize = localStorage.getItem('size');
        const savedPadding = localStorage.getItem('padding');

        if (savedMode) {
            modeSelect.value = savedMode;
        }
        if (savedPosition) {
            if (savedPosition === 'leftRight') {
                leftRightRadio.checked = true;
            } else if (savedPosition === 'topBottom') {
                topBottomRadio.checked = true;
            }
        }
        if (savedAutoReset) {
            autoResetCheckbox.checked = savedAutoReset === 'true';
        }
        if (savedErrorCorrection) {
            errorCorrectionSelect.value = savedErrorCorrection;
        }
        if (savedSize) {
            sizeInput.value = savedSize;
        }
        if (savedPadding) {
            paddingInput.value = savedPadding;
        }

        modeSelect.addEventListener('change', function() {
            localStorage.setItem('mode', modeSelect.value);
        });

        leftRightRadio.addEventListener('change', function() {
            localStorage.setItem('position', 'leftRight');
        });

        topBottomRadio.addEventListener('change', function() {
            localStorage.setItem('position', 'topBottom');
        });

        autoResetCheckbox.addEventListener('change', function() {
            localStorage.setItem('autoReset', autoResetCheckbox.checked);
        });

        errorCorrectionSelect.addEventListener('change', function() {
            localStorage.setItem('error_correction', errorCorrectionSelect.value);
        });

        sizeInput.addEventListener('change', function() {
            localStorage.setItem('size', sizeInput.value);
        });

        paddingInput.addEventListener('change', function() {
            localStorage.setItem('padding', paddingInput.value);
        });

        function updateImage() {
            const data = dataInput.value;
            const mode = modeSelect.value;
            let position = 'topBottom';
            if (mode === 'both') {
                if (leftRightRadio.checked) {
                    position = 'leftRight';
                } else {
                    position = 'topBottom';
                }
            }
            const errorCorrection = errorCorrectionSelect.value;
            const size = sizeInput.value;
            const padding = paddingInput.value;

            let url = '/generate_qrcode?data=' + encodeURIComponent(data) + '&mode=' + mode + '&position=' + position + '&error_correction=' + errorCorrection + '&size=' + size + '&padding=' + padding;
            fetch(url)
                .then(response => response.blob())
                .then(blob => {
                    const imageUrl = URL.createObjectURL(blob);
                    qrcodeImage.src = imageUrl;
                    if (autoResetCheckbox.checked) {
                        dataInput.value = '';
                    }
                });
        }

        dataInput.addEventListener('keydown', function(event) {
            if (event.keyCode === 13) {
                event.preventDefault();
                updateImage();
                if (autoResetCheckbox.checked) {
                    dataInput.value = '';
                }
            }
        });

        dataInput.addEventListener('input', function() {
            if (!autoResetCheckbox.checked) {
                updateImage();
            }
        });

        form.addEventListener('submit', function(event) {
            event.preventDefault();
        });

        // Generate default QR code on page load
        updateImage();
    </script>
    """


@app.route('/generate_qrcode', methods=['GET'])
def generate_qrcode():
    """
    Generates a QR code from the provided data.
    """
    data = request.args.get('data', '')
    mode = request.args.get('mode', 'both')
    position = request.args.get('position', 'topBottom')
    error_correction = request.args.get('error_correction', 'L')
    size = int(request.args.get('size', 10))
    padding = int(request.args.get('padding', 4))

    if not data:
        data = "Default QR Code"

    qr_img = None
    barcode_img = None

    # Generate QR Code
    if mode in ('qr', 'both'):
        error_correction_level = {
            'L': qrcode.constants.ERROR_CORRECT_L,
            'M': qrcode.constants.ERROR_CORRECT_M,
            'Q': qrcode.constants.ERROR_CORRECT_Q,
            'H': qrcode.constants.ERROR_CORRECT_H,
        }.get(error_correction, qrcode.constants.ERROR_CORRECT_L)

        qr = qrcode.QRCode(
            version=1,
            error_correction=error_correction_level,
            box_size=size,
            border=padding,
        )
        qr.add_data(data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")

    # Generate Barcode
    if mode in ('barcode', 'both'):
        try:
            code128 = barcode.get('code128', data, writer=ImageWriter())
            barcode_img_buffer = BytesIO()
            code128.write(barcode_img_buffer, options={"module_width": size/20, "quiet_zone": padding})
            barcode_img_buffer.seek(0)
            barcode_img = Image.open(barcode_img_buffer)
        except Exception as e:
            return f"Error generating barcode: {str(e)}", 500

    # Combine images
    if mode == 'both':
        qr_width, qr_height = qr_img.size
        barcode_width, barcode_height = barcode_img.size

        if position == 'leftRight':
            combined_width = qr_width + barcode_width
            combined_height = max(qr_height, barcode_height)
            combined_img = Image.new("RGB", (combined_width, combined_height), "white")
            offset = (combined_height - barcode_height) // 2
            combined_img.paste(qr_img, (0, 0))
            combined_img.paste(barcode_img, (qr_width, offset))
        else:  # topBottom
            combined_width = max(qr_width, barcode_width)
            combined_height = qr_height + barcode_height
            combined_img = Image.new("RGB", (combined_width, combined_height), "white")
            combined_img.paste(qr_img, ((combined_width - qr_width) // 2, 0))
            combined_img.paste(barcode_img, ((combined_width - barcode_width) // 2, qr_height))

    elif mode == 'qr':
        combined_img = qr_img
    else:
        combined_img = barcode_img

    img_buffer = BytesIO()
    combined_img.save(img_buffer, 'PNG')
    img_buffer.seek(0)

    return send_file(img_buffer, mimetype='image/png')

if __name__ == '__main__':
    # Use the following line for development with a test certificate.
    #  Remove for production, and handle SSL appropriately for your deployment.
    app.run(ssl_context=(r'D:\Tools\mkcert\localhost+2.pem', r'D:\Tools\mkcert\localhost+2-key.pem'), debug=False,host='0.0.0.0',port=8500)
    # For a production deployment, use a proper WSGI server and configure SSL properly.
    # Example:
    # from waitress import serve
    # serve(app, host='0.0.0.0', port=5000, url_scheme='https', ssl_pem='path/to/certificate.pem', ssl_key='path/to/key.pem')
