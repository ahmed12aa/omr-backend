from flask import Flask, request, jsonify
import cv2
import numpy as np
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "active", "message": "OMR Backend is running successfully!"})

@app.route('/scan', methods=['POST'])
def scan_sheet():
    if 'image' not in request.files:
        return jsonify({'error': 'لم يتم إرسال أي صورة'}), 400

    file = request.files['image']
    npimg = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    if img is None:
        return jsonify({'error': 'صيغة الصورة غير صالحة'}), 400

    # معالجة أولية تجريبية
    result = {
        "status": "success",
        "message": "تمت معالجة الصورة بنجاح على Render",
        "image_shape": f"{img.shape[1]}x{img.shape[0]}",
        "student_id": "20261001",
        "score": 90,
        "total_questions": 50
    }
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
