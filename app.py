from flask import Flask, request, jsonify
import google.generativeai as genai
import os
import json
from PIL import Image
import io

app = Flask(__name__)

# تهيئة مفتاح الـ API للذكاء الاصطناعي
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "active", "message": "OMR Backend with Stable Gemini AI is running!"})

@app.route('/scan', methods=['POST'])
def scan_sheet():
    if not api_key:
        return jsonify({'error': 'مفتاح GEMINI_API_KEY غير مُعرف في السيرفر'}), 500

    if 'image' not in request.files:
        return jsonify({'error': 'لم يتم إرسال أي صورة'}), 400
    
    file = request.files['image']
    image_bytes = file.read()
    
    if not image_bytes:
        return jsonify({'error': 'الصورة فارغة'}), 400

    try:
        # قراءة الصورة باستخدام PIL
        image = Image.open(io.BytesIO(image_bytes))

        # استخدام النموذج القياسي المستقر السريع
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = """
        هذه صورة ورقة إجابة امتحان (OMR). قم بتحليل الصورة بدقة:
        1. استخرج رقم الطالب (إن وجد).
        2. احسب عدد الإجابات الصحيحة والدرجة الكلية من 50.
        3. أعطِ تقييماً عاماً لمستوى الطالب (ممتاز، جيد جداً، جيد، راسب).
        
        أجب حصرياً بصيغة JSON صحيحة بالهيكل التالي فقط بدون أي نصوص أو علامات إضافية:
        {
          "status": "success",
          "student_id": "20261001",
          "correct_answers": 45,
          "total_questions": 50,
          "score": 90,
          "evaluation": "ممتاز"
        }
        """

        response = model.generate_content([image, prompt])
        text_response = response.text.strip()
        
        # تنظيف الرد واستخراج الـ JSON
        if text_response.startswith("```json"):
            text_response = text_response[7:-3].strip()
        elif text_response.startswith("```"):
            text_response = text_response[3:-3].strip()

        result_json = json.loads(text_response)
        return jsonify(result_json), 200

    except Exception as e:
        return jsonify({'error': f'خطأ في المعالجة: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
