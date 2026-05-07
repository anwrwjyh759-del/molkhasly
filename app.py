import streamlit as st
import requests
import base64

st.set_page_config(page_title="ملخصلي", page_icon="📚", layout="centered")
st.title("📚 ملخصلي - لخص دروسك بالذكاء الاصطناعي")

# عداد المحاولات المجانية
if "count" not in st.session_state:
    st.session_state.count = 0

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

# نظام الاشتراك بعد 3 محاولات
if st.session_state.count >= 3:
    st.error("⚠️ خلصت الـ 3 محاولات المجانية")
    st.warning("💎 اشترك بـ 200 جنيه شهرياً للمحاولات غير المحدودة")

    st.info("""
    **خطوات الاشتراك:**
    1. حول 200 جنيه على اورنج كاش: **`01289590022`**
    2. خد سكرين شوت للتحويل
    3. ابعت السكرين على الواتساب عشان أفعل اشتراكك خلال ساعة
    """)

    st.link_button("📱 كلم خدمة العملاء واتساب", "https://wa.me/201289590022?text=حولت 200 جنيه اشتراك ملخصلي. ودي سكرين التحويل")
    st.stop()

# التطبيق الأساسي
st.success(f"فاضلك {3 - st.session_state.count} محاولات مجانية 🎁")
uploaded_file = st.file_uploader("ارفع صورة الدرس", type=["png", "jpg", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, use_column_width=True)
    if st.button("لخص الدرس ✨"):
        st.session_state.count += 1
        with st.spinner("بجهز الملخص..."):
            image_bytes = uploaded_file.getvalue()
            image_base64 = base64.b64encode(image_bytes).decode()

            headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Content-Type": "application/json"}
            data = {
                "messages": [
                    {"role": "system", "content": "انت مدرس شاطر. لخص الدرس اللي في الصورة للمرحلة الاعدادية بلغة بسيطة واعمل 3 أسئلة اختيار من متعدد بالإجابات."},
                    {"role": "user", "content": [{"type": "text", "text": "لخصلي الدرس ده"}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}]}
                ],
                "model": "gpt-4o-mini"
            }

            response = requests.post("https://models.inference.ai.azure.com/chat/completions", headers=headers, json=data)

            if response.status_code == 200:
                answer = response.json()["choices"][0]["message"]["content"]
                st.success("خلصت ✅")
                st.markdown(answer)
            else:
                st.session_state.count -= 1
                st.error("حصلت مشكلة في الاتصال، جرب تاني")
