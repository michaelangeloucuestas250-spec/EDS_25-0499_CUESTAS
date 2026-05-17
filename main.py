import os
import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

class ChillerDataPipeline:
    def __init__(self, input_path="data/dataset_original.csv", output_dir="outputs"):
        """Initialize the pipeline paths and ensure output directories exist."""
        self.input_path = input_path
        self.output_dir = output_dir
        self.raw_data = None
        self.cleaned_data = None
        self.analytics_results = {}
        
        # Ensure output and data folders exist
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs("data", exist_ok=True)

    def ingest_data(self):
        """Stage 1: Ingest the raw HVAC CSV data safely with error handling."""
        print("====== STAGE 1: DATA INGESTION ======")
        try:
            self.raw_data = pd.read_csv(self.input_path, parse_dates=True, index_col=0)
            print(f"[SUCCESS] Data loaded successfully. Shape: {self.raw_data.shape}")
            return True
        except FileNotFoundError:
            print(f"[ERROR] '{self.input_path}' not found! Please check your directory structure.")
            return False
        except Exception as e:
            print(f"[ERROR] Failed to read data: {str(e)}")
            return False

    def clean_and_filter(self):
        """Stage 2: Clean data and apply a unique filter slice to obey the 'No Sharing' rule."""
        print("\n====== STAGE 2: DATA CLEANING & UNIQUE FILTERING ======")
        try:
            df = self.raw_data.drop_duplicates()
            
            if not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index)
                
            if df.isnull().sum().sum() > 0:
                print(f"[INFO] Found {df.isnull().sum().sum()} null values. Applying forward fill.")
                df = df.ffill().bfill()
            
            # UNIQUE FILTER LOGIC: October 2019 data slice
            print("[INFO] Applying unique programmatic filter: Selecting October 2019 data slice.")
            self.cleaned_data = df.loc['2019-10-01':'2019-10-31'].copy()
            
            cleaned_path = "data/dataset_cleaned.csv"
            self.cleaned_data.to_csv(cleaned_path)
            print(f"[SUCCESS] Isolated {len(self.cleaned_data)} unique records. Saved to '{cleaned_path}'.")
            return True
        except Exception as e:
            print(f"[ERROR] Cleaning failed: {str(e)}")
            return False

    def compute_cop_and_analytics(self):
        """Stage 3: Calculate COP using thermodynamic properties and run NumPy statistics."""
        print("\n====== STAGE 3: ENGINEERING DATA ANALYTICS ======")
        try:
            df = self.cleaned_data
            
            load_col = [c for c in df.columns if 'Load' in c or 'RT' in c][0]
            energy_col = [c for c in df.columns if 'Energy' in c or 'Consumption' in c or 'kWh' in c][0]
            
            # 1 RT = 3.517 kW of thermal cooling capacity. 
            cooling_energy_kwh = df[load_col].to_numpy() * 3.517 * 0.5
            electrical_input_kwh = df[energy_col].to_numpy()
            
            electrical_input_kwh = np.where(electrical_input_kwh == 0, 1e-5, electrical_input_kwh)
            
            df['COP'] = cooling_energy_kwh / electrical_input_kwh
            cop_array = df['COP'].to_numpy()
            
            # --- NUMPY STATISTICAL COMPUTATIONS ---
            self.analytics_results['mean'] = np.mean(cop_array)
            self.analytics_results['median'] = np.median(cop_array)
            self.analytics_results['std_dev'] = np.std(cop_array)
            self.analytics_results['variance'] = np.var(cop_array)
            self.analytics_results['skewness'] = stats.skew(cop_array)
            
            peak_mask = (df.index.hour >= 10) & (df.index.hour <= 16)
            off_peak_mask = (df.index.hour >= 22) | (df.index.hour <= 4)
            
            self.analytics_results['peak_mean_cop'] = np.mean(cop_array[peak_mask])
            self.analytics_results['off_peak_mean_cop'] = np.mean(cop_array[off_peak_mask])
            
            print(f"Calculated System Metrics for Chiller Plant COP:")
            print(f"  • Mean COP:         {self.analytics_results['mean']:.4f}")
            print(f"  • Median COP:       {self.analytics_results['median']:.4f}")
            print(f"  • Std Deviation:    {self.analytics_results['std_dev']:.4f}")
            print(f"  • COP Variance:     {self.analytics_results['variance']:.4f}")
            print(f"  • Skewness Metric:  {self.analytics_results['skewness']:.4f}")
            print(f"  • Peak Hours Mean:  {self.analytics_results['peak_mean_cop']:.4f}")
            print(f"  • Off-Peak Mean:    {self.analytics_results['off_peak_mean_cop']:.4f}")
            
            return True
        except Exception as e:
            print(f"[ERROR] Analytics failed: {str(e)}")
            return False

    def generate_static_plots(self):
        """Stage 4: Create the 3 mandatory engineering static plots."""
        print("\n====== STAGE 4: GENERATING STATIC GRAPHICS ======")
        try:
            df = self.cleaned_data
            
            # Plot 1: Histogram
            plt.figure(figsize=(6, 4))
            plt.hist(df['COP'], bins=30, color='royalblue', edgecolor='black', alpha=0.7)
            plt.title('Distribution Profile of Chiller Plant COP')
            plt.xlabel('Coefficient of Performance (COP)')
            plt.ylabel('Frequency Count')
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.savefig(f"{self.output_dir}/static_plot_1_histogram.png", bbox_inches='tight')
            plt.close()

            # Plot 2: Boxplot
            plt.figure(figsize=(6, 4))
            df['Period'] = 'Normal'
            df.loc[(df.index.hour >= 10) & (df.index.hour <= 16), 'Period'] = 'Peak Demand'
            df.loc[(df.index.hour >= 22) | (df.index.hour <= 4), 'Period'] = 'Off-Peak Night'
            df.boxplot(column='COP', by='Period', grid=False, patch_artist=True)
            plt.title('COP Variance Profile across Operational Shifts')
            plt.suptitle('') 
            plt.ylabel('COP Value')
            plt.savefig(f"{self.output_dir}/static_plot_2_boxplot.png", bbox_inches='tight')
            plt.close()

            # Plot 3: Scatter plot
            temp_col = [c for c in df.columns if 'Temp' in c or 'Dew' in c or 'Hum' in c][0]
            plt.figure(figsize=(6, 4))
            plt.scatter(df[temp_col], df['COP'], alpha=0.4, color='darkorange', edgecolor='none')
            plt.title('Chiller COP Efficiency vs Outside Thermal Load')
            plt.xlabel(f'Ambient Climate Variable ({temp_col})')
            plt.ylabel('Resulting COP')
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.savefig(f"{self.output_dir}/static_plot_3_scatterplot.png", bbox_inches='tight')
            plt.close()

            print("[SUCCESS] All 3 static graphs generated successfully.")
            return True
        except Exception as e:
            print(f"[ERROR] Static plotting failed: {str(e)}")
            return False

    def generate_animations(self):
        """Stage 5: Create 2 interactive, animated charts stored safely as HTML formats."""
        print("\n====== STAGE 5: GENERATING SYSTEM ANIMATIONS ======")
        try:
            # Prepare an incremental timeline framework for dynamic animations
            df_slice = self.cleaned_data.head(60).copy().reset_index()
            df_slice['Frame'] = df_slice.index
            
            # --- ANIMATION 1: COP Time-Series Progression (HTML) ---
            print("[INFO] Building Animation 1 HTML interactive timeline...")
            
            # Form an incremental frame expansion dataset
            expanded_records = []
            for i in range(1, len(df_slice) + 1):
                temp_subset = df_slice.head(i).copy()
                temp_subset['Frame_ID'] = i
                expanded_records.append(temp_subset)
            
            df_anim1 = pd.concat(expanded_records)
            
            fig1 = px.line(
                df_anim1, 
                x='Frame', 
                y='COP', 
                animation_frame='Frame_ID',
                title='Real-time Chiller COP Progression Map',
                labels={'Frame': 'Operational Step Intervals', 'COP': 'Calculated Coefficient of Performance'},
                range_x=[0, len(df_slice)],
                range_y=[float(df_slice['COP'].min() - 0.5), float(df_slice['COP'].max() + 0.5)]
            )
            fig1.write_html(f"{self.output_dir}/animation_1_time_progression.html")

            # --- ANIMATION 2: Expanding Distribution Profile (HTML) ---
            print("[INFO] Building Animation 2 HTML interactive density profile...")
            fig2 = px.histogram(
                df_anim1, 
                x='COP', 
                animation_frame='Frame_ID',
                title='Expanding Operational Distribution Profile Spectrum',
                labels={'COP': 'COP Spectrum Bounds'},
                range_x=[float(df_slice['COP'].min() - 0.5), float(df_slice['COP'].max() + 0.5)],
                range_y=[0, 15]
            )
            fig2.write_html(f"{self.output_dir}/animation_2_distribution_shift.html")

            print("[SUCCESS] Interactive HTML validation assets created without corruption.")
            return True
        except Exception as e:
            print(f"[ERROR] Animation build failed: {str(e)}")
            return False

if __name__ == "__main__":
    pipeline = ChillerDataPipeline()
    if pipeline.ingest_data():
        if pipeline.clean_and_filter():
            if pipeline.compute_cop_and_analytics():
                pipeline.generate_static_plots()
                pipeline.generate_animations()
                print("\n=======================================================")
                print("[COMPLETE] Data Pipeline Execution concluded successfully!")
                print("=======================================================")