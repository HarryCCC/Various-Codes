def knapsack(weights, values, capacity):
    n = len(weights)
    dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]
    keep = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(1, capacity + 1):
            if weights[i - 1] <= w and values[i - 1] + dp[i - 1][w - weights[i - 1]] > dp[i - 1][w]:
                dp[i][w] = values[i - 1] + dp[i - 1][w - weights[i - 1]]
                keep[i][w] = 1
            else:
                dp[i][w] = dp[i - 1][w]

    items = []
    w = capacity
    for i in range(n, 0, -1):
        if keep[i][w] == 1:
            items.append(weights[i - 1])
            w -= weights[i - 1]

    return dp[n][capacity], items

weights = [1,2,3,4,5,6,7,8]
values = [3,4,5,6,7,8,9,10]
capacity = 25
print(knapsack(weights, values, capacity))
