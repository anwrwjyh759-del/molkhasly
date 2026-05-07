import streamlit as st
import requests
import base64
from datetime import datetime, timedelta
import extra_streamlit_components as stx

st.set_page_config(page_title="ملخصلي", page_icon="📚", layout="centered")
st.title("📚 ملخصلي - لخص دروسك بالذكاء الاصطناعي")

# مدير الكوكيز
cookie_manager = stx.CookieManager()

# نقرا البيانات من الكوكيز
trial_count = cookie_manager.get(cookie="trial_count")
is_subscribed = cookie_manager.get(cookie="subscribed")

if trial_count is None:
    trial_count = 0
else:
    trial_count = int(trial_count)

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

# --- نظام كود التفعيل الشهري التلقائي ---
now = datetime.now()
current_month = now.month # 1 لـ 12
current_year = now.year % 100 # 26 لسنة 2026
ADMIN_CODE = f"molkhasly{current_month}{current_year}" # الكود الحالي

# لو مش مشترك وخلص المحاولات
if is_subscribed!= "true" and trial_count >= 3:
    st.error("⚠️ خلصت الـ 3 محاولات المجانية")
    st.warning("💎 اشترك بـ 200 جنيه شهرياً للمحاولات غير المحدودة")

    st.info(f"""
    **خطوات الاشتراك:**
    1. حول 200 جنيه على اورنج كاش: **`01289590022`**
    2. خد سكرين شوت للتحويل
    3. ابعت السكرين على الواتساب عشان تاخد كود التفعيل لشهر {current_month}
    """)

    st.link_button("📱 كلم خدمة العملاء واتساب", f"https://wa.me/201289590022?text=حولت 200 جنيه اشتراك ملخصلي لشهر {current_month}. عايز كود التفعيل")

    # خانة كود التفعيل
    activation_code = st.text_input("اكتب كود التفعيل هنا:", type="password")
    if st.button("تفعيل الاشتراك"):
        if activation_code == ADMIN_CODE:
            # نفعل الاشتراك لمدة 31 يوم
            expires_at = datetime.now() + timedelta(days=31)
            cookie_manager.set("subscribed", "true", expires_at=expires_at)
            st.success(f"✅ تم التفعيل بنجاح لشهر {current_month}!")
            st.balloons()
            st.rerun()
        else:
            st.error("كود التفعيل غلط أو بتاع شهر قديم")
    st.stop()

# --- التطبيق الأساسي ---
if is_subscribed == "true":
    st.success("🎉 انت مشترك في ملخصلي - محاولات غير محدودة")
else:
    st.success(f"فاضلك {3 - trial_count} محاولات مجانية 🎁")

uploaded_file = st.file_uploader("ارفع صورة الدرس", type=["png", "jpg", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, use_column_width=True)
    if st.button("لخص الدرس ✨"):
        # نزود العداد بس لو مش مشترك
        if is_subscribed!= "true":
            trial_count += 1
            expires_at = datetime.now() + timedelta(days=730) # سنتين
            cookie_manager.set("trial_count", trial_count, expires_at=expires_at)

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
                st.rerun()
            else:
                if is_subscribed!= "true":
                    trial_count -= 1
                    cookie_manager.set("trial_count", trial_count, expires_at=expires_at)
                st.error("حصلت مشكلة في الاتصال، جرب تاني")
