import os
import pathlib
import textwrap
import google.generativeai as genai
import streamlit as st
import toml
from datetime import date
import random

hide_github_icon = """
    <style>
    .css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob,
    .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137,
    .viewerBadge_text__1JaDK{ display: none; }
    #MainMenu{ visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    </style>
"""

st.markdown(hide_github_icon, unsafe_allow_html=True)

# 세션 상태 초기화
if 'response_text' not in st.session_state:
    st.session_state['response_text'] = ""
if 'student_input' not in st.session_state:
    st.session_state['student_input'] = ""

# 사용자 입력을 세션 상태에 저장하는 함수
def save_student_input():
    st.session_state['student_input'] = st.session_state['student_input_text']

# secrets.toml 파일 경로 및 읽기
secrets_path = pathlib.Path(__file__).parent.parent / ".streamlit/secrets.toml"
with open(secrets_path, "r") as f:
    secrets = toml.load(f)

# API 키 리스트 생성
api_keys = [secrets.get(f"gemini_api_key{i}") for i in range(1, 13) if secrets.get(f"gemini_api_key{i}")]

# Google Generative AI 모델 설정
def configure_genai(api_key):
    genai.configure(api_key=api_key)
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
    }
    return genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )

# 콘텐츠 생성 함수
def generate_content(model, prompt_parts):
    try:
        response = model.generate_content(prompt_parts)
        return response.text
    except Exception as e:
        st.error(f"API 호출 실패: {str(e)}")
        return None

st.title("어머니 전교회장이 되고 싶습니다.")
st.write("회장선거 포스터용 학생이름 3행시 생성기")

# 학생 이름 입력
student_input = st.text_input("학생의 이름을 입력하세요", value=st.session_state['student_input'], key='student_input_text')

# 버튼 클릭 시 3행시 생성
if st.button("3행시 생성", key="generate"):
    # 랜덤으로 API 키 선택
    selected_api_key = random.choice(api_keys)
    
    # 사용자 입력 프롬프트 생성
    user_input_prompt = f"input: {student_input}"

    # 전체 프롬프트
    prompt = [
        "이 assistant는 초등학생의 학생회장선거 홍보 도움을 주는 assistant 이다.\n"
        "이름을 넣으면 학생회장의 자질을 표현한 3행시를 짓는다.",
        "input: 이준호",
        "output: ## 이준호 3행시\n**이**롭게 세상을 변화시키고\n**준**비된 리더쉽으로\n**호**감을 주는 회장이 되겠습니다.",
        "input: 이준호",
        "output: ## 이준호 3행시\n\n**이**끌리는 매력으로 친구들과 하나 되는\n**준**비된 리더십, 학교를 빛낼 꿈을 펼치는\n**호**기심 가득한 눈빛, 밝은 미래를 향해 나아가는 이준호",
        "input: 김민정",
        "output: ## 김민정 3행시\n\n**김**빛나는 미소로 모두를 밝히고\n**민**첩한 생각으로 학교를 더욱 발전시키고\n**정**의로운 마음, 친구들의 목소리에 귀 기울이겠습니다.",
        "input: 최유진",
        "output: ## 최유진 3행시\n\n**최**고의 친구, 든든한 힘이 되어줄\n**유**쾌한 에너지로 학교를 즐겁게 만들고\n**진**심으로 소통하며 함께 성장하는 최유진",
        "input: 박유진",
        "output: ## 박유진 3행시\n\n**박**진감 넘치는 아이디어로 학교를 흥미롭게\n**유**연한 리더십으로 모두의 의견을 존중하고\n**진**심으로 학교를 사랑하는 박유진을 응원해주세요!",
        "input: 김수현",
        "output: ## 김수현 3행시\n**김**이 모락모락 피어나는 열정으로\n**수**많은 아이디어를\n**현**실로 만들겠습니다!",
        "input: 박지민",
        "output: ## 박지민 3행시\n**박**수받는 리더가 되어\n**지**혜롭게 여러분을 이끌고\n**민**심을 잘 대변하겠습니다!",
        "input: 최태민",
        "output: ## 최태민 3행시\n\n**최**고의 학교를 만들기 위해\n**태**양처럼 밝은 에너지를\n**민**주적인 리더십으로 보여드리겠습니다!",
        "input: 이서연",
        "output: ## 이서연 3행시\n\n**이** 세상을 밝게 빛내는 \n**서**정적인 감성으로 \n**연**결된 학교를 만들겠습니다!",
        user_input_prompt,
        "output: "
    ]
    
    model = configure_genai(selected_api_key)
    response = generate_content(model, prompt)
    if response:
        st.session_state['response_text'] = response

# 생성된 3행시를 보여주는 부분
if st.session_state['response_text']:
    st.markdown("### 📝 생성된 3행시:")
    st.markdown(f"> {st.session_state['response_text']}")

    st.download_button('3행시 다운로드', data=st.session_state['response_text'], file_name='3행시.txt', mime='text/plain')
