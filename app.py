import streamlit as st
import PyPDF2
import requests
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from PIL import Image
import easyocr
import numpy as np

# إعدادات الصفحة
st.set_page_config(page_title="ملخصلي", page_icon="📝", layout="centered")

# بانر الاشتراك الشهري
st.warning("🔒 **للاستخدام الكامل: اشتراك شهري 200 جنيه**\n\nادفع على أورنج كاش: **01289590022**\n\nابعت سكرين الدفع على نفس الرقم واتساب للتفعيل")

st.title("📝 ملخصلي")
st.write("ارفع ملف PDF أو صورة JPG/PNG وهيطلعلك ملخص عربي + سؤال وجواب")

# رفع الملف
uploaded_file = st.file_uploader("ارفع ملفك هنا", type=['pdf', 'jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    text = ""
    
    # لو PDF
    if uploaded_file.type == "application/pdf":
        st.info("جاري قراءة ملف PDF...")
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    
    # لو صورة
    else:
        st.info("جاري قراءة الصورة بـ EasyOCR... ده بياخد 30 ثانية")
        image = Image.open(uploaded_file)
        img_array = np.array(image)
        
        reader = easyocr.Reader(['ar', 'en'], gpu=False)
        result = reader.readtext(img_array, detail=0, paragraph=True)
        text = ' '.join(result)
    
    # نتأكد إن في نص طلع
    if len(text.strip()) < 50:
        st.error("مقدرتش أطلع نص كفاية من الملف. اتأكد إن الصورة واضحة والكلام باين")
    else:
        st.success("تم استخراج النص بنجاح ✅")
        
        # عرض النص المستخرج
        with st.expander("شوف النص اللي طلعته"):
            st.text(text[:1000] + "...")
        
        # التلخيص
        if st.button("لخصلي النص"):
            with st.spinner('جاري التلخيص...'):
                try:
                    # تلخيص باستخدام sumy
                    parser = PlaintextParser.from_string(text, Tokenizer("arabic"))
                    summarizer = LsaSummarizer()
                    summary_sentences = summarizer(parser.document, 5)
                    
                    summary = ""
                    for sentence in summary_sentences:
                        summary += str(sentence) + " "
                    
                    st.subheader("📌 الملخص:")
                    st.write(summary)
                    
                    # سؤال وجواب
                    st.subheader("❓ سؤال وجواب")
                    question = st.text_input("اسأل سؤال عن النص:")
                    
                    if question:
                        with st.spinner('بدور على الإجابة...'):
                            API_URL = "https://api-inference.huggingface.co/models/deepset/xlm-roberta-base-squad2"
                            headers = {"Authorization": "Bearer hf_xxx"}  # حط التوكن بتاعك هنا
                            
                            payload = {
                                "inputs": {
                                    "question": question,
                                    "context": text[:2000]
                                }
                            }
                            
                            response = requests.post(API_URL, headers=headers, json=payload)
                            result = response.json()
                            
                            if 'answer' in result:
                                st.write(f"**الإجابة:** {result['answer']}")
                            else:
                                st.write("مقدرتش ألاقي إجابة. جرب سؤال تاني")
                                
                except Exception as e:
                    st.error(f"حصل خطأ: {str(e)}")
