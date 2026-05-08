import streamlit as st
import PyPDF2
from datetime import datetime
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import nltk

@st.cache_resource
def download_nltk_data():
    nltk.download('punkt')

download_nltk_data()

st.set_page_config(page_title="ملخصي - اشتراك شهري 200ج", page_icon="📝")

# من Secrets
MONTHLY_CODE = st.secrets["MONTHLY_CODE"]
ADMIN_KEY = st.secrets["ADMIN_KEY"]
CURRENT_MONTH_YEAR = datetime.now().strftime("%m-%Y")

# رقم أورنج كاش
ORANGE_CASH_NUMBER = "01289590022"

if 'subscribed' not in st.session_state:
    st.session_state.subscribed = False

st.title("📝 ملخصي - النسخة المدفوعة")

# لوحة الأدمن
with st.sidebar:
    st.subheader("🔑 لوحة الأدمن")
    admin_input = st.text_input("مفتاح الأدمن:", type="password")
    if admin_input == ADMIN_KEY:
        st.success("أهلاً أدمن ✅")
        st.info(f"كود التفعيل الحالي: **{MONTHLY_CODE}**")
        st.warning("لتغيير الكود: Settings > Secrets > عدل MONTHLY_CODE")
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
        if code_input == MONTHLY_CODE:
            st.session_state.subscribed = True
            st.success("تم التفعيل ✅")
            st.rerun()
        else:
            st.error("الكود غلط")
else:
    st.success("اشتراكك مفعل ✅")
    st.subheader("📤 ارفع ملف PDF للتلخيص")
    
    uploaded_file = st.file_uploader("اختر ملف PDF", type="pdf", help="أقصى حجم 200MB")
    
    if uploaded_file:
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            st.info(f"عدد الصفحات: {len(pdf_reader.pages)}")
            
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            if len(text.strip()) < 50:
                st.error("الملف فاضي أو الصور بس. اتأكد إن الـ PDF فيه نص مش صور")
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
            st.error("حصل خطأ في قراءة الملف: تأكد إنه PDF سليم")
