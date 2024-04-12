import pandas as pd
import numpy as np
import statsmodels.api as sm

# 读取数据文件
data = pd.read_excel('FINM3008 - Assignment Analysis S1 2024.xlsx', sheet_name='Fundamental Factor Data')

# 提取因子数据和资产收益率数据
factors = data.iloc[:, 1:10]  # B-J列的因子数据
returns = data.iloc[:, 11:]  # L-Z列的资产收益率数据

# 计算每类资产关于不同因子的beta值
betas = {}
rf = 0.0075  # 季度无风险利率

for asset in returns.columns:
    asset_betas = []
    for factor in factors.columns:
        # 计算超额收益率
        excess_return = returns[asset] - rf
        
        # 对因子和超额收益率进行线性回归
        X = sm.add_constant(factors[factor])
        model = sm.OLS(excess_return, X)
        results = model.fit()
        
        # 提取beta值
        beta = results.params.iloc[1]
        asset_betas.append(beta)
    
    betas[asset] = asset_betas

# 将beta值存储到数据框中
beta_df = pd.DataFrame(betas, index=factors.columns)

# 将结果输出到txt文件
with open('asset_betas.txt', 'w') as file:
    file.write(beta_df.to_string(index=True))

# 打印每类资产的beta值
print(beta_df)