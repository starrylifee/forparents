import pathlib
import textwrap
import google.generativeai as genai
import streamlit as st
import toml
from PIL import Image
import io
import random

def to_markdown(text):
    text = text.replace('•', '*')
    return textwrap.indent(text, '> ', predicate=lambda _: True)

# secrets.toml 파일 경로
secrets_path = pathlib.Path(__file__).parent.parent / ".streamlit/secrets.toml"

# secrets.toml 파일 읽기
with open(secrets_path, "r") as f:
    secrets = toml.load(f)

# secrets.toml 파일에서 API 키 값 가져오기
api_keys = [secrets.get(f"gemini_api_key{i}") for i in range(1, 13)]

def get_random_api_key():
    return random.choice(api_keys)

def try_generate_content(api_key, image):
    # API 키를 설정
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro-vision')
    try:
        # 콘텐츠 생성 시도
        response = model.generate_content(["학부모의 입장으로 학생의 방이나 책상 정리를 더 해야 할 곳을 찾아주는 vision 앱", image])
        response.resolve()
        return response
    except Exception as e:
        # 예외 발생시 None 반환
        print(f"API 호출 실패: {e}")
        return None

st.title("얘야 여기를 더 치워야지")

st.markdown("""
### 앱 사용 설명
1. 핸드폰으로 학생의 방이나 책상 사진을 가로로 찍어주세요.
2. 아래의 파일 업로드 버튼을 클릭하여 사진을 업로드합니다.
3. AI가 사진을 분석하여 더 치워야 할 곳을 찾아줍니다.
4. 분석 결과를 확인하고, 정리해야 할 곳을 청소합니다.
5. 필요 시, 결과를 저장하거나 공유할 수 있습니다.
""")

# 핸드폰 사진 업로드 기능 추가
uploaded_file = st.file_uploader("핸드폰으로 학생의 방이나 책상을 가로로 찍어주세요.")

# 이미지가 업로드되었는지 확인
if uploaded_file is not None:
    # 이미지 바이트 문자열로 변환
    img_bytes = uploaded_file.read()

    # bytes 타입의 이미지 데이터를 PIL.Image.Image 객체로 변환
    img = Image.open(io.BytesIO(img_bytes))

    # 랜덤 API 키로 시도
    selected_api_key = get_random_api_key()
    response = try_generate_content(selected_api_key, img)
    
    # 첫 번째 API 키 실패 시, 다른 API 키로 재시도
    if response is None:
        print("첫 번째 API 호출에 실패하여 다른 API 키로 재시도합니다.")
        for _ in range(len(api_keys) - 1):  # 이미 시도한 키를 제외하고 재시도
            selected_api_key = get_random_api_key()
            response = try_generate_content(selected_api_key, img)
            if response is not None:
                break
    
    # 결과가 성공적으로 반환되었는지 확인
    if response is not None:
        # 결과 표시
        st.image(img)  # 업로드된 사진 출력
        st.markdown(response.text)
    else:
        st.markdown("API 호출에 실패했습니다. 나중에 다시 시도해주세요.")
else:
    st.markdown("핸드폰 사진을 업로드하세요.")
