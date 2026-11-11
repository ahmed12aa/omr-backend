from flask import Flask, request, jsonify
from google import genai
from google.genai import types
import os
import json

app = Flask(__name__)

# تهيئة العميل باستخدام المفتاح المعتمد من البيئة (Environment Variables)
# لضمان عدم تسريب المفاتيح داخل الكود البرمجي
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is missing!")

client = genai.Client(api_key=api_key)

@app.route('/health', methods=['GET'])
def health_check():
    """ نقطة فحص حالة المنصة للتأكد من عمل السيرفر بنجاح """
    return jsonify({
        "status": "active",
        "platform": "Google Cloud Production Ready",
        "version": "1.0.0"
    }), 200

@app.route('/scan-exam', methods=['POST'])
def scan_exam_sheet():
    """ نقطة النهاية الأساسية لاستلام ورقة الامتحان وتحليلها """
    if 'image' not in request.files:
        return jsonify({'error': 'لم يتم إرسال ملف الصورة'}), 400
    
    file = request.files['image']
    image_bytes = file.read()
    
    if not image_bytes:
        return jsonify({'error': 'ملف الصورة فارغ'}), 400

    try:
        # التوجيه الهندسي المتقدم للنموذج لاستخراج النتيجة بدقة معمارية
        prompt = """
        أنت نظام ذكاء اصطناعي متخصّص في تصحيح أوراق الامتحانات الآلية (OMR).
        قم بتحليل صورة ورقة الإجابة المرفقة بدقة بالغة واستخرج البيانات التالية:
        1. رقم الطالب (Student ID).
        2. عدد الإجابات الصحيحة.
        3. الدرجة النهائية من 50.
        4. التقدير العام (ممتاز، جيد جداً، جيد، راسب).
        
        أجب حصرياً بصيغة JSON صحيحة ومتوافقة مع المعيار التالي بدون أي نصوص إضافية:
        {
          "status": "success",
          "student_id": "رقم الطالب المستخرج",
          "correct_answers": عدد صحيح,
          "total_questions": 50,
          "score": الدرجة,
          "evaluation": "التقدير"
        }
        """

        # استدعاء أحدث النماذج المعتمَدَة من منصة Google AI
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type='image/jpeg',
                ),
                prompt
            ]
        )

        # تنظيف استجابة الـ Model واستخراج صيغة الـ JSON بدقة
        text_response = response.text.strip()
        if text_response.startswith("```json"):
            text_response = text_response[7:-3].strip()
        elif text_response.startswith("```"):
            text_response = text_response[3:-3].strip()

        result_json = json.loads(text_response)
        return jsonify(result_json), 200

    except Exception as e:
        return jsonify({'error': f'حدث خطأ داخلي أثناء المعالجة: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
