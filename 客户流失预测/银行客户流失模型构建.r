# 加载所需的包
library(dplyr)
library(caret)
library(rpart)
library(randomForest)
library(e1071)

# 读取数据
cat("Reading data...\n")
data <- read.csv("C:/Users/11470/Desktop/Churn_Modelling.csv", stringsAsFactors = FALSE)
cat("Data loaded.\n")

# 排除无效输入列
cat("Excluding invalid input columns...\n")
data <- data %>% select(-c(RowNumber, CustomerId, Surname))

# 数据预处理
cat("Preprocessing data...\n")
# 处理缺失值
cat("Handling missing values...\n")
data <- data %>%
  mutate_all(~ifelse(is.na(.), median(., na.rm = TRUE), .))
# 分类变量转换为因子
cat("Converting categorical variables to factors...\n")
data$Geography <- as.factor(data$Geography)
data$Gender <- as.factor(data$Gender)
data$HasCrCard <- as.factor(data$HasCrCard)
data$IsActiveMember <- as.factor(data$IsActiveMember)
# 特征缩放
cat("Scaling features...\n")
num_cols <- c("CreditScore", "Age", "Tenure", "Balance", "NumOfProducts", "EstimatedSalary")
scaling_params <- lapply(data[, num_cols], function(x) c(center = mean(x), scale = sd(x)))
data[, num_cols] <- scale(data[, num_cols])
cat("Data preprocessing completed.\n")

# 划分特征变量X和目标变量y
cat("Splitting features and target...\n")
X <- data %>% select(-Exited)
y <- data$Exited
# 将Exited转换为因子变量
y <- as.factor(y)

# 划分训练集和测试集
cat("Splitting data into train and test sets...\n")
set.seed(42)
trainIndex <- createDataPartition(y, p = 0.8, list = FALSE)
X_train <- X[trainIndex, ]
X_test <- X[-trainIndex, ]
y_train <- y[trainIndex]
y_test <- y[-trainIndex]
cat("Data split completed.\n")

# 训练多个模型
cat("Training started...\n")
# 逻辑回归
cat("Training logistic regression model...\n")
lr_model <- glm(y_train ~ ., data = cbind(X_train, y_train), family = "binomial")

# 决策树
cat("Training decision tree model...\n")
dt_model <- rpart(y_train ~ ., data = cbind(X_train, y_train), method = "class")

# 随机森林
cat("Training random forest model...\n")
rf_model <- randomForest(y_train ~ ., data = cbind(X_train, y_train))

# 支持向量机
cat("Training support vector machine model...\n")
svm_model <- svm(y_train ~ ., data = cbind(X_train, y_train), kernel = "radial", probability = TRUE)

# 朴素贝叶斯
cat("Training naive Bayes model...\n")
nb_model <- naiveBayes(X_train, y_train)

cat("Model training completed.\n")

# 模型评估与预测
cat("Evaluating models and making predictions...\n")
# 逻辑回归
lr_pred <- predict(lr_model, newdata = X_test, type = "response")
# 决策树
dt_pred <- predict(dt_model, newdata = X_test, type = "prob")[, 2]
# 随机森林
rf_pred <- predict(rf_model, newdata = X_test, type = "prob")[, 2]
# 支持向量机
svm_pred <- attr(predict(svm_model, newdata = X_test, probability = TRUE), "probabilities")[, 2]
# 朴素贝叶斯
nb_pred <- predict(nb_model, newdata = X_test, type = "raw")[, 2]

# 加权平均预测结果
weights <- c(0.125, 0.25, 0.25, 0.25, 0.125)  # 可根据模型性能调整权重
weighted_pred <- lr_pred * weights[1] + dt_pred * weights[2] + rf_pred * weights[3] +
                 svm_pred * weights[4] + nb_pred * weights[5]

# 转换为二元类别
y_pred_class <- ifelse(weighted_pred > 0.5, 1, 0)

# 评估性能
accuracy <- mean(y_pred_class == y_test)
confusion_mat <- table(y_test, y_pred_class)
cat(paste("Accuracy:", accuracy, "\n"))
cat("Confusion Matrix:\n")
print(confusion_mat)
cat("Model evaluation completed.\n")

# 保存训练好的模型和缩放参数
cat("Saving trained models and scaling parameters...\n")
saveRDS(lr_model, "C:/Users/11470/Desktop/logistic_regression_model.rds")
saveRDS(dt_model, "C:/Users/11470/Desktop/decision_tree_model.rds")
saveRDS(rf_model, "C:/Users/11470/Desktop/random_forest_model.rds")
saveRDS(svm_model, "C:/Users/11470/Desktop/support_vector_machine_model.rds")
saveRDS(nb_model, "C:/Users/11470/Desktop/naive_Bayes_model.rds")
saveRDS(scaling_params, "C:/Users/11470/Desktop/scaling_params.rds")
cat("Models and scaling parameters saved.\n")