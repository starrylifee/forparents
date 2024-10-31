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
print(f"[DEBUG] secrets_path: {secrets_path}")
with open(secrets_path, "r") as f:
    secrets = toml.load(f)
print(f"[DEBUG] secrets loaded: {secrets}")

# Streamlit UI 설정
st.title("체험학습 보고서 자동 생성 도구")

# 추가 입력 필드
user_grade = st.selectbox("학년을 선택하세요. (선택)", ["1학년", "2학년", "3학년", "4학년", "5학년", "6학년"])  # (new)
user_class = st.text_input("반을 입력하세요. 예시: 5. (선택)")
user_number = st.text_input("번호를 입력하세요. 예시: 13. (선택)")
user_gender = st.selectbox("성별을 선택하세요. (선택)", ("남자", "여자"))

# 학습 일시 입력 필드를 구조화하여 입력 오류를 방지
start_date = st.date_input("학습 시작일을 선택하세요. (필수)")
end_date = st.date_input("학습 종료일을 선택하세요. (필수)")
if end_date < start_date:
    st.error("종료일은 시작일 이후여야 합니다. 다시 선택해주세요.")  # (new)
duration = (end_date - start_date).days + 1 if start_date != end_date else 1  # (new)
user_date = f"{start_date.strftime('%Y년%m월%d일')} ~ {end_date.strftime('%Y년%m월%d일')} ({duration}일간)"

user_school = st.text_input("학교 이름을 입력하세요. 예시: 서울한국초등학교 (선택)")

user_input = st.text_area("학생이 체험한 내용을 입력하세요. (필수)")
print(f"[DEBUG] user_input: {user_input}")

# 사용자에게 문서 공유 이메일을 먼저 입력받음
user_email = st.text_input("체험학습 보고서를 받을 이메일을 입력하세요. (필수)")
print(f"[DEBUG] User email input: {user_email}")

# OpenAI API 키 설정
client = OpenAI(api_key=secrets['openai']['api_key'])
print("[DEBUG] OpenAI client initialized")

# Google 서비스 계정 설정
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["GCP_SERVICE_ACCOUNT"],
    scopes=["https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/drive"]
)
print("[DEBUG] Google service account credentials created")
docs_service = build('docs', 'v1', credentials=credentials)
drive_service = build('drive', 'v3', credentials=credentials)
print("[DEBUG] Google Docs and Drive services initialized")

# OpenAI로부터 응답을 생성하는 함수
def generate_response(prompt):
    print(f"[DEBUG] Generating response for prompt: {prompt}")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"학생이 체험한 내용을 바탕으로 교육적인 체험 보고서를 작성해주세요. 보고서는 간단히 전체 15줄 이하로, 마크다운 문법 사용하지 않고 텍스트 위주로 출력, 다음의 내용은 미출력 (일시, 장소, 참가자 등), 체험보고서 본문만 출력: {prompt}"}
        ]
    )
    generated_message = response.choices[0].message.content.strip()
    print(f"[DEBUG] Generated response: {generated_message}")
    return generated_message

# Google 문서 템플릿 복사 함수
def copy_template_document(template_document_id, title):
    copied_file = drive_service.files().copy(
        fileId=template_document_id,
        body={"name": title}
    ).execute()
    return copied_file["id"]

# 특정 양식을 갖지는 Google 문서에 내용 채용기
def fill_template_google_doc(document_id, placeholders_contents):
    print(f"[DEBUG] Filling Google Doc with ID: {document_id}")
    requests = []
    for placeholder, content in placeholders_contents.items():
        print(f"[DEBUG] Replacing placeholder: {placeholder} with content: {content}")
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
    print(f"[DEBUG] Google Doc updated with content")

# 사용자와 Google 문서를 공유하는 함수
def share_google_doc(document_id, user_email):
    print(f"[DEBUG] Sharing Google Doc with ID: {document_id} to email: {user_email}")
    drive_service.permissions().create(
        fileId=document_id,
        body={
            'type': 'user',
            'role': 'writer',
            'emailAddress': user_email
        },
        fields='id'
    ).execute()
    print(f"[DEBUG] Google Doc shared with {user_email}")

# 단계 1: 응답 생성
if st.button("채험학습 보고서 생성") and end_date >= start_date:
    print("[DEBUG] Generate Response button clicked")
    if end_date < start_date:
        st.warning("종료일은 시작일 이후여야 합니다. 보고서를 생성할 수 없습니다.")
        print("[DEBUG] Invalid date range: end_date is before start_date")
        st.stop()  # (new)
    if user_input:
        # OpenAI로부터 응답 생성
        ai_response = generate_response(user_input)
        st.text_area("AI가 생성한 보고서. 내용을 살펴보고 수정하세요.", ai_response, height=300)
        st.session_state['ai_response'] = ai_response
    else:
        st.warning("내용을 입력하세요.")
        print("[DEBUG] No user input provided")

# 단계 2: Google 문서로 저장
if st.button("체험학습 보고서를 E-mail로 받아보기"):
    print("[DEBUG] Save to Google Doc button clicked")
    if 'ai_response' in st.session_state and user_email:
        # 고유한 문서 제목 생성
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        doc_title = f"체험학습 보고서 - {timestamp}"
        print(f"[DEBUG] Generated document title: {doc_title}")

        # Google 템플릿 문서를 복사하고 새 문서 ID 검색
        template_document_id = "1YXgIIb64mPDXn0PmVgIi36xM52MMVWVEOXNoWBY53PM"  # 미리 생성된 템플릿 문서 ID를 사용
        document_id = copy_template_document(template_document_id, doc_title)
        print(f"[DEBUG] Copied Google Doc with new ID: {document_id}")

        # 템플릿의 플레이스홀더들을 AI 응답과 사용자 입력으로 대체
        placeholders_contents = {
            "{{user_grade}}": user_grade,
            "{{user_class}}": user_class,
            "{{user_number}}": user_number,
            "{{user_gender}}": user_gender,
            "{{user_date}}": user_date,
            "{{user_school}}": user_school,
            "{{ai_response}}": st.session_state['ai_response']
        }
        fill_template_google_doc(document_id, placeholders_contents)

        # 사용자에게 문서 공유
        share_google_doc(document_id, user_email)
        st.success(f"문서가 성공적으로 생성되고 공유되었습니다! 문서 ID: {document_id}")
    elif not user_email:
        st.warning("이메일을 입력하세요.")
        print("[DEBUG] No user email provided")
    elif 'ai_response' not in st.session_state:
        st.warning("먼저 보고서를 생성하세요.")
        print("[DEBUG] No AI response available")
