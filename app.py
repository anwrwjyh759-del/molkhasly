import streamlit as st
import PyPDF2
import requests
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from PIL import Image
import pytesseract

# إعدادات الصفحة
st.set_page_config(page_title="ملخصلي", page_icon="📝", layout="centered")

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
        st.info("جاري معالجة الصورة... ده ممكن ياخد 10 ثواني")
        image = Image.open(uploaded_file)
        
        # 1. كبر الصورة لو صغيرة عشان الحروف تبان
        width, height = image.size
        if width < 1000:
            ratio = 1000 / width
            new_size = (int(width * ratio), int(height * ratio))
            image = image.resize(new_size, Image.LANCZOS)
        
        # 2. حولها أبيض وأسود وحسّن التباين عشان تشيل التشويش
        image = image.convert('L')
        image = image.point(lambda x: 0 if x < 128 else 255, '1')
        
        # 3. اقرأ بأقوى إعدادات للعربي
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(image, lang='ara+eng', config=custom_config)
    
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
                    summary_sentences = summarizer(parser.document, 5)  # 5 جمل
                    
                    summary = ""
                    for sentence in summary_sentences:
                        summary += str(sentence) + " "
                    
                    st.subheader("📌 الملخص:")
                    st.write(summary)
                    
                    # سؤال وجواب باستخدام Hugging Face
                    st.subheader("❓ سؤال وجواب")
                    question = st.text_input("اسأل سؤال عن النص:")
                    
                    if question:
                        with st.spinner('بدور على الإجابة...'):
                            API_URL = "https://api-inference.huggingface.co/models/deepset/xlm-roberta-base-squad2"
                            headers = {"Authorization": "Bearer hf_xxx"}  # حط التوكن بتاعك هنا
                            
                            payload = {
                                "inputs": {
                                    "question": question,
                                    "context": text[:2000]  # أول 2000 حرف بس عشان السرعة
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
