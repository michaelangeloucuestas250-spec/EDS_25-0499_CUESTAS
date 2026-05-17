# Engineering Data Systems Pipeline (EDS) — Topic HVA-01

## 👤 Student Information
* **Name:** Cuestas, Michael Angelou
* **Student Number:** TUPM-25-0499
* **Course:** Computer Programming (Academic Year 2026)
* **Assigned Pillar:** Pillar 9 — HVAC & Building Systems
* **Assigned Topic:** HVA-01 — Chiller Plant COP Variance

---

## 🏗️ Project Overview
This repository implements an automated, production-grade Python data pipeline using an Object-Oriented Programming (OOP) architecture. The software ingests, sanitizes, and evaluates real-world mechanical HVAC operational telemetry to calculate the running **Coefficient of Performance (COP)** and analyze its operational variance. 

To strictly comply with the syllabus **"No Sharing" Rule**, this implementation applies a unique programmatic data slice isolating **October 2019 SCADA observations**, rendering the mathematical results completely unique.

---

## 🗂️ Repository Structure
The repository is strictly structured according to the course engineering standards:
```text
EDS_25-0499_CUESTAS/
├── data/
│   ├── dataset_original.csv      # Raw downloaded Kaggle HVAC data
│   └── dataset_cleaned.csv       # Mathematically unique filtered data slice
├── outputs/
│   ├── static_plot_1_histogram.png
│   ├── static_plot_2_boxplot.png
│   ├── static_plot_3_scatterplot.png
│   └── animation_1_time_progression.html
│   └── animation_2_distribution_shift.html
├── .gitignore
├── main.py                       # Modular automation pipeline script
├── README.md                     # Project documentation
└── requirements.txt              # Pipeline library dependencies
```

---

## ⚙️ Modular Architecture
The core software pipeline inside `main.py` is divided into five distinct operational stages wrapped in a robust execution class:
1. **Data Ingestion Module**: Executes safe system file-reads with integrated `try-except` crash-prevention blocks.
2. **Data Cleaning Module**: Automates time-series forward/backward missing value mitigation and enforces the unique October 2019 chronological filter.
3. **Analytics Module**: Leverages `NumPy` array vectors to compute system metrics including mean, median, standard deviation, and variance profile distributions.
4. **Visualization Module**: Compiles three static validation plots detailing historical COP behaviors against thermal load factors.
5. **Animation Module**: Compiles multi-frame sequence assets capturing transient time-series shifts over operational timelines.

---

## 🚀 Execution & Setup Instructions

### 1. Environment Preparation
Ensure your repository workspace is active in your terminal environment, then batch-install the necessary engineering libraries:
```bash
pip install -r requirements.txt
```

### 2. Dataset Setup
1. Download the target dataset from Kaggle (**HVAC Operational Data / Chiller Energy Data**).
2. Save the target file inside the `data/` subdirectory.
3. Rename the active file exactly to: `dataset_original.csv`.

### 3. Pipeline Execution
Run the execution loop to process data, write metrics, and output graphical assets:
```bash
python main.py
```
