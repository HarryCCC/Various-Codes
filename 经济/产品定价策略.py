'''

针对以下需求：
消费者行为与定价策略模拟
项目内容：模拟不同类型的消费者和不同的定价策略，观察销售额和利润的变化。

我写了以下说明：
1. 消费者，价格接受度&人数&每日购买概率：
a. 冲动购买：￥100，100人，1/365；b. 品牌忠诚：￥80，200人，6/365；c. 价值导向：￥60，400人，4/365；d. 省钱节约：￥40，300人，2/365。

2. 成本：
a. 产品成本：30元/个；
b. 营运成本：固定每年20,000元；
c. 库存成本：库存数量一直在100个以下时，零成本；
   库存最大数量大于100时：库存300以下时固定每年10000元，库存500以下时固定每年2*10000元，库存700以下时固定每年3*10000元，库存900以下时固定每年4*10000元；
d. 货运成本：2元/个。

3. 产品定价：
a. 高价：90元；b. 中高价：70元；c. 中低价：50元；d. 低价：30元；

4. 时间：
a. 旺季（1-3月和6-8月）：所有消费者类型的购买概率在初始购买频率的基础上增加1倍；
b. 淡季（4-5月和9-12月）：所有消费者类型的购买概率维持初始购买频率；
c. 周五到周日：所有消费者类型的购买概率在初始购买频率的基础上增加0.5倍；
d. 周一到周四：所有消费者类型的购买概率维持初始购买频率。
（当同时是旺季且是周五到周日时，所有消费者类型的购买概率在初始购买频率的基础上增加1.5倍）

目标：
1. 建立class和对应的attributes
2. 写一个优化函数，即输入一个特定的观察周期（这里，365天），借助说明中的所有数据，计算出一个最优的进货周期和单次进货数量，分别输出四种定价策略下的最优结果
3. 每次计算前，给出预测计算次数，并在控制台用进度条显示进度
4. 最终的输出改为有文字描述的形式：最优-进货周期：。。。；最优-单次进货数量：。。。；最优-定价加权平均观察期总利润：。。。；
5. 辅助函数包括但不限于：# Helper function to calculate inventory cost based on inventory level - def inventory_cost_structure(inventory_level)
                       # Helper function to adjust the probability based on seasonality - def adjust_probability(prob, current_date)

'''


import numpy as np
from tqdm import tqdm

class Consumer:
    def __init__(self, willingness_to_pay, population, daily_prob):
        self.willingness_to_pay = willingness_to_pay
        self.population = population
        self.daily_prob = daily_prob

class Scenario:
    def __init__(self, consumers):
        self.consumers = consumers
        self.operational_cost = 20000 / 365  # Daily operational cost

    def adjust_probability(self, prob, current_date):
        multiplier = 1
        if (current_date <= 90 or (current_date >= 152 and current_date <= 243)):
            multiplier *= 2
        if current_date % 7 >= 4:
            multiplier *= 1.5
        return prob * multiplier

    
    def inventory_cost_structure(self, inventory_level):
        if inventory_level < 100:
            return 0
        elif inventory_level < 300:
            return 10000
        elif inventory_level < 500:
            return 2 * 10000
        elif inventory_level < 700:
            return 3 * 10000
        else:
            return 4 * 10000

    def optimize_all(self, days=365):
        best_profit = -float("inf")
        best_reorder_cycle = 0
        best_order_quantity = 0
        best_price = 0

        pricing_strategies = range(30, 101, 10)
        total_iterations = len(pricing_strategies) * 30 * 90  # 4 prices, 90 reorder cycles, 18 order quantities

        pbar = tqdm(total=total_iterations, desc="Optimizing for all parameters")

        for pricing in pricing_strategies:
            for reorder_cycle in range(1, 31, 1):  # 1-30 days as potential reorder cycles
                for order_quantity in range(10, 901,10):  # 50-900 as potential order quantities
                    pbar.update(1)
                    inventory = 0
                    total_profit = 0

                    for day in range(1, days + 1):
                        daily_profit = 0  # Initialize daily_profit for each day
                        daily_profit -= self.operational_cost  # Add operational cost

                        if day % reorder_cycle == 0:
                            inventory += order_quantity

                        for consumer_type in self.consumers.values():
                            adjusted_prob = self.adjust_probability(consumer_type.daily_prob, day)
                            potential_buyers = int(consumer_type.population * adjusted_prob)

                            actual_buyers = min(potential_buyers, inventory)
                            if pricing <= consumer_type.willingness_to_pay:
                                daily_profit += (pricing - 30 - 2) * actual_buyers

                            inventory -= actual_buyers

                        daily_profit -= self.inventory_cost_structure(inventory)
                        total_profit += daily_profit

                    if total_profit > best_profit:
                        best_profit = total_profit
                        best_reorder_cycle = reorder_cycle
                        best_order_quantity = order_quantity
                        best_price = pricing

        print(f"全参数最优解：最优-定价：{best_price}元；最优-进货周期：{best_reorder_cycle}天；最优-单次进货数量：{best_order_quantity}个；最优-观察期总利润：{best_profit}元。")
        pbar.close()

# Initialize consumer types
consumers = {
    "impulsive": Consumer(100, 100, 1/365),
    "loyal": Consumer(80, 200, 6/365),
    "value_oriented": Consumer(60, 400, 4/365),
    "frugal": Consumer(40, 300, 2/365)
}

scenario = Scenario(consumers)
scenario.optimize_all()
