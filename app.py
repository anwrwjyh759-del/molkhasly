from flask import Flask, request, render_template_string
import PyPDF2
from PIL import Image
import pytesseract
import os

app = Flask(__name__)

# غيري الكود ده كل شهر من Render > Environment Variables
ACTIVATION_CODE = os.environ.get('ACTIVATION_CODE', 'molkhasly512')

HTML = '''
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ملخصلي - لخص ملفاتك في ثواني</title>
    <style>
        body { font-family: Arial; max-width: 700px; margin: 20px auto; padding: 20px; background: #f5f5f5; }
        .box { background: white; padding: 20px; border-radius: 12px; margin: 15px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        input, button, textarea { width: 100%; padding: 12px; margin: 8px 0; border-radius: 8px; border: 1px solid #ddd; font-size: 16px; box-sizing: border-box; }
        button { background: #4CAF50; color: white; cursor: pointer; font-weight: bold; border: none; }
        button:hover { background: #45a049; }
        h1 { color: #333; text-align: center; margin-bottom: 10px; }
        .sub { background: #fff3cd; padding: 15px; border-radius: 8px; border-right: 5px solid #ffc107; }
        .whatsapp-btn { background: #25D366; display: block; text-align: center; text-decoration: none; color: white; padding: 12px; border-radius: 8px; font-weight: bold; }
        .whatsapp-btn:hover { background: #20bd5a; }
        .warning { color: #d32f2f; font-size: 14px; }
    </style>
</head>
<body>
    <h1>📝 ملخصلي</h1>
    <p style="text-align:center; color:#666;">ارفع PDF أو صورة وطلع النص والملخص فوراً</p>
    
    <div class="box sub">
        <b>💳 الاشتراك الشهري: 200 جنيه</b><br>
        الدفع أورنج كاش على: <b>01289590022</b><br><br>
        <a href="https://wa.me/201289590022?text=عايز%20اشترك%20في%20ملخصلي%20واشتريت%20بـ200%20جنيه" class="whatsapp-btn">
            📱 كلمنا واتساب بعد الدفع عشان نفعل حسابك
        </a>
        <p class="warning">⚠️ ملاحظة: للصور الجودة الضعيفة نتيجتها مش دقيقة. PDF أفضل بكتير</p>
    </div>
    
    <form method="POST" enctype="multipart/form-data" class="box">
        <label><b>1. كود التفعيل الشهري:</b></label>
        <input type="password" name="code" placeholder="دخّل الكود اللي خته مننا" required>
        
        <label><b>2. ارفع ملفك:</b></label>
        <input type="file" name="file" accept=".pdf,.jpg,.jpeg,.png" required>
        
        <button type="submit">🚀 استخرج ولخص دلوقتي</button>
    </form>
    
    {% if status %}
    <div class="box">
        <h3>الحالة:</h3>
        <p>{{ status }}</p>
    </div>
    {% endif %}
    
    {% if text %}
    <div class="box">
        <h3>📄 النص المستخرج:</h3>
        <textarea rows="10" readonly>{{ text }}</textarea>
    </div>
    {% endif %}
    
    {% if summary %}
    <div class="box">
        <h3>📌 الملخص السريع:</h3>
        <p style="white-space: pre-line;">{{ summary }}</p>
    </div>
    {% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    status = text = summary = ""
    if request.method == 'POST':
        code = request.form.get('code', '')
        if code != ACTIVATION_CODE:
            return render_template_string(HTML, status="❌ كود التفعيل غلط. لو دفعت كلمنا واتساب نفعل حسابك")
        
        file = request.files.get('file')
        if not file or file.filename == '':
            return render_template_string(HTML, status="❌ لازم ترفع ملف الأول")
        
        try:
            if file.filename.lower().endswith('.pdf'):
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            else:
                image = Image.open(file)
                text = pytesseract.image_to_string(image, lang='ara+eng')
        except Exception as e:
            return render_template_string(HTML, status=f"❌ حصل خطأ: تأكد إن الملف سليم وواضح")
        
        if len(text.strip()) < 30:
            status = "⚠️ مقدرتش أطلع نص كفاية. الصورة مش واضحة أو الملف فاضي. جرب PDF أو صورة أوضح"
        else:
            status = "✅ تم استخراج النص بنجاح"
            # تلخيص بسيط: أول 5 سطور مهمين
            lines = [line.strip() for line in text.split('\n') if len(line.strip()) > 25]
            summary = '\n'.join(lines[:5]) if lines else "النص قصير جداً"
    
    return render_template_string(HTML, status=status, text=text, summary=summary)

if __name__ == '__main__':
    app.run()
