import streamlit as st

st.title("학부모를 위한 인공지능 도구 모음")

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <h4>1. 교외체험학습 계획서 도우미</h4>
        <a href="https://for-parents.streamlit.app/%EA%B5%90%EC%99%B8%EC%B2%B4%ED%97%98%ED%95%99%EC%8A%B5_%EA%B3%84%ED%9A%8D%EC%84%9C_%EB%8F%84%EC%9A%B0%EB%AF%B8" target="_blank" style="text-decoration: none;">
            <span style="font-size: 100px;">🏫</span>
            <div style="text-align: center; font-size: 20px;">클릭하세요</div>
        </a>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <h4>2. 학교에 못갈 것 같아요</h4>
        <a href="https://for-parents.streamlit.app/%ED%95%99%EA%B5%90%EC%97%90_%EB%AA%BB%EA%B0%88%EA%B2%83_%EA%B0%99%EC%95%84%EC%9A%94" target="_blank" style="text-decoration: none;">
            <span style="font-size: 100px;">🏥</span>
            <div style="text-align: center; font-size: 20px;">클릭하세요</div>
        </a>
        """,
        unsafe_allow_html=True
    )

with col1:
    st.markdown(
        """
        <h4>3. 얘야 여기를 더 치워야지</h4>
        <a href="https://for-parents.streamlit.app/%EC%96%98%EC%95%BC_%EC%97%AC%EA%B8%B0%EB%A5%BC_%EB%8D%94_%EC%B9%98%EC%9B%8C%EC%95%BC%EC%A7%80" target="_blank" style="text-decoration: none;">
            <span style="font-size: 100px;">🧹</span>
            <div style="text-align: center; font-size: 20px;">클릭하세요</div>
        </a>
        """,
        unsafe_allow_html=True
    )

# 4번 자리에 3행시 생성기 추가
with col2:
    st.markdown(
        """
        <h4>4. 어머니 전교회장이 되고 싶습니다 </h4>
        <a href="https://for-parents.streamlit.app/%EC%96%B4%EB%A8%B8%EB%8B%88_%EC%A0%84%EA%B5%90%ED%9A%8C%EC%9E%A5%EC%9D%B4_%EB%90%98%EA%B3%A0_%EC%8B%B6%EC%8A%B5%EB%8B%88%EB%8B%A4" target="_blank" style="text-decoration: none;">
            <span style="font-size: 100px;">🎓</span>
            <div style="text-align: center; font-size: 20px;">클릭하세요</div>
        </a>
        """,
        unsafe_allow_html=True
    )
