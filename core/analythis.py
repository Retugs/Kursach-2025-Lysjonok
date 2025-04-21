import argparse
import os
import json
import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

def load_data(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return pd.DataFrame(data)

def summarize_data(df, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    # overall summary
    summary = df.describe(include='all')
    summary.to_csv(os.path.join(output_dir, 'full_summary.csv'))
    # group by parameters
    grouped = df.groupby(['N_modes','N_F','N_M']).agg(
        mean_error=('error','mean'),
        std_error=('error','std'),
        mean_time=('time_s','mean'),
        mean_iters=('iterations','mean'),
        count=('error','count')
    ).reset_index()
    grouped.to_csv(os.path.join(output_dir,'grouped_summary.csv'), index=False)
    return grouped

def regression_analysis(grouped, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    # log transform
    X = np.log(grouped[['N_modes','N_F','N_M']].values)
    y = np.log(grouped['mean_error'].values)
    reg = LinearRegression().fit(X, y)
    coeffs = reg.coef_
    intercept = reg.intercept_
    C = np.exp(intercept)
    # save coefficients
    coefs_df = pd.DataFrame({
        'parameter':['N_modes','N_F','N_M'],
        'exponent': coeffs
    })
    coefs_df.to_csv(os.path.join(output_dir,'regression_exponents.csv'), index=False)
    # formula
    formula = (f"mean_error ≈ {C:.3e} "
               f"* N_modes^{coeffs[0]:.3f} "
               f"* N_F^{coeffs[1]:.3f} "
               f"* N_M^{coeffs[2]:.3f}")
    with open(os.path.join(output_dir,'regression_formula.txt'),'w',encoding='utf-8') as f:
        f.write(formula + '\n')
    # scatter plot actual vs predicted
    pred_log = reg.predict(X)
    pred = np.exp(pred_log)
    plt.figure(figsize=(6,6))
    plt.scatter(grouped['mean_error'], pred, alpha=0.6)
    mn = min(grouped['mean_error'].min(), pred.min())
    mx = max(grouped['mean_error'].max(), pred.max())
    plt.plot([mn,mx],[mn,mx], 'k--', lw=1)
    plt.xscale('log'); plt.yscale('log')
    plt.xlabel('Actual Mean Error'); plt.ylabel('Predicted Mean Error')
    plt.title('Actual vs Predicted Mean Error')
    plt.grid(True, which='both', ls='--')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir,'actual_vs_predicted.png'))
    plt.close()
    return reg, coefs_df, formula

def plot_sensitivity(grouped, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    # plot error vs each parameter (averaging over others)
    for param in ['N_modes','N_F','N_M']:
        pivot = grouped.groupby(param)['mean_error'].mean().reset_index()
        plt.figure()
        plt.plot(pivot[param], pivot['mean_error'], marker='o')
        plt.xscale('linear')
        plt.yscale('log')
        plt.xlabel(param)
        plt.ylabel('Mean Error')
        plt.title(f'Error vs {param}')
        plt.grid(True, which='both', ls='--')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir,f'error_vs_{param}.png'))
        plt.close()

def main():
    parser = argparse.ArgumentParser(description="Analyze parameter_study.json")
    parser.add_argument('--input', '-i', default='data/parameter_study.json',
                        help='Path to parameter_study.json')
    parser.add_argument('--out', '-o', default='results',
                        help='Output directory for analysis results')
    args = parser.parse_args()

    df = load_data(args.input)
    grouped = summarize_data(df, args.out)
    reg, coefs_df, formula = regression_analysis(grouped, args.out)
    plot_sensitivity(grouped, args.out)

    # print summary to console
    print("\n=== Regression Formula ===")
    print(formula)
    print("\n=== Regression Exponents ===")
    print(coefs_df.to_string(index=False))
    print(f"\nAnalysis complete. Results saved in '{args.out}' directory.")

if __name__ == '__main__':
    main()