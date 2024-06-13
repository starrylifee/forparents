import streamlit as st

st.title("학부모를 위한 인공지능 도구 모음")

col1, col2 = st.columns(2)

with col1:
    st.header("1. 교외체험학습 계획서 도우미")
    if st.button("🏫"):
        st.write("[교외체험학습 계획서 도우미](https://for-parents.streamlit.app/%EA%B5%90%EC%99%B8%EC%B2%B4%ED%97%98%ED%95%99%EC%8A%B5%EA%B3%84%ED%9A%8D%EC%84%9C_%EB%B3%B4%EC%A1%B0)")

with col2:
    st.header("2. 학교에 못갈 것 같아요")
    if st.button("🏥"):
        st.write("[학교에 못갈 것 같아요](https://for-parents.streamlit.app/%ED%95%99%EA%B5%90%EC%97%90_%EB%AA%BB%EA%B0%88%EA%B2%83_%EA%B0%99%EC%95%84%EC%9A%94)")
