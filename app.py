import streamlit as st
import PyPDF2
import requests
import base64
import json
from datetime import datetime
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import nltk
from PIL import Image
import pytesseract

@st.cache_resource
def download_nltk_data():
    nltk.download('punkt')

download_nltk_data()

st.set_page_config(page_title="ملخصي - اشتراك شهري 200ج", page_icon="📝")

# من Secrets
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
ADMIN_KEY = st.secrets["ADMIN_KEY"]
GITHUB_REPO = "anwrwjyh759-del/molkhasly"
GITHUB_FILE_PATH = "current_code.json"
CURRENT_MONTH_YEAR = datetime.now().strftime("%m-%Y")

ORANGE_CASH_NUMBER = "01289590022"

def get_current_code():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        content = base64.b64decode(r.json()['content']).decode()
        data = json.loads(content)
        return data.get('code', ''), r.json()['sha']
    return '', None

def update_code(new_code, sha):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    data = {
        "message": f"Update code {CURRENT_MONTH_YEAR}",
        "content": base64.b64encode(json.dumps({"code": new_code}).encode()).decode(),
        "sha": sha
    }
    r = requests.put(url, headers=headers, json=data)
    return r.status_code == 200

CURRENT_CODE, FILE_SHA = get_current_code()

if 'subscribed' not in st.session_state:
    st.session_state.subscribed = False

st.title("📝 ملخصي - النسخة المدفوعة")

# لوحة الأدمن
with st.sidebar:
    st.subheader("🔑 لوحة الأدمن")
    admin_input = st.text_input("مفتاح الأدمن:", type="password")
    if admin_input == ADMIN_KEY:
        st.success("أهلاً أدمن ✅")
        st.info(f"الكود الحالي: {CURRENT_CODE}")
        new_code_input = st.text_input("الكود الجديد للشهر:", value=CURRENT_CODE)
        if st.button("حدث كود الشهر"):
            if FILE_SHA and update_code(new_code_input, FILE_SHA):
                st.success("الكود اتحدث ✅")
                st.rerun()
            else:
                st.error("فشل التحديث")
    elif admin_input != "":
        st.error("مفتاح الأدمن غلط")

# واجهة المستخدم
if not st.session_state.subscribed:
    st.warning(f"⚠️ اشتراك شهر {CURRENT_MONTH_YEAR} مطلوب - 200 جنيه")
    with st.container(border=True):
        st.subheader("💳 طريقة الاشتراك")
        st.write("1. حول 200 جنيه على أورنج كاش:")
        st.code(ORANGE_CASH_NUMBER, language=None)
        st.write("2. ابعت سكرين التحويل على واتساب: 01289590022")
        st.write("3. هبعتلك كود التفعيل فوراً")
    code_input = st.text_input(f"دخل كود شهر {CURRENT_MONTH_YEAR} بعد الدفع:")
    if st.button("تفعيل"):
        if code_input == CURRENT_CODE:
            st.session_state.subscribed = True
            st.success("تم التفعيل ✅")
            st.rerun()
        else:
            st.error("الكود غلط")
else:
    st.success("اشتراكك مفعل ✅")
    st.subheader("📤 ارفع PDF أو صورة للتلخيص")
    
    uploaded_file = st.file_uploader("اختر ملف", type=["pdf", "png", "jpg", "jpeg"])
    
    if uploaded_file:
        text = ""
        try:
            if uploaded_file.type == "application/pdf":
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                st.info(f"عدد الصفحات: {len(pdf_reader.pages)}")
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            else:
                st.info("جاري قراءة النص من الصورة... ممكن تاخد دقيقة")
                image = Image.open(uploaded_file)
                text = pytesseract.image_to_string(image, lang='ara+eng')
            
            if len(text.strip()) < 50:
                st.error("النص قليل أو مش واضح. اتأكد إن الصورة جودتها عالية والكلام واضح")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    num_sentences = st.slider("عدد جمل الملخص:", 3, 10, 5)
                with col2:
                    if st.button("✨ لخص الملف", type="primary"):
                        with st.spinner("جاري التلخيص..."):
                            parser = PlaintextParser.from_string(text, Tokenizer("arabic"))
                            summarizer = LsaSummarizer()
                            summary = summarizer(parser.document, num_sentences)
                            result = " ".join([str(s) for s in summary])
                            st.subheader("📝 الملخص:")
                            st.write(result)
                            st.download_button("📥 حمل الملخص", result, file_name="summary.txt")
        except Exception as e:
            st.error(f"حصل خطأ: {e}")
