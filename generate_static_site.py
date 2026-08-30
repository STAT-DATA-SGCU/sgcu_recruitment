"""
Static Web Dashboard Generator for SGCU Recruitment (Rounds 1-4).
Generates an exact visual and functional replica of app.py:
- Sidebar on the left with identical filter controls
- Header, KPI Cards, Tabs, Expanders, and Charts matching app.py 1:1
- 100% Anonymized (All PII removed: No Names, No Student IDs, No Emails)
- Pure White Theme
- Standalone HTML5 + CSS + Plotly.js + Client-Side JS (No Streamlit toolbars or backend required)
"""

import json
import os
import sys
from pathlib import Path
import pandas as pd

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


def build_anonymized_payload():
    """Builds clean, fully anonymized JSON data payload for the static website."""
    df_app, df_ch = process_all_recruitment_data("data")

    # Map unique candidate names to consistent anonymous person IDs
    unique_names = sorted(df_app["name"].unique())
    name_to_anon_id = {name: f"นิสิตนิรนาม #{i+1:03d}" for i, name in enumerate(unique_names)}

    # Anonymize df_app
    df_app_anon = df_app.copy()
    df_app_anon["applicant_id"] = [f"ผู้สมัคร #{i+1:03d}" for i in range(len(df_app_anon))]
    df_app_anon["person_anon_id"] = df_app_anon["name"].map(name_to_anon_id)
    df_app_anon = df_app_anon.drop(columns=["name", "student_id", "email"], errors="ignore")

    # Anonymize df_ch
    df_ch_anon = df_ch.copy()
    df_ch_anon["person_anon_id"] = df_ch_anon["name"].map(name_to_anon_id)
    df_ch_anon = df_ch_anon.drop(columns=["name", "student_id"], errors="ignore")

    # Anonymized Re-applicant analysis
    df_reapps, re_stats = get_reapplicant_analysis(df_app)
    df_reapps_anon = df_reapps.copy()
    if "ชื่อ-สกุล" in df_reapps_anon.columns:
        df_reapps_anon = df_reapps_anon.drop(columns=["ชื่อ-สกุล", "รหัสนิสิต"], errors="ignore")
    if "รหัสผู้สมัครนิรนาม" not in df_reapps_anon.columns:
        df_reapps_anon["รหัสผู้สมัครนิรนาม"] = [f"ผู้สมัครซ้ำ #{i+1:02d}" for i in range(len(df_reapps_anon))]
    df_reapps_anon = df_reapps_anon[["รหัสผู้สมัครนิรนาม", "คณะ", "จำนวนรอบที่สมัคร", "รอบที่สมัคร", "เคยผ่านการคัดเลือก"]]

    payload = {
        "applicants": df_app_anon.to_dict(orient="records"),
        "choices": df_ch_anon.to_dict(orient="records"),
        "reapplicants": df_reapps_anon.to_dict(orient="records"),
        "reapplicant_stats": re_stats,
        "faculties": sorted([f for f in df_app_anon["faculty"].unique() if f]),
        "years": sorted([y for y in df_app_anon["year"].unique() if y]),
        "departments": sorted([d for d in df_ch_anon["department"].unique() if d]),
    }

    return payload


def generate_html_content(data_json_str: str) -> str:
    """Generates the single-page standalone HTML document matching app.py layout 1:1."""
    html_template = f"""<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SGCU Recruitment Dashboard (Rounds 1-4) - อบจ. จุฬาฯ</title>
    <!-- Google Fonts: Sarabun -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <!-- Plotly.js (CDN) -->
    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            font-family: 'Sarabun', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: #FFFFFF;
            color: #0F172A;
            line-height: 1.5;
            display: flex;
            min-height: 100vh;
        }}
        
        /* ---------------- SIDEBAR (MATCHING APP.PY) ---------------- */
        .sidebar {{
            width: 320px;
            background-color: #F8FAFC;
            border-right: 1px solid #E2E8F0;
            padding: 24px 20px;
            flex-shrink: 0;
            display: flex;
            flex-direction: column;
            gap: 16px;
            overflow-y: auto;
            max-height: 100vh;
            position: sticky;
            top: 0;
        }}
        .sidebar h3 {{
            font-size: 1.25rem;
            font-weight: 700;
            color: #0F172A;
            margin-bottom: 2px;
        }}
        .sidebar p.caption {{
            font-size: 0.85rem;
            color: #64748B;
            margin-bottom: 8px;
        }}
        .form-group {{
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}
        .form-group label {{
            font-size: 0.85rem;
            font-weight: 600;
            color: #334155;
        }}
        .form-control {{
            width: 100%;
            background-color: #FFFFFF;
            border: 1px solid #CBD5E1;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 0.85rem;
            font-family: inherit;
            color: #0F172A;
            outline: none;
            transition: border-color 0.15s ease;
        }}
        .form-control:focus {{
            border-color: #E03177;
            box-shadow: 0 0 0 2px rgba(224, 49, 119, 0.15);
        }}
        .radio-group {{
            display: flex;
            flex-direction: column;
            gap: 8px;
            font-size: 0.85rem;
        }}
        .radio-item {{
            display: flex;
            align-items: flex-start;
            gap: 8px;
            cursor: pointer;
            color: #334155;
        }}
        .radio-item input {{
            margin-top: 3px;
            accent-color: #E03177;
        }}
        .sidebar-divider {{
            height: 1px;
            background-color: #E2E8F0;
            margin: 8px 0;
        }}
        .sidebar-info-box {{
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 12px 14px;
            font-size: 0.8rem;
            color: #475569;
            line-height: 1.6;
        }}
        
        /* ---------------- MAIN CONTENT AREA ---------------- */
        .main-container {{
            flex-grow: 1;
            padding: 24px 36px 48px 36px;
            max-width: 1400px;
            overflow-y: auto;
            background-color: #FFFFFF;
        }}
        
        /* White Clean Header */
        .dashboard-header {{
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-left: 6px solid #E03177;
            border-radius: 12px;
            padding: 20px 24px;
            margin-bottom: 22px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        }}
        .header-title {{
            font-size: 1.85rem;
            font-weight: 700;
            letter-spacing: -0.5px;
            margin: 0;
            color: #0F172A;
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
        }}
        .header-title span.highlight {{
            color: #E03177;
        }}
        .header-subtitle {{
            font-size: 0.95rem;
            color: #475569;
            margin-top: 6px;
            font-weight: 400;
        }}
        .header-badge {{
            display: inline-block;
            background-color: #FCE7F3;
            color: #BE185D;
            border: 1px solid #FBCFE8;
            padding: 2px 12px;
            border-radius: 20px;
            font-size: 0.82rem;
            font-weight: 600;
        }}

        /* KPI Cards Grid */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 14px;
            margin-bottom: 24px;
        }}
        .kpi-container {{
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 16px 18px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
            transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        .kpi-container:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.06);
            border-color: #CBD5E1;
        }}
        .kpi-label {{
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #64748B;
            margin-bottom: 4px;
        }}
        .kpi-value {{
            font-size: 1.95rem;
            font-weight: 700;
            color: #0F172A;
            line-height: 1.2;
        }}
        .kpi-subtext {{
            font-size: 0.8rem;
            color: #64748B;
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px solid #F1F5F9;
        }}
        .kpi-subtext b {{
            color: #1E293B;
        }}
        .kpi-pink {{ color: #E03177; }}
        .kpi-green {{ color: #059669; }}
        .kpi-blue {{ color: #2563EB; }}
        .kpi-purple {{ color: #7C3AED; }}

        /* Tabs (Streamlit Look & Feel) */
        .tabs-header {{
            display: flex;
            gap: 8px;
            border-bottom: 2px solid #E2E8F0;
            margin-bottom: 22px;
            overflow-x: auto;
        }}
        .tab-btn {{
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-bottom: none;
            border-radius: 8px 8px 0 0;
            padding: 10px 20px;
            font-size: 0.92rem;
            font-weight: 600;
            color: #64748B;
            cursor: pointer;
            font-family: inherit;
            transition: all 0.15s ease;
            white-space: nowrap;
        }}
        .tab-btn:hover {{
            color: #E03177;
        }}
        .tab-btn.active {{
            background: #FFFFFF;
            color: #E03177;
            border-color: #E2E8F0 #E2E8F0 #FFFFFF #E2E8F0;
            border-top: 3px solid #E03177;
            margin-bottom: -2px;
        }}
        .tab-content {{
            display: none;
        }}
        .tab-content.active {{
            display: block;
        }}

        /* Section Headings */
        .section-title {{
            font-size: 1.25rem;
            font-weight: 700;
            color: #0F172A;
            margin-bottom: 16px;
        }}
        .chart-card-title {{
            font-size: 1rem;
            font-weight: 700;
            color: #1E293B;
            margin-bottom: 4px;
        }}
        .chart-card-desc {{
            font-size: 0.82rem;
            color: #64748B;
            margin-bottom: 12px;
        }}

        /* Grid Rows */
        .grid-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 24px;
        }}
        .grid-3-2 {{
            display: grid;
            grid-template-columns: 3fr 2fr;
            gap: 20px;
            margin-bottom: 24px;
        }}
        .chart-box {{
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
            margin-bottom: 24px;
        }}

        /* Streamlit Expander Style (<details>) */
        details.st-expander {{
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            margin-top: 14px;
            margin-bottom: 8px;
            padding: 0;
            overflow: hidden;
        }}
        details.st-expander summary {{
            padding: 10px 14px;
            font-size: 0.85rem;
            font-weight: 600;
            color: #334155;
            cursor: pointer;
            background-color: #F8FAFC;
            border-radius: 8px;
            user-select: none;
            transition: background 0.15s ease;
        }}
        details.st-expander summary:hover {{
            background-color: #F1F5F9;
        }}
        details.st-expander[open] summary {{
            border-bottom: 1px solid #E2E8F0;
            border-radius: 8px 8px 0 0;
        }}
        .expander-content {{
            padding: 12px;
            overflow-x: auto;
        }}

        /* Data Tables */
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.82rem;
            text-align: left;
        }}
        .data-table th {{
            background-color: #F8FAFC;
            color: #475569;
            font-weight: 700;
            padding: 10px 12px;
            border-bottom: 1px solid #E2E8F0;
            white-space: nowrap;
        }}
        .data-table td {{
            padding: 9px 12px;
            border-bottom: 1px solid #F1F5F9;
            color: #334155;
            white-space: nowrap;
        }}
        .data-table tr:hover td {{
            background-color: #F8FAFC;
        }}

        /* UI Buttons */
        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 16px;
            font-size: 0.85rem;
            font-weight: 600;
            border-radius: 8px;
            border: 1px solid #CBD5E1;
            background: #FFFFFF;
            color: #334155;
            cursor: pointer;
            font-family: inherit;
            transition: all 0.15s ease;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }}
        .btn:hover {{
            background-color: #F8FAFC;
            border-color: #94A3B8;
        }}

        /* Footer */
        .footer {{
            text-align: center;
            color: #94A3B8;
            font-size: 0.82rem;
            margin-top: 40px;
            padding-top: 18px;
            border-top: 1px solid #E2E8F0;
        }}

        @media (max-width: 1024px) {{
            body {{ flex-direction: column; }}
            .sidebar {{ width: 100%; max-height: none; position: relative; }}
            .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
            .grid-2, .grid-3-2 {{ grid-template-columns: 1fr; }}
            .main-container {{ padding: 16px; }}
        }}
    </style>
</head>
<body>

    <!-- ---------------- SIDEBAR (EXACT REPLICA OF APP.PY) ---------------- -->
    <aside class="sidebar">
        <div>
            <h3>🎛️ ตัวกรองข้อมูล (Filters)</h3>
            <p class="caption">ปรับแต่งมุมมองข้อมูลตามที่ต้องการ</p>
        </div>

        <!-- 1. Round Filter -->
        <div class="form-group">
            <label for="filterRound">📅 เลือกรอบการสมัคร:</label>
            <select id="filterRound" class="form-control" onchange="applyFilters()">
                <option value="ALL">ทั้งหมด (All Rounds)</option>
                <option value="1">รอบที่ 1</option>
                <option value="2">รอบที่ 2</option>
                <option value="3">รอบที่ 3</option>
                <option value="4">รอบที่ 4</option>
            </select>
        </div>

        <!-- 2. Choice Filter -->
        <div class="form-group">
            <label for="filterChoice">🎯 ลำดับการเลือก (Choice):</label>
            <select id="filterChoice" class="form-control" onchange="applyFilters()">
                <option value="ALL">รวมทุกอันดับ (Choice 1 & 2)</option>
                <option value="อันดับ 1">เฉพาะอันดับ 1</option>
                <option value="อันดับ 2">เฉพาะอันดับ 2</option>
            </select>
        </div>

        <!-- 3. Pass Criteria Radio -->
        <div class="form-group">
            <label>✅ เกณฑ์การนับผู้ผ่านการคัดเลือก:</label>
            <div class="radio-group">
                <label class="radio-item">
                    <input type="radio" name="passMode" value="any" checked onchange="applyFilters()">
                    <span>ผ่านทุกประเภท (ขั้นสุดท้าย + ฟอร์ม + สัมภาษณ์)</span>
                </label>
                <label class="radio-item">
                    <input type="radio" name="passMode" value="final" onchange="applyFilters()">
                    <span>ผ่านขั้นสุดท้ายเท่านั้น (Final Only)</span>
                </label>
            </div>
        </div>

        <div class="sidebar-divider"></div>

        <div>
            <label style="font-size:0.9rem; font-weight:700; color:#1E293B;">🔍 ตัวกรองขั้นสูง (Demographics)</label>
        </div>

        <!-- 4. Faculty Filter -->
        <div class="form-group">
            <label for="filterFaculty">🏛️ กรองเฉพาะคณะ:</label>
            <select id="filterFaculty" class="form-control" onchange="applyFilters()">
                <option value="ALL">ทุกคณะ (All Faculties)</option>
            </select>
        </div>

        <!-- 5. Year Filter -->
        <div class="form-group">
            <label for="filterYear">🎓 กรองเฉพาะชั้นปี:</label>
            <select id="filterYear" class="form-control" onchange="applyFilters()">
                <option value="ALL">ทุกชั้นปี (All Years)</option>
            </select>
        </div>

        <div class="sidebar-divider"></div>

        <!-- Info Box -->
        <div class="sidebar-info-box">
            <b>📌 แหล่งข้อมูล:</b> อบจ. จุฬาฯ รอบ 1-4<br>
            <b>👥 ผู้สมัครรวม:</b> 527 คน-ครั้ง<br>
            <b>👤 ไม่ซ้ำคน:</b> 478 คน (สมัครซ้ำ 44 คน)<br>
            <b>📝 ใบสมัครฝ่าย:</b> 725 อันดับ<br>
            <b>🔒 ปลอดข้อมูลส่วนบุคคล (100% Anonymized)</b>
        </div>
    </aside>

    <!-- ---------------- MAIN CONTENT AREA ---------------- -->
    <main class="main-container">
        
        <!-- Header -->
        <div class="dashboard-header">
            <div class="header-title">
                🎓 ระบบวิเคราะห์ข้อมูลการรับสมัคร <span class="highlight">อบจ. จุฬาฯ</span>
                <span class="header-badge" id="headerRoundBadge">ทั้งหมด (All Rounds)</span>
            </div>
            <div class="header-subtitle">
                องค์การบริหารสโมสรนิสิตจุฬาลงกรณ์มหาวิทยาลัย • SGCU Recruitment Intelligence Dashboard (Rounds 1 - 4)
            </div>
        </div>

        <!-- Level 1 Headline KPIs (5 Columns Row) -->
        <div class="kpi-grid">
            <!-- KPI 1 -->
            <div class="kpi-container">
                <div>
                    <div class="kpi-label">👥 ผู้สมัครทั้งหมด</div>
                    <div id="kpiTotalApps" class="kpi-value kpi-blue">0</div>
                </div>
                <div class="kpi-subtext">
                    👤 ไม่ซ้ำคน: <b id="kpiUniqueApps">0</b> คน
                </div>
            </div>

            <!-- KPI 2 -->
            <div class="kpi-container">
                <div>
                    <div class="kpi-label">📝 ใบสมัครฝ่าย</div>
                    <div id="kpiTotalChoices" class="kpi-value kpi-pink">0</div>
                </div>
                <div class="kpi-subtext">
                    🎯 สมัคร 2 อันดับ: <b id="kpiDualChoice">0%</b>
                </div>
            </div>

            <!-- KPI 3 -->
            <div class="kpi-container">
                <div>
                    <div class="kpi-label">🎉 ผู้ผ่านการคัดเลือก</div>
                    <div id="kpiPassedCount" class="kpi-value kpi-green">0</div>
                </div>
                <div class="kpi-subtext">
                    📋 มีผลประเมิน: <b id="kpiEvaluatedCount">0</b> / <span id="kpiTotalAppsSub">0</span>
                </div>
            </div>

            <!-- KPI 4 -->
            <div class="kpi-container">
                <div>
                    <div class="kpi-label">📈 อัตราการผ่านรวม</div>
                    <div id="kpiPassRate" class="kpi-value kpi-purple">0%</div>
                </div>
                <div class="kpi-subtext">
                    ⭐ จากผู้ที่ประเมิน: <b id="kpiPassRateEval">0%</b>
                </div>
            </div>

            <!-- KPI 5 -->
            <div class="kpi-container">
                <div>
                    <div class="kpi-label">🏛️ ความหลากหลาย</div>
                    <div id="kpiNumDepts" class="kpi-value">0 <span style="font-size:1rem;color:#64748B;">ฝ่าย</span></div>
                </div>
                <div class="kpi-subtext">
                    🏫 จากทั้งหมด <b id="kpiNumFacs">0</b> คณะ
                </div>
            </div>
        </div>

        <!-- Tabs Header (Streamlit Style) -->
        <div class="tabs-header">
            <button class="tab-btn active" onclick="switchTab('tab1')" id="btnTab1">📊 1. จัดอันดับ ชั้นปี / คณะ / ฝ่าย</button>
            <button class="tab-btn" onclick="switchTab('tab2')" id="btnTab2">🎯 2. เทียบคนผ่าน vs คนสมัครแต่ละฝ่าย</button>
            <button class="tab-btn" onclick="switchTab('tab3')" id="btnTab3">🔄 3. เปรียบเทียบรอบที่ 1 - 4</button>
            <button class="tab-btn" onclick="switchTab('tab4')" id="btnTab4">📋 4. ข้อมูลรายบุคคลและการสืบค้น (Data Explorer)</button>
        </div>

        <!-- =============================================================== -->
        <!-- TAB 1: DEMOGRAPHICS & RANKINGS -->
        <!-- =============================================================== -->
        <div id="tab1" class="tab-content active">
            <div class="section-title">📌 การจัดอันดับและสถิติประชากรศาสตร์ (Demographics & Rankings)</div>

            <!-- Row 1: Year & Faculty -->
            <div class="grid-2">
                <div class="chart-box">
                    <div class="chart-card-title">🎓 จัดอันดับตามชั้นปี (Academic Year)</div>
                    <div class="chart-card-desc">จำนวนผู้สมัครจำแนกตามชั้นปี</div>
                    <div id="chartYear" style="height:340px;"></div>
                    <details class="st-expander">
                        <summary>📄 ดูตารางสถิติตามชั้นปี</summary>
                        <div class="expander-content">
                            <table class="data-table">
                                <thead>
                                    <tr>
                                        <th>ชั้นปี</th>
                                        <th style="text-align:center;">จำนวนผู้สมัคร</th>
                                        <th style="text-align:center;">จำนวนผู้มีผลประเมิน</th>
                                        <th style="text-align:center;">จำนวนผู้ผ่าน</th>
                                        <th style="text-align:right;">อัตราการผ่าน (%)</th>
                                        <th style="text-align:right;">สัดส่วนผู้สมัคร (%)</th>
                                    </tr>
                                </thead>
                                <tbody id="tableYearBody"></tbody>
                            </table>
                        </div>
                    </details>
                </div>

                <div class="chart-box">
                    <div class="chart-card-title">🏛️ จัดอันดับตามคณะ (Faculty Ranking)</div>
                    <div class="chart-card-desc">Top 10 คณะที่มีผู้สมัครมากที่สุด (คน)</div>
                    <div id="chartFaculty" style="height:340px;"></div>
                    <details class="st-expander">
                        <summary>📄 ดูตารางสถิติตามคณะทั้งหมด</summary>
                        <div class="expander-content">
                            <table class="data-table">
                                <thead>
                                    <tr>
                                        <th>อันดับ</th>
                                        <th>คณะ</th>
                                        <th style="text-align:center;">จำนวนผู้สมัคร</th>
                                        <th style="text-align:center;">จำนวนผู้มีผลประเมิน</th>
                                        <th style="text-align:center;">จำนวนผู้ผ่าน</th>
                                        <th style="text-align:right;">อัตราการผ่าน (%)</th>
                                        <th style="text-align:right;">สัดส่วนผู้สมัคร (%)</th>
                                    </tr>
                                </thead>
                                <tbody id="tableFacultyBody"></tbody>
                            </table>
                        </div>
                    </details>
                </div>
            </div>

            <div class="sidebar-divider" style="margin-bottom:24px;"></div>

            <!-- Row 2: Department Ranking (Stacked + Donut) -->
            <div class="chart-card-title" style="font-size:1.15rem; margin-bottom:12px;">🏢 จัดอันดับฝ่ายที่คนสมัคร (Department Ranking)</div>
            <div class="grid-3-2">
                <div class="chart-box">
                    <div class="chart-card-desc">จำนวนใบสมัครแยกตามอันดับที่เลือก (Choice 1 vs Choice 2)</div>
                    <div id="chartDeptStacked" style="height:420px;"></div>
                </div>
                <div class="chart-box">
                    <div class="chart-card-desc">สัดส่วนความต้องการของฝ่ายทั้งหมด (%)</div>
                    <div id="chartDeptDonut" style="height:420px;"></div>
                </div>
            </div>

            <details class="st-expander" style="margin-bottom:24px;">
                <summary>📄 ตารางสรุปการจัดอันดับฝ่ายทั้งหมด</summary>
                <div class="expander-content">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>อันดับ</th>
                                <th>ฝ่าย</th>
                                <th style="text-align:center;">จำนวนใบสมัคร</th>
                                <th style="text-align:center;">เลือกอันดับ 1</th>
                                <th style="text-align:center;">เลือกอันดับ 2</th>
                                <th style="text-align:center;">จำนวนผู้มีผลประเมิน</th>
                                <th style="text-align:center;">จำนวนผู้ผ่าน</th>
                                <th style="text-align:right;">อัตราการผ่าน (%)</th>
                                <th style="text-align:right;">อัตราการผ่านจากผู้ที่ประเมิน (%)</th>
                            </tr>
                        </thead>
                        <tbody id="tableDeptRankingBody"></tbody>
                    </table>
                </div>
            </details>

            <!-- Row 3: Subdepartments / Roles -->
            <div class="chart-box">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin-bottom:14px;">
                    <div>
                        <div class="chart-card-title">🎯 เจาะลึกฝ่ายย่อยและตำแหน่ง (Subdepartment / Roles)</div>
                        <div class="chart-card-desc">ดูรายละเอียดตำแหน่งย่อยภายในฝ่าย</div>
                    </div>
                    <div style="width:260px;">
                        <select id="subdeptFilterDept" class="form-control" onchange="renderSubdeptTable()">
                            <option value="ALL">ทุกฝ่าย (All Departments)</option>
                        </select>
                    </div>
                </div>
                <div style="overflow-x:auto;">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>ฝ่ายหลัก</th>
                                <th>ฝ่ายย่อย/ตำแหน่ง</th>
                                <th style="text-align:center;">จำนวนใบสมัคร</th>
                                <th style="text-align:center;">เลือกอันดับ 1</th>
                                <th style="text-align:center;">เลือกอันดับ 2</th>
                                <th style="text-align:center;">จำนวนผู้ผ่าน</th>
                                <th style="text-align:right;">อัตราการผ่าน (%)</th>
                            </tr>
                        </thead>
                        <tbody id="tableSubdeptBody"></tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- =============================================================== -->
        <!-- TAB 2: APPLICANTS VS PASSED PER DEPARTMENT -->
        <!-- =============================================================== -->
        <div id="tab2" class="tab-content">
            <div class="section-title">🎯 เปรียบเทียบจำนวนผู้สมัคร vs ผู้ผ่านการคัดเลือกแต่ละฝ่าย (Applicants vs. Passed)</div>

            <!-- Grouped Bar Chart -->
            <div class="chart-box">
                <div class="chart-card-title">เปรียบเทียบยอดผู้สมัคร vs ผู้ผ่านการคัดเลือกแต่ละฝ่าย</div>
                <div class="chart-card-desc">แสดงจำนวนผู้สมัครทั้งหมดเทียบกับจำนวนผู้ผ่านการคัดเลือก</div>
                <div id="chartDeptComp" style="height:450px;"></div>
            </div>

            <!-- 2 Columns: Pass Rate & Status Breakdown -->
            <div class="grid-2">
                <div class="chart-box">
                    <div class="chart-card-title">📈 อัตราการผ่านการคัดเลือก (Pass Rate %)</div>
                    <div class="chart-card-desc">อัตราการผ่านการคัดเลือกตามฝ่าย (%)</div>
                    <div id="chartPassRate" style="height:380px;"></div>
                </div>
                <div class="chart-box">
                    <div class="chart-card-title">📋 การกระจายตัวของผลการคัดเลือก (Status Breakdown)</div>
                    <div class="chart-card-desc">สัดส่วนสถานะผลการคัดเลือกในแต่ละฝ่าย</div>
                    <div id="chartStatusDist" style="height:380px;"></div>
                </div>
            </div>

            <!-- Summary Table -->
            <div class="chart-box">
                <div class="chart-card-title" style="margin-bottom:12px;">📊 ตารางสรุปเปรียบเทียบผู้สมัครและผู้ผ่านการคัดเลือก</div>
                <div style="overflow-x:auto;">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>อันดับ</th>
                                <th>ฝ่าย</th>
                                <th style="text-align:center;">จำนวนใบสมัคร</th>
                                <th style="text-align:center;">เลือกอันดับ 1</th>
                                <th style="text-align:center;">เลือกอันดับ 2</th>
                                <th style="text-align:center;">จำนวนผู้มีผลประเมิน</th>
                                <th style="text-align:center;">จำนวนผู้ผ่าน</th>
                                <th style="text-align:right;">อัตราการผ่าน (%)</th>
                                <th style="text-align:right;">อัตราการผ่านจากผู้ที่ประเมิน (%)</th>
                            </tr>
                        </thead>
                        <tbody id="tableDeptCompBody"></tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- =============================================================== -->
        <!-- TAB 3: CROSS-ROUND COMPARISON (เปรียบเทียบรอบที่ 1 - 4) -->
        <!-- =============================================================== -->
        <div id="tab3" class="tab-content">
            <div class="section-title">🔄 เปรียบเทียบภาพรวมการสมัครข้ามรอบ (รอบที่ 1 - 4)</div>

            <!-- Timeline Trends -->
            <div class="grid-2">
                <div class="chart-box">
                    <div class="chart-card-title">แนวโน้มจำนวนผู้สมัครและผู้ผ่านการคัดเลือก (รอบ 1 - 4)</div>
                    <div class="chart-card-desc">เปรียบเทียบยอดรวมผู้สมัครและผู้ผ่านในแต่ละรอบ</div>
                    <div id="chartRoundTrend" style="height:360px;"></div>
                </div>
                <div class="chart-box">
                    <div class="chart-card-title">อัตราการผ่านการคัดเลือกในแต่ละรอบ (%)</div>
                    <div class="chart-card-desc">Pass Rate รายรอบ</div>
                    <div id="chartRoundPassRate" style="height:360px;"></div>
                </div>
            </div>

            <div class="sidebar-divider" style="margin-bottom:24px;"></div>

            <!-- Matrix Heatmap -->
            <div class="chart-box">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin-bottom:14px;">
                    <div>
                        <div class="chart-card-title">🏢 เมทริกซ์เปรียบเทียบรายฝ่ายในแต่ละรอบ (Department Matrix across Rounds)</div>
                        <div class="chart-card-desc">Heatmap เปรียบเทียบรายฝ่ายในแต่ละรอบ</div>
                    </div>
                    <div style="display:flex; align-items:center; gap:12px; font-size:0.85rem;">
                        <label class="radio-item">
                            <input type="radio" name="matrixMetric" value="applications" checked onchange="renderHeatmap()">
                            <span>จำนวนผู้สมัคร</span>
                        </label>
                        <label class="radio-item">
                            <input type="radio" name="matrixMetric" value="passed" onchange="renderHeatmap()">
                            <span>จำนวนผู้ผ่าน</span>
                        </label>
                        <label class="radio-item">
                            <input type="radio" name="matrixMetric" value="pass_rate" onchange="renderHeatmap()">
                            <span>อัตราการผ่าน (%)</span>
                        </label>
                    </div>
                </div>
                <div id="chartHeatmap" style="height:450px;"></div>
            </div>

            <div class="sidebar-divider" style="margin-bottom:24px;"></div>

            <!-- Re-applicant Analysis -->
            <div class="chart-box">
                <div class="chart-card-title" style="margin-bottom:14px;">🔁 การวิเคราะห์นิสิตที่สมัครซ้ำหลายรอบ (Re-applicants Tracking)</div>
                
                <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:14px; margin-bottom:16px;">
                    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:12px 14px;">
                        <div style="font-size:0.8rem; color:#64748B; font-weight:600;">จำนวนนิสิตที่สมัครมากกว่า 1 รอบ</div>
                        <div id="reappCountText" style="font-size:1.6rem; font-weight:700; color:#E03177; margin-top:2px;">44 คน</div>
                        <div style="font-size:0.75rem; color:#64748B;">9.2% ของผู้สมัครทั้งหมด</div>
                    </div>
                    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:12px 14px;">
                        <div style="font-size:0.8rem; color:#64748B; font-weight:600;">สมัคร 2 รอบ</div>
                        <div id="reapp2Text" style="font-size:1.6rem; font-weight:700; color:#0F172A; margin-top:2px;">42 คน</div>
                        <div style="font-size:0.75rem; color:#64748B;">ความมุ่งมั่นสูง</div>
                    </div>
                    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:12px 14px;">
                        <div style="font-size:0.8rem; color:#64748B; font-weight:600;">สมัคร 3 รอบขึ้นไป</div>
                        <div id="reapp3Text" style="font-size:1.6rem; font-weight:700; color:#0F172A; margin-top:2px;">2 คน</div>
                        <div style="font-size:0.75rem; color:#64748B;">พยายามต่อเนื่อง</div>
                    </div>
                </div>

                <details class="st-expander" open>
                    <summary>📄 รายชื่อนิสิตที่สมัครซ้ำหลายรอบ (ข้อมูลนิรนาม)</summary>
                    <div class="expander-content" style="max-height:300px; overflow-y:auto;">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>รหัสผู้สมัครนิรนาม</th>
                                    <th>คณะ</th>
                                    <th style="text-align:center;">จำนวนรอบที่สมัคร</th>
                                    <th>รอบที่สมัคร</th>
                                    <th style="text-align:center;">เคยผ่านการคัดเลือก</th>
                                </tr>
                            </thead>
                            <tbody id="tableReapplicantBody"></tbody>
                        </table>
                    </div>
                </details>
            </div>
        </div>

        <!-- =============================================================== -->
        <!-- TAB 4: DATA EXPLORER & EXPORT (ANONYMIZED) -->
        <!-- =============================================================== -->
        <div id="tab4" class="tab-content">
            <div class="section-title">📋 ค้นหาและสืบค้นข้อมูลรายบุคคล (Data Explorer)</div>

            <div class="chart-box">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin-bottom:16px;">
                    <div style="flex-grow:1; max-width:500px;">
                        <input type="text" id="tableSearchInput" oninput="renderDataTable()" class="form-control" placeholder="🔍 ค้นหาด้วยรหัสผู้สมัคร, คณะ, ชั้นปี, หรือฝ่าย...">
                    </div>
                    <div>
                        <button onclick="downloadCSV()" class="btn">📥 ดาวน์โหลดข้อมูลเป็น CSV</button>
                    </div>
                </div>

                <div style="margin-bottom:8px; font-size:0.85rem; color:#475569;">
                    ผลการค้นหา: <b id="tableShowingCount" style="color:#0F172A;">0</b> รายการ
                </div>

                <div style="overflow-x:auto; border:1px solid #E2E8F0; border-radius:8px;">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>รหัสผู้สมัคร</th>
                                <th>รอบ</th>
                                <th>คณะ</th>
                                <th style="text-align:center;">ชั้นปี</th>
                                <th>ฝ่ายอันดับ 1</th>
                                <th>ฝ่ายย่อยอันดับ 1</th>
                                <th>ผลการสมัครอันดับ 1</th>
                                <th>ฝ่ายอันดับ 2</th>
                                <th>ฝ่ายย่อยอันดับ 2</th>
                                <th>ผลการสมัครอันดับ 2</th>
                            </tr>
                        </thead>
                        <tbody id="tableDataBody"></tbody>
                    </table>
                </div>

                <!-- Pagination -->
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:14px; font-size:0.82rem; color:#64748B;">
                    <div>หน้า <span id="tablePageText">1 / 1</span></div>
                    <div style="display:flex; gap:6px;">
                        <button onclick="prevPage()" id="btnPrev" class="btn" style="padding:4px 10px;">ก่อนหน้า</button>
                        <button onclick="nextPage()" id="btnNext" class="btn" style="padding:4px 10px;">ถัดไป</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            องค์การบริหารสโมสรนิสิตจุฬาลงกรณ์มหาวิทยาลัย (อบจ. จุฬาฯ) • SGCU Recruitment Data Analytics Dashboard
        </div>
    </main>

    <!-- DATASET JSON EMBED -->
    <script id="dashboardDataPayload" type="application/json">
{data_json_str}
    </script>

    <!-- CLIENT-SIDE SCRIPT -->
    <script>
        const RAW_DATA = JSON.parse(document.getElementById('dashboardDataPayload').textContent);
        let currentFilteredApplicants = [...RAW_DATA.applicants];
        let currentFilteredChoices = [...RAW_DATA.choices];
        let currentTablePage = 1;
        const TABLE_PAGE_SIZE = 25;

        function initDropdowns() {{
            const facSelect = document.getElementById('filterFaculty');
            RAW_DATA.faculties.forEach(f => {{
                const opt = document.createElement('option');
                opt.value = f;
                opt.textContent = f;
                facSelect.appendChild(opt);
            }});

            const yrSelect = document.getElementById('filterYear');
            RAW_DATA.years.forEach(y => {{
                const opt = document.createElement('option');
                opt.value = y;
                opt.textContent = y;
                yrSelect.appendChild(opt);
            }});

            const subdeptSelect = document.getElementById('subdeptFilterDept');
            RAW_DATA.departments.forEach(d => {{
                const opt = document.createElement('option');
                opt.value = d;
                opt.textContent = d;
                subdeptSelect.appendChild(opt);
            }});
        }}

        function switchTab(tabId) {{
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

            if (tabId === 'tab1') document.getElementById('btnTab1').classList.add('active');
            if (tabId === 'tab2') document.getElementById('btnTab2').classList.add('active');
            if (tabId === 'tab3') document.getElementById('btnTab3').classList.add('active');
            if (tabId === 'tab4') document.getElementById('btnTab4').classList.add('active');

            document.getElementById(tabId).classList.add('active');

            setTimeout(() => {{
                window.dispatchEvent(new Event('resize'));
            }}, 50);
        }}

        function applyFilters() {{
            const rVal = document.getElementById('filterRound').value;
            const cVal = document.getElementById('filterChoice').value;
            const pVal = document.querySelector('input[name="passMode"]:checked').value;
            const fVal = document.getElementById('filterFaculty').value;
            const yVal = document.getElementById('filterYear').value;

            // Update badge text
            const roundBadgeText = rVal === 'ALL' ? 'ทั้งหมด (All Rounds)' : `รอบที่ ${{rVal}}`;
            document.getElementById('headerRoundBadge').textContent = roundBadgeText;

            currentFilteredApplicants = RAW_DATA.applicants.filter(a => {{
                if (rVal !== 'ALL' && a.round !== parseInt(rVal)) return false;
                if (fVal !== 'ALL' && a.faculty !== fVal) return false;
                if (yVal !== 'ALL' && a.year !== yVal) return false;
                return true;
            }});

            currentFilteredChoices = RAW_DATA.choices.filter(c => {{
                if (rVal !== 'ALL' && c.round !== parseInt(rVal)) return false;
                if (cVal !== 'ALL' && c.choice_order !== cVal) return false;
                if (fVal !== 'ALL' && c.faculty !== fVal) return false;
                if (yVal !== 'ALL' && c.year !== yVal) return false;
                return true;
            }});

            currentTablePage = 1;
            renderKPIs(pVal);
            renderTab1(pVal);
            renderTab2(pVal);
            renderTab3(pVal);
            renderDataTable();
        }}

        function renderKPIs(passMode) {{
            const totalApps = currentFilteredApplicants.length;
            const uniquePeople = new Set(currentFilteredApplicants.map(a => a.person_anon_id)).size;
            const totalChoices = currentFilteredChoices.length;
            const dualCount = currentFilteredApplicants.filter(a => a.num_choices === 2).length;
            const dualPct = totalApps > 0 ? ((dualCount / totalApps) * 100).toFixed(1) : 0;

            const evaluatedCount = currentFilteredApplicants.filter(a => a.has_evaluation).length;
            const passedCount = currentFilteredApplicants.filter(a => passMode === 'any' ? a.passed_overall_any : a.passed_final_any).length;
            const passRateOverall = totalApps > 0 ? ((passedCount / totalApps) * 100).toFixed(1) : 0;
            const passRateEval = evaluatedCount > 0 ? ((passedCount / evaluatedCount) * 100).toFixed(1) : 0;

            const numDepts = new Set(currentFilteredChoices.map(c => c.department)).size;
            const numFacs = new Set(currentFilteredApplicants.map(a => a.faculty)).size;

            document.getElementById('kpiTotalApps').textContent = totalApps.toLocaleString();
            document.getElementById('kpiTotalAppsSub').textContent = totalApps.toLocaleString();
            document.getElementById('kpiUniqueApps').textContent = uniquePeople.toLocaleString();
            document.getElementById('kpiTotalChoices').textContent = totalChoices.toLocaleString();
            document.getElementById('kpiDualChoice').textContent = dualPct + '%';
            document.getElementById('kpiPassedCount').textContent = passedCount.toLocaleString();
            document.getElementById('kpiEvaluatedCount').textContent = evaluatedCount.toLocaleString();
            document.getElementById('kpiPassRate').textContent = passRateOverall + '%';
            document.getElementById('kpiPassRateEval').textContent = passRateEval + '%';
            document.getElementById('kpiNumDepts').innerHTML = `${{numDepts}} <span style="font-size:1rem;color:#64748B;">ฝ่าย</span>`;
            document.getElementById('kpiNumFacs').textContent = numFacs;
        }}

        // Render Tab 1 (Rankings)
        function renderTab1(passMode) {{
            const passCol = passMode === 'any' ? 'passed_any' : 'passed_final';
            const passColApp = passMode === 'any' ? 'passed_overall_any' : 'passed_final_any';

            // 1. Year Ranking
            const yearMap = {{}};
            currentFilteredApplicants.forEach(a => {{
                if (!yearMap[a.year]) yearMap[a.year] = {{ year: a.year, total: 0, eval: 0, passed: 0 }};
                yearMap[a.year].total += 1;
                if (a.has_evaluation) yearMap[a.year].eval += 1;
                if (a[passColApp]) yearMap[a.year].passed += 1;
            }});

            const yearOrder = ['ปี 1', 'ปี 2', 'ปี 3', 'ปี 4', 'ปี 6'];
            const yearList = yearOrder.filter(y => yearMap[y] !== undefined).map(y => yearMap[y]);
            const totalApps = currentFilteredApplicants.length;

            const tableYearBody = document.getElementById('tableYearBody');
            tableYearBody.innerHTML = '';
            yearList.forEach(item => {{
                const rate = item.total > 0 ? ((item.passed / item.total) * 100).toFixed(1) : 0;
                const pct = totalApps > 0 ? ((item.total / totalApps) * 100).toFixed(1) : 0;
                tableYearBody.innerHTML += `
                    <tr>
                        <td style="font-weight:600;">${{item.year}}</td>
                        <td style="text-align:center; font-weight:700;">${{item.total}}</td>
                        <td style="text-align:center;">${{item.eval}}</td>
                        <td style="text-align:center; font-weight:700; color:#059669;">${{item.passed}}</td>
                        <td style="text-align:right; font-weight:600;">${{rate}}%</td>
                        <td style="text-align:right;">${{pct}}%</td>
                    </tr>
                `;
            }});

            Plotly.react('chartYear', [{{
                x: yearList.map(y => y.year),
                y: yearList.map(y => y.total),
                type: 'bar',
                text: yearList.map(y => y.total),
                textposition: 'outside',
                cliponaxis: false,
                marker: {{ color: ['#E03177', '#8E24AA', '#2563EB', '#0284C7', '#10B981'] }}
            }}], {{
                margin: {{ t: 20, b: 30, l: 40, r: 20 }},
                paper_bgcolor: '#FFFFFF',
                plot_bgcolor: '#FFFFFF',
                yaxis: {{ gridcolor: '#F1F5F9' }},
                font: {{ family: 'Sarabun', size: 12 }}
            }}, {{ responsive: true, displayModeBar: false }});

            // 2. Faculty Ranking
            const facMap = {{}};
            currentFilteredApplicants.forEach(a => {{
                if (!a.faculty) return;
                if (!facMap[a.faculty]) facMap[a.faculty] = {{ faculty: a.faculty, total: 0, eval: 0, passed: 0 }};
                facMap[a.faculty].total += 1;
                if (a.has_evaluation) facMap[a.faculty].eval += 1;
                if (a[passColApp]) facMap[a.faculty].passed += 1;
            }});

            const sortedFacs = Object.values(facMap).sort((a, b) => b.total - a.total);
            const tableFacultyBody = document.getElementById('tableFacultyBody');
            tableFacultyBody.innerHTML = '';
            sortedFacs.forEach((item, idx) => {{
                const rate = item.total > 0 ? ((item.passed / item.total) * 100).toFixed(1) : 0;
                const pct = totalApps > 0 ? ((item.total / totalApps) * 100).toFixed(1) : 0;
                tableFacultyBody.innerHTML += `
                    <tr>
                        <td style="color:#64748B;">${{idx + 1}}</td>
                        <td style="font-weight:600;">${{item.faculty}}</td>
                        <td style="text-align:center; font-weight:700;">${{item.total}}</td>
                        <td style="text-align:center;">${{item.eval}}</td>
                        <td style="text-align:center; font-weight:700; color:#059669;">${{item.passed}}</td>
                        <td style="text-align:right; font-weight:600;">${{rate}}%</td>
                        <td style="text-align:right;">${{pct}}%</td>
                    </tr>
                `;
            }});

            const top10Facs = sortedFacs.slice(0, 10).reverse();
            Plotly.react('chartFaculty', [{{
                y: top10Facs.map(f => f.faculty),
                x: top10Facs.map(f => f.total),
                type: 'bar',
                orientation: 'h',
                text: top10Facs.map(f => f.total),
                textposition: 'outside',
                cliponaxis: false,
                marker: {{ color: '#0D9488' }}
            }}], {{
                margin: {{ t: 20, b: 30, l: 200, r: 30 }},
                paper_bgcolor: '#FFFFFF',
                plot_bgcolor: '#FFFFFF',
                xaxis: {{ gridcolor: '#F1F5F9' }},
                font: {{ family: 'Sarabun', size: 11 }}
            }}, {{ responsive: true, displayModeBar: false }});

            // 3. Department Rankings
            const deptMap = {{}};
            currentFilteredChoices.forEach(c => {{
                if (!deptMap[c.department]) deptMap[c.department] = {{ dept: c.department, total: 0, c1: 0, c2: 0, eval: 0, passed: 0 }};
                deptMap[c.department].total += 1;
                if (c.choice_order === 'อันดับ 1') deptMap[c.department].c1 += 1;
                if (c.choice_order === 'อันดับ 2') deptMap[c.department].c2 += 1;
                if (c.is_evaluated) deptMap[c.department].eval += 1;
                if (c[passCol]) deptMap[c.department].passed += 1;
            }});

            const sortedDepts = Object.values(deptMap).sort((a, b) => b.total - a.total);
            const tableDeptRankingBody = document.getElementById('tableDeptRankingBody');
            tableDeptRankingBody.innerHTML = '';
            sortedDepts.forEach((item, idx) => {{
                const rateOverall = item.total > 0 ? ((item.passed / item.total) * 100).toFixed(1) : 0;
                const rateEval = item.eval > 0 ? ((item.passed / item.eval) * 100).toFixed(1) : 0;
                tableDeptRankingBody.innerHTML += `
                    <tr>
                        <td style="color:#64748B;">${{idx + 1}}</td>
                        <td style="font-weight:700;">${{item.dept}}</td>
                        <td style="text-align:center; font-weight:700; color:#2563EB;">${{item.total}}</td>
                        <td style="text-align:center; color:#E03177;">${{item.c1}}</td>
                        <td style="text-align:center; color:#F472B6;">${{item.c2}}</td>
                        <td style="text-align:center;">${{item.eval}}</td>
                        <td style="text-align:center; font-weight:700; color:#059669;">${{item.passed}}</td>
                        <td style="text-align:right; font-weight:700;">${{rateOverall}}%</td>
                        <td style="text-align:right;">${{rateEval}}%</td>
                    </tr>
                `;
            }});

            const deptsAsc = [...sortedDepts].reverse();
            Plotly.react('chartDeptStacked', [
                {{
                    y: deptsAsc.map(d => d.dept),
                    x: deptsAsc.map(d => d.c1),
                    name: 'อันดับ 1 (Choice 1)',
                    type: 'bar',
                    orientation: 'h',
                    marker: {{ color: '#E03177' }}
                }},
                {{
                    y: deptsAsc.map(d => d.dept),
                    x: deptsAsc.map(d => d.c2),
                    name: 'อันดับ 2 (Choice 2)',
                    type: 'bar',
                    orientation: 'h',
                    marker: {{ color: '#FBCFE8' }}
                }}
            ], {{
                barmode: 'stack',
                margin: {{ t: 20, b: 30, l: 190, r: 20 }},
                legend: {{ orientation: 'h', y: 1.1, x: 0.5, xanchor: 'center' }},
                paper_bgcolor: '#FFFFFF',
                plot_bgcolor: '#FFFFFF',
                xaxis: {{ gridcolor: '#F1F5F9' }},
                font: {{ family: 'Sarabun', size: 11 }}
            }}, {{ responsive: true, displayModeBar: false }});

            Plotly.react('chartDeptDonut', [{{
                labels: sortedDepts.map(d => d.dept),
                values: sortedDepts.map(d => d.total),
                type: 'pie',
                hole: 0.45,
                textinfo: 'percent',
                textposition: 'inside',
                marker: {{
                    colors: ['#E03177', '#8E24AA', '#3B82F6', '#0284C7', '#10B981', '#F59E0B', '#6366F1', '#EC4899', '#14B8A6', '#64748B']
                }}
            }}], {{
                margin: {{ t: 20, b: 20, l: 20, r: 20 }},
                paper_bgcolor: '#FFFFFF',
                font: {{ family: 'Sarabun', size: 11 }}
            }}, {{ responsive: true, displayModeBar: false }});

            renderSubdeptTable();
        }}

        function renderSubdeptTable() {{
            const selectedDept = document.getElementById('subdeptFilterDept').value;
            const tbody = document.getElementById('tableSubdeptBody');
            tbody.innerHTML = '';

            const subdeptMap = {{}};
            currentFilteredChoices.forEach(c => {{
                if (selectedDept !== 'ALL' && c.department !== selectedDept) return;
                const key = `${{c.department}}|||${{c.subdepartment || 'ไม่ระบุตำแหน่งย่อย'}}`;
                if (!subdeptMap[key]) {{
                    subdeptMap[key] = {{ dept: c.department, subdept: c.subdepartment || 'ไม่ระบุตำแหน่งย่อย', total: 0, c1: 0, c2: 0, passed: 0 }};
                }}
                subdeptMap[key].total += 1;
                if (c.choice_order === 'อันดับ 1') subdeptMap[key].c1 += 1;
                if (c.choice_order === 'อันดับ 2') subdeptMap[key].c2 += 1;
                if (c.passed_any) subdeptMap[key].passed += 1;
            }});

            const sorted = Object.values(subdeptMap).sort((a, b) => b.total - a.total);
            sorted.forEach(item => {{
                const rate = item.total > 0 ? ((item.passed / item.total) * 100).toFixed(1) : 0;
                tbody.innerHTML += `
                    <tr>
                        <td style="font-weight:600;">${{item.dept}}</td>
                        <td style="color:#475569;">${{item.subdept}}</td>
                        <td style="text-align:center; font-weight:700;">${{item.total}}</td>
                        <td style="text-align:center; color:#E03177;">${{item.c1}}</td>
                        <td style="text-align:center; color:#F472B6;">${{item.c2}}</td>
                        <td style="text-align:center; font-weight:700; color:#059669;">${{item.passed}}</td>
                        <td style="text-align:right; font-weight:600;">${{rate}}%</td>
                    </tr>
                `;
            }});
        }}

        // Render Tab 2 (Applicants vs Passed)
        function renderTab2(passMode) {{
            const passCol = passMode === 'any' ? 'passed_any' : 'passed_final';
            const deptMap = {{}};
            currentFilteredChoices.forEach(c => {{
                if (!deptMap[c.department]) deptMap[c.department] = {{ dept: c.department, total: 0, c1: 0, c2: 0, eval: 0, passed: 0 }};
                deptMap[c.department].total += 1;
                if (c.choice_order === 'อันดับ 1') deptMap[c.department].c1 += 1;
                if (c.choice_order === 'อันดับ 2') deptMap[c.department].c2 += 1;
                if (c.is_evaluated) deptMap[c.department].eval += 1;
                if (c[passCol]) deptMap[c.department].passed += 1;
            }});

            const sortedDepts = Object.values(deptMap).sort((a, b) => b.total - a.total);
            const tableDeptCompBody = document.getElementById('tableDeptCompBody');
            tableDeptCompBody.innerHTML = '';
            sortedDepts.forEach((item, idx) => {{
                const rateOverall = item.total > 0 ? ((item.passed / item.total) * 100).toFixed(1) : 0;
                const rateEval = item.eval > 0 ? ((item.passed / item.eval) * 100).toFixed(1) : 0;
                tableDeptCompBody.innerHTML += `
                    <tr>
                        <td style="color:#64748B;">${{idx + 1}}</td>
                        <td style="font-weight:700;">${{item.dept}}</td>
                        <td style="text-align:center; font-weight:700; color:#2563EB;">${{item.total}}</td>
                        <td style="text-align:center; color:#E03177;">${{item.c1}}</td>
                        <td style="text-align:center; color:#F472B6;">${{item.c2}}</td>
                        <td style="text-align:center;">${{item.eval}}</td>
                        <td style="text-align:center; font-weight:700; color:#059669;">${{item.passed}}</td>
                        <td style="text-align:right; font-weight:700;">${{rateOverall}}%</td>
                        <td style="text-align:right;">${{rateEval}}%</td>
                    </tr>
                `;
            }});

            Plotly.react('chartDeptComp', [
                {{
                    x: sortedDepts.map(d => d.dept),
                    y: sortedDepts.map(d => d.total),
                    name: 'จำนวนใบสมัครทั้งหมด (Applicants)',
                    type: 'bar',
                    text: sortedDepts.map(d => d.total),
                    textposition: 'outside',
                    cliponaxis: false,
                    marker: {{ color: '#90CAF9' }}
                }},
                {{
                    x: sortedDepts.map(d => d.dept),
                    y: sortedDepts.map(d => d.passed),
                    name: 'จำนวนผู้ผ่านการคัดเลือก (Passed)',
                    type: 'bar',
                    text: sortedDepts.map(d => d.passed),
                    textposition: 'outside',
                    cliponaxis: false,
                    marker: {{ color: '#2E7D32' }}
                }}
            ], {{
                barmode: 'group',
                margin: {{ t: 30, b: 70, l: 40, r: 20 }},
                xaxis: {{ tickangle: -25 }},
                legend: {{ orientation: 'h', y: 1.12, x: 0.5, xanchor: 'center' }},
                paper_bgcolor: '#FFFFFF',
                plot_bgcolor: '#FFFFFF',
                yaxis: {{ gridcolor: '#F1F5F9' }},
                font: {{ family: 'Sarabun', size: 11 }}
            }}, {{ responsive: true, displayModeBar: false }});

            const sortedByRate = [...sortedDepts].sort((a, b) => {{
                const rA = a.total > 0 ? (a.passed / a.total) * 100 : 0;
                const rB = b.total > 0 ? (b.passed / b.total) * 100 : 0;
                return rA - rB;
            }});

            Plotly.react('chartPassRate', [{{
                y: sortedByRate.map(d => d.dept),
                x: sortedByRate.map(d => d.total > 0 ? ((d.passed / d.total) * 100).toFixed(1) : 0),
                type: 'bar',
                orientation: 'h',
                text: sortedByRate.map(d => (d.total > 0 ? ((d.passed / d.total) * 100).toFixed(1) : 0) + '%'),
                textposition: 'outside',
                cliponaxis: false,
                marker: {{
                    color: sortedByRate.map(d => {{
                        const r = d.total > 0 ? (d.passed / d.total) * 100 : 0;
                        return r > 40 ? '#10B981' : (r > 20 ? '#F59E0B' : '#EF4444');
                    }})
                }}
            }}], {{
                margin: {{ t: 20, b: 30, l: 190, r: 40 }},
                paper_bgcolor: '#FFFFFF',
                plot_bgcolor: '#FFFFFF',
                xaxis: {{ gridcolor: '#F1F5F9' }},
                font: {{ family: 'Sarabun', size: 11 }}
            }}, {{ responsive: true, displayModeBar: false }});

            // Status Distribution
            const statusCats = ['ผ่านการคัดเลือก (ขั้นสุดท้าย)', 'ผ่านการคัดเลือกเฉพาะฟอร์ม', 'ผ่านการคัดเลือกไปสัมภาษณ์', 'ไม่ผ่านการคัดเลือก', 'ไม่ผ่านไปสัมภาษณ์', 'ไม่มีข้อมูลผลลัพธ์'];
            const statusColors = {{
                'ผ่านการคัดเลือก (ขั้นสุดท้าย)': '#10B981',
                'ผ่านการคัดเลือกเฉพาะฟอร์ม': '#34D399',
                'ผ่านการคัดเลือกไปสัมภาษณ์': '#6EE7B7',
                'ไม่ผ่านการคัดเลือก': '#F87171',
                'ไม่ผ่านไปสัมภาษณ์': '#FCA5A5',
                'ไม่มีข้อมูลผลลัพธ์': '#CBD5E1'
            }};

            const statusTraces = statusCats.map(cat => {{
                return {{
                    x: sortedDepts.map(d => d.dept),
                    y: sortedDepts.map(d => currentFilteredChoices.filter(c => c.department === d.dept && c.status_category === cat).length),
                    name: cat,
                    type: 'bar',
                    marker: {{ color: statusColors[cat] }}
                }};
            }});

            Plotly.react('chartStatusDist', statusTraces, {{
                barmode: 'stack',
                margin: {{ t: 30, b: 70, l: 40, r: 20 }},
                xaxis: {{ tickangle: -25 }},
                legend: {{ orientation: 'h', y: 1.15, x: 0.5, xanchor: 'center', font: {{ size: 9 }} }},
                paper_bgcolor: '#FFFFFF',
                plot_bgcolor: '#FFFFFF',
                yaxis: {{ gridcolor: '#F1F5F9' }},
                font: {{ family: 'Sarabun', size: 11 }}
            }}, {{ responsive: true, displayModeBar: false }});
        }}

        // Render Tab 3 (Cross-Round)
        function renderTab3(passMode) {{
            const roundOverview = [1, 2, 3, 4].map(r => {{
                const rApps = RAW_DATA.applicants.filter(a => a.round === r);
                const rPassed = rApps.filter(a => passMode === 'any' ? a.passed_overall_any : a.passed_final_any).length;
                const rRate = rApps.length > 0 ? ((rPassed / rApps.length) * 100).toFixed(1) : 0;
                return {{ round: `รอบที่ ${{r}}`, apps: rApps.length, passed: rPassed, rate: parseFloat(rRate) }};
            }});

            Plotly.react('chartRoundTrend', [
                {{
                    x: roundOverview.map(r => r.round),
                    y: roundOverview.map(r => r.apps),
                    mode: 'lines+markers+text',
                    name: 'จำนวนผู้สมัคร (Applicants)',
                    text: roundOverview.map(r => r.apps),
                    textposition: 'top center',
                    line: {{ color: '#1976D2', width: 3 }},
                    marker: {{ size: 10, color: '#1976D2' }}
                }},
                {{
                    x: roundOverview.map(r => r.round),
                    y: roundOverview.map(r => r.passed),
                    mode: 'lines+markers+text',
                    name: 'จำนวนผู้ผ่าน (Passed)',
                    text: roundOverview.map(r => r.passed),
                    textposition: 'top center',
                    line: {{ color: '#388E3C', width: 3 }},
                    marker: {{ size: 10, color: '#388E3C' }}
                }}
            ], {{
                margin: {{ t: 30, b: 30, l: 40, r: 20 }},
                legend: {{ orientation: 'h', y: 1.1, x: 0.5, xanchor: 'center' }},
                paper_bgcolor: '#FFFFFF',
                plot_bgcolor: '#FFFFFF',
                yaxis: {{ gridcolor: '#F1F5F9' }},
                font: {{ family: 'Sarabun', size: 11 }}
            }}, {{ responsive: true, displayModeBar: false }});

            Plotly.react('chartRoundPassRate', [{{
                x: roundOverview.map(r => r.round),
                y: roundOverview.map(r => r.rate),
                type: 'bar',
                text: roundOverview.map(r => r.rate + '%'),
                textposition: 'outside',
                cliponaxis: false,
                marker: {{ color: ['#E03177', '#8E24AA', '#3949AB', '#00897B'] }}
            }}], {{
                margin: {{ t: 20, b: 30, l: 40, r: 20 }},
                paper_bgcolor: '#FFFFFF',
                plot_bgcolor: '#FFFFFF',
                yaxis: {{ gridcolor: '#F1F5F9' }},
                font: {{ family: 'Sarabun', size: 11 }}
            }}, {{ responsive: true, displayModeBar: false }});

            renderHeatmap();

            // Re-applicants
            const tbody = document.getElementById('tableReapplicantBody');
            tbody.innerHTML = '';
            RAW_DATA.reapplicants.forEach(item => {{
                tbody.innerHTML += `
                    <tr>
                        <td style="font-weight:600;">${{item['รหัสผู้สมัครนิรนาม']}}</td>
                        <td>${{item['คณะ']}}</td>
                        <td style="text-align:center; font-weight:700; color:#E03177;">${{item['จำนวนรอบที่สมัคร']}} รอบ</td>
                        <td>${{item['รอบที่สมัคร']}}</td>
                        <td style="text-align:center;">
                            <span style="display:inline-block; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:700; background:${{item['เคยผ่านการคัดเลือก'] ? '#D1FAE5; color:#065F46;' : '#F1F5F9; color:#475569;'}}">
                                ${{item['เคยผ่านการคัดเลือก'] ? '✅ เคยผ่าน' : '❌ ไม่ผ่าน'}}
                            </span>
                        </td>
                    </tr>
                `;
            }});
        }}

        function renderHeatmap() {{
            const metric = document.querySelector('input[name="matrixMetric"]:checked').value;
            const passMode = document.querySelector('input[name="passMode"]:checked').value;
            const passCol = passMode === 'any' ? 'passed_any' : 'passed_final';

            const depts = RAW_DATA.departments;
            const rounds = ['รอบที่ 1', 'รอบที่ 2', 'รอบที่ 3', 'รอบที่ 4'];
            
            const matrixZ = depts.map(d => {{
                return [1, 2, 3, 4].map(r => {{
                    const subset = RAW_DATA.choices.filter(c => c.department === d && c.round === r);
                    if (metric === 'applications') return subset.length;
                    if (metric === 'passed') return subset.filter(c => c[passCol]).length;
                    if (metric === 'pass_rate') {{
                        const passed = subset.filter(c => c[passCol]).length;
                        return subset.length > 0 ? parseFloat(((passed / subset.length) * 100).toFixed(1)) : 0;
                    }}
                    return 0;
                }});
            }});

            Plotly.react('chartHeatmap', [{{
                z: matrixZ,
                x: rounds,
                y: depts,
                type: 'heatmap',
                colorscale: 'Purp',
                hoverongaps: false
            }}], {{
                margin: {{ t: 20, b: 30, l: 190, r: 20 }},
                paper_bgcolor: '#FFFFFF',
                font: {{ family: 'Sarabun', size: 11 }}
            }}, {{ responsive: true, displayModeBar: false }});
        }}

        // Render Tab 4 (Data Explorer)
        function renderDataTable() {{
            const query = document.getElementById('tableSearchInput').value.toLowerCase().trim();
            const filtered = currentFilteredApplicants.filter(a => {{
                if (!query) return true;
                return (
                    (a.applicant_id && a.applicant_id.toLowerCase().includes(query)) ||
                    (a.faculty && a.faculty.toLowerCase().includes(query)) ||
                    (a.year && a.year.toLowerCase().includes(query)) ||
                    (a.dept_choice_1 && a.dept_choice_1.toLowerCase().includes(query)) ||
                    (a.dept_choice_2 && a.dept_choice_2.toLowerCase().includes(query))
                );
            }});

            const total = filtered.length;
            const totalPages = Math.ceil(total / TABLE_PAGE_SIZE) || 1;
            if (currentTablePage > totalPages) currentTablePage = totalPages;

            const start = (currentTablePage - 1) * TABLE_PAGE_SIZE;
            const end = Math.min(start + TABLE_PAGE_SIZE, total);
            const pageData = filtered.slice(start, end);

            const tbody = document.getElementById('tableDataBody');
            tbody.innerHTML = '';

            pageData.forEach(item => {{
                tbody.innerHTML += `
                    <tr>
                        <td style="font-weight:600;">${{item.applicant_id}}</td>
                        <td>${{item.round_label}}</td>
                        <td>${{item.faculty}}</td>
                        <td style="text-align:center;">${{item.year}}</td>
                        <td style="font-weight:600;">${{item.dept_choice_1 || '-'}}</td>
                        <td style="color:#64748B;">${{item.subdept_choice_1 || '-'}}</td>
                        <td style="font-weight:600; color:${{item.status_clean_1.includes('ผ่าน') ? '#059669;' : '#64748B;'}}">${{item.status_clean_1 || '-'}}</td>
                        <td style="font-weight:600;">${{item.dept_choice_2 || '-'}}</td>
                        <td style="color:#64748B;">${{item.subdept_choice_2 || '-'}}</td>
                        <td style="font-weight:600; color:${{item.status_clean_2.includes('ผ่าน') ? '#059669;' : '#64748B;'}}">${{item.status_clean_2 || '-'}}</td>
                    </tr>
                `;
            }});

            document.getElementById('tableShowingCount').textContent = total.toLocaleString();
            document.getElementById('tablePageText').textContent = `${{currentTablePage}} / ${{totalPages}}`;
            document.getElementById('btnPrev').disabled = currentTablePage <= 1;
            document.getElementById('btnNext').disabled = currentTablePage >= totalPages;
        }}

        function prevPage() {{
            if (currentTablePage > 1) {{
                currentTablePage -= 1;
                renderDataTable();
            }}
        }}

        function nextPage() {{
            currentTablePage += 1;
            renderDataTable();
        }}

        function downloadCSV() {{
            const headers = ['รหัสผู้สมัคร', 'รอบ', 'คณะ', 'ชั้นปี', 'ฝ่ายอันดับ 1', 'ฝ่ายย่อยอันดับ 1', 'ผลการสมัครอันดับ 1', 'ฝ่ายอันดับ 2', 'ฝ่ายย่อยอันดับ 2', 'ผลการสมัครอันดับ 2'];
            const rows = currentFilteredApplicants.map(a => [
                a.applicant_id,
                a.round_label,
                `"${{a.faculty}}"`,
                a.year,
                `"${{a.dept_choice_1 || ''}}"`,
                `"${{a.subdept_choice_1 || ''}}"`,
                `"${{a.status_clean_1 || ''}}"`,
                `"${{a.dept_choice_2 || ''}}"`,
                `"${{a.subdept_choice_2 || ''}}"`,
                `"${{a.status_clean_2 || ''}}"`
            ]);

            const csvContent = '\uFEFF' + [headers.join(','), ...rows.map(r => r.join(','))].join('\\n');
            const blob = new Blob([csvContent], {{ type: 'text/csv;charset=utf-8;' }});
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.setAttribute('href', url);
            link.setAttribute('download', 'sgcu_recruitment_anonymized.csv');
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }}

        window.addEventListener('DOMContentLoaded', () => {{
            initDropdowns();
            applyFilters();
        }});
    </script>
</body>
</html>
"""
    return html_template


def export_static_site(output_path: str = "index.html"):
    """Builds and writes the static site to file."""
    payload = build_anonymized_payload()
    data_json_str = json.dumps(payload, ensure_ascii=False)
    html_content = generate_html_content(data_json_str)

    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html_content, encoding="utf-8")
    print(f"[SUCCESS] Static site generated at: {target.resolve()}")


if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "index.html"
    export_static_site(out_file)
