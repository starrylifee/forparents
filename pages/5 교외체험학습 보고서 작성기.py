import pathlib
import toml
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from openai import OpenAI
import datetime

# secrets.toml 파일 경로 및 읽기
secrets_path = pathlib.Path(__file__).parent.parent / ".streamlit/secrets.toml"
print(f"[DEBUG] secrets_path: {secrets_path}")
with open(secrets_path, "r") as f:
    secrets = toml.load(f)
print(f"[DEBUG] secrets loaded: {secrets}")

# Streamlit UI 설정
st.title("체험학습 보고서 자동 생성 도구")
user_input = st.text_area("학생이 체험한 내용을 입력하세요:")
print(f"[DEBUG] user_input: {user_input}")

# 사용자에게 문서 공유 이메일을 먼저 입력받음
user_email = st.text_input("문서를 공유할 이메일을 입력하세요:")
if not user_email:
    st.warning("문서를 공유하려면 이메일을 입력하세요.")
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
            {"role": "user", "content": f"학생이 체험한 내용을 바탕으로 교육적인 체험 보고서를 작성해줘: {prompt}"}
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

# 특정 양식을 가진 Google 문서에 내용 채우기
def fill_template_google_doc(document_id, placeholder, content):
    print(f"[DEBUG] Filling Google Doc with ID: {document_id}, placeholder: {placeholder}, content: {content}")
    # 문서의 특정 플레이스홀더를 내용으로 대체
    requests = [
        {
            'replaceAllText': {
                'containsText': {
                    'text': placeholder,
                    'matchCase': True
                },
                'replaceText': content
            }
        }
    ]
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

# 응답 생성 및 저장
if st.button("Generate and Save to Google Doc"):
    print("[DEBUG] Generate and Save button clicked")
    if user_input and user_email:
        # OpenAI로부터 응답 생성
        ai_response = generate_response(user_input)

        # 고유한 문서 제목 생성
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        doc_title = f"체험학습 보고서 - {timestamp}"
        print(f"[DEBUG] Generated document title: {doc_title}")

        # Google 템플릿 문서를 복사하고 새 문서 ID 가져오기
        template_document_id = "1mIkx-eUYcgigOyhAY33-9xT5yfLkuVmGc2fTsJZbfAs"  # 미리 생성된 템플릿 문서 ID를 사용
        document_id = copy_template_document(template_document_id, doc_title)
        print(f"[DEBUG] Copied Google Doc with new ID: {document_id}")

        # 템플릿의 플레이스홀더를 AI 응답으로 대체
        fill_template_google_doc(document_id, "{{placeholder}}", ai_response)

        # 사용자에게 문서 공유
        share_google_doc(document_id, user_email)
        st.success(f"문서가 성공적으로 생성되고 공유되었습니다! 문서 ID: {document_id}")
    elif not user_input:
        st.warning("입력을 입력하세요.")
        print("[DEBUG] No user input provided")
    elif not user_email:
        st.warning("이메일을 입력하세요.")
        print("[DEBUG] No user email provided")
