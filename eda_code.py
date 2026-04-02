# chi squared test between target and categorical variables
from scipy.stats import chi2_contingency
# H0: independent
# Ha: dependent

alpha = 0.05

dependent_cols = []
independent_cols = []
for categorical_col in categorical_cols:
    contingency_table = pd.crosstab(df[categorical_col], df[target_col])
    chi2, p, dof, expected = chi2_contingency(contingency_table)
    if p <= alpha:
        # reject H0
        dependent_cols.append(categorical_col)
    else:
        # accept H0 i.e. independent
        independent_cols.append(categorical_col)
        
# ============================================================================

# 100% stacked bar chart for each category in the col (x-axis) and target categories (y-axis)
import matplotlib.pyplot as plt

# Grid layout
n_cols = 3
n_rows = (len(independent_cols) + n_cols - 1) // n_cols  # ceil division

fig, axes = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4*n_rows))
axes = axes.flatten()

for i, col in enumerate(independent_cols):
    ct = pd.crosstab(df[col], df[target_col], normalize='index')
    ct.plot(kind='bar', stacked=True, ax=axes[i], legend=(i==0))  # show legend only on first plot
    axes[i].set_title(f'{col} vs {target_col}')
    axes[i].set_ylabel('Proportion')
    axes[i].yaxis.set_major_formatter(plt.matplotlib.ticker.PercentFormatter(1.0))

# Hide any unused subplots
for j in range(i+1, len(axes)):
    axes[j].set_visible(False)

plt.tight_layout()
plt.show()

# ===============================================================================

import seaborn as sns
sns.histplot(
    data=df,
    x=numerical_cols[0],
    hue="attrition",
    bins=50,
    stat="density",
    common_norm=False,
    kde=True
)