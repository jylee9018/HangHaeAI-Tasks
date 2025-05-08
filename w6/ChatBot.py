import base64
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

load_dotenv()

st.title("🖼️ Image Q&A Bot")
model = ChatOpenAI(model="gpt-4o-mini")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "images_encoded" not in st.session_state:
    st.session_state.images_encoded = []

# 이미지 업로드
images_uploaded = st.file_uploader("여러 장의 사진을 올려주세요!", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

# 이미지가 새로 업로드되었을 경우 인코딩하여 세션에 저장
if images_uploaded:
    if len(images_uploaded) < 1:
        st.warning("최소 한 장 이상의 이미지를 올려주세요!")
    else:
        # 이미지 base64 인코딩
        images_encoded = []
        for image in images_uploaded:
            images_encoded.append(base64.b64encode(image.read()).decode("utf-8"))
        
        # 이미지 - 세션 저장    
        st.session_state.images_encoded = images_encoded
        
        st.image(images_uploaded, caption=[f"이미지 {i + 1}" for i in range(len(images_uploaded))])
        st.success(f"{len(images_uploaded)} 장의 이미지가 저장되었습니다. 이제 질문해 보세요!")

# 이전 대화 기록 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력
user_input = st.chat_input("업로드한 이미지에 대해 무엇이 궁금한가요?")
    
# GPT 호출
if user_input and st.session_state.images_encoded:
    # 사용자 질문 - 화면 출력
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # 사용자 질문 - 세션 저장
    st.session_state.messages.append({"role": "user", "content": user_input})

    # GPT 메시지 구성 (텍스트(사용자 질문) + 이미지 다수)
    content = [{"type": "text", "text": user_input}]
    for image_encoded in st.session_state.images_encoded:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{image_encoded}"}
        })

    # GPT 응답
    message = HumanMessage(content=content)
    result = model.invoke([message])
    response = result.content

    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

elif user_input and not st.session_state.images_encoded:
    st.warning("질문 전에 이미지를 먼저 올려주세요!")