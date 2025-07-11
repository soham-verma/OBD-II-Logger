#!/usr/bin/env python3
import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def main():
    parser = argparse.ArgumentParser(description='OBD Data Analysis')
    parser.add_argument('--input', '-i', required=True, help='Path to all_obd.csv')
    parser.add_argument('--output', '-o', default='obd_analysis_output', help='Directory to save analysis results')
    args = parser.parse_args()

    # Prepare output directory
    output_dir = args.output
    ensure_dir(output_dir)

    # Load data
    df = pd.read_csv(args.input, parse_dates=['timestamp'])
    print(f"Loaded {{len(df)}} records from {{args.input}}")

    # Summary statistics
    stats = df[['RPM', 'SPEED', 'COOLANT_TEMP', 'ENGINE_LOAD']].describe()
    stats.to_csv(os.path.join(output_dir, 'summary_stats.csv'))
    print(f"Summary statistics saved to {{os.path.join(output_dir, 'summary_stats.csv')}}")

    # Time-series plots
    plt.figure()
    df.set_index('timestamp')['RPM'].plot(title='RPM over Time')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'rpm_over_time.png'))
    plt.close()

    plt.figure()
    df.set_index('timestamp')['SPEED'].plot(title='Speed over Time')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'speed_over_time.png'))
    plt.close()

    plt.figure()
    df.set_index('timestamp')['COOLANT_TEMP'].plot(title='Coolant Temperature over Time')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'coolant_temp_over_time.png'))
    plt.close()

    # Histogram of Speed
    plt.figure()
    df['SPEED'].hist(bins=20)
    plt.title('Speed Distribution')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'speed_distribution.png'))
    plt.close()

    # Scatter: Engine Load vs RPM
    plt.figure()
    plt.scatter(df['RPM'], df['ENGINE_LOAD'], s=5)
    plt.title('Engine Load vs RPM')
    plt.xlabel('RPM')
    plt.ylabel('Engine Load')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'load_vs_rpm.png'))
    plt.close()

    print(f"Plots saved to {{output_dir}}")

if __name__ == '__main__':
    main()
