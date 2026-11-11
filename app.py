from flask import Flask, request, jsonify
from google import genai
from google.genai import types
import os
import json

app = Flask(__name__)

# تهيئة عميل Google GenAI باستخدام المفتاح من متغيرات البيئة
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "active", "message": "OMR Backend with Google AI is running!"})

@app.route('/scan', methods=['POST'])
def scan_sheet():
    if 'image' not in request.files:
        return jsonify({'error': 'لم يتم إرسال أي صورة'}), 400
    
    file = request.files['image']
    image_bytes = file.read()
    
    if not image_bytes:
        return jsonify({'error': 'الصورة فارغة'}), 400

    try:
        # إرسال الصورة إلى نموذج Gemini مع توجيه دقيق لاستخراج الدرجة والإجابات
        prompt = """
        هذه صورة ورقة إجابة امتحان (OMR). قم بتحليل الصورة بدقة:
        1. استخرج رقم الطالب (إن وجد).
        2. احسب عدد الإجابات الصحيحة والدرجة الكلية من 50.
        3. أعطِ تقييماً عاماً لمستوى الطالب (ممتاز، جيد جداً، جيد، راسب).
        
        يجب أن تكون الإجابة بصيغة JSON صالحة حصرياً بالشكل التالي بدون أي نصوص إضافية خارج الـ JSON:
        {
          "status": "success",
          "student_id": "رقم الطالب المستخرج أو افتراضي",
          "correct_answers": عدد صحيح,
          "total_questions": 50,
          "score": الدرجة من 100,
          "evaluation": "التقييم"
        }
        """

        response = client.models.generate_content(
            model='gemini-2.5-flash', # نموذج سريع ودقيق لتحليل الصور
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type='image/jpeg',
                ),
                prompt
            ]
        )

        # تنظيف الرد واستخراج الـ JSON
        text_response = response.text.strip()
        if text_response.startswith("```json"):
            text_response = text_response[7:-3].strip()
        elif text_response.startswith("```"):
            text_response = text_response[3:-3].strip()

        result_json = json.loads(text_response)
        return jsonify(result_json), 200

    except Exception as e:
        return jsonify({'error': f'حدث خطأ أثناء تحليل الذكاء الاصطناعي: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
