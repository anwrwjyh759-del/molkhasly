import streamlit as st
import base64
from together import Together

st.set_page_config(page_title="ملخصلي", page_icon="📝")
st.title("📝 ملخصلي - لخص أي سبورة في ثانية")

client = Together(api_key=st.secrets["TOGETHER_API_KEY"])

uploaded_file = st.file_uploader("📤 ارفع صورة السبورة", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="السبورة المرفوعة", use_column_width=True)
    with st.spinner("جاري تلخيص السبورة..."):
        base64_image = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "لخصلي المكتوب في السبورة دي في 5 نقاط واضحة بالعربي. لو فيها معادلات اشرحها ببساطة."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }],
            max_tokens=1024
        )
        st.success("✅ ملخص السبورة:")
        st.write(response.choices[0].message.content)

st.markdown("---")
st.caption("صُنع بـ ❤️ للمدرسين في مصر")
