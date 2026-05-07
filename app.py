
import streamlit as st
import requests
import base64

st.set_page_config(page_title="ملخصلي", page_icon="📚")

st.title("📚 ملخصلي - لخص دروسك بالذكاء الاصطناعي")
st.write("ارفع صورة الدرس وهطلعلك ملخص + أسئلة")

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

uploaded_file = st.file_uploader("ارفع صورة الدرس", type=["png", "jpg", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="الصورة اللي رفعتها", use_column_width=True)

    if st.button("لخص الدرس ✨"):
        with st.spinner("بقرأ الصورة وبجهز الملخص..."):
            image_bytes = uploaded_file.getvalue()
            image_base64 = base64.b64encode(image_bytes).decode()

            headers = {
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Content-Type": "application/json"
            }

            data = {
                "messages": [
                    {
                        "role": "system",
                        "content": "انت مدرس شاطر. لخص الدرس اللي في الصورة واعمل 3 أسئلة اختيار من متعدد بالإجابات."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "لخصلي الدرس ده واعملي أسئلة عليه"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                "model": "gpt-4o-mini"
            }

            response = requests.post(
                "https://models.inference.ai.azure.com/chat/completions",
                headers=headers,
                json=data
            )

            if response.status_code == 200:
                result = response.json()
                answer = result["choices"][0]["message"]["content"]
                st.success("خلصت ✅")
                st.markdown(answer)
            else:
                st.error(f"حصلت مشكلة: {response.text}")
