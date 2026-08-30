"""
Unit and Validation Tests for SGCU Recruitment Pipeline and Analytics.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

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


def test_data_pipeline():
    df_app, df_ch = process_all_recruitment_data("data")
    assert len(df_app) == 527, f"Expected 527 applicants, got {len(df_app)}"
    assert len(df_ch) == 725, f"Expected 725 choice applications, got {len(df_ch)}"
    print("[PASS] test_data_pipeline: 527 applicants, 725 choices validated.")


def test_analytics_metrics():
    df_app, df_ch = process_all_recruitment_data("data")

    # Overall summary
    sum_all = get_overall_summary(df_app, df_ch)
    assert sum_all["total_applications"] == 527
    assert sum_all["unique_applicants"] == 478
    print(f"[PASS] test_analytics_metrics: Overall summary validated: {sum_all}")

    # Year ranking
    df_year = get_ranking_by_year(df_app)
    assert not df_year.empty
    assert "ชั้นปี" in df_year.columns
    assert "จำนวนผู้สมัคร" in df_year.columns
    print(f"[PASS] test_analytics_metrics: Year ranking validated:\n{df_year}")

    # Faculty ranking
    df_fac = get_ranking_by_faculty(df_app)
    assert not df_fac.empty
    assert "คณะ" in df_fac.columns
    assert "คณะพานิชยศาสตร์และการบัญชี" not in df_fac["คณะ"].values  # typo cleaned
    assert "คณะพาณิชยศาสตร์และการบัญชี" in df_fac["คณะ"].values
    print(f"[PASS] test_analytics_metrics: Faculty ranking validated (Top 3):\n{df_fac.head(3)}")

    # Department ranking
    df_dept = get_ranking_by_department(df_ch)
    assert not df_dept.empty
    assert "ฝ่าย" in df_dept.columns
    print(f"[PASS] test_analytics_metrics: Department ranking validated:\n{df_dept[['อันดับ', 'ฝ่าย', 'จำนวนใบสมัคร', 'จำนวนผู้ผ่าน', 'อัตราการผ่าน (%)']]}")

    # Cross round matrix
    df_mat_apps = get_cross_round_department_matrix(df_ch, metric="applications")
    assert not df_mat_apps.empty
    assert "รอบที่ 1" in df_mat_apps.columns
    assert "รอบที่ 4" in df_mat_apps.columns
    print(f"[PASS] test_analytics_metrics: Cross-round applications matrix validated:\n{df_mat_apps.head(4)}")

    # Reapplicant analysis
    df_reapps, stats = get_reapplicant_analysis(df_app)
    assert stats["reapplicants_count"] >= 0
    print(f"[PASS] test_analytics_metrics: Re-applicant tracking validated: {stats}")


if __name__ == "__main__":
    test_data_pipeline()
    test_analytics_metrics()
    print("\n>>> ALL VALIDATION TESTS PASSED SUCCESSFULLY! <<<")
