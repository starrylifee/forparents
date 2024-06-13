import streamlit as st

st.title("학교에 못갈 것 같아요")
st.write("""
학생이 학교에 결석했을 때 관련 안내를 해주는 프로그램입니다.""")
st.write("""
학교에 자주 발생하는 결석사유를 중심으로 만들어졌으며, 이외의 사유는 학교에 문의하세요.
""")

def emphasized_text(text):
    st.markdown(f"""
    <div style="border: 2px solid black; padding: 10px; border-radius: 5px;">
        <b>{text}</b>
    </div>
    """, unsafe_allow_html=True)

# 첫 번째 질문
sick = st.radio("학생이 아파서 학교에 결석했나요?", ("예", "아니오"))

if sick == "예":
    # 두 번째 질문 (법정감염병 여부)
    infection = st.radio("법정감염병으로 아파서 학교에 결석했나요?", ("예", "아니오"))

    if infection == "예":
        emphasized_text("출석인정결석입니다. 의사의 진단서 또는 의견서를 첨부하여 학교의 안내를 받으세요.")
    else:
        # 세 번째 질문 (결석 일수)
        sick_days = st.number_input("몇일 결석했나요?", min_value=1, step=1)

        if sick_days <= 2:
            emphasized_text("질병결석입니다. <span style='color: red; font-weight: bold;'>학부모의견서 또는 처방전</span>을 결석계와 함께 5일 이내에 제출하세요.")
        else:
            emphasized_text("질병결석입니다. <span style='color: red; font-weight: bold;'>의사 진단서 또는 의견서</span>를 결석계와 함께 5일 이내 제출하세요.")
else:
    # 경조사 여부 확인
    event = st.radio("다음 경조사로 인하여 출석하지 못한 경우에 해당하나요?", ("예", "아니오"))

    if event == "예":
        # 경조사 세부 사항
        event_type = st.selectbox("경조사 유형을 선택하세요:", [
            "결혼 (형제, 자매, 부 또는 모)",
            "입양 (학생 본인)",
            "사망 (부모, 조부모, 외조부모)",
            "사망 (부모의 조부모, 부모의 외조부모)",
            "사망 (형제·자매 및 그의 배우자)",
            "사망 (부모의 형제·자매 및 그의 배우자)"
        ])

        if event_type == "결혼 (형제, 자매, 부 또는 모)":
            emphasized_text("출석인정결석입니다. 결석 기간은 1일입니다.")
        elif event_type == "입양 (학생 본인)":
            emphasized_text("출석인정결석입니다. 결석 기간은 20일입니다.")
        elif event_type == "사망 (부모, 조부모, 외조부모)":
            emphasized_text("출석인정결석입니다. 결석 기간은 5일입니다.")
        elif event_type == "사망 (부모의 조부모, 부모의 외조부모)":
            emphasized_text("출석인정결석입니다. 결석 기간은 5일입니다.")
        elif event_type == "사망 (형제·자매 및 그의 배우자)":
            emphasized_text("출석인정결석입니다. 결석 기간은 3일입니다.")
        elif event_type == "사망 (부모의 형제·자매 및 그의 배우자)":
            emphasized_text("출석인정결석입니다. 결석 기간은 1일입니다.")
        
        emphasized_text("관련 서류를 첨부하여 학교에 제출하세요.")
        st.write("""
        ※ 경조사 일수에 재량휴업일과 공휴일 및 토요일은 산입하지 않으며, 해당 기간 내에는 학생의 상황과 여건에 따라 출석 가능합니다.""")
        st.write("""
        ※ 경조사 사안 발생일 전ㆍ후에 출석하지 못한 경우에도 가능 일수 내에서 출석으로 인정할 수 있습니다.
        """)
    else:
        # 체육, 음악, 미술 관련 대회나 훈련 여부 확인
        competition = st.radio("체육 대회나 훈련을 위해 결석하나요?", ("예", "아니오"))

        if competition == "예":
            # 학생선수 등록 여부 확인
            registered = st.radio("학교장의 허가를 받아 학생선수로 등록했나요?", ("예", "아니오"))

            if registered == "예":
                emphasized_text("출석인정결석입니다. 자세한 사항은 학교 담당자에게 문의하세요.")
            else:
                emphasized_text("미인정결석입니다. 자세한 사항은 학교 담당자에게 문의하세요.")
        else:
            emphasized_text("미인정 결석 사유를 확인해보세요:")
            st.write("""
            가. 다음의 경우에는 미인정 결석으로 처리함:
            1) ｢학교폭력 예방 및 대책에 관한 법률｣ 제17조(가해학생에 대한 조치) 제1항 제6호에 따른 출석정지
            2) 「교원의 지위 향상 및 교육활동 보호를 위한 특별법」제18조제1항제4호에 따른 출석정지
            3) ｢초·중등교육법 시행령｣ 제31조(학생의 징계 등)제1항 제4호에 따른 출석정지
            4) ｢초·중등교육법 시행령｣ 제31조(학생의 징계 등)제6항의 가정학습 기간
            5) 범법행위로 인한 책임 있는 사유로 결석한 경우(관련 기관 출석, 체포, 도피, 구속(구인, 구금, 구류 포함), 교도소 수감 등)
            6) 태만, 가출, 출석 거부 등 고의로 결석한 경우
            7) 기타 합당하지 않은 사유로 인한 결석
            """)
            emphasized_text("미인정결석이 반복되면 경찰에 수사의뢰할 수 있습니다.")
            st.write("학교 현장에서 자주 발생하는 결석 사유를 통해 만든 간단한 프로그램으로 개별적인 상황(미세먼지 민감군에 의한 출석인정 결석, 학교폭력 예방 및 대책에 관한 법률에 의한 출석인정 결석 등)이 있을 수 있으니 자세한 문의는 학교에 문의하세요.")
