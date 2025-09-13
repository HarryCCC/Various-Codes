# -*- coding: utf-8 -*-

import numpy as np

# --- 核心参数配置 ---
# 您可以根据需要调整这些数值

# 1. 房屋和租金参数
TOTAL_PRICE = 5_000_000  # 房屋总价 (元)
LOAN_YEARS = 10          # 贷款年限 (年)
RENT_TO_SALE_RATIO_ANNUAL = 0.018 # 年租售比 (1.8%)

# 2. 贷款政策和利率参数 (基于2024-2025年上海市场情况)
# 上海首套房最低首付比例
MIN_DOWN_PAYMENT_RATIO = 0.20
# 商业贷款年利率 (假设5年期LPR为3.95%，首套房利率为LPR-10基点)
COMMERCIAL_RATE_ANNUAL = 0.0385
# 公积金贷款年利率 (5年及以下)
PF_RATE_ANNUAL = 0.0235 # 5年期及以下公积金利率调整为2.35%
# 家庭公积金贷款最高额度 (元)
PF_LOAN_MAX = 1_200_000

# --- 计算模块 ---

def calculate_monthly_payment(principal, annual_rate, years):
    """计算等额本息下的月供"""
    if principal <= 0 or annual_rate <= 0:
        return 0
    monthly_rate = annual_rate / 12
    num_months = years * 12
    # 等额本息计算公式
    monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**num_months) / ((1 + monthly_rate)**num_months - 1)
    return monthly_payment

def calculate_avg_monthly_interest(down_payment, total_price, loan_years):
    """根据给定的首付，计算混合贷款下的月均利息"""
    total_loan = total_price - down_payment
    if total_loan <= 0:
        return 0

    # 拆分贷款为公积金和商业两部分
    pf_loan = min(total_loan, PF_LOAN_MAX)
    commercial_loan = total_loan - pf_loan

    # 分别计算两部分的月供
    pf_monthly_payment = calculate_monthly_payment(pf_loan, PF_RATE_ANNUAL, loan_years)
    commercial_monthly_payment = calculate_monthly_payment(commercial_loan, COMMERCIAL_RATE_ANNUAL, loan_years)

    # 计算总利息
    total_months = loan_years * 12
    total_pf_interest = (pf_monthly_payment * total_months) - pf_loan if pf_loan > 0 else 0
    total_commercial_interest = (commercial_monthly_payment * total_months) - commercial_loan if commercial_loan > 0 else 0
    total_interest = total_pf_interest + total_commercial_interest

    # 计算月均利息
    avg_monthly_interest = total_interest / total_months
    return avg_monthly_interest

# --- 主逻辑 ---

def find_equilibrium_down_payment():
    """主函数，执行计算和分析"""
    # 1. 计算目标月租金
    monthly_rent = (TOTAL_PRICE * RENT_TO_SALE_RATIO_ANNUAL) / 12

    print("--- 计算参数 ---")
    print(f"房屋总价: {TOTAL_PRICE:,.0f} 元")
    print(f"贷款年限: {LOAN_YEARS} 年")
    print(f"年租售比: {RENT_TO_SALE_RATIO_ANNUAL:.2%}")
    print(f"商业贷款年利率: {COMMERCIAL_RATE_ANNUAL:.3%}")
    print(f"公积金贷款年利率: {PF_RATE_ANNUAL:.3%}")
    print(f"家庭公积金最高可贷额度: {PF_LOAN_MAX:,.0f} 元")
    print("-" * 20)
    print(f"计算得出的目标月租金: {monthly_rent:,.2f} 元")
    print("-" * 20)

    # 2. 检查在最低首付情况下，利息是否已经低于租金
    min_down_payment = TOTAL_PRICE * MIN_DOWN_PAYMENT_RATIO
    interest_at_min_dp = calculate_avg_monthly_interest(min_down_payment, TOTAL_PRICE, LOAN_YEARS)

    # 计算并输出月供
    min_dp_loan = TOTAL_PRICE - min_down_payment
    min_dp_pf_loan = min(min_dp_loan, PF_LOAN_MAX)
    min_dp_com_loan = min_dp_loan - min_dp_pf_loan
    min_dp_pf_monthly = calculate_monthly_payment(min_dp_pf_loan, PF_RATE_ANNUAL, LOAN_YEARS)
    min_dp_com_monthly = calculate_monthly_payment(min_dp_com_loan, COMMERCIAL_RATE_ANNUAL, LOAN_YEARS)
    min_dp_total_monthly = min_dp_pf_monthly + min_dp_com_monthly

    print(f"首先，我们计算在政策允许的最低首付（{MIN_DOWN_PAYMENT_RATIO:.0%}，即 {min_down_payment:,.0f} 元）下的情况...")
    print(f"最低首付下的月均贷款利息为: {interest_at_min_dp:,.2f} 元")
    print(f"最低首付下的总月供为: {min_dp_total_monthly:,.2f} 元 (公积金: {min_dp_pf_monthly:,.2f} + 商贷: {min_dp_com_monthly:,.2f})")

    print("-" * 20)
    # --- 新增：计算并输出50%首付情景 ---
    print("我们再来分析一下在首付为50%的情况...")
    dp_50_percent = TOTAL_PRICE * 0.50
    interest_at_50_dp = calculate_avg_monthly_interest(dp_50_percent, TOTAL_PRICE, LOAN_YEARS)

    # 计算月供
    loan_50_dp = TOTAL_PRICE - dp_50_percent
    pf_loan_50_dp = min(loan_50_dp, PF_LOAN_MAX)
    com_loan_50_dp = loan_50_dp - pf_loan_50_dp
    pf_monthly_50_dp = calculate_monthly_payment(pf_loan_50_dp, PF_RATE_ANNUAL, LOAN_YEARS)
    com_monthly_50_dp = calculate_monthly_payment(com_loan_50_dp, COMMERCIAL_RATE_ANNUAL, LOAN_YEARS)
    total_monthly_50_dp = pf_monthly_50_dp + com_monthly_50_dp

    print(f"50%首付金额: {dp_50_percent:,.0f} 元")
    print(f"50%首付下的月均贷款利息为: {interest_at_50_dp:,.2f} 元")
    print(f"50%首付下的总月供为: {total_monthly_50_dp:,.2f} 元 (公积金: {pf_monthly_50_dp:,.2f} + 商贷: {com_monthly_50_dp:,.2f})")


    if interest_at_min_dp < monthly_rent:
        print("\n--- 结论 ---")
        print(f"分析发现：在您设定的{LOAN_YEARS}年贷款期限下，即便是支付最低首付，月均贷款利息也已经低于月租金。")
        print("由于增加首付只会进一步降低利息，所以在当前参数下，不存在一个能让月均利息和租金'打平'的首付点。")
        print("这通常意味着，从纯粹的'利息 vs 租金'角度看，买房的资金成本相对更低。")
        return

    # 3. 如果有可能打平，则使用二分法寻找平衡点
    # (此部分逻辑在当前参数下不会被触发，但为模型完整性保留)
    low_dp = min_down_payment
    high_dp = TOTAL_PRICE
    solution_found = False

    for _ in range(100):  # 迭代100次以获得高精度
        mid_dp = (low_dp + high_dp) / 2
        current_interest = calculate_avg_monthly_interest(mid_dp, TOTAL_PRICE, LOAN_YEARS)

        if abs(current_interest - monthly_rent) < 0.01: # 精度控制
            solution_found = True
            break
        elif current_interest > monthly_rent:
            low_dp = mid_dp
        else:
            high_dp = mid_dp
    
    if solution_found:
        print("\n--- 计算结果 ---")
        print(f"找到平衡点！要使月均利息约等于月租金 ({monthly_rent:,.2f} 元)，您需要支付的首付为：")
        print(f"首付金额: {mid_dp:,.0f} 元")
        print(f"首付比例: {mid_dp / TOTAL_PRICE:.2%}")

        # 输出详细信息
        final_loan = TOTAL_PRICE - mid_dp
        final_pf_loan = min(final_loan, PF_LOAN_MAX)
        final_com_loan = final_loan - final_pf_loan
        
        # 计算并输出月供
        final_pf_monthly = calculate_monthly_payment(final_pf_loan, PF_RATE_ANNUAL, LOAN_YEARS)
        final_com_monthly = calculate_monthly_payment(final_com_loan, COMMERCIAL_RATE_ANNUAL, LOAN_YEARS)
        final_total_monthly = final_pf_monthly + final_com_monthly

        print("\n--- 贷款详情 ---")
        print(f"总贷款额: {final_loan:,.0f} 元")
        print(f"  - 公积金贷款: {final_pf_loan:,.0f} 元")
        print(f"  - 商业贷款: {final_com_loan:,.0f} 元")
        print(f"总月供: {final_total_monthly:,.2f} 元 (公积金: {final_pf_monthly:,.2f} + 商贷: {final_com_monthly:,.2f})")


if __name__ == '__main__':
    find_equilibrium_down_payment()

