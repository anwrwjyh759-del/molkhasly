import os
import cohere
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import PyPDF2
import docx

app = Flask(__name__)

# المفتاح بيتقري من Vercel تلقائي
co = cohere.Client(os.environ.get('COHERE_API_KEY'))

# كود التفعيل الشهري - هتغيره كل شهر من هنا بس
VALID_ACTIVATION_CODE = "ANWAR2026"
SUBSCRIPTION_PRICE = "150 جنيه"
ORANGE_CASH_NUMBER = "01289590022"

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def summarize_with_cohere(text):
    try:
        response = co.summarize(
            text=text,
            length='long',
            format='paragraph',
            model='summarize-xlarge',
            additional_command='لخص باللغة العربية الفصحى المبسطة مع ذكر أهم النقاط',
            temperature=0.3,
        )
        return response.summary
    except Exception as e:
        return f"حصل خطأ في التلخيص: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html', 
                         price=SUBSCRIPTION_PRICE, 
                         number=ORANGE_CASH_NUMBER)

@app.route('/summarize', methods=['POST'])
def summarize():
    # 1. اتأكد من كود التفعيل
    activation_code = request.form.get('activation_code')
    if activation_code != VALID_ACTIVATION_CODE:
        return jsonify({
            'status': 'error',
            'message': f'كود التفعيل غلط ❌\nللاشتراك الشهري {SUBSCRIPTION_PRICE} حول على أورنج كاش: {ORANGE_CASH_NUMBER}'
        })

    # 2. اتأكد إن فيه ملف
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'مرفعتش ملف'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'مخترتش ملف'})

    # 3. استخرج النص من الملف
    try:
        filename = secure_filename(file.filename)
        if filename.endswith('.pdf'):
            text = extract_text_from_pdf(file)
        elif filename.endswith('.docx'):
            text = extract_text_from_docx(file)
        elif filename.endswith('.txt'):
            text = file.read().decode('utf-8')
        else:
            return jsonify({'status': 'error', 'message': 'صيغة الملف مش مدعومة. ارفع PDF أو DOCX أو TXT'})

        if not text.strip():
            return jsonify({'status': 'error', 'message': 'الملف فاضي أو معرفتش أقراه'})

        # 4. لخص النص
        summary = summarize_with_cohere(text)
        
        return jsonify({
            'status': 'success',
            'summary': summary
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'حصل خطأ: تأكد إن الملف سليم وواضح'
        })

if __name__ == '__main__':
    app.run(debug=True)
