def calculate_max_drawdown(prices):
    # 初始化
    max_drawdown = 0
    peak = prices[0]
    
    # 遍历
    for price in prices:
        # 更新最高价
        if price > peak:
            peak = price
        # 当前点的回撤
        drawdown = (peak - price) / peak
        # 更新最大回撤
        if drawdown > max_drawdown:
            max_drawdown = drawdown
    
    return max_drawdown

# 示例
prices = [100, 110, 107, 115, 155, 135, 130, 125, 140, 133, 137, 129, 95]
print("最大回撤为:", calculate_max_drawdown(prices))
