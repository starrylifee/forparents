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
    # 랜덤으로 API 키 선택
    selected_api_key = random.choice(api_keys)
    
    # 사용자 입력 프롬프트 생성
    user_input_prompt = f"{destination}에 {'와'.join(companions)} 함께 갈거야.\n주요 활동: {activity1}, {activity2}"
    
    # 전체 프롬프트
    prompt = [
        "이 assistant는 초등학생의 교외현장체험학습 계획서를 쓰는데 도움을 주는 assistant 이다.\n"
        "초등학생이 교외 현장체험학습을 할때 학생이 어떤 것을 어떻게 배울 수 있는지 계획을 간단히 개조식으로 출력한다.\n\n"
        "###규칙\nuser는 여행의 계획을 자세히 입력한다.\n"
        "user의 여행계획에서 초등학생이 교외현장체험에서 배울수 있는 점을 개조식으로 출력한다.",
        "경주에 가족과 함께 놀러갔어",
        "국어\n듣기 및 말하기: 경주의 문화재 해설을 들으면서 주요 내용을 이해하고 이를 가족과 이야기 해보기.\n읽기: 경주의 유적지와 안내판을 읽고 내용을 이해하기.\n\n사회\n고장과 지역사회의 변화: 경주의 역사와 문화를 체험하면서 우리나라 문화유산의 소중함 습득.\n\n역사: 불국사, 석굴암, 천마총 등 경주의 주요 역사 유적지를 방문하면서 직접 보고 체험.\n\n수학: 경주의 유적지에서 발생하는 다양한 수학적 요소들을 이해하고 측정해보기 (예: 탑의 높이, 길이 등)\n\n과학: 자연과 환경: 경주 주변의 자연환경을 관찰하여 생태계와 지형 지물을 조사.\n\n가족 및 공공생활\n예절과 규칙: 가족과 함께 다니면서 공공장소에서의 예절과 규칙을 배우고 실천.\n가족활동 기록: 경주에서의 체험을 일기로 기록하고 가족과 함께 한 경험을 발표하기.",
        "가족과 함께 롯데월드를 갔어",
        "국어\n듣기 및 말하기: 다른 사람과의 대화에서 예의 바르게 말하고, 다른 사람의 말을 경청하는 방법 습득.\n읽기: 롯데월드의 안내표지판, 지도 등을 읽으며 정보 찾기 .\n\n수학\n길이 측정: 놀이기구 줄에서 대기 시간과 길이 등을 시각과 시간 단위로 읽고 이해하기 .\n도형 인식: 롯데월드의 다양한 건축물과 구조물을 관찰하며 입체 도형을 인식하고 이름 짓기 .\n\n사회\n여러 가지 놀이와 제도: 롯데월드에서 진행되는 쇼와 퍼레이드를 통해 사회적 활동과 규칙 이해하기 .\n\n창의적 체험활동예술 및 체육활동: 롯데월드의 다양한 공연(뮤지컬 쇼, 행진 등)을 관람하면서 신체 표현력과 예술 감상능력을 신장 .\n\n자기이해활동: 다양한 놀이를 통해 본인의 흥미와 적성을 탐색해 본다.\n\n가족과의 활동\n가족과의 협동: 가족과 함께 놀이기구를 체험하면서 가족 구성원 간의 역할 분담과 협동을 배우기\n\n가족 활동 조사 및 발표: 롯데월드 방문 후 가족과 함께 한 활동을 조사하고 함께 했던 경험을 친구들 앞에서 발표하기",
        "할머니 생신을 축하하러 가족들과 함께 부산에 갈거야.",
        "가족과 친척 간의 예절 실천:가족 및 친척 간의 예절을 실천.\n\n가족과 친척의 관계 조사:학생이 자신의 가족과 친척의 관계를 알고, 그들과 함께 하는 행사나 활동을 조사.\n\n감사와 존중 표현:가족 구성원들이 하는 역할에 대해 고마움을 느끼고 이를 작품으로 표현.\n\n부산 지역의 특징 탐구:학생이 부산의 다양한 특징을 관찰하고, 이를 통해 지역사회의 구조를 이해.\n\n예절과 질서 교육:가족 모임이나 공공장소에서 예절과 질서를 지키는 습관  습득..\n\n여름철 건강과 안전 습관:여름철 부산 여행을 통해 건강하고 안전하게 생활하는 방법을 배움.\n\n동네와 마을 조사:여행하는 부산 지역의 이웃과 동네 모습을 조사하고 발표.",
        "강화도에 가서 루지를 탈꺼야",
        "교통 안전 교육: 루지 타기와 같은 활동을 통해 학생들은 교통 안전과 관련된 규칙을  습득.\n\n공공시설물의 이용 및 질서 유지: 루지와 같은 공공시설물을 이용하면서 공공 예절과 질서를 지키는 중요성을  습득.\n\n협력과 팀워크:가족 혹은 친구들과 함께 루지를 타며 팀워크를 발휘하고 협력하는 방법을  습득.\n\n체육\n활동을 통한 신체 발달: 루지 타기는 체력과 균형 감각신장.\n\n룰과 규칙 준수의 중요성: 루지 타는 과정에서 안전 룰과 규칙의 중요성 배움.",
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
