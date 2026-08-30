"""
Analytics and Aggregation Module for SGCU Recruitment.
Provides metrics, rankings, department comparisons, and cross-round trends.
"""

import pandas as pd
import numpy as np


def get_overall_summary(df_applicants: pd.DataFrame, df_choices: pd.DataFrame, round_filter=None, pass_mode: str = "any") -> dict:
    """Calculates high-level KPI metrics."""
    df_app = df_applicants.copy()
    df_ch = df_choices.copy()

    if round_filter and round_filter != "ทั้งหมด (All Rounds)":
        if isinstance(round_filter, int):
            r_num = round_filter
        else:
            r_num = int(str(round_filter).replace("รอบที่ ", "").strip())
        df_app = df_app[df_app["round"] == r_num]
        df_ch = df_ch[df_ch["round"] == r_num]

    pass_col_app = "passed_overall_any" if pass_mode == "any" else "passed_final_any"
    pass_col_ch = "passed_any" if pass_mode == "any" else "passed_final"

    total_apps = len(df_app)
    unique_applicants = df_app["name"].nunique()
    
    # Applicants with evaluations
    evaluated_apps = int(df_app["has_evaluation"].sum())
    
    # Passed counts
    passed_apps = int(df_app[pass_col_app].sum())
    pass_rate_overall = (passed_apps / total_apps * 100) if total_apps > 0 else 0
    pass_rate_evaluated = (passed_apps / evaluated_apps * 100) if evaluated_apps > 0 else 0

    # Choices stats
    total_choices = len(df_ch)
    dual_choice_count = int((df_app["num_choices"] == 2).sum())
    dual_choice_pct = (dual_choice_count / total_apps * 100) if total_apps > 0 else 0

    return {
        "total_applications": total_apps,
        "unique_applicants": unique_applicants,
        "evaluated_applications": evaluated_apps,
        "passed_applications": passed_apps,
        "pass_rate_overall": round(float(pass_rate_overall), 1),
        "pass_rate_evaluated": round(float(pass_rate_evaluated), 1),
        "total_choices": total_choices,
        "dual_choice_count": dual_choice_count,
        "dual_choice_pct": round(float(dual_choice_pct), 1),
        "num_faculties": int(df_app["faculty"].nunique()),
        "num_departments": int(df_ch["department"].nunique()),
    }


def get_ranking_by_year(df_applicants: pd.DataFrame, round_filter=None, pass_mode: str = "any") -> pd.DataFrame:
    """Ranks and aggregates applicant statistics by Academic Year."""
    df = df_applicants.copy()
    if round_filter and round_filter != "ทั้งหมด (All Rounds)":
        r_num = round_filter if isinstance(round_filter, int) else int(str(round_filter).replace("รอบที่ ", "").strip())
        df = df[df["round"] == r_num]

    pass_col = "passed_overall_any" if pass_mode == "any" else "passed_final_any"

    agg_dict = {
        "จำนวนผู้สมัคร": ("name", "count"),
        "จำนวนผู้มีผลประเมิน": ("has_evaluation", "sum"),
        "จำนวนผู้ผ่าน": (pass_col, "sum"),
    }
    grouped = df.groupby("year", as_index=False).agg(**agg_dict)

    grouped["อัตราการผ่าน (%)"] = (grouped["จำนวนผู้ผ่าน"] / grouped["จำนวนผู้สมัคร"] * 100).round(1)
    grouped["สัดส่วนผู้สมัคร (%)"] = (grouped["จำนวนผู้สมัคร"] / grouped["จำนวนผู้สมัคร"].sum() * 100).round(1)

    # Sort logically by Year if possible
    def year_sort_key(y):
        y_str = str(y)
        digits = "".join(c for c in y_str if c.isdigit())
        return int(digits) if digits else 999

    grouped["sort_order"] = grouped["year"].apply(year_sort_key)
    grouped = grouped.sort_values(by="sort_order").drop(columns=["sort_order"]).reset_index(drop=True)
    grouped.rename(columns={"year": "ชั้นปี"}, inplace=True)
    return grouped


def get_ranking_by_faculty(df_applicants: pd.DataFrame, round_filter=None, pass_mode: str = "any") -> pd.DataFrame:
    """Ranks and aggregates applicant statistics by Faculty."""
    df = df_applicants.copy()
    if round_filter and round_filter != "ทั้งหมด (All Rounds)":
        r_num = round_filter if isinstance(round_filter, int) else int(str(round_filter).replace("รอบที่ ", "").strip())
        df = df[df["round"] == r_num]

    pass_col = "passed_overall_any" if pass_mode == "any" else "passed_final_any"

    agg_dict = {
        "จำนวนผู้สมัคร": ("name", "count"),
        "จำนวนผู้มีผลประเมิน": ("has_evaluation", "sum"),
        "จำนวนผู้ผ่าน": (pass_col, "sum"),
    }
    grouped = df.groupby("faculty", as_index=False).agg(**agg_dict)

    grouped["อัตราการผ่าน (%)"] = (grouped["จำนวนผู้ผ่าน"] / grouped["จำนวนผู้สมัคร"] * 100).round(1)
    grouped["สัดส่วนผู้สมัคร (%)"] = (grouped["จำนวนผู้สมัคร"] / grouped["จำนวนผู้สมัคร"].sum() * 100).round(1)
    grouped = grouped.sort_values(by="จำนวนผู้สมัคร", ascending=False).reset_index(drop=True)
    grouped.rename(columns={"faculty": "คณะ"}, inplace=True)
    grouped.index = grouped.index + 1
    grouped.reset_index(inplace=True)
    grouped.rename(columns={"index": "อันดับ"}, inplace=True)
    return grouped


def get_ranking_by_department(df_choices: pd.DataFrame, round_filter=None, choice_filter=None, pass_mode: str = "any") -> pd.DataFrame:
    """Ranks departments by number of choice applications and compares pass rates."""
    df = df_choices.copy()
    if round_filter and round_filter != "ทั้งหมด (All Rounds)":
        r_num = round_filter if isinstance(round_filter, int) else int(str(round_filter).replace("รอบที่ ", "").strip())
        df = df[df["round"] == r_num]

    if choice_filter and choice_filter != "รวมทุกอันดับ":
        df = df[df["choice_order"] == choice_filter]

    pass_col = "passed_any" if pass_mode == "any" else "passed_final"

    # Add helper binary columns
    df["is_choice_1"] = (df["choice_order"] == "อันดับ 1").astype(int)
    df["is_choice_2"] = (df["choice_order"] == "อันดับ 2").astype(int)

    agg_dict = {
        "จำนวนใบสมัคร": ("name", "count"),
        "จำนวนอันดับ_1": ("is_choice_1", "sum"),
        "จำนวนอันดับ_2": ("is_choice_2", "sum"),
        "จำนวนผู้มีผลประเมิน": ("is_evaluated", "sum"),
        "จำนวนผู้ผ่าน": (pass_col, "sum"),
    }
    grouped = df.groupby("department", as_index=False).agg(**agg_dict)

    grouped["อัตราการผ่าน (%)"] = (grouped["จำนวนผู้ผ่าน"] / grouped["จำนวนใบสมัคร"] * 100).round(1)
    grouped["อัตราการผ่านจากผู้ที่ประเมิน (%)"] = (
        np.where(grouped["จำนวนผู้มีผลประเมิน"] > 0, 
                 (grouped["จำนวนผู้ผ่าน"] / grouped["จำนวนผู้มีผลประเมิน"] * 100).round(1), 
                 0.0)
    )
    grouped["สัดส่วนใบสมัคร (%)"] = (grouped["จำนวนใบสมัคร"] / grouped["จำนวนใบสมัคร"].sum() * 100).round(1)
    grouped = grouped.sort_values(by="จำนวนใบสมัคร", ascending=False).reset_index(drop=True)
    grouped.rename(columns={
        "department": "ฝ่าย",
        "จำนวนอันดับ_1": "เลือกอันดับ 1",
        "จำนวนอันดับ_2": "เลือกอันดับ 2",
    }, inplace=True)
    grouped.index = grouped.index + 1
    grouped.reset_index(inplace=True)
    grouped.rename(columns={"index": "อันดับ"}, inplace=True)
    return grouped


def get_subdepartment_breakdown(df_choices: pd.DataFrame, dept_name: str = None, round_filter=None, pass_mode: str = "any") -> pd.DataFrame:
    """Breakdown of subdepartments/roles within a department or across all departments."""
    df = df_choices.copy()
    if round_filter and round_filter != "ทั้งหมด (All Rounds)":
        r_num = round_filter if isinstance(round_filter, int) else int(str(round_filter).replace("รอบที่ ", "").strip())
        df = df[df["round"] == r_num]

    if dept_name and dept_name != "ทุกฝ่าย":
        df = df[df["department"] == dept_name]

    pass_col = "passed_any" if pass_mode == "any" else "passed_final"

    df["is_choice_1"] = (df["choice_order"] == "อันดับ 1").astype(int)
    df["is_choice_2"] = (df["choice_order"] == "อันดับ 2").astype(int)

    agg_dict = {
        "จำนวนใบสมัคร": ("name", "count"),
        "จำนวนอันดับ_1": ("is_choice_1", "sum"),
        "จำนวนอันดับ_2": ("is_choice_2", "sum"),
        "จำนวนผู้ผ่าน": (pass_col, "sum"),
    }
    grouped = df.groupby(["department", "subdepartment"], as_index=False).agg(**agg_dict)

    grouped["อัตราการผ่าน (%)"] = (grouped["จำนวนผู้ผ่าน"] / grouped["จำนวนใบสมัคร"] * 100).round(1)
    grouped = grouped.sort_values(by="จำนวนใบสมัคร", ascending=False).reset_index(drop=True)
    grouped.rename(columns={
        "department": "ฝ่ายหลัก",
        "subdepartment": "ฝ่ายย่อย/ตำแหน่ง",
        "จำนวนอันดับ_1": "เลือกอันดับ 1",
        "จำนวนอันดับ_2": "เลือกอันดับ 2",
    }, inplace=True)
    return grouped


def get_cross_round_department_matrix(df_choices: pd.DataFrame, metric: str = "applications", pass_mode: str = "any") -> pd.DataFrame:
    """
    Creates a cross-round matrix (Pivot Table) comparing rounds 1 to 4 for all departments.
    metric: 'applications' (จำนวนสมัคร), 'passed' (จำนวนผ่าน), 'pass_rate' (อัตราการผ่าน %)
    """
    df = df_choices.copy()
    pass_col = "passed_any" if pass_mode == "any" else "passed_final"

    pivots = []
    for r in range(1, 5):
        rdf = df[df["round"] == r]
        if rdf.empty:
            grp = pd.DataFrame({"department": sorted(df["department"].unique()), f"รอบ {r}_สมัคร": 0, f"รอบ {r}_ผ่าน": 0, f"รอบ {r}_อัตราผ่าน": 0.0})
        else:
            agg_dict = {
                "apps": ("name", "count"),
                "passed": (pass_col, "sum"),
            }
            grp = rdf.groupby("department", as_index=False).agg(**agg_dict)
            grp[f"รอบ {r}_สมัคร"] = grp["apps"]
            grp[f"รอบ {r}_ผ่าน"] = grp["passed"]
            grp[f"รอบ {r}_อัตราผ่าน"] = (grp["passed"] / grp["apps"] * 100).round(1)
        pivots.append(grp[["department", f"รอบ {r}_สมัคร", f"รอบ {r}_ผ่าน", f"รอบ {r}_อัตราผ่าน"]])

    # Merge all 4 rounds
    all_depts = pd.DataFrame({"department": sorted(df["department"].unique())})
    for p in pivots:
        all_depts = all_depts.merge(p, on="department", how="left")

    all_depts.fillna(0, inplace=True)

    if metric == "applications":
        cols = ["department", "รอบ 1_สมัคร", "รอบ 2_สมัคร", "รอบ 3_สมัคร", "รอบ 4_สมัคร"]
        res = all_depts[cols].copy()
        res["รวม 4 รอบ"] = res[["รอบ 1_สมัคร", "รอบ 2_สมัคร", "รอบ 3_สมัคร", "รอบ 4_สมัคร"]].sum(axis=1)
        res = res.sort_values(by="รวม 4 รอบ", ascending=False).reset_index(drop=True)
        res.rename(columns={"department": "ฝ่าย", "รอบ 1_สมัคร": "รอบที่ 1", "รอบ 2_สมัคร": "รอบที่ 2", "รอบ 3_สมัคร": "รอบที่ 3", "รอบ 4_สมัคร": "รอบที่ 4"}, inplace=True)
        return res

    elif metric == "passed":
        cols = ["department", "รอบ 1_ผ่าน", "รอบ 2_ผ่าน", "รอบ 3_ผ่าน", "รอบ 4_ผ่าน"]
        res = all_depts[cols].copy()
        res["รวมผ่าน 4 รอบ"] = res[["รอบ 1_ผ่าน", "รอบ 2_ผ่าน", "รอบ 3_ผ่าน", "รอบ 4_ผ่าน"]].sum(axis=1)
        res = res.sort_values(by="รวมผ่าน 4 รอบ", ascending=False).reset_index(drop=True)
        res.rename(columns={"department": "ฝ่าย", "รอบ 1_ผ่าน": "รอบที่ 1", "รอบ 2_ผ่าน": "รอบที่ 2", "รอบ 3_ผ่าน": "รอบที่ 3", "รอบ 4_ผ่าน": "รอบที่ 4"}, inplace=True)
        return res

    elif metric == "pass_rate":
        cols = ["department", "รอบ 1_อัตราผ่าน", "รอบ 2_อัตราผ่าน", "รอบ 3_อัตราผ่าน", "รอบ 4_อัตราผ่าน"]
        res = all_depts[cols].copy()
        total_apps = all_depts[["รอบ 1_สมัคร", "รอบ 2_สมัคร", "รอบ 3_สมัคร", "รอบ 4_สมัคร"]].sum(axis=1)
        total_pass = all_depts[["รอบ 1_ผ่าน", "รอบ 2_ผ่าน", "รอบ 3_ผ่าน", "รอบ 4_ผ่าน"]].sum(axis=1)
        res["อัตราผ่านรวม (%)"] = np.where(total_apps > 0, (total_pass / total_apps * 100).round(1), 0.0)
        res = res.sort_values(by="อัตราผ่านรวม (%)", ascending=False).reset_index(drop=True)
        res.rename(columns={"department": "ฝ่าย", "รอบ 1_อัตราผ่าน": "รอบที่ 1 (%)", "รอบ 2_อัตราผ่าน": "รอบที่ 2 (%)", "รอบ 3_อัตราผ่าน": "รอบที่ 3 (%)", "รอบ 4_อัตราผ่าน": "รอบที่ 4 (%)"}, inplace=True)
        return res

    return all_depts


def get_reapplicant_analysis(df_applicants: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Finds candidates who applied in more than one round."""
    name_counts = df_applicants.groupby("name").agg(
        rounds_applied=("round", lambda r: sorted(list(set(r)))),
        num_rounds=("round", "nunique"),
        faculty=("faculty", "first"),
        student_id=("student_id", "first"),
        passed_any=("passed_overall_any", "any"),
    ).reset_index()

    reapplicants = name_counts[name_counts["num_rounds"] > 1].copy()
    reapplicants["rounds_applied_str"] = reapplicants["rounds_applied"].apply(lambda r: ", ".join([f"รอบ {x}" for x in r]))
    reapplicants = reapplicants.sort_values(by="num_rounds", ascending=False).reset_index(drop=True)

    stats = {
        "total_unique_people": len(name_counts),
        "reapplicants_count": len(reapplicants),
        "reapplicants_pct": round(len(reapplicants) / len(name_counts) * 100, 1),
        "applied_2_rounds": int((name_counts["num_rounds"] == 2).sum()),
        "applied_3_rounds": int((name_counts["num_rounds"] == 3).sum()),
        "applied_4_rounds": int((name_counts["num_rounds"] == 4).sum()),
    }

    reapplicants.rename(columns={
        "name": "ชื่อ-สกุล",
        "student_id": "รหัสนิสิต",
        "faculty": "คณะ",
        "num_rounds": "จำนวนรอบที่สมัคร",
        "rounds_applied_str": "รอบที่สมัคร",
        "passed_any": "เคยผ่านการคัดเลือก",
    }, inplace=True)

    return reapplicants[["ชื่อ-สกุล", "รหัสนิสิต", "คณะ", "จำนวนรอบที่สมัคร", "รอบที่สมัคร", "เคยผ่านการคัดเลือก"]], stats

