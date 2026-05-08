import streamlit as st
import PyPDF2
from datetime import datetime, timedelta
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import nltk
import extra_streamlit_components as stx

@st.cache_resource
def download_nltk_data():
    nltk.download('punkt')

download_nltk_data()

st.set_page_config(page_title="ملخصي - اشتراك شهري 200ج", page_icon="📝")

cookie_manager = stx.CookieManager()

try:
    MONTHLY_CODE = st.secrets["MONTHLY_CODE"]
except:
    st.error("الكود الشهري مش متضاف في Secrets. ضيفه من Settings > Secrets")
    st.stop()

CURRENT_MONTH_YEAR = datetime.now().strftime("%m-%Y")

cookies = cookie_manager.get_all()
if cookies.get("molkhasly_sub") == CURRENT_MONTH_YEAR:
    st.session_state.subscribed = True
else:
    if 'subscribed' not in st.session_state:
        st.session_state.subscribed = False

st.title("📝 ملخصي - النسخة المدفوعة")
st.caption("اشتراك شهري 200 جنيه")

if not st.session_state.subscribed:
    st.warning(f"⚠️ اشتراك شهر {CURRENT_MONTH_YEAR} مطلوب - 200 جنيه")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("طريقة الاشتراك")
        st.info("""
        **السعر: 200 جنيه شهرياً**
        
        **1. حول على Orange Cash:**  
        **01289590022**  
        
        **2. ابعت سكرين التحويل واتساب على نفس الرقم**
        
        **3. هبعتلك كود الشهر فوراً**
        """)
        st.error("الكود ينتهي يوم 31 في الشهر")
    
    with col2:
        st.subheader("تفعيل اشتراك الشهر")
        code_input = st.text_input(f"دخل كود شهر {CURRENT_MONTH_YEAR}:")
        if st.button("تفعيل", type="primary"):
            if code_input.upper() == MONTHLY_CODE.upper():
                last_day = (datetime.now().replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
                cookie_manager.set("molkhasly_sub", CURRENT_MONTH_YEAR, expires_at=last_day)
                st.session_state.subscribed = True
                st.success(f"تم التفعيل ✅ شغال لحد يوم {last_day.strftime('%d-%m-%Y')}")
                st.balloons()
                st.rerun()
            else:
                st.error("الكود غلط. تواصل على 01289590022")
    
    st.stop()

last_day = (datetime.now().replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
st.success(f"مرحباً - اشتراكك مفعل لحد يوم {last_day.strftime('%d-%m-%Y')}")
col1, col2 = st.columns([3,1])
with col2:
    if st.button("تسجيل خروج"):
        cookie_manager.delete("molkhasly_sub")
        st.session_state.subscribed = False
        st.rerun()

tab1, tab2 = st.tabs(["📄 رفع PDF", "✍️ لصق نص"])

def summarize_text(text, sentences_count):
    try:
        parser = PlaintextParser.from_string(text, Tokenizer("arabic"))
        summarizer = LsaSummarizer()
        summary = summarizer(parser.document, sentences_count)
        result = ""
        for sentence in summary:
            result += str(sentence) + " "
        return result if result.strip() else "النص قصير جداً للتلخيص"
    except:
        return "حصل خطأ في التلخيص"

with tab1:
    uploaded_file = st.file_uploader("ارفع ملف PDF", type="pdf")
    sentences_count_pdf = st.slider("عدد الجمل للـ PDF:", 1, 20, 5, key="pdf")
    
    if uploaded_file:
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            if st.button("لخص الـ PDF", type="primary"):
                with st.spinner("جاري التلخيص..."):
                    result = summarize_text(text, sentences_count_pdf)
                    st.subheader("الملخص:")
                    st.success(result)
                    st.download_button("تحميل الملخص", result, file_name="summary.txt")
        except Exception as e:
            st.error(f"مشكلة في قراية الملف: {e}")

with tab2:
    text_input = st.text_area("الصق النص هنا:", height=300)
    sentences_count_text = st.slider("عدد الجمل للنص:", 1, 20, 3, key="text")
    
    if st.button("لخص النص", type="primary"):
        if text_input.strip():
            with st.spinner("جاري التلخيص..."):
                result = summarize_text(text_input, sentences_count_text)
                st.subheader("الملخص:")
                st.success(result)
                st.download_button("تحميل الملخص", result, file_name="summary.txt")
        else:
            st.warning("اكتب نص الأول")

st.divider()
st.caption(f"للتجديد والاشتراك: 01289590022 | Orange Cash")
