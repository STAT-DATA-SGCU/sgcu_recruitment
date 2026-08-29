import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import pandas as pd
    import polars as pl

    return mo, pd, pl


@app.cell
def _():
    import matplotlib.pyplot as plt
    import plotly.express as px
    import plotly.graph_objects as go

    return


@app.cell
def _(mo):
    mo.md(r"""
    # Project Notebook

    Standard data science environment initialized with **Pandas**, **Polars**, **NumPy**, **Altair**, **Plotly**, and **Matplotlib**.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Read Files from Directory

    Specify a directory path to scan for data files (`.csv`, `.parquet`, `.json`, `.xlsx`) and load them into DataFrames.
    """)
    return


@app.cell
def _(mo):
    import os
    from pathlib import Path

    dir_input = mo.ui.text(
        value=".",
        label="Directory path:",
        placeholder="e.g. ./data or /path/to/files"
    )
    dir_input
    return Path, dir_input, os


@app.cell
def _(Path, dir_input, mo):
    target_dir = Path(dir_input.value)
    valid_extensions = {".csv", ".parquet", ".json", ".xlsx", ".xls", ".tsv"}

    if target_dir.exists() and target_dir.is_dir():
        matched_files = sorted([
            str(f) for f in target_dir.glob("**/*")
            if f.suffix.lower() in valid_extensions and f.is_file()
        ])
    else:
        matched_files = []

    file_dropdown = mo.ui.dropdown(
        options=matched_files,
        value=matched_files[0] if matched_files else None,
        label="Select a data file to load:"
    )
    file_dropdown
    return (file_dropdown,)


@app.cell
def _(Path, file_dropdown, os, pd, pl):
    selected_file_path = file_dropdown.value

    def load_dataset(file_path: str):
        if not file_path or not os.path.exists(file_path):
            return None
    
        ext = Path(file_path).suffix.lower()
        if ext in [".csv", ".tsv"]:
            sep = "\t" if ext == ".tsv" else ","
            return pl.read_csv(file_path, separator=sep)
        elif ext == ".parquet":
            return pl.read_parquet(file_path)
        elif ext == ".json":
            return pl.read_json(file_path)
        elif ext in [".xlsx", ".xls"]:
            return pd.read_excel(file_path)
        return None

    df_loaded = load_dataset(selected_file_path)
    return df_loaded, selected_file_path


@app.cell
def _(df_loaded, mo, pd, selected_file_path):
    if df_loaded is not None:
        display_content = mo.vstack([
            mo.md(f"### Loaded: `{selected_file_path}`"),
            mo.md(f"**Shape:** `{df_loaded.shape[0]}` rows × `{df_loaded.shape[1]}` columns"),
            mo.ui.table(df_loaded.head(100) if isinstance(df_loaded, pd.DataFrame) else df_loaded.head(100).to_pandas())
        ])
    else:
        display_content = mo.md("⚠️ *No valid data file selected or found in directory.*")

    display_content
    return


@app.cell
def _(df_loaded, mo, pd, pl):
    if df_loaded is not None:
        if isinstance(df_loaded, pl.DataFrame):
            _col_info = pd.DataFrame({
                "Column Name": df_loaded.columns,
                "Data Type": [str(dt) for dt in df_loaded.dtypes],
                "Null Count": [df_loaded[col].null_count() for col in df_loaded.columns],
                "Null %": [round(df_loaded[col].null_count() / max(len(df_loaded), 1) * 100, 2) for col in df_loaded.columns]
            })
        else:
            _col_info = pd.DataFrame({
                "Column Name": list(df_loaded.columns),
                "Data Type": [str(dt) for dt in df_loaded.dtypes],
                "Null Count": [df_loaded[col].isna().sum() for col in df_loaded.columns],
                "Null %": [round(df_loaded[col].isna().sum() / max(len(df_loaded), 1) * 100, 2) for col in df_loaded.columns]
            })
        column_summary_view = mo.vstack([
            mo.md(f"### Columns Summary ({len(_col_info)} total)"),
            mo.ui.table(_col_info)
        ])
    else:
        column_summary_view = mo.md("⚠️ *No data loaded yet. Please select a file above.*")

    column_summary_view
    return


@app.cell
def _():
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## PDPA & Privacy Column Filter

    Functionality to filter out or isolate sensitive personal data (PII) columns according to PDPA guidelines.
    """)
    return


@app.cell
def _(pd, pl):
    DEFAULT_PRIVACY_COLUMNS = [
        "ประทับเวลา",
        "ที่อยู่อีเมล",
        "ตามที่พระราชบัญญัติคุ้มครองข้อมูลส่วนบุคคล พ.ศ. 2562 (Personal Data Protection Act: PDPA) ได้ระบุให้องค์กรต่าง ๆ แจ้งวัตถุประสงค์ของการเก็บรวบรวม ใช้ หรือเปิดเผยข้อมูลส่วนบุคคล เพื่อขอความยินยอมจากเจ้าของข้อมูลส่วนบุคคลก่อนดำเนินการเก็บข้อมูลนั้น\n\nในการรับสมัครผู้ปฏิบัติงานครั้งนี้ องค์การบริหารสโมสรนิสิตจุฬาฯ ซึ่งเป็นผู้ควบคุมข้อมูลส่วนบุคคล จึงใคร่ขอความยินยอมจากท่านซึ่งเป็นเจ้าของข้อมูลส่วนบุคคล ในการเก็บข้อมูลดังต่อไปนี้\n     1. ข้อมูลส่วนบุคคลเบื้องต้น\n     2. ข้อมูล ภาพ เสียง และภาพเคลื่อนไหว จากการบันทึกวิดีโอระหว่างการสัมภาษณ์ หรือ บันทึกวิดีโอทดแทนการสัมภาษณ์\n\nทั้งนี้ การเก็บข้อมูลครั้งนี้มีวัตถุประสงค์เพื่อใช้ในการคัดเลือกผู้ปฎิบัติงานขององค์การบริหารสโมสรนิสิตจุฬาฯเท่านั้น จะไม่มีการเปิดเผยข้อมูลออกไปให้ผู้ใด นอกจากคณะกรรมการพิจารณารับผู้ปฏิบัติงาน \n\nหากท่านพบว่ามีการใช้ข้อมูลไม่ตรงตามวัตถุประสงค์ สามารถแจ้งขอให้ดำเนินการลบข้อมูลของท่านได้ตามสิทธิที่ระบุไว้ในพระราชบัญญัติคุ้มครองข้อมูลส่วนบุคคล พ.ศ. 2562 ",
        "ชื่อ-สกุล (ไม่ต้องมีคำนำหน้า)",
        "ชื่อเล่น",
        "เบอร์โทร (กรอกเฉพาะตัวเลข)",
        "Line id",
        "โซเชียลมีเดีย/ช่องทางการต่อเพิ่มเติม",
        "Privacy Filter Output PreviewResult Shape: 146 rows × 522 columns"
    ]

    def filter_privacy_columns(
        df: pd.DataFrame | pl.DataFrame, 
        privacy_columns: list[str] = None, 
        action: str = "drop", 
        exact_match: bool = False
    ):
        """
        Filters out or selects critical privacy columns from a DataFrame (Polars or Pandas).
    
        Parameters:
        - df: The input Pandas or Polars DataFrame.
        - privacy_columns: List of column names considered critical privacy columns.
        - action: 'drop' to remove privacy columns (anonymize), 
                  'keep' to extract only privacy columns, 
                  'mask' to redact privacy column values with '***REDACTED***'.
        - exact_match: If True, matches column names exactly. If False, checks if any key phrase exists in column name.
    
        Returns:
        - Processed DataFrame of the same type as input.
        """
        if df is None:
            return None

        if privacy_columns is None:
            privacy_columns = DEFAULT_PRIVACY_COLUMNS

        df_cols = list(df.columns)
    
        if exact_match:
            target_cols = [c for c in df_cols if c in privacy_columns]
        else:
            # Match if column name matches exactly or contains privacy column keywords
            keywords = [c.strip() for c in privacy_columns if c.strip()]
            target_cols = [
                c for c in df_cols 
                if any(kw == c or (len(kw) > 5 and kw in c) or (c in kw and len(c) > 5) for kw in keywords)
            ]

        if isinstance(df, pl.DataFrame):
            if action == "drop":
                return df.drop([c for c in target_cols if c in df.columns])
            elif action == "keep":
                return df.select([c for c in target_cols if c in df.columns])
            elif action == "mask":
                expressions = [
                    pl.lit("***REDACTED***").alias(c) if c in target_cols else pl.col(c)
                    for c in df.columns
                ]
                return df.select(expressions)
        else:
            df_copy = df.copy()
            if action == "drop":
                return df_copy.drop(columns=[c for c in target_cols if c in df_copy.columns])
            elif action == "keep":
                return df_copy[[c for c in target_cols if c in df_copy.columns]]
            elif action == "mask":
                for c in target_cols:
                    if c in df_copy.columns:
                        df_copy[c] = "***REDACTED***"
                return df_copy

        return df

    return (filter_privacy_columns,)


@app.cell
def _(mo):
    privacy_action_radio = mo.ui.radio(
        options=["drop", "mask", "keep"],
        value="drop",
        label="Select Privacy Action:"
    )
    privacy_action_radio
    return (privacy_action_radio,)


@app.cell
def _(df_loaded, filter_privacy_columns, mo, pd, privacy_action_radio):
    if df_loaded is not None:
        df_sanitized = filter_privacy_columns(df_loaded, action=privacy_action_radio.value)
        privacy_view = mo.vstack([
            mo.md("### Privacy Filter Output Preview"),
            mo.md(f"**Result Shape:** `{df_sanitized.shape[0]}` rows × `{df_sanitized.shape[1]}` columns"),
            mo.ui.table(df_sanitized.head(100) if isinstance(df_sanitized, pd.DataFrame) else df_sanitized.head(100).to_pandas())
        ])
    else:
        privacy_view = mo.md("💡 *Load a data file above to demonstrate privacy filtering.*")

    privacy_view
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
