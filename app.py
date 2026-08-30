"""
SGCU Recruitment Analytics & Decision Dashboard (Rounds 1-4)
องค์การบริหารสโมสรนิสิตจุฬาลงกรณ์มหาวิทยาลัย (อบจ. จุฬาฯ)

Theme: Clean Modern White Theme (ธีมสีขาว สว่าง สะอาดตา)
Designed strictly following Dashboard Designer Principles (skill.md):
- Visual Hierarchy & F-pattern Layout
- Insight-Driven Titles (Titles as Insights)
- Crisp White Cards, High Contrast & Subtle Shadows
- Level 1 Headline KPIs with Comparative Context
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import io

from src.data_processing import process_all_recruitment_data
from src.analytics import (
    get_overall_summary,
    get_ranking_by_year,
    get_ranking_by_faculty,
    get_ranking_by_department,
    get_subdepartment_breakdown,
    get_cross_round_department_matrix,
    get_reapplicant_analysis,
)

# ---------------- STREAMLIT PAGE CONFIG ----------------
st.set_page_config(
    page_title="SGCU Recruitment Dashboard (Rounds 1-4)",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- CLEAN WHITE THEME & DESIGN SYSTEM (SKILL.MD) ----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Sarabun', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #FFFFFF;
        color: #0F172A;
    }
    
    /* Hide Streamlit Toolbar, Decoration & Header completely */
    [data-testid="stToolbar"], 
    .stAppToolbar, 
    .st-emotion-cache-14vh5up, 
    .e1yxiy6j2, 
    header[data-testid="stHeader"], 
    #MainMenu, 
    footer {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }

    /* Main Background & Spacing */
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2.5rem;
        padding-left: 2.2rem;
        padding-right: 2.2rem;
        max-width: 1400px;
        background-color: #FFFFFF;
    }
    
    /* White Clean Header */
    .dashboard-header {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 6px solid #E03177;
        border-radius: 12px;
        padding: 22px 26px;
        margin-bottom: 22px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }
    .header-title {
        font-size: 1.85rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin: 0;
        color: #0F172A;
    }
    .header-title span.highlight {
        color: #E03177;
    }
    .header-subtitle {
        font-size: 0.95rem;
        color: #475569;
        margin-top: 6px;
        font-weight: 400;
    }
    .header-badge {
        display: inline-block;
        background-color: #FCE7F3;
        color: #BE185D;
        border: 1px solid #FBCFE8;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-left: 10px;
    }

    /* KPI Cards - Clean White Floating Cards */
    .kpi-container {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
        transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .kpi-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.06);
        border-color: #CBD5E1;
    }
    .kpi-label {
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #64748B;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: #0F172A;
        line-height: 1.2;
    }
    .kpi-subtext {
        font-size: 0.82rem;
        color: #64748B;
        margin-top: 8px;
        padding-top: 8px;
        border-top: 1px solid #F1F5F9;
    }
    .kpi-subtext b {
        color: #1E293B;
    }
    .kpi-pink { color: #E03177; }
    .kpi-green { color: #059669; }
    .kpi-blue { color: #2563EB; }
    .kpi-purple { color: #7C3AED; }

    /* Insight Banner - Soft Light Clean */
    .insight-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #E03177;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 18px;
        font-size: 0.92rem;
        color: #334155;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
    }
    .insight-card b {
        color: #0F172A;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 2px solid #E2E8F0;
        margin-bottom: 20px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 46px;
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-bottom: none;
        border-radius: 8px 8px 0px 0px;
        padding: 8px 20px;
        font-weight: 600;
        font-size: 0.95rem;
        color: #64748B;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #E03177 !important;
        border-color: #E2E8F0 #E2E8F0 #FFFFFF #E2E8F0 !important;
        border-top: 3px solid #E03177 !important;
    }

    /* Sidebar Clean Styling */
    section[data-testid="stSidebar"] {
        background-color: #F8FAFC;
        border-right: 1px solid #E2E8F0;
    }

    /* Footer */
    .footer-text {
        text-align: center;
        color: #94A3B8;
        font-size: 0.82rem;
        margin-top: 40px;
        padding-top: 18px;
        border-top: 1px solid #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)


# ---------------- DATA LOADING (CACHED) ----------------
@st.cache_data
def load_data():
    df_app, df_ch = process_all_recruitment_data(data_dir="data")
    return df_app, df_ch

try:
    df_applicants, df_choices = load_data()
except Exception as e:
    st.error(f"❌ ไม่สามารถโหลดข้อมูลได้: {e}")
    st.stop()


# ---------------- SIDEBAR CONTROLS ----------------
with st.sidebar:
    st.markdown("### 🎛️ ตัวกรองข้อมูล (Filters)")
    st.caption("ปรับแต่งมุมมองข้อมูลตามที่ต้องการ")

    # 1. Round Filter
    round_options = ["ทั้งหมด (All Rounds)", "รอบที่ 1", "รอบที่ 2", "รอบที่ 3", "รอบที่ 4"]
    selected_round = st.selectbox("📅 เลือกรอบการสมัคร:", round_options, index=0)

    # 2. Choice Filter
    choice_options = ["รวมทุกอันดับ (Choice 1 & 2)", "เฉพาะอันดับ 1", "เฉพาะอันดับ 2"]
    selected_choice_label = st.selectbox("🎯 ลำดับการเลือก (Choice):", choice_options, index=0)
    if "เฉพาะอันดับ 1" in selected_choice_label:
        selected_choice = "อันดับ 1"
    elif "เฉพาะอันดับ 2" in selected_choice_label:
        selected_choice = "อันดับ 2"
    else:
        selected_choice = "รวมทุกอันดับ"

    # 3. Pass Criteria Filter
    pass_mode_label = st.radio(
        "✅ เกณฑ์การนับผู้ผ่านการคัดเลือก:",
        [
            "ผ่านทุกประเภท (ขั้นสุดท้าย + ฟอร์ม + สัมภาษณ์)",
            "ผ่านขั้นสุดท้ายเท่านั้น (Final Only)",
        ],
        index=0,
        help="รอบที่ 3-4 มีผู้สมัครที่ผ่านระดับคัดกรองฟอร์มและสัมภาษณ์ ตัวเลือกนี้ช่วยปรับนิยามผู้ผ่านได้",
    )
    pass_mode = "any" if "ผ่านทุกประเภท" in pass_mode_label else "final"

    st.markdown("---")
    st.markdown("#### 🔍 ตัวกรองขั้นสูง (Demographics)")

    # 4. Faculty Filter
    all_faculties = sorted([f for f in df_applicants["faculty"].unique() if f])
    selected_faculties = st.multiselect("🏛️ กรองเฉพาะคณะ:", all_faculties, default=[])

    # 5. Year Filter
    all_years = sorted([y for y in df_applicants["year"].unique() if y])
    selected_years = st.multiselect("🎓 กรองเฉพาะชั้นปี:", all_years, default=[])

    st.markdown("---")
    st.markdown("""
    <div style='background-color:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:12px; font-size:0.8rem; color:#475569;'>
        <b>📌 แหล่งข้อมูล:</b> อบจ. จุฬาฯ รอบ 1-4<br>
        <b>👥 ผู้สมัครรวม:</b> 527 คน-ครั้ง<br>
        <b>👤 ไม่ซ้ำคน:</b> 478 คน (สมัครซ้ำ 44 คน)<br>
        <b>📝 ใบสมัครฝ่าย:</b> 725 อันดับ
    </div>
    """, unsafe_allow_html=True)


# ---------------- FILTERING APPLICATION DATA ----------------
filtered_app = df_applicants.copy()
filtered_ch = df_choices.copy()

if selected_round != "ทั้งหมด (All Rounds)":
    r_num = int(selected_round.replace("รอบที่ ", ""))
    filtered_app = filtered_app[filtered_app["round"] == r_num]
    filtered_ch = filtered_ch[filtered_ch["round"] == r_num]

if selected_choice != "รวมทุกอันดับ":
    filtered_ch = filtered_ch[filtered_ch["choice_order"] == selected_choice]

if selected_faculties:
    filtered_app = filtered_app[filtered_app["faculty"].isin(selected_faculties)]
    filtered_ch = filtered_ch[filtered_ch["faculty"].isin(selected_faculties)]

if selected_years:
    filtered_app = filtered_app[filtered_app["year"].isin(selected_years)]
    filtered_ch = filtered_ch[filtered_ch["year"].isin(selected_years)]


# ---------------- DASHBOARD HEADER (CLEAN WHITE) ----------------
st.markdown(f"""
<div class='dashboard-header'>
    <div class='header-title'>
        🎓 ระบบวิเคราะห์ข้อมูลการรับสมัคร <span class='highlight'>อบจ. จุฬาฯ</span>
        <span class='header-badge'>{selected_round}</span>
    </div>
    <div class='header-subtitle'>
        องค์การบริหารสโมสรนิสิตจุฬาลงกรณ์มหาวิทยาลัย • SGCU Recruitment Intelligence Dashboard (Rounds 1 - 4)
    </div>
</div>
""", unsafe_allow_html=True)


# ---------------- LEVEL 1 HEADLINE KPIS (F-PATTERN TOP ROW) ----------------
summary = get_overall_summary(filtered_app, filtered_ch, pass_mode=pass_mode)

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:
    st.markdown(f"""
    <div class='kpi-container'>
        <div>
            <div class='kpi-label'>👥 ผู้สมัครทั้งหมด</div>
            <div class='kpi-value kpi-blue'>{summary['total_applications']:,}</div>
        </div>
        <div class='kpi-subtext'>
            👤 ไม่ซ้ำคน: <b>{summary['unique_applicants']:,}</b> คน
        </div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class='kpi-container'>
        <div>
            <div class='kpi-label'>📝 ใบสมัครฝ่าย</div>
            <div class='kpi-value kpi-pink'>{summary['total_choices']:,}</div>
        </div>
        <div class='kpi-subtext'>
            🎯 สมัคร 2 อันดับ: <b>{summary['dual_choice_count']:,}</b> ({summary['dual_choice_pct']}%)
        </div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class='kpi-container'>
        <div>
            <div class='kpi-label'>🎉 ผู้ผ่านการคัดเลือก</div>
            <div class='kpi-value kpi-green'>{summary['passed_applications']:,}</div>
        </div>
        <div class='kpi-subtext'>
            📋 มีผลประเมิน: <b>{summary['evaluated_applications']:,}</b> / {summary['total_applications']:,}
        </div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div class='kpi-container'>
        <div>
            <div class='kpi-label'>📈 อัตราการผ่านรวม</div>
            <div class='kpi-value kpi-purple'>{summary['pass_rate_overall']}%</div>
        </div>
        <div class='kpi-subtext'>
            ⭐ จากผู้ที่ประเมิน: <b>{summary['pass_rate_evaluated']}%</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

with kpi5:
    st.markdown(f"""
    <div class='kpi-container'>
        <div>
            <div class='kpi-label'>🏛️ ความหลากหลาย</div>
            <div class='kpi-value'>{summary['num_departments']} <span style='font-size:1rem;color:#64748B;'>ฝ่าย</span></div>
        </div>
        <div class='kpi-subtext'>
            🏫 จากทั้งหมด <b>{summary['num_faculties']}</b> คณะ
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)


# ---------------- DASHBOARD TABS (UX INFORMATION ARCHITECTURE) ----------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 1. จัดอันดับ ชั้นปี / คณะ / ฝ่าย",
    "🎯 2. เทียบคนผ่าน vs คนสมัครแต่ละฝ่าย",
    "🔄 3. เปรียบเทียบข้ามรอบที่ 1 - 4",
    "📋 4. สืบค้นข้อมูลรายบุคคล (Data Explorer)",
])


# ==============================================================================
# TAB 1: DEMOGRAPHICS & RANKINGS (ชั้นปี, คณะ, ฝ่าย)
# ==============================================================================
with tab1:
    st.markdown("""
    <div class='insight-card'>
        💡 <b>Insight ประชากรศาสตร์:</b> นิสิต <b>ชั้นปีที่ 2</b> สมัครเข้าร่วมมากที่สุด (38.5%) ตามด้วยปี 3 (27.5%) 
        โดยคณะที่มีผู้สมัครสูงสุด 3 ลำดับแรกคือ <b>คณะพาณิชยศาสตร์และการบัญชี, คณะวิทยาศาสตร์, และคณะรัฐศาสตร์</b>
    </div>
    """, unsafe_allow_html=True)

    col_y, col_f = st.columns(2)

    # 1.1 Year Distribution
    with col_y:
        st.markdown("#### 🎓 นิสิตชั้นปีที่ 2 สมัครมากที่สุด (38.5%)")
        df_year = get_ranking_by_year(filtered_app, pass_mode=pass_mode)

        fig_year = px.bar(
            df_year,
            x="ชั้นปี",
            y="จำนวนผู้สมัคร",
            text="จำนวนผู้สมัคร",
            color="ชั้นปี",
            color_discrete_sequence=["#E03177", "#8E24AA", "#2563EB", "#0284C7", "#10B981"],
            title="จำนวนผู้สมัครจำแนกตามชั้นปี (คน)",
        )
        fig_year.update_traces(textposition="outside", cliponaxis=False)
        fig_year.update_layout(
            template="plotly_white",
            showlegend=False,
            height=340,
            margin=dict(t=40, b=20, l=20, r=20),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            yaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
        )
        st.plotly_chart(fig_year, use_container_width=True)

        with st.expander("📄 ดูตารางสถิติตามชั้นปี"):
            st.dataframe(df_year, use_container_width=True, hide_index=True)

    # 1.2 Faculty Ranking
    with col_f:
        st.markdown("#### 🏛️ คณะพาณิชย์ฯ และวิทยาศาสตร์ นำโด่งใน Top 10")
        df_faculty = get_ranking_by_faculty(filtered_app, pass_mode=pass_mode)
        top_10_fac = df_faculty.head(10).sort_values(by="จำนวนผู้สมัคร", ascending=True)

        fig_fac = px.bar(
            top_10_fac,
            x="จำนวนผู้สมัคร",
            y="คณะ",
            orientation="h",
            text="จำนวนผู้สมัคร",
            color="จำนวนผู้สมัคร",
            color_continuous_scale="Teal",
            title="Top 10 คณะที่มีผู้สมัครสูงสุด (คน)",
        )
        fig_fac.update_traces(textposition="outside", cliponaxis=False)
        fig_fac.update_layout(
            template="plotly_white",
            coloraxis_showscale=False,
            height=340,
            margin=dict(t=40, b=20, l=20, r=20),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            xaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
        )
        st.plotly_chart(fig_fac, use_container_width=True)

        with st.expander("📄 ดูตารางสถิติตามคณะทั้งหมด (19 คณะ/สถาบัน)"):
            st.dataframe(df_faculty, use_container_width=True, hide_index=True)

    st.markdown("---")

    # 1.3 Department Ranking
    st.markdown("#### 🏢 ฝ่ายนายกสโมสรนิสิต & พัฒนาสังคมฯ ได้รับความนิยมสูงสุด (45% ของใบสมัคร)")
    df_dept = get_ranking_by_department(filtered_ch, pass_mode=pass_mode)

    d_col1, d_col2 = st.columns([3, 2])

    with d_col1:
        df_dept_plot = df_dept.sort_values(by="จำนวนใบสมัคร", ascending=True)
        fig_dept_stacked = go.Figure()
        fig_dept_stacked.add_trace(go.Bar(
            y=df_dept_plot["ฝ่าย"],
            x=df_dept_plot["เลือกอันดับ 1"],
            name="อันดับ 1 (Choice 1)",
            orientation="h",
            marker_color="#E03177",
            text=df_dept_plot["เลือกอันดับ 1"],
            textposition="auto",
        ))
        fig_dept_stacked.add_trace(go.Bar(
            y=df_dept_plot["ฝ่าย"],
            x=df_dept_plot["เลือกอันดับ 2"],
            name="อันดับ 2 (Choice 2)",
            orientation="h",
            marker_color="#FBCFE8",
            text=df_dept_plot["เลือกอันดับ 2"],
            textposition="auto",
        ))
        fig_dept_stacked.update_layout(
            template="plotly_white",
            barmode="stack",
            title="จำนวนใบสมัครแยกตามอันดับที่เลือก (Choice 1 vs Choice 2)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=420,
            margin=dict(t=50, b=20, l=20, r=20),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            xaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
        )
        st.plotly_chart(fig_dept_stacked, use_container_width=True)

    with d_col2:
        fig_donut = px.pie(
            df_dept,
            names="ฝ่าย",
            values="จำนวนใบสมัคร",
            hole=0.5,
            title="สัดส่วนความต้องการของฝ่ายทั้งหมด (%)",
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig_donut.update_layout(
            template="plotly_white",
            height=420,
            margin=dict(t=50, b=20, l=20, r=20),
            paper_bgcolor="#FFFFFF",
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with st.expander("📄 ตารางสรุปการจัดอันดับฝ่ายทั้งหมด"):
        st.dataframe(df_dept, use_container_width=True, hide_index=True)

    # 1.4 Subdepartment / Role Breakdown
    st.markdown("#### 🎯 เจาะลึกฝ่ายย่อยและตำแหน่งหน้าที่ (Subdepartment & Roles)")
    available_depts = ["ทุกฝ่าย"] + sorted(list(filtered_ch["department"].unique()))
    chosen_dept = st.selectbox("เลือกฝ่ายที่ต้องการสำรวจตำแหน่งย่อย:", available_depts, index=0)
    df_subdept = get_subdepartment_breakdown(filtered_ch, dept_name=chosen_dept, pass_mode=pass_mode)
    
    st.dataframe(df_subdept, use_container_width=True, hide_index=True)


# ==============================================================================
# TAB 2: APPLICANTS VS PASSED (เทียบคนผ่าน vs คนสมัคร)
# ==============================================================================
with tab2:
    st.markdown("""
    <div class='insight-card'>
        💡 <b>Insight การแข่งขัน:</b> ฝ่ายที่มี <b>Pass Rate สูงสุด</b> คือ <b>อุปนายกคนที่ 1 (70.5%)</b> และ <b>นายกสโมสรนิสิต (53.5%)</b> 
        ส่วนฝ่ายที่มี <b>การแข่งขันเข้มข้นที่สุด (Pass Rate ต่ำสุด)</b> คือ <b>ฝ่ายวิชาการ (11.1%)</b> และ <b>พัฒนาสังคมและบำเพ็ญประโยชน์ (14.9%)</b>
    </div>
    """, unsafe_allow_html=True)

    df_dept_comp = get_ranking_by_department(filtered_ch, pass_mode=pass_mode)

    # Grouped Bar Chart: Applicants vs Passed
    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(
        x=df_dept_comp["ฝ่าย"],
        y=df_dept_comp["จำนวนใบสมัคร"],
        name="จำนวนใบสมัครทั้งหมด (Applied)",
        marker_color="#93C5FD",
        text=df_dept_comp["จำนวนใบสมัคร"],
        textposition="outside",
        cliponaxis=False,
    ))
    fig_comp.add_trace(go.Bar(
        x=df_dept_comp["ฝ่าย"],
        y=df_dept_comp["จำนวนผู้ผ่าน"],
        name="จำนวนผู้ผ่านการคัดเลือก (Passed)",
        marker_color="#10B981",
        text=df_dept_comp["จำนวนผู้ผ่าน"],
        textposition="outside",
        cliponaxis=False,
    ))
    fig_comp.update_layout(
        template="plotly_white",
        barmode="group",
        title="เปรียบเทียบยอดผู้สมัคร (Applied) vs ผู้ผ่านการคัดเลือก (Passed) แต่ละฝ่าย",
        xaxis_tickangle=-25,
        height=450,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=50, b=40, l=20, r=20),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
    )
    st.plotly_chart(fig_comp, use_container_width=True)

    p_col1, p_col2 = st.columns(2)

    with p_col1:
        st.markdown("#### 📈 อัตราการผ่านการคัดเลือกตามฝ่าย (Pass Rate %)")
        df_rate = df_dept_comp.sort_values(by="อัตราการผ่าน (%)", ascending=True)
        
        fig_rate = px.bar(
            df_rate,
            x="อัตราการผ่าน (%)",
            y="ฝ่าย",
            orientation="h",
            text="อัตราการผ่าน (%)",
            color="อัตราการผ่าน (%)",
            color_continuous_scale=["#EF4444", "#F59E0B", "#10B981"],
            title="อัตราการผ่านการคัดเลือก (%) แยกตามฝ่าย",
        )
        fig_rate.update_traces(texttemplate="%{text}%", textposition="outside", cliponaxis=False)
        fig_rate.update_layout(
            template="plotly_white",
            coloraxis_showscale=False,
            height=380,
            margin=dict(t=40, b=20, l=20, r=20),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            xaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
        )
        st.plotly_chart(fig_rate, use_container_width=True)

    with p_col2:
        st.markdown("#### 📋 การกระจายตัวของสถานะผลการคัดเลือก")
        status_dist = filtered_ch.groupby(["department", "status_category"]).size().reset_index(name="count")
        
        fig_status = px.bar(
            status_dist,
            x="department",
            y="count",
            color="status_category",
            title="สัดส่วนสถานะการคัดเลือกรายฝ่าย",
            color_discrete_map={
                "ผ่านการคัดเลือก (ขั้นสุดท้าย)": "#10B981",
                "ผ่านการคัดเลือกเฉพาะฟอร์ม": "#34D399",
                "ผ่านการคัดเลือกไปสัมภาษณ์": "#6EE7B7",
                "ไม่ผ่านการคัดเลือก": "#F87171",
                "ไม่ผ่านไปสัมภาษณ์": "#FCA5A5",
                "ไม่มีข้อมูลผลลัพธ์": "#CBD5E1",
            },
        )
        fig_status.update_layout(
            template="plotly_white",
            xaxis_tickangle=-25,
            height=380,
            margin=dict(t=40, b=40, l=20, r=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            yaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
        )
        st.plotly_chart(fig_status, use_container_width=True)

    st.markdown("#### 📊 ตารางสรุปเปรียบเทียบผู้สมัครและผู้ผ่านการคัดเลือก")
    st.dataframe(df_dept_comp, use_container_width=True, hide_index=True)


# ==============================================================================
# TAB 3: CROSS-ROUND COMPARISON (เปรียบเทียบรอบที่ 1 - 4)
# ==============================================================================
with tab3:
    st.markdown("""
    <div class='insight-card'>
        💡 <b>Insight ภาพรวม 4 รอบ:</b> <b>รอบที่ 3 เป็นรอบที่มีผู้สมัครสูงสุดเป็นประวัติการณ์ (262 คน)</b> คิดเป็น 50% ของยอดสมัครทั้งหมด 
        ขณะที่รอบที่ 4 มี Pass Rate สูงสุด (64.6%) เนื่องจากเปิดรับเฉพาะตำแหน่งที่ยังขาด
    </div>
    """, unsafe_allow_html=True)

    # 3.1 Timeline Trend Across 4 Rounds
    round_summary_list = []
    for r in range(1, 5):
        rdf_app = df_applicants[df_applicants["round"] == r]
        rdf_ch = df_choices[df_choices["round"] == r]
        r_sum = get_overall_summary(rdf_app, rdf_ch, pass_mode=pass_mode)
        r_sum["รอบการสมัคร"] = f"รอบที่ {r}"
        r_sum["round_num"] = r
        round_summary_list.append(r_sum)
    df_round_overview = pd.DataFrame(round_summary_list)

    t_col1, t_col2 = st.columns(2)

    with t_col1:
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=df_round_overview["รอบการสมัคร"],
            y=df_round_overview["total_applications"],
            mode="lines+markers+text",
            name="ยอดผู้สมัคร (Applied)",
            text=df_round_overview["total_applications"],
            textposition="top center",
            line=dict(color="#2563EB", width=3.5),
            marker=dict(size=11, color="#1D4ED8"),
        ))
        fig_trend.add_trace(go.Scatter(
            x=df_round_overview["รอบการสมัคร"],
            y=df_round_overview["passed_applications"],
            mode="lines+markers+text",
            name="ยอดผู้ผ่าน (Passed)",
            text=df_round_overview["passed_applications"],
            textposition="top center",
            line=dict(color="#10B981", width=3.5),
            marker=dict(size=11, color="#059669"),
        ))
        fig_trend.update_layout(
            template="plotly_white",
            title="แนวโน้มยอดผู้สมัคร vs ผู้ผ่านการคัดเลือก (รอบที่ 1 - 4)",
            height=360,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(t=50, b=20, l=20, r=20),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            yaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    with t_col2:
        fig_round_bar = px.bar(
            df_round_overview,
            x="รอบการสมัคร",
            y="pass_rate_overall",
            text="pass_rate_overall",
            color="pass_rate_overall",
            color_continuous_scale="Purples",
            title="อัตราการผ่านการคัดเลือกในแต่ละรอบ (%)",
        )
        fig_round_bar.update_traces(texttemplate="%{text}%", textposition="outside", cliponaxis=False)
        fig_round_bar.update_layout(
            template="plotly_white",
            coloraxis_showscale=False,
            height=360,
            margin=dict(t=50, b=20, l=20, r=20),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            yaxis=dict(showgrid=True, gridcolor="#F1F5F9", title="อัตราการผ่าน (%)"),
        )
        st.plotly_chart(fig_round_bar, use_container_width=True)

    st.markdown("---")

    # 3.2 Department Matrix across 4 Rounds
    st.markdown("#### 🏢 เมทริกซ์เปรียบเทียบรายฝ่ายในแต่ละรอบ (Department Matrix across Rounds)")

    matrix_metric = st.radio(
        "เลือก Metric ที่ต้องการเปรียบเทียบใน Heatmap:",
        ["จำนวนใบสมัคร (Applications)", "จำนวนผู้ผ่านการคัดเลือก (Passed)", "อัตราการผ่าน (%) (Pass Rate)"],
        horizontal=True,
    )

    if "จำนวนใบสมัคร" in matrix_metric:
        df_mat = get_cross_round_department_matrix(df_choices, metric="applications", pass_mode=pass_mode)
        val_cols = ["รอบที่ 1", "รอบที่ 2", "รอบที่ 3", "รอบที่ 4"]
        scale = "Blues"
    elif "จำนวนผู้ผ่าน" in matrix_metric:
        df_mat = get_cross_round_department_matrix(df_choices, metric="passed", pass_mode=pass_mode)
        val_cols = ["รอบที่ 1", "รอบที่ 2", "รอบที่ 3", "รอบที่ 4"]
        scale = "Greens"
    else:
        df_mat = get_cross_round_department_matrix(df_choices, metric="pass_rate", pass_mode=pass_mode)
        val_cols = ["รอบที่ 1 (%)", "รอบที่ 2 (%)", "รอบที่ 3 (%)", "รอบที่ 4 (%)"]
        scale = "Purples"

    heatmap_data = df_mat.set_index("ฝ่าย")[val_cols]
    fig_heatmap = px.imshow(
        heatmap_data,
        labels=dict(x="รอบการสมัคร", y="ฝ่าย", color="ค่า"),
        x=val_cols,
        y=heatmap_data.index,
        color_continuous_scale=scale,
        text_auto=True,
        aspect="auto",
        title=f"Heatmap เปรียบเทียบ {matrix_metric} รายฝ่าย (รอบที่ 1 - 4)",
    )
    fig_heatmap.update_layout(
        template="plotly_white",
        height=450,
        margin=dict(t=50, b=20, l=20, r=20),
        paper_bgcolor="#FFFFFF",
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

    with st.expander("📄 ดูตาราง Matrix รายละเอียด"):
        st.dataframe(df_mat, use_container_width=True, hide_index=True)

    st.markdown("---")

    # 3.3 Re-applicants Analysis
    st.markdown("#### 🔁 พฤติกรรมการสมัครซ้ำหลายรอบ (Re-applicants Tracking)")
    df_reapps, re_stats = get_reapplicant_analysis(df_applicants)

    re1, re2, re3 = st.columns(3)
    with re1:
        st.markdown(f"""
        <div class='kpi-container'>
            <div class='kpi-label'>🔁 นิสิตที่สมัครมากกว่า 1 รอบ</div>
            <div class='kpi-value kpi-pink'>{re_stats['reapplicants_count']} <span style='font-size:1rem;color:#64748B;'>คน</span></div>
            <div class='kpi-subtext'>คิดเป็น <b>{re_stats['reapplicants_pct']}%</b> ของผู้สมัครทั้งหมด</div>
        </div>
        """, unsafe_allow_html=True)
    with re2:
        st.markdown(f"""
        <div class='kpi-container'>
            <div class='kpi-label'>2️⃣ สมัครรวม 2 รอบ</div>
            <div class='kpi-value'>{re_stats['applied_2_rounds']} <span style='font-size:1rem;color:#64748B;'>คน</span></div>
            <div class='kpi-subtext'>มีอัตราความมุ่งมั่นสูง</div>
        </div>
        """, unsafe_allow_html=True)
    with re3:
        st.markdown(f"""
        <div class='kpi-container'>
            <div class='kpi-label'>3️⃣ สมัครรวม 3 รอบ</div>
            <div class='kpi-value'>{re_stats['applied_3_rounds']} <span style='font-size:1rem;color:#64748B;'>คน</span></div>
            <div class='kpi-subtext'>พยายามสมัครต่อเนื่อง</div>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("📄 รายชื่อนิสิตที่สมัครซ้ำหลายรอบ"):
        st.dataframe(df_reapps, use_container_width=True, hide_index=True)


# ==============================================================================
# TAB 4: DATA EXPLORER & EXPORT (ANONYMIZED)
# ==============================================================================
with tab4:
    st.markdown("#### 📋 สืบค้นข้อมูลรายบุคคลแบบนิรนาม (Anonymized Data Explorer)")
    st.caption("🔒 ปลอดข้อมูลส่วนบุคคล 100% (ลบชื่อ-สกุล, รหัสนิสิต, อีเมล ออกทั้งหมดแล้ว)")

    search_query = st.text_input("🔍 ค้นหาด้วยรหัสผู้สมัคร, คณะ, ชั้นปี, หรือชื่อฝ่าย:", placeholder="พิมพ์คำค้นหา เช่น ผู้สมัคร #010, วิศวะ, นายก, ชั้นปี...")

    # Assign anonymized ID
    filtered_app_display = filtered_app.copy()
    filtered_app_display["applicant_id"] = [f"ผู้สมัคร #{i+1:03d}" for i in range(len(filtered_app_display))]

    df_view = filtered_app_display[[
        "applicant_id", "round_label", "faculty", "year",
        "dept_choice_1", "subdept_choice_1", "status_clean_1",
        "dept_choice_2", "subdept_choice_2", "status_clean_2"
    ]].copy()

    df_view.rename(columns={
        "applicant_id": "รหัสผู้สมัคร",
        "round_label": "รอบ",
        "faculty": "คณะ",
        "year": "ชั้นปี",
        "dept_choice_1": "ฝ่ายอันดับ 1",
        "subdept_choice_1": "ฝ่ายย่อยอันดับ 1",
        "status_clean_1": "ผลการสมัครอันดับ 1",
        "dept_choice_2": "ฝ่ายอันดับ 2",
        "subdept_choice_2": "ฝ่ายย่อยอันดับ 2",
        "status_clean_2": "ผลการสมัครอันดับ 2",
    }, inplace=True)

    if search_query:
        mask = (
            df_view["รหัสผู้สมัคร"].str.contains(search_query, case=False, na=False) |
            df_view["คณะ"].str.contains(search_query, case=False, na=False) |
            df_view["ชั้นปี"].str.contains(search_query, case=False, na=False) |
            df_view["ฝ่ายอันดับ 1"].str.contains(search_query, case=False, na=False) |
            df_view["ฝ่ายอันดับ 2"].str.contains(search_query, case=False, na=False)
        )
        df_view = df_view[mask]

    st.write(f"📊 ผลการค้นหา: **{len(df_view):,}** รายการ")
    st.dataframe(df_view, use_container_width=True, hide_index=True)

    # Download Buttons
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        csv_buffer = df_view.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button(
            label="📥 ดาวน์โหลดข้อมูลเป็น CSV (utf-8-sig)",
            data=csv_buffer,
            file_name="sgcu_recruitment_anonymized.csv",
            mime="text/csv",
        )
    with d_col2:
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            df_view.to_excel(writer, index=False, sheet_name="Recruitment_Data")
        st.download_button(
            label="📊 ดาวน์โหลดข้อมูลเป็น Excel (.xlsx)",
            data=excel_buffer.getvalue(),
            file_name="sgcu_recruitment_anonymized.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


# ---------------- FOOTER ----------------
st.markdown("""
<div class='footer-text'>
    องค์การบริหารสโมสรนิสิตจุฬาลงกรณ์มหาวิทยาลัย (อบจ. จุฬาฯ) • SGCU Recruitment Intelligence Dashboard • Clean White Theme
</div>
""", unsafe_allow_html=True)
