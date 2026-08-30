"""
Data Processing and Cleansing Module for SGCU Recruitment Data (Rounds 1-4).
"""

import os
import glob
import unicodedata
import pandas as pd
import numpy as np
from pathlib import Path


def normalize_text(text) -> str:
    """Normalizes Thai string, strips spaces, and fixes Unicode composition."""
    if pd.isna(text) or text is None:
        return ""
    text = str(text).strip()
    # Normalize NFC
    text = unicodedata.normalize("NFC", text)
    # Normalize sara am
    text = text.replace("\u0e33", "ำ").replace("\u0e4d\u0e32", "ำ")
    # Fix known typos in faculty names
    text = text.replace("พานิชยศาสตร์", "พาณิชยศาสตร์")
    text = text.replace("นวัฒกรรม", "นวัตกรรม")
    # Fix typo in status
    text = text.replace("สัมภาษณฺ์", "สัมภาษณ์")
    # Clean hyphens
    if text in ["-", " - ", "—", "N/A", "nan", "None"]:
        return ""
    return text.strip()


def parse_pass_status(status: str) -> dict:
    """
    Parses a raw status string into structured pass status flags.
    
    Status categories:
    - passed_final: 'ผ่านการคัดเลือก' (or special position offer like 'ไปเป็นประธานฝ่ายสวัสดิการ')
    - passed_form: 'ผ่านการคัดเลือกเฉพาะฟอร์ม'
    - passed_interview: 'ผ่านการคัดเลือกไปสัมภาษณ์'
    - passed_any: True if any of the passed categories is True
    - not_passed: 'ไม่ผ่านการคัดเลือก', 'ไม่ผ่านการคัดเลือกไปสัมภาษณ์'
    - no_data: Candidate not found in result file or empty
    """
    s = normalize_text(status)
    if not s:
        return {
            "status_clean": "ไม่มีข้อมูลในไฟล์ผลลัพธ์",
            "passed_final": False,
            "passed_form": False,
            "passed_interview": False,
            "passed_any": False,
            "is_evaluated": False,
            "status_category": "ไม่มีข้อมูลผลลัพธ์",
        }

    if s.startswith("ไม่ผ่าน"):
        category = "ไม่ผ่านการคัดเลือก" if "สัมภาษณ์" not in s else "ไม่ผ่านไปสัมภาษณ์"
        return {
            "status_clean": s,
            "passed_final": False,
            "passed_form": False,
            "passed_interview": False,
            "passed_any": False,
            "is_evaluated": True,
            "status_category": category,
        }

    is_form = "เฉพาะฟอร์ม" in s
    is_interview = "ไปสัมภาษณ์" in s
    is_final = ("ผ่านการคัดเลือก" in s and not is_form and not is_interview) or ("ไปเป็นประธาน" in s)
    is_any = is_final or is_form or is_interview

    if is_final:
        category = "ผ่านการคัดเลือก (ขั้นสุดท้าย)"
    elif is_interview:
        category = "ผ่านการคัดเลือกไปสัมภาษณ์"
    elif is_form:
        category = "ผ่านการคัดเลือกเฉพาะฟอร์ม"
    else:
        category = s

    return {
        "status_clean": s,
        "passed_final": is_final,
        "passed_form": is_form,
        "passed_interview": is_interview,
        "passed_any": is_any,
        "is_evaluated": True,
        "status_category": category,
    }


def clean_year(year_val) -> str:
    """Standardizes academic year."""
    if pd.isna(year_val):
        return "ไม่ระบุ"
    s = str(year_val).strip()
    s = s.replace(".0", "")
    if s in ["1", "2", "3", "4", "5", "6"]:
        return f"ปี {s}"
    return s if s else "ไม่ระบุ"


def load_raw_data(data_dir: str = "data") -> tuple[dict, dict]:
    """Loads all raw query and result CSV files."""
    data_path = Path(data_dir)
    query_dfs = {}
    result_dfs = {}

    for r in range(1, 5):
        q_file = data_path / f"qry_recruit{r}.csv"
        res_file = data_path / f"filtered_result{r}.csv"

        if q_file.exists():
            query_dfs[r] = pd.read_csv(q_file, dtype=str, encoding="utf-8-sig")
        if res_file.exists():
            result_dfs[r] = pd.read_csv(res_file, dtype=str, encoding="utf-8-sig")

    return query_dfs, result_dfs


def process_all_recruitment_data(data_dir: str = "data") -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Processes and merges recruitment query forms and result files for rounds 1-4.
    
    Returns:
    - df_applicants: 1 row per applicant per round (527 rows)
    - df_choices: Unpivoted table (1 row per choice application, ~717 rows)
    """
    query_dfs, result_dfs = load_raw_data(data_dir)
    applicant_records = []
    choice_records = []

    for round_num in range(1, 5):
        q_df = query_dfs.get(round_num)
        res_df = result_dfs.get(round_num)

        if q_df is None:
            continue

        # Build lookup map for results
        res_map = {}
        if res_df is not None:
            for _, rrow in res_df.iterrows():
                name = normalize_text(rrow.get("ชื่อ-สกุล (ไม่ต้องมีคำนำหน้า)", ""))
                if name:
                    res_map[name] = rrow

        # Column name variants
        d1_col = "ฝ่ายหลักลำดับที่ 1"
        d2_col = "ฝ่ายหลักลำดับที่2" if "ฝ่ายหลักลำดับที่2" in q_df.columns else "ฝ่ายหลักลำดับที่ 2"
        sd1_col = "ฝ่ายย่อยลำดับที่ 1"
        sd2_col = "ฝ่ายย่อยลำดับที่2" if "ฝ่ายย่อยลำดับที่2" in q_df.columns else "ฝ่ายย่อยลำดับที่ 2"

        for _, qrow in q_df.iterrows():
            raw_name = qrow.get("ชื่อ-สกุล (ไม่ต้องมีคำนำหน้า)", "")
            name = normalize_text(raw_name)
            student_id = normalize_text(qrow.get("รหัสนิสิต", ""))
            faculty = normalize_text(qrow.get("คณะ", ""))
            year = clean_year(qrow.get("ชั้นปีการศึกษา", ""))

            # Choice 1
            dept1 = normalize_text(qrow.get(d1_col, ""))
            subdept1 = normalize_text(qrow.get(sd1_col, ""))

            # Choice 2
            dept2 = normalize_text(qrow.get(d2_col, ""))
            subdept2 = normalize_text(qrow.get(sd2_col, ""))

            # Result lookups
            res_row = res_map.get(name)
            raw_status1 = ""
            raw_status2 = ""
            email = ""

            if res_row is not None:
                raw_status1 = str(res_row.get("ผลการสมัครอันดับที่ 1", ""))
                raw_status2 = str(res_row.get("ผลการสมัครอันดับที่ 2", ""))
                email = normalize_text(res_row.get("email", ""))

            st1_info = parse_pass_status(raw_status1)
            st2_info = parse_pass_status(raw_status2)

            passed_any_final = st1_info["passed_final"] or st2_info["passed_final"]
            passed_any_overall = st1_info["passed_any"] or st2_info["passed_any"]
            has_eval = st1_info["is_evaluated"] or st2_info["is_evaluated"]

            record = {
                "round": round_num,
                "round_label": f"รอบที่ {round_num}",
                "name": name,
                "student_id": student_id,
                "faculty": faculty,
                "year": year,
                "email": email,
                "dept_choice_1": dept1,
                "subdept_choice_1": subdept1,
                "status_raw_1": raw_status1,
                "status_clean_1": st1_info["status_clean"],
                "status_cat_1": st1_info["status_category"],
                "passed_final_1": st1_info["passed_final"],
                "passed_form_1": st1_info["passed_form"],
                "passed_interview_1": st1_info["passed_interview"],
                "passed_any_1": st1_info["passed_any"],
                "is_evaluated_1": st1_info["is_evaluated"],
                "dept_choice_2": dept2,
                "subdept_choice_2": subdept2,
                "status_raw_2": raw_status2,
                "status_clean_2": st2_info["status_clean"],
                "status_cat_2": st2_info["status_category"],
                "passed_final_2": st2_info["passed_final"],
                "passed_form_2": st2_info["passed_form"],
                "passed_interview_2": st2_info["passed_interview"],
                "passed_any_2": st2_info["passed_any"],
                "is_evaluated_2": st2_info["is_evaluated"],
                "num_choices": 2 if dept2 else 1,
                "has_evaluation": has_eval,
                "passed_final_any": passed_any_final,
                "passed_overall_any": passed_any_overall,
            }
            applicant_records.append(record)

            # Add to unpivoted choice records
            if dept1:
                choice_records.append({
                    "round": round_num,
                    "round_label": f"รอบที่ {round_num}",
                    "name": name,
                    "student_id": student_id,
                    "faculty": faculty,
                    "year": year,
                    "choice_order": "อันดับ 1",
                    "choice_num": 1,
                    "department": dept1,
                    "subdepartment": subdept1,
                    "status_clean": st1_info["status_clean"],
                    "status_category": st1_info["status_category"],
                    "passed_final": st1_info["passed_final"],
                    "passed_form": st1_info["passed_form"],
                    "passed_interview": st1_info["passed_interview"],
                    "passed_any": st1_info["passed_any"],
                    "is_evaluated": st1_info["is_evaluated"],
                })

            if dept2:
                choice_records.append({
                    "round": round_num,
                    "round_label": f"รอบที่ {round_num}",
                    "name": name,
                    "student_id": student_id,
                    "faculty": faculty,
                    "year": year,
                    "choice_order": "อันดับ 2",
                    "choice_num": 2,
                    "department": dept2,
                    "subdepartment": subdept2,
                    "status_clean": st2_info["status_clean"],
                    "status_category": st2_info["status_category"],
                    "passed_final": st2_info["passed_final"],
                    "passed_form": st2_info["passed_form"],
                    "passed_interview": st2_info["passed_interview"],
                    "passed_any": st2_info["passed_any"],
                    "is_evaluated": st2_info["is_evaluated"],
                })

    df_applicants = pd.DataFrame(applicant_records)
    df_choices = pd.DataFrame(choice_records)

    return df_applicants, df_choices


def export_processed_datasets(data_dir: str = "data", output_dir: str = "data/processed") -> None:
    """Processes and saves unified datasets to disk."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    df_applicants, df_choices = process_all_recruitment_data(data_dir)
    df_applicants.to_csv(out_path / "sgcu_recruitment_all_rounds.csv", index=False, encoding="utf-8-sig")
    df_choices.to_csv(out_path / "sgcu_recruitment_choices.csv", index=False, encoding="utf-8-sig")
    print(f"Successfully exported cleaned datasets to {output_dir}")


if __name__ == "__main__":
    df_applicants, df_choices = process_all_recruitment_data()
    print(f"Total applicants: {len(df_applicants)}")
    print(f"Total choice applications: {len(df_choices)}")
    export_processed_datasets()

