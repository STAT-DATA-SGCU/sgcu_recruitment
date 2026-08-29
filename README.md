# SGCU Recruitment Data Analysis

A comprehensive data analysis project for analyzing recruitment data from SGCU (องค์การบริหารสโมสรนิสิตจุฬาฯ - Chulalongkorn University Student Organization). This project processes, analyzes, and visualizes recruitment form responses to extract insights and statistics.

## Project Overview

This project performs end-to-end analysis of recruitment data including:

- **Data Exploration**: Interactive exploration of recruitment datasets using Marimo notebooks
- **Data Merging**: Combining multiple recruitment data sources into unified datasets
- **Statistical Analysis**: Computing recruitment statistics and key metrics
- **Data Cleaning**: Processing and filtering recruitment responses for analysis-ready datasets
- **Visualization**: Creating interactive visualizations and dashboards

## Directory Structure

```
sgcu_recruitment/
│
├── data/                      # All recruitment data files
│   ├── raw/                   # Original recruitment survey responses
│   │   ├── recruitment_1.csv through recruitment_4.csv
│   │   └── result_1.csv through result_4.csv
│   ├── processed/             # Merged and processed datasets
│   │   ├── query_recruit1.csv through query_recruit4.csv
│   │   └── filtered_result1.csv through filtered_result4.csv
│   └── cleaned/               # Final, analysis-ready datasets
│
├── notebooks/                 # Interactive Marimo notebooks
│   ├── explore_data.py        # Data exploration and profiling
│   ├── merge_table_data.py    # Merging multiple data sources
│   └── statistic_data.py      # Statistical analysis
│
├── scripts/                   # Standalone scripts
│   └── archive/               # Deprecated scripts
│
├── src/                       # Reusable source code
│   ├── data/                  # Data processing utilities
│   ├── features/              # Feature engineering code
│   ├── models/                # Analysis and modeling code
│   └── visualization/         # Visualization utilities
│
├── results/                   # Analysis outputs
│   └── figures/               # Generated charts and visualizations
│
├── models/                    # Model artifacts
│   └── logs/                  # Analysis logs and metrics
│
├── docs/                      # Documentation
├── references/                # Related materials and references
├── reports/                   # Final analysis reports
├── layouts/                   # Marimo notebook layout files
│
├── .gitignore                 # Git configuration
├── requirements.txt           # Python dependencies
├── environment.yml            # Conda environment file
├── LICENSE                    # License information
└── README.md                  # This file
```

## Key Technologies

- **Marimo**: Interactive reactive Python notebooks for data exploration and analysis
- **Data Processing**: Pandas, Polars, NumPy for data manipulation
- **Visualization**: Plotly, Seaborn, Matplotlib for interactive and static visualizations
- **Analytics**: Scikit-learn for statistical analysis and modeling
- **Dashboard**: Dash with Bootstrap components for interactive dashboards
- **Tools**: DuckDB for SQL queries, PyGWalker for visual analytics, YData Profiling for data profiling

## Workflow

### 1. Data Preparation

- Raw recruitment data is stored in `data/raw/`
- Multiple CSV files (recruitment_1-4, result_1-4) are merged using `merge_table_data.py`
- Processed data is saved to `data/processed/`

### 2. Data Exploration

- `explore_data.py` provides interactive exploration of the datasets
- Profiling and quality checks are performed
- Descriptive statistics and distributions are analyzed

### 3. Statistical Analysis

- `statistic_data.py` computes recruitment statistics
- Key metrics and trends are calculated
- Results are exported for reporting

### 4. Visualization & Reporting

- Results are visualized using Plotly and Matplotlib
- Figures are saved to `results/figures/`
- Interactive dashboards can be created using Dash

## Setup & Installation

### Prerequisites

- Python 3.8+
- pip or conda

### Installation Steps

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd sgcu_recruitment
   ```

2. **Create virtual environment** (optional but recommended)

   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Analysis

**To run interactive Marimo notebooks:**

```bash
marimo run notebooks/explore_data.py
marimo run notebooks/merge_table_data.py
marimo run notebooks/statistic_data.py
```

## Data Description

The recruitment data includes responses from multiple recruitment campaigns containing:

- Timestamp information
- Contact details
- PDPA consent information
- Applicant responses and qualifications
- Status and tracking information

## Best Practices in This Project

## Best Practices in This Project

### Data Management

- **Immutable raw data**: Original recruitment data in `data/raw/` is never modified
- **Clear data pipeline**: Raw → Processed → Cleaned stages clearly separate transformation steps
- **Multiple data sources**: Properly handling and merging data from 4 recruitment campaigns
- **Version control**: Data processing steps are documented in notebooks and scripts

### Code Organization

- **Interactive notebooks**: Marimo notebooks provide exploratory analysis with reactive cells
- **Modular structure**: Reusable utilities in `src/` directory organized by function
- **Focused notebooks**: Each notebook addresses a specific analysis step
- **Clear naming**: Descriptive file names indicate data stages (raw, processed, cleaned, filtered, queried)

### Reproducibility

- **Dependency tracking**: `requirements.txt` and `environment.yml` specify exact versions
- **Marimo layouts**: Slide layouts preserve presentation structure across runs
- **Relative paths**: Code uses relative paths for cross-platform compatibility
- **Data documentation**: Processing steps are logged in notebook outputs

## Project Status & Next Steps

Current analysis focuses on:

- ✅ Data loading and exploration
- ✅ Merging multiple recruitment datasets
- ✅ Data cleaning and filtering
- 🔄 Statistical analysis and reporting
- 📊 Visualization and dashboard creation

## Contributing

To contribute to this project:

1. Create a feature branch for your changes
2. Work in the appropriate notebook or script
3. Document your analysis and findings
4. Update this README if adding new analyses or datasets

## License

See LICENSE file for details.

## Contact

For questions about this recruitment analysis project, please contact the project maintainers.

1. Clone this repository
2. Create a virtual environment: `python -m venv env` or `conda env create -f environment.yml`
3. Activate the environment: `source env/bin/activate` or `conda activate environment_name`
4. Install dependencies: `pip install -r requirements.txt`
5. Start your analysis by exploring the data in the notebooks directory

## Contributing

Feel free to fork this repository and submit suggestions or issues through the issues module.

## License

This project is licensed under the terms of the MIT License file included in this repository.
