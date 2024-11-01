import pathlib
import toml
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from openai import OpenAI
import datetime

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

# secrets.toml 파일 경로 및 읽기
secrets_path = pathlib.Path(__file__).parent.parent / ".streamlit/secrets.toml"
with open(secrets_path, "r") as f:
    secrets = toml.load(f)

# Streamlit UI 설정
st.title("체험학습 계획서 자동 생성 도구")

# 필수 입력 필드
st.header("필수 입력 항목")
user_grade = st.selectbox("학년을 선택하세요.", ["1학년", "2학년", "3학년", "4학년", "5학년", "6학년"])
start_date = st.date_input("학습 시작일을 선택하세요.")
end_date = st.date_input("학습 종료일을 선택하세요.")
if end_date < start_date:
    st.error("종료일은 시작일 이후여야 합니다. 다시 선택해주세요.")
duration = (end_date - start_date).days + 1 if start_date != end_date else 1
user_date = f"{start_date.strftime('%Y년%m월%d일')} ~ {end_date.strftime('%Y년%m월%d일')} ({duration}일간)"

purpose = st.text_area("체험학습의 목적을 입력하세요.")
location = st.text_input("체험학습 장소를 입력하세요. 예시: 국립과학관")
user_email = st.text_input("체험학습 계획서를 받을 이메일을 입력하세요.")

# 선택 입력 필드
st.header("선택 입력 항목")
user_name = st.text_input("학생 이름을 입력하세요. (선택)")
user_school = st.text_input("학교 이름을 입력하세요. 예시: 서울한국초등학교 (선택)")
user_class = st.text_input("반을 입력하세요. 예시: 5. (선택)")
user_contact = st.text_input("연락처를 입력하세요. 예시: 010-1234-5678 (선택)")
study_plan = st.text_area("학습 계획을 입력하세요. (선택)")


# OpenAI API 키 설정
client = OpenAI(api_key=secrets['openai']['api_key'])

# Google 서비스 계정 설정
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["GCP_SERVICE_ACCOUNT"],
    scopes=["https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/drive"]
)
docs_service = build('docs', 'v1', credentials=credentials)
drive_service = build('drive', 'v3', credentials=credentials)

# OpenAI로부터 응답을 생성하는 함수
def generate_response_for_plan(user_grade, location, purpose, user_date):
    prompt = f"학년: {user_grade}, 장소: {location}, 목적: {purpose}, 기간: {user_date}. 이를 바탕으로 체험학습 계획서를 10줄 이하로 작성해주세요. 계획서는 마크다운을 사용하지 않고 줄글 형태의 텍스트로 출력해주세요."
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    generated_message = response.choices[0].message.content.strip()
    return generated_message

# Google 문서 템플릿 복사 함수
def copy_template_document(template_document_id, title):
    copied_file = drive_service.files().copy(
        fileId=template_document_id,
        body={"name": title}
    ).execute()
    return copied_file["id"]

# 특정 양식을 갖는 Google 문서에 내용 채용기
def fill_template_google_doc(document_id, placeholders_contents):
    requests = []
    for placeholder, content in placeholders_contents.items():
        requests.append({
            'replaceAllText': {
                'containsText': {
                    'text': placeholder,
                    'matchCase': True
                },
                'replaceText': content
            }
        })
    docs_service.documents().batchUpdate(documentId=document_id, body={"requests": requests}).execute()

# 사용자와 Google 문서를 공유하는 함수
def share_google_doc(document_id, user_email):
    drive_service.permissions().create(
        fileId=document_id,
        body={
            'type': 'user',
            'role': 'writer',
            'emailAddress': user_email
        },
        fields='id'
    ).execute()

# 체험학습 계획서 생성 버튼
if st.button("체험학습 계획서 생성") and end_date >= start_date:
    with st.spinner("체험학습 계획서를 생성 중입니다..."):
        if not (user_grade and location and purpose and user_date and user_email):
            st.warning("필수 항목을 모두 입력하세요.")
        else:
            # OpenAI로부터 체험학습 계획서 응답 생성
            ai_response = generate_response_for_plan(user_grade, location, purpose, user_date)
            st.text_area("AI가 생성한 계획서. 내용을 살펴보고 수정하세요.", ai_response, height=300, key="ai_response_area")
            st.session_state['ai_response'] = ai_response
            st.session_state['plan_generated'] = True

# 이메일로 전송 버튼
if st.session_state.get('plan_generated', False):
    if st.button("수정한 계획서를 이메일로 보내기"):
        with st.spinner("이메일을 보내는 중입니다..."):
            if 'ai_response' not in st.session_state or not st.session_state['ai_response']:
                st.warning("먼저 계획서를 생성하고 내용을 수정하세요.")
            elif not user_email:
                st.warning("이메일을 입력하세요.")
            else:
                # 고유한 문서 제목 생성
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                doc_title = f"체험학습 계획서 - {timestamp}"

                # Google 템플릿 문서를 복사하고 새 문서 ID 검색
                template_document_id = "1cXFmvGX_UQNvIZXCvUpOnaCgG6et2HkqTbdGiDs8khM"  # 미리 생성된 템플릿 문서 ID를 사용
                document_id = copy_template_document(template_document_id, doc_title)

                # 템플릿의 플레이스홀더들을 사용자 입력과 AI 응답으로 대체
                placeholders_contents = {
                    "{{user_name}}": user_name,
                    "{{user_grade}}": user_grade,
                    "{{user_class}}": user_class,
                    "{{user_contact}}": user_contact,
                    "{{user_school}}": user_school,
                    "{{user_date}}": user_date,
                    "{{purpose}}": purpose,
                    "{{location}}": location,
                    "{{study_plan}}": st.session_state['ai_response']
                }
                fill_template_google_doc(document_id, placeholders_contents)

                # 사용자에게 문서 공유
                share_google_doc(document_id, user_email)
                st.success(f"문서가 성공적으로 생성되고 공유되었습니다! 문서 ID: {document_id}")
