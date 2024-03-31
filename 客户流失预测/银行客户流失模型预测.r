# 加载所需的包
library(dplyr)
library(caret) 
library(rpart)
library(randomForest)
library(e1071)

# 加载训练好的模型和缩放参数
lr_model <- readRDS("C:/Users/11470/Desktop/logistic_regression_model.rds")
dt_model <- readRDS("C:/Users/11470/Desktop/decision_tree_model.rds")
rf_model <- readRDS("C:/Users/11470/Desktop/random_forest_model.rds")
svm_model <- readRDS("C:/Users/11470/Desktop/support_vector_machine_model.rds") 
nb_model <- readRDS("C:/Users/11470/Desktop/naive_Bayes_model.rds")
scaling_params <- readRDS("C:/Users/11470/Desktop/scaling_params.rds")

# 硬编码输入参数值
CreditScore <- 700
Geography <- "France"
Gender <- "Female"  
Age <- 60
Tenure <- 10
Balance <- 0000
NumOfProducts <- 1
HasCrCard <- "1" 
IsActiveMember <- "1"
EstimatedSalary <- 100000

# 创建输入数据框,确保变量顺序与训练数据相同
input_data <- data.frame(
  CreditScore = CreditScore,
  Geography = Geography,
  Gender = Gender,
  Age = Age, 
  Tenure = Tenure,
  Balance = Balance,
  NumOfProducts = NumOfProducts,
  HasCrCard = HasCrCard,
  IsActiveMember = IsActiveMember,
  EstimatedSalary = EstimatedSalary,  
  stringsAsFactors = FALSE
)

# 将分类变量转换为因子,与训练数据保持一致
input_data$Geography <- factor(input_data$Geography, levels = c("France", "Spain", "Germany"))  
input_data$Gender <- factor(input_data$Gender, levels = c("Female", "Male"))
input_data$HasCrCard <- factor(input_data$HasCrCard, levels = c("0", "1"))
input_data$IsActiveMember <- factor(input_data$IsActiveMember, levels = c("0", "1"))  

# 特征缩放,使用保存的缩放参数
num_cols <- c("CreditScore", "Age", "Tenure", "Balance", "NumOfProducts", "EstimatedSalary")  
scaled_input_data <- input_data
for (i in seq_along(num_cols)) {
  scaled_input_data[[num_cols[i]]] <- (input_data[[num_cols[i]]] - scaling_params[[num_cols[i]]][["center"]]) / 
    scaling_params[[num_cols[i]]][["scale"]]
}

# 使用训练好的模型进行预测
lr_pred <- predict(lr_model, newdata = scaled_input_data, type = "response")
dt_pred <- predict(dt_model, newdata = scaled_input_data, type = "prob")[, 2] 
rf_pred <- predict(rf_model, newdata = scaled_input_data, type = "prob")[, 2]
svm_pred <- predict(svm_model, newdata = scaled_input_data, probability = TRUE)
svm_pred <- attr(svm_pred, "probabilities")[, 2]  
nb_pred <- predict(nb_model, newdata = scaled_input_data, type = "raw")[, 2]

# 加权平均预测结果
weights <- c(0.125, 0.25, 0.25, 0.25, 0.125)  # 可根据模型性能调整权重
weighted_pred <- lr_pred * weights[1] + dt_pred * weights[2] + rf_pred * weights[3] + 
  svm_pred * weights[4] + nb_pred * weights[5]

# 输出预测结果  
cat("Weighted prediction:", weighted_pred, "\n")
if (weighted_pred > 0.5) {
  cat("The customer is likely to churn.\n")
} else {
  cat("The customer is likely to stay.\n")  
}