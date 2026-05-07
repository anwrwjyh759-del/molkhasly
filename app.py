import streamlit as st
from together import Together
import base64

st.set_page_config(page_title="ملخصلي", page_icon="📚", layout="centered")

# ========== الإعدادات ==========
ORANGE_CASH_NUMBER = "01289590022" # حط رقم أورانج كاش بتاعك هنا ضروري
PRICE = "200 جنيه شهرياً"
FREE_TRIALS = 3 # عدد المرات المجانية

# أكواد التفعيل - للمدرسين اللي دفعوا اشتراك
VALID_CODES = [
    "MDRS001", "MDRS002", "MDRS003", "MDRS004", "MDRS005",
    "MDRS006", "MDRS007", "MDRS008", "MDRS009", "MDRS010"
]
# ==============================

st.title("📚 ملخصلي")

# متغيرات الجلسة
if 'activated' not in st.session_state:
    st.session_state.activated = False
if 'trial_count' not in st.session_state:
    st.session_state.trial_count = 0

# دالة التحقق هل يقدر يستخدم التطبيق
def can_use_app():
    return st.session_state.activated or st.session_state.trial_count < FREE_TRIALS

# لو خلص المجاني ومش مفعل، نعرض شاشة الاشتراك
if not can_use_app():
    st.error("⛔ انتهت التجربة المجانية")

    st.markdown(f"### 💳 للاشتراك والاستمرار:")
    st.info(f"""
    1. حول **{PRICE}** على أورانج كاش: **{ORANGE_CASH_NUMBER}**
    2. ابعت سكرين التحويل على واتساب لنفس الرقم
    3. هيتبعتلك كود تفعيل يفتحلك التطبيق مدى الحياة
    """)

    st.markdown("---")

    code = st.text_input("🔑 دخل كود التفعيل هنا:", placeholder="MDRS001")

    if st.button("تفعيل الحساب", type="primary", use_container_width=True):
        if code.strip().upper() in VALID_CODES:
            st.session_state.activated = True
            st.success("✅ تم التفعيل بنجاح! تقدر تستخدم التطبيق براحتك")
            st.balloons()
            st.rerun()
        else:
            st.error("❌ كود التفعيل غلط. اتأكد من الكود أو اشترك.")

    st.stop()

# ========== التطبيق الأساسي ==========
if st.session_state.activated:
    st.success("✅ حسابك مفعل - استخدام غير محدود")
else:
    remaining = FREE_TRIALS - st.session_state.trial_count
    st.info(f"🎁 فاضلك {remaining} تجربة مجانية من أصل {FREE_TRIALS}")

try:
    client = Together(api_key=st.secrets["TOGETHER_API_KEY"])
except Exception as e:
    st.error("مفتاح Together API مش موجود. كلم صاحب التطبيق")
    st.stop()

st.write("ارفع صورة السبورة وهنلخصها في ثواني")

uploaded_file = st.file_uploader("📸 ارفع صورة السبورة", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="الصورة اللي رفعتها", use_column_width=True)

    if st.button("✨ لخصلي السبورة دلوقتي", use_container_width=True):
        with st.spinner("الذكاء الاصطناعي بيقرأ السبورة..."):
            try:
                img_bytes = uploaded_file.getvalue()
                img_base64 = base64.b64encode(img_bytes).decode('utf-8')

                response = client.chat.completions.create(
                    model="meta-llama/Llama-4-Scout-17B-16E-Instruct",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "انت مدرس شاطر. لخص محتوى السبورة دي في نقاط واضحة ومختصرة باللهجة المصرية. طلع أهم العناوين والتعريفات والقوانين. لو فيها مسائل حل أول واحدة كمثال."},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
                                }
                            ]
                        }
                    ],
                    max_tokens=1000
                )

                result = response.choices[0].message.content

                # لو مش مفعل، نزود العداد
                if not st.session_state.activated:
                    st.session_state.trial_count += 1

                st.markdown("### 📝 الملخص:")
                st.write(result)
                st.download_button("📥 تحميل الملخص", result, file_name="ملخص_السبورة.txt")

                # لو دي كانت آخر مرة مجانية
                if st.session_state.trial_count == FREE_TRIALS and not st.session_state.activated:
                    st.warning("⚠️ دي كانت آخر تجربة مجانية. اشترك عشان تكمل استخدام التطبيق")
                    st.rerun()

            except Exception as e:
                st.error(f"حصل خطأ: {e}")

st.markdown("---")
st.caption("صُنع بـ ❤️ للمدرسين في مصر")
if st.session_state.activated:
    if st.button("تسجيل خروج"):
        st.session_state.activated = False
        st.session_state.trial_count = 0
        st.rerun()
