import sympy as sp
from scipy.optimize import fsolve

# 定义符号
L, K, P, w, r = sp.symbols('L K P w r')
alpha, beta = sp.symbols('alpha beta')

# 假设我们有一些给定的参数值
params = {alpha: 0.35, w: 27.5, r: 0.01}

# Cobb-Douglas生产函数
Q = (K**alpha) * (L**(1-alpha))

# 生产者问题：最大化利润
profit = P*Q - (w*L + r*K)
FOC_L = sp.diff(profit, L)
FOC_K = sp.diff(profit, K)

# 使用 lambdify 将 SymPy 表达式转换为函数
FOC_L_func = sp.lambdify((L, K, P), FOC_L.subs(params))
FOC_K_func = sp.lambdify((L, K, P), FOC_K.subs(params))

# 定义方程
def equations(vars):
    L, K = vars
    eq1 = FOC_L_func(L, K, 0.5)  # 假设价格
    eq2 = FOC_K_func(L, K, 0.5)
    return [eq1, eq2]

# 初始猜测值
initial_guess = [1, 1]
optimal_L, optimal_K = fsolve(equations, initial_guess)

# 输出结果
print(f"Optimal L: {optimal_L}")
print(f"Optimal K: {optimal_K}")
