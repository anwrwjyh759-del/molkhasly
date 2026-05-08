import streamlit as st
import PyPDF2
import requests
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from PIL import Image, ImageEnhance
import easyocr
import numpy as np
import cv2

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
if st.sidebar.button("تسجيل خروج"):
    st.session_state.activated = False
    st.rerun()

uploaded_file = st.file_uploader("ارفع أي ملف PDF أو صورة", type=['pdf', 'jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    text = ""
    
    if uploaded_file.type == "application/pdf":
        st.info("جاري قراءة PDF...")
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    
    else:
        st.info("جاري محاولة قراءة الصورة بـ 3 طرق... ده بياخد دقيقة")
        image = Image.open(uploaded_file)
        img_array = np.array(image)
        
        # الطريقة 1: الصورة زي ما هي
        reader = easyocr.Reader(['ar', 'en'], gpu=False)
        result1 = reader.readtext(img_array, detail=0, paragraph=True)
        text1 = ' '.join(result1)
        
        # الطريقة 2: أبيض وأسود + تكبير
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY) if len(img_array.shape) == 3 else img_array
        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        result2 = reader.readtext(thresh, detail=0, paragraph=True)
        text2 = ' '.join(result2)
        
        # الطريقة 3: زيادة التباين
        enhancer = ImageEnhance.Contrast(Image.fromarray(gray))
        enhanced = enhancer.enhance(2.0)
        result3 = reader.readtext(np.array(enhanced), detail=0, paragraph=True)
        text3 = ' '.join(result3)
        
        # اختار أطول نص - غالباً هو الصح
        text = max([text1, text2, text3], key=len)
    
    if len(text.strip()) < 50:
        st.error("مقدرتش أطلع نص. الصورة جودتها ضعيفة جداً أو مفيهاش كلام واضح")
        st.info("نصائح: صور في إضاءة كويسة، خلي الكاميرا عدلة، كبّر الخط")
    else:
        st.success(f"تم استخراج {len(text)} حرف ✅")
        with st.expander("شوف النص اللي طلعته"):
            st.text(text)
        
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
