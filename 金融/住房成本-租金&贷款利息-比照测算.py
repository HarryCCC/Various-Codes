# -*- coding: utf-8 -*-

import numpy as np

# --- 核心参数配置 ---
# 您可以根据需要调整这些数值

# 1. 房屋和租金参数
TOTAL_PRICE = 5_000_000  # 房屋总价 (元)
LOAN_YEARS = 7          # 贷款年限 (年)
RENT_TO_SALE_RATIO_ANNUAL = 0.02 + 0.005 # 年租售比 (1.8%)

# 2. 贷款政策和利率参数 (基于2024-2025年上海市场情况)
# 上海首套房最低首付比例
MIN_DOWN_PAYMENT_RATIO = 0.20
# 商业贷款年利率 (5年期以上LPR为3.95%，首套房利率为LPR-10基点)
COMMERCIAL_RATE_ANNUAL = 0.0385
# 公积金贷款年利率 (区分5年及以下/以上)
PF_RATE_ANNUAL_LE_5Y = 0.0235 # 5年期及以下
PF_RATE_ANNUAL_GT_5Y = 0.0285 # 5年期以上
# 家庭公积金贷款最高额度 (元)
PF_LOAN_MAX = 1_200_000

# 3. 新增：机会成本参数
# 假设首付款如果用于投资，可以获得的无风险年化回报率
# 这个比率对结果影响很大，可以设为您认为合理的稳健投资收益率，例如国债、银行理财等
OPPORTUNITY_COST_RATE_ANNUAL = 0.04 # 首付款机会成本的年化回报率 (3.0%)

# --- 计算模块 ---

def get_pf_rate(years):
    """根据贷款年限返回正确的公积金利率"""
    return PF_RATE_ANNUAL_LE_5Y if years <= 5 else PF_RATE_ANNUAL_GT_5Y

def calculate_monthly_payment(principal, annual_rate, years):
    """计算等额本息下的月供"""
    if principal <= 0 or annual_rate <= 0:
        return 0
    monthly_rate = annual_rate / 12
    num_months = years * 12
    monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**num_months) / ((1 + monthly_rate)**num_months - 1)
    return monthly_payment

def calculate_ownership_costs(down_payment, total_price, loan_years):
    """
    计算并返回购房的总月均持有成本（利息 + 机会成本）
    """
    # a. 计算机会成本
    monthly_opportunity_cost = (down_payment * OPPORTUNITY_COST_RATE_ANNUAL) / 12

    # b. 计算月均利息
    total_loan = total_price - down_payment
    if total_loan <= 0:
        return monthly_opportunity_cost, 0, monthly_opportunity_cost

    pf_rate = get_pf_rate(loan_years)
    pf_loan = min(total_loan, PF_LOAN_MAX)
    commercial_loan = total_loan - pf_loan

    pf_monthly_payment = calculate_monthly_payment(pf_loan, pf_rate, loan_years)
    commercial_monthly_payment = calculate_monthly_payment(commercial_loan, COMMERCIAL_RATE_ANNUAL, loan_years)

    total_months = loan_years * 12
    total_pf_interest = (pf_monthly_payment * total_months) - pf_loan if pf_loan > 0 else 0
    total_commercial_interest = (commercial_monthly_payment * total_months) - commercial_loan if commercial_loan > 0 else 0
    total_interest = total_pf_interest + total_commercial_interest
    avg_monthly_interest = total_interest / total_months if total_months > 0 else 0

    # c. 计算总成本
    total_monthly_cost = avg_monthly_interest + monthly_opportunity_cost
    
    return total_monthly_cost, avg_monthly_interest, monthly_opportunity_cost

# --- 主逻辑 ---

def find_equilibrium_down_payment():
    """主函数，执行计算和分析"""
    monthly_rent = (TOTAL_PRICE * RENT_TO_SALE_RATIO_ANNUAL) / 12
    pf_rate = get_pf_rate(LOAN_YEARS)

    print("--- 计算参数 ---")
    print(f"房屋总价: {TOTAL_PRICE:,.0f} 元")
    print(f"贷款年限: {LOAN_YEARS} 年 (适用公积金年利率: {pf_rate:.3%})")
    print(f"年租售比: {RENT_TO_SALE_RATIO_ANNUAL:.2%}")
    print(f"首付款机会成本年化率: {OPPORTUNITY_COST_RATE_ANNUAL:.2%}")
    print("-" * 20)
    print(f"计算得出的目标月租金 (月度机会成本): {monthly_rent:,.2f} 元")
    print("-" * 20)

    # 分析最低首付情况
    min_down_payment = TOTAL_PRICE * MIN_DOWN_PAYMENT_RATIO
    cost_at_min_dp, interest_at_min_dp, opp_cost_at_min_dp = calculate_ownership_costs(min_down_payment, TOTAL_PRICE, LOAN_YEARS)
    
    print(f"首先，分析在最低首付（{MIN_DOWN_PAYMENT_RATIO:.0%}，即 {min_down_payment:,.0f} 元）下的情况...")
    print(f"月均总持有成本为: {cost_at_min_dp:,.2f} 元")
    print(f"  - 其中月均利息: {interest_at_min_dp:,.2f} 元")
    print(f"  - 其中机会成本: {opp_cost_at_min_dp:,.2f} 元")
    
    # 分析50%首付情况
    print("-" * 20)
    dp_50_percent = TOTAL_PRICE * 0.50
    cost_at_50_dp, interest_at_50_dp, opp_cost_at_50_dp = calculate_ownership_costs(dp_50_percent, TOTAL_PRICE, LOAN_YEARS)

    print(f"其次，分析在首付为50%（即 {dp_50_percent:,.0f} 元）的情况...")
    print(f"月均总持有成本为: {cost_at_50_dp:,.2f} 元")
    print(f"  - 其中月均利息: {interest_at_50_dp:,.2f} 元")
    print(f"  - 其中机会成本: {opp_cost_at_50_dp:,.2f} 元")


    # 寻找平衡点
    # 如果最低首付的总成本已经低于租金，说明增加首付只会让成本更低，不可能打平
    if cost_at_min_dp <= monthly_rent:
        print("\n--- 结论 ---")
        print(f"关键发现：在计入首付款机会成本后，即便支付最低首付，您的月均总持有成本 ({cost_at_min_dp:,.2f}元) 依然低于月租金 ({monthly_rent:,.2f}元)。")
        print("这意味着在当前参数下，购房的综合资金成本（利息+机会成本）比租房更具优势，无法找到一个让两者'打平'的首付点。")
        return

    # 使用二分法寻找平衡点
    low_dp = min_down_payment
    high_dp = TOTAL_PRICE
    solution_found = False
    final_dp = 0

    for _ in range(100):
        mid_dp = (low_dp + high_dp) / 2
        current_cost, _, _ = calculate_ownership_costs(mid_dp, TOTAL_PRICE, LOAN_YEARS)
        if abs(current_cost - monthly_rent) < 0.01:
            solution_found = True
            final_dp = mid_dp
            break
        elif current_cost > monthly_rent:
             high_dp = mid_dp
        else:
            low_dp = mid_dp
    
    if solution_found:
        print("\n" + "="*25)
        print("     🎉 找到平衡点! 🎉")
        print("="*25)
        print(f"\n要使'月均总持有成本'约等于'月租金'({monthly_rent:,.2f}元)，您需要支付的首付为：")
        print(f"👉 首付金额: {final_dp:,.0f} 元")
        print(f"👉 首付比例: {final_dp / TOTAL_PRICE:.2%}")

        final_cost, final_interest, final_opp_cost = calculate_ownership_costs(final_dp, TOTAL_PRICE, LOAN_YEARS)
        final_loan = TOTAL_PRICE - final_dp
        final_pf_loan = min(final_loan, PF_LOAN_MAX)
        final_com_loan = final_loan - final_pf_loan
        
        final_pf_monthly = calculate_monthly_payment(final_pf_loan, pf_rate, LOAN_YEARS)
        final_com_monthly = calculate_monthly_payment(final_com_loan, COMMERCIAL_RATE_ANNUAL, LOAN_YEARS)
        final_total_monthly = final_pf_monthly + final_com_monthly

        print("\n--- 在此平衡点下的详细财务情况 ---")
        print(f"总月供 (还本付息): {final_total_monthly:,.2f} 元")
        print(f"月均总持有成本: {final_cost:,.2f} 元")
        print(f"  - 其中月均利息: {final_interest:,.2f} 元")
        print(f"  - 其中机会成本: {final_opp_cost:,.2f} 元")


if __name__ == '__main__':
    find_equilibrium_down_payment()
