import streamlit as st
import PyPDF2
import requests
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from PIL import Image
import pytesseract

st.set_page_config(page_title="ملخصلي", page_icon="📝", layout="centered")

# ===== كود التفعيل الشهري - غيره كل شهر =====
ACTIVATION_CODE = "molkhasly512"
# ============================================

if 'activated' not in st.session_state:
    st.session_state.activated = False

if not st.session_state.activated:
    st.title("🔒 ملخصلي - صفحة التفعيل")
    st.warning("**اشتراك شهري 200 جنيه**\n\n1. ادفع على أورنج كاش: **01289590022**\n2. ابعت سكرين الدفع واتساب\n3. هتاخد كود التفعيل الشهري")
    user_code = st.text_input("دخل كود التفعيل:", type="password")
    if st.button("تفعيل"):
        if user_code == ACTIVATION_CODE:
            st.session_state.activated = True
            st.rerun()
        else:
            st.error("كود التفعيل غلط")
    st.stop()

st.title("📝 ملخصلي")
st.caption("⚠️ للصور: الجودة الضعيفة أو الألوان الكتير نتيجتها مش دقيقة. PDF أفضل بكتير")
if st.sidebar.button("تسجيل خروج"):
    st.session_state.activated = False
    st.rerun()

uploaded_file = st.file_uploader("ارفع PDF أو صورة", type=['pdf', 'jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    text = ""
    
    if uploaded_file.type == "application/pdf":
        st.info("جاري قراءة PDF...")
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    
    else:
        st.info("جاري قراءة الصورة...")
        image = Image.open(uploaded_file)
        text = pytesseract.image_to_string(image, lang='ara+eng')
    
    if len(text.strip()) < 50:
        st.error("مقدرتش أطلع نص. جرب صورة أوضح أو ارفع PDF")
    else:
        st.success(f"تم استخراج النص ✅")
        with st.expander("شوف النص اللي طلعته"):
            st.text(text[:1000])
        
        if st.button("لخصلي النص"):
            with st.spinner('جاري التلخيص...'):
                try:
                    parser = PlaintextParser.from_string(text, Tokenizer("arabic"))
                    summarizer = LsaSummarizer()
                    summary_sentences = summarizer(parser.document, 5)
                    summary = " ".join([str(s) for s in summary_sentences])
                    
                    st.subheader("📌 الملخص:")
                    st.write(summary)
                    
                    st.subheader("❓ سؤال وجواب")
                    question = st.text_input("اسأل سؤال عن النص:")
                    if question:
                        API_URL = "https://api-inference.huggingface.co/models/deepset/xlm-roberta-base-squad2"
                        headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}
                        payload = {"inputs": {"question": question, "context": text[:2000]}}
                        response = requests.post(API_URL, headers=headers, json=payload)
                        result = response.json()
                        st.write(f"**الإجابة:** {result.get('answer', 'مقدرتش ألاقي إجابة')}")
                except Exception as e:
                    st.error(f"حصل خطأ: {str(e)}")
