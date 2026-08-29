import marimo

__generated_with = "0.24.0"
app = marimo.App(
    width="medium",
    layout_file="layouts/explore_data.slides.json",
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## IMPORT SESSION
    """)
    return


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import pandas as pd
    import polars as pl
    import re

    return mo, pd, pl, re


@app.cell
def _():
    import matplotlib.pyplot as plt
    import plotly.express as px
    import plotly.graph_objects as go
    from difflib import SequenceMatcher
    import itertools

    return SequenceMatcher, itertools


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
    return file_dropdown, target_dir


@app.cell
def _(Path, file_dropdown, os, pd, pl):
    selected_file_path = file_dropdown.value

    def load_dataset(file_path: str):
        if not file_path or not os.path.exists(file_path):
            return None

        ext = Path(file_path).suffix.lower()
        if ext in [".csv", ".tsv"]:
            sep = "\t" if ext == ".tsv" else ","
            try:
                return pl.read_csv(file_path, separator=sep, infer_schema_length=None)
            except Exception:
                return pd.read_csv(file_path, separator=sep, dtype=str)
        elif ext == ".parquet":
            return pl.read_parquet(file_path)
        elif ext == ".json":
            return pl.read_json(file_path)
        elif ext in [".xlsx", ".xls"]:
            return pd.read_excel(file_path)
        return None

    df_loaded = load_dataset(selected_file_path)
    return df_loaded, selected_file_path


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## FUNCTION TO INSPECT DATAFRAME
    """)
    return


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
def _(mo, pd, pl):
    def render_column_summary(df):
        """Generates a Marimo UI table summarizing columns for Polars or Pandas DataFrames."""
        if df is None:
            return mo.md("⚠️ *No data loaded yet. Please select a file above.*")

        # Auto-convert Pandas to Polars if necessary
        if isinstance(df, pd.DataFrame):
            df = pl.from_pandas(df)

        if not isinstance(df, pl.DataFrame) or df.is_empty():
            return mo.md("⚠️ *No data loaded yet or DataFrame is empty.*")

        total_rows = max(len(df), 1)

        col_info = pl.DataFrame({
            "Column Name": df.columns,
            "Data Type": [str(dt) for dt in df.dtypes],
            "Null Count": list(df.null_count().row(0)),
        }).with_columns(
            (pl.col("Null Count") / total_rows * 100).round(2).alias("Null %")
        )

        return mo.vstack([
            mo.md(f"### Columns Summary ({len(col_info)} total)"),
            mo.ui.table(col_info),
        ])
    print("How to use : render_column_summary(df)")
    return (render_column_summary,)


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
        "ชื่อเล่น",
        "เบอร์โทร (กรอกเฉพาะตัวเลข)",
        "Line id",
        "โซเชียลมีเดีย/ช่องทางการต่อเพิ่มเติม",
        "1. ประสบการณ์การทำงาน (สามารถอัพโหลดลิ้งก์ผลงานในไดรฟ์/resume)",
        "ช่องทางติดต่อ อื่น ๆ",
        "column_0"
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
    return (df_sanitized,)


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Merging Function for multiple choice response answering

    A Reusable function for solving multiple choices googleform problem
    """)
    return


@app.cell(hide_code=True)
def _(pd, re):
    def merge_all_duplicate_columns(
        df, method: str = "coalesce", sep: str = ", "
    ) -> pd.DataFrame:
        # Safely convert Polars / PyArrow to Pandas if needed
        if hasattr(df, "to_pandas"):
            df = df.to_pandas()
        else:
            df = df.copy()

        col_groups = {}
        for col in df.columns:
            base_name = re.sub(r"_duplicated_\d+$", "", str(col))
            col_groups.setdefault(base_name, []).append(col)

        new_data = {}
        for base_name, cols in col_groups.items():
            if len(cols) == 1:
                new_data[base_name] = df[cols[0]]
            else:
                if method == "coalesce":
                    new_data[base_name] = df[cols].bfill(axis=1).iloc[:, 0]
                elif method == "join":
                    new_data[base_name] = (
                        df[cols]
                        .astype(str)
                        .replace({"nan": None, "None": None, "<NA>": None})
                        .apply(
                            lambda row: sep.join(
                                [val for val in row.dropna() if val.strip()]
                            ),
                            axis=1,
                        )
                    )

        return pd.DataFrame(new_data, index=df.index)
    print("function is ready to use")
    print("for single choice use : clean_df = merge_all_duplicate_columns(df, method='coalesce')")
    print("Multi-Select / Checkbox answers uses : clean_df = merge_all_duplicate_columns(df, method='join', sep=',')")
    return (merge_all_duplicate_columns,)


@app.cell
def _(df_sanitized, merge_all_duplicate_columns, render_column_summary):
    df_filtered = merge_all_duplicate_columns(df_sanitized,method='coalesce')
    render_column_summary(df_filtered)
    return (df_filtered,)


@app.cell
def _(df_filtered):
    df_filtered
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Export function to csv file ###
    """)
    return


@app.cell
def _(df, dir_picker, filename_input, mo, save_btn):
    if save_btn.value:
        target_dir = dir_picker.path() or "."
        final_path = f"{target_dir}/{filename_input.value}"
    
        df.write_csv(final_path)
        mo.md(f"✅ Saved to: `{final_path}`")
    return (target_dir,)


@app.cell
def _(available_dfs, mo):
    # Dropdown to choose which DataFrame to export
    df_select = mo.ui.dropdown(
        options=available_dfs,
        label="Select DataFrame:"
    )

    dir_picker = mo.ui.file_browser(
        initial_path="./data/", 
        selection_mode="directory", 
        multiple=False,
        label="Select Output Directory",
        restrict_navigation=False
    )

    filename_input = mo.ui.text(label="File Name:", value="export.csv")
    save_btn = mo.ui.button(label="Export to CSV")

    mo.vstack([df_select, dir_picker, filename_input, save_btn])
    return df_select, dir_picker, filename_input, save_btn


@app.cell
def _(Path, df_select, dir_picker, filename_input, mo, save_btn, target_dir):

    if save_btn.value:
        selected_df = df_select.value

        if selected_df is None:
            status = mo.md("⚠️ **Please select a DataFrame from the dropdown first.**")
        else:
            # Safely resolve directory (defaults to current directory if unselected)
            try:
                target_directory = dir_picker.path(0) or Path(".")
            except (IndexError, TypeError, AttributeError):
                target_directory = Path(".")

            full_path = Path(target_dir) / filename_input.value

            try:
                full_path.parent.mkdir(parents=True, exist_ok=True)

                # Polars Export
                if hasattr(selected_df, "write_csv"):
                    selected_df.write_csv(full_path)
                # Pandas Export
                elif hasattr(selected_df, "to_csv"):
                    selected_df.to_csv(full_path, index=False)
                else:
                    raise TypeError("Selected object is neither a Polars nor Pandas DataFrame.")

                status = mo.md(f"✅ **Successfully exported to:** `{full_path.resolve()}`")
            except Exception as e:
                status = mo.md(f"❌ **Export failed:** `{e}`")

        status
    return


@app.cell
def _(Path, df_select, export_btn, filename_input, mo, path_input):
    if export_btn.value:
        selected_df = df_select.value

        if selected_df is None:
            status = mo.md("⚠️ **Please select a DataFrame first.**")
        else:
            placeholder_filename = "filtered_data.csv"
            user_filename = filename_input.value.strip()

            # 1. Fallback to placeholder if input is empty
            raw_filename = user_filename if user_filename else placeholder_filename

            # 2. Automatically append .csv extension if missing
            if not raw_filename.lower().endswith(".csv"):
                raw_filename += ".csv"

            # 3. Build full path
            target_path = Path(path_input.value.strip() or "./data/processed/")
        
            if target_path.suffix.lower() == ".csv":
                full_path = target_path
            else:
                full_path = target_path / raw_filename

            try:
                # 4. Ensure parent directory exists
                full_path.parent.mkdir(parents=True, exist_ok=True)

                # 5. Export safely (Supports Polars and Pandas)
                if hasattr(selected_df, "write_csv"):
                    selected_df.write_csv(full_path)
                elif hasattr(selected_df, "to_csv"):
                    selected_df.to_csv(full_path, index=False, encoding="utf-8")

                status = mo.md(f"✅ **Exported successfully to:** `{full_path.resolve()}`")
            except Exception as e:
                status = mo.md(f"❌ **Export failed:** `{e}`")

        status
    return


@app.cell
def _(Path, df_filtered):
    target_path = Path("./data/processed/")
    filename = "processed_recruit4.csv"

    # 1. Resolve path based on file extension
    if target_path.suffix.lower() == ".csv":
        full_path = target_path
    else:
        full_path = target_path / filename

    # 2. Ensure parent directory exists
    full_path.parent.mkdir(parents=True, exist_ok=True)

    # 3. Export safely (supports both Polars and Pandas)
    if hasattr(df_filtered, "write_csv"):
        df_filtered.write_csv(full_path)
    elif hasattr(df_filtered, "to_csv"):
        df_filtered.to_csv(full_path, index=False, encoding="utf-8")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Finding Possible Duplicate Columns
    """)
    return


@app.cell
def _(SequenceMatcher, itertools, pd, re):
    def find_similar_columns(
        df: pd.DataFrame, name_threshold: float = 0.7, check_values: bool = True
    ) -> pd.DataFrame:
        """Detects potential duplicate or similar columns in a Pandas DataFrame.

        Parameters:
        - df: The input Pandas DataFrame.
        - name_threshold: Float (0.0 to 1.0) for fuzzy name matching sensitivity (default 0.7).
        - check_values: If True, compares exact and partial row value matches between columns.

        Returns:
        - pd.DataFrame listing candidate column pairs and their similarity metrics.
        """
        if hasattr(df, "to_pandas"):
            df = df.to_pandas()

        cols = df.columns
        results = []

        for col1, col2 in itertools.combinations(cols, 2):
            s1_str, s2_str = str(col1), str(col2)

            # 1. Name Fuzzy Similarity Ratio (0% to 100%)
            name_sim = SequenceMatcher(None, s1_str, s2_str).ratio()

            # 2. Base Name Comparison (stripping suffixes like _duplicated_1, .1, _copy)
            c1_clean = re.sub(
                r"(_duplicated_\d+|\.\d+|_copy\d*)$", "", s1_str
            ).strip()
            c2_clean = re.sub(
                r"(_duplicated_\d+|\.\d+|_copy\d*)$", "", s2_str
            ).strip()
            same_base = c1_clean.lower() == c2_clean.lower()

            # 3. Value Match Inspection
            exact_value_match = False
            value_overlap_pct = 0.0

            if check_values:
                exact_value_match = df[col1].equals(df[col2])

                # Calculate overlap % on rows where both columns have non-null values
                s1, s2 = df[col1], df[col2]
                valid_mask = s1.notna() & s2.notna()
                if valid_mask.any():
                    value_overlap_pct = (s1[valid_mask] == s2[valid_mask]).mean() * 100

            # Include pair if names are similar, share base names, or share identical values
            if (
                name_sim >= name_threshold
                or same_base
                or exact_value_match
                or value_overlap_pct >= 90.0
            ):
                results.append({
                    "Column A": col1,
                    "Column B": col2,
                    "Name Similarity (%)": round(name_sim * 100, 1),
                    "Same Base Name": same_base,
                    "Exact Value Match": exact_value_match,
                    "Value Overlap (%)": round(value_overlap_pct, 1),
                })

        results_df = pd.DataFrame(results)

        if not results_df.empty:
            results_df = results_df.sort_values(
                by=["Same Base Name", "Exact Value Match", "Name Similarity (%)"],
                ascending=False,
            ).reset_index(drop=True)

        return results_df

    return (find_similar_columns,)


@app.cell
def _(df_filtered, find_similar_columns):
    similar_cols_df = find_similar_columns(df_filtered)
    return (similar_cols_df,)


@app.cell
def _(similar_cols_df):
    similar_cols_df
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
