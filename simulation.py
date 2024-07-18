import random
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from termcolor import colored

pd.set_option('display.float_format', lambda x: '%.3f' % x)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

class Vault:
    def __init__(self, id, collateral, debt, mcr):
        self.id = id
        self.collateral = collateral
        self.debt = debt
        self.mcr = mcr
        self.ncr = self.calculate_ncr()

    def calculate_ncr(self):
        if self.debt == 0:
            return float('inf')
        return self.collateral / self.debt

def calculate_ars(vault, mcr_factor):
    mcr_component = mcr_factor * (vault.mcr / 100)
    return vault.ncr + mcr_component, mcr_component

def generate_vaults(num_vaults):
    vaults = []
    for i in range(num_vaults):
        collateral = round(random.uniform(100, 10000), 2)
        debt = round(random.uniform(50, collateral * 0.9), 2)  # Ensure debt is less than collateral
        mcr = round(random.uniform(110, 300), 2)  # MCR between 110% and 300%
        vaults.append(Vault(i+1, collateral, debt, mcr))
    return vaults

def simulate_ars(num_vaults, mcr_factor):
    vaults = generate_vaults(num_vaults)
    results = []
    for vault in vaults:
        ars, mcr_component = calculate_ars(vault, mcr_factor)
        results.append({
            'Vault ID': vault.id,
            'Collateral': vault.collateral,
            'Debt': vault.debt,
            'MCR (%)': vault.mcr,
            'NCR': vault.ncr,
            'MCR Component': mcr_component,
            'ARS': ars,
            'MCR Impact (%)': (mcr_component / vault.ncr) * 100
        })
    return pd.DataFrame(results)

def print_separator(text=""):
    width = 100
    print("\n" + "=" * width)
    if text:
        print(colored(text.center(width), 'yellow', attrs=['bold']))
        print("=" * width)

def plot_ncr_vs_ars(results_df):
    # Full view
    fig, ax = plt.subplots(figsize=(12, 8))

    scatter = ax.scatter(results_df['NCR'], results_df['ARS'], alpha=0.6, c=results_df['MCR Impact (%)'], cmap='viridis')
    ax.plot([0, max(results_df['NCR'].max(), results_df['ARS'].max())], 
            [0, max(results_df['NCR'].max(), results_df['ARS'].max())], 
            'r--', label='NCR = ARS')

    ax.set_xlabel('NCR')
    ax.set_ylabel('ARS')
    ax.set_title('NCR vs ARS: Impact of MCR Component (Full View)')
    ax.legend()

    # Set the main axes to show only up to 95th percentile of the data
    xlim = np.percentile(results_df['NCR'], 95)
    ylim = np.percentile(results_df['ARS'], 95)
    ax.set_xlim(0, xlim)
    ax.set_ylim(0, ylim)

    # Add colorbar
    cbar = plt.colorbar(scatter)
    cbar.set_label('MCR Impact (%)')

    plt.savefig('ncr_vs_ars_impact_full.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Zoomed view
    fig, ax = plt.subplots(figsize=(12, 8))

    scatter = ax.scatter(results_df['NCR'], results_df['ARS'], alpha=0.6, c=results_df['MCR Impact (%)'], cmap='viridis')
    ax.plot([0, max(results_df['NCR'].max(), results_df['ARS'].max())], 
            [0, max(results_df['NCR'].max(), results_df['ARS'].max())], 
            'r--', label='NCR = ARS')

    ax.set_xlabel('NCR')
    ax.set_ylabel('ARS')
    ax.set_title('NCR vs ARS: Impact of MCR Component (Zoomed View)')
    ax.legend()

    # Set the axes to show only up to 75th percentile of the data for the zoomed view
    xlim = np.percentile(results_df['NCR'], 75)
    ylim = np.percentile(results_df['ARS'], 75)
    ax.set_xlim(0, xlim)
    ax.set_ylim(0, ylim)

    # Add colorbar
    cbar = plt.colorbar(scatter)
    cbar.set_label('MCR Impact (%)')

    plt.savefig('ncr_vs_ars_impact_zoomed.png', dpi=300, bbox_inches='tight')
    plt.close()

# Run simulation
num_vaults = 100
mcr_factor = 0.2  # 0.2 represents 20% weight for MCR

results_df = simulate_ars(num_vaults, mcr_factor)

# Display summary of results
print_separator("Summary Statistics")
print(results_df.describe())

print_separator("MCR Impact Statistics")
print(colored("MCR Factor:", 'cyan'), f"{mcr_factor}")
print(colored("Average MCR Impact:", 'cyan'), f"{results_df['MCR Impact (%)'].mean():.2f}%")
print(colored("Median MCR Impact:", 'cyan'), f"{results_df['MCR Impact (%)'].median():.2f}%")
print(colored("Range of MCR Impact:", 'cyan'))
print(f"  Min: {results_df['MCR Impact (%)'].min():.2f}%")
print(f"  Max: {results_df['MCR Impact (%)'].max():.2f}%")

# Find vaults with highest and lowest MCR impact
highest_impact = results_df.loc[results_df['MCR Impact (%)'].idxmax()]
lowest_impact = results_df.loc[results_df['MCR Impact (%)'].idxmin()]

print_separator("Extreme Cases")
print(colored("Vault with Highest MCR Impact:", 'green'))
print(highest_impact.to_string())
print("\n" + colored("Vault with Lowest MCR Impact:", 'red'))
print(lowest_impact.to_string())

# Display top 10 and bottom 10 vaults by ARS
columns_to_display = ['Vault ID', 'Collateral', 'Debt', 'MCR (%)', 'NCR', 'MCR Component', 'ARS', 'MCR Impact (%)']

print_separator("Top 10 Vaults by ARS (Highest Risk of Redemption)")
print(results_df.nsmallest(10, 'ARS')[columns_to_display])

print_separator("Bottom 10 Vaults by ARS (Lowest Risk of Redemption)")
print(results_df.nlargest(10, 'ARS')[columns_to_display])

# Generate graphs
plot_ncr_vs_ars(results_df)

plt.figure(figsize=(12, 8))
plt.scatter(results_df['Collateral']/results_df['Debt'], results_df['MCR Impact (%)'], alpha=0.6)
plt.xlabel('Collateral/Debt Ratio')
plt.ylabel('MCR Impact (%)')
plt.title('Collateral/Debt Ratio vs MCR Impact')
plt.colorbar(plt.scatter(results_df['Collateral']/results_df['Debt'], results_df['MCR Impact (%)'], c=results_df['MCR (%)'], alpha=0.6), label='MCR (%)')
plt.savefig('collateral_debt_ratio_vs_mcr_impact.png')
plt.close()

plt.figure(figsize=(12, 8))
sns.histplot(results_df['MCR Impact (%)'], bins=20, kde=True)
plt.xlabel('MCR Impact (%)')
plt.ylabel('Frequency')
plt.title('Distribution of MCR Impact')
plt.savefig('mcr_impact_distribution.png')
plt.close()

plt.figure(figsize=(12, 10))
correlations = results_df[['Collateral', 'Debt', 'MCR (%)', 'NCR', 'MCR Component', 'ARS', 'MCR Impact (%)']].corr()
sns.heatmap(correlations, annot=True, cmap='coolwarm', vmin=-1, vmax=1, center=0)
plt.title('Correlation Heatmap')
plt.savefig('correlation_heatmap.png')
plt.close()

print_separator("Graphs Generated")
print("The following graphs have been saved:")
print("1. ncr_vs_ars_impact_full.png - NCR vs ARS: Impact of MCR Component (Full View)")
print("2. ncr_vs_ars_impact_zoomed.png - NCR vs ARS: Impact of MCR Component (Zoomed View)")
print("3. collateral_debt_ratio_vs_mcr_impact.png - Collateral/Debt Ratio vs MCR Impact")
print("4. mcr_impact_distribution.png - Distribution of MCR Impact")
print("5. correlation_heatmap.png - Correlation Heatmap")

print_separator("Simulation Complete")