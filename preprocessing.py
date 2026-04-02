# cap and floor outliers
example = numerical_cols_with_outliers[1]
col_name = example["col_name"]
print(col_name)
lower_extreme = example["lower_extreme"]
upper_extreme = example["upper_extreme"]

# cap and floor to extremes
df[col_name] = df[col_name].clip(lower=lower_extreme, upper=upper_extreme)