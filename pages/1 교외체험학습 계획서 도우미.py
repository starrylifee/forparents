import pathlib
import textwrap
import google.generativeai as genai
import streamlit as st
import toml
from datetime import date
from PIL import Image
import io
import random

hide_github_icon = """
    <style>
    .css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob,
    .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137,
    .viewerBadge_text__1JaDK{ display: none; }
    #MainMenu{ visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    .css-1rs6os.edgvbvh3 { visibility: visible !important; }  /* Running 상태 보이기 */
    </style>
"""

st.markdown(hide_github_icon, unsafe_allow_html=True)

# 세션 상태 초기화
if 'response_text' not in st.session_state:
    st.session_state['response_text'] = ""
if 'student_input' not in st.session_state:
    st.session_state['student_input'] = ""
if 'month' not in st.session_state:
    st.session_state['month'] = 6  # 기본값 설정
if 'companions' not in st.session_state:
    st.session_state['companions'] = []
if 'destination' not in st.session_state:
    st.session_state['destination'] = ""
if 'activities' not in st.session_state:
    st.session_state['activities'] = ["", ""]

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

st.title("교외체험학습 계획서 도우미")

# 여행 날짜 선택
month = st.slider("여행 월을 선택하세요", min_value=1, max_value=12, value=st.session_state['month'], key='month_slider')
st.session_state['month'] = month

# 동행자 선택
companions = st.multiselect("누구와 함께 가나요?", ["가족", "친구", "조부모", "친척"], default=st.session_state['companions'], key='companions')

# 여행 목적지 입력
destination = st.text_input("어디로 가나요?", value=st.session_state['destination'], key='destination')

# 주요 활동 입력
activity1 = st.text_input("주요 활동 1", value=st.session_state['activities'][0], key='activity1')
activity2 = st.text_input("주요 활동 2", value=st.session_state['activities'][1], key='activity2')

# 버튼 클릭 시 계획서 생성
if st.button("계획서 생성", key="generate"):
    with st.spinner("계획서를 생성중입니다. 잠시만 기다려주세요..."):
        # 랜덤으로 API 키 선택
        selected_api_key = random.choice(api_keys)
        
        # 사용자 입력 프롬프트 생성
        user_input_prompt = f"{destination}에 {'와'.join(companions)} 함께 갈 예정입니다. 주요 활동은 다음과 같습니다: {activity1}, {activity2}"
        
        # 전체 프롬프트
        prompt = [
            "이 assistant는 초등학생의 교외현장체험학습 계획서를 작성하는 데 도움을 주는 assistant 이다.\n"
            "초등학생이 교외 현장체험학습을 할 때 작성해야 하는 계획서를 다음 형식으로 출력한다:\n\n"
            "행사명: [행사명을 작성]\n"
            "행사목적: [행사목적을 작성]\n"
            "세부계획:\n1. [첫 번째 세부계획]\n2. [두 번째 세부계획]\n3. [세 번째 세부계획]\n4. [네 번째 세부계획]\n5. [다섯 번째 세부계획]\n"
            "출력 형식이 정확히 이 형식에 맞게 작성되어야 한다.",
            "행사명 출력 이후 줄을 바꾸고 행사목적을 출력한 후 줄을 바꾸고 세부계획을 작성한다.",
            "경주에 가족과 함께 놀러갔어",
            "행사명: 경주 가족 여행\n행사목적: 우리나라 문화유산의 소중함을 체험하고 가족과의 유대를 강화.\n세부계획:\n1. 경주의 문화재 해설을 듣고 이해하기.\n2. 경주의 유적지 안내판을 읽고 내용 이해.\n3. 불국사, 석굴암 등 주요 역사 유적지 방문.\n4. 유적지에서 발생하는 수학적 요소 이해 및 측정.\n5. 자연환경 관찰 및 생태계 조사.",
            "가족과 함께 롯데월드를 갔어",
            "행사명: 롯데월드 가족 체험\n행사목적: 다양한 놀이기구와 공연을 통해 창의력과 협동심을 기르기.\n세부계획:\n1. 안내표지판과 지도를 읽으며 정보 찾기.\n2. 놀이기구 줄에서 대기 시간 이해 및 측정.\n3. 다양한 건축물 관찰 및 입체 도형 인식.\n4. 쇼와 퍼레이드를 통해 사회적 활동 이해.\n5. 가족과의 협동을 통해 역할 분담 배우기.",
            "할머니 생신을 축하하러 가족들과 함께 부산에 갈거야.",
            "행사명: 부산 가족 모임\n행사목적: 가족 간의 유대감 강화 및 부산 지역사회 이해.\n세부계획:\n1. 가족 및 친척 간의 예절 실천.\n2. 부산의 다양한 특징 관찰 및 이해.\n3. 여름철 건강과 안전 습관 습득.\n4. 가족과 함께 한 활동 기록 및 발표.\n5. 부산 지역의 동네 조사 및 발표.",
            "강화도에 가서 루지를 탈꺼야",
            "행사명: 강화도 루지 체험\n행사목적: 안전 규칙과 협동심을 배우고 신체 발달을 도모.\n세부계획:\n1. 교통 안전 교육 습득.\n2. 공공시설물 이용 시 예절과 질서 습득.\n3. 가족과의 팀워크 발휘.\n4. 루지 타기를 통한 균형 감각 신장.\n5. 안전 룰과 규칙 준수의 중요성 배우기.",
            user_input_prompt,
        ]
        model = configure_genai(selected_api_key)
        response = generate_content(model, prompt)
        if response:
            st.session_state['response_text'] = response

# 생성된 계획서를 보여주는 부분
if st.session_state['response_text']:
    st.markdown("### 📝 생성된 계획서:")
    st.markdown(f"> {st.session_state['response_text']}")

    st.download_button('계획서 다운로드', data=st.session_state['response_text'], file_name='계획서.txt', mime='text/plain')
