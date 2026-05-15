create database ecommerce_db;

# 查询数据
use ecommerce_db;
# 查看前10行数据
select * from ecommerce_customer_churn_data limit 10;

# 查看总行数
select count(*)  总行数 from ecommerce_customer_churn_data;

# 查看空值情况
describe ecommerce_customer_churn_data;

# 统计缺失值
select
    sum(case when CustomerID is null then 1 else 0 end) as missing_CustomerID,
    sum(case when Age is null then 1 else 0 end) as missing_Age,
    sum(case when ecommerce_customer_churn_data.Subscription_Duration_Months is null then 1 else 0 end) as missing_Subscription_Duration_Months,
    sum(case when Contract_Type is null then 1 else 0 end) as missing_Contract_Type,
    sum(case when ecommerce_customer_churn_data.Monthly_Logins is null then 1 else 0 end) as missing_Monthly_Logins,
    sum(case when ecommerce_customer_churn_data.Last_Purchase_Days_Ago is null then 1 else 0 end) as missing_Last_Purchase_Days_Ago,
    sum(case when ecommerce_customer_churn_data.App_Usage_Time_Min is null then 1 else 0 end) as missing_App_Usage_Time_Min,
    sum(case when ecommerce_customer_churn_data.Monthly_Spend is null then 1 else 0 end) as missing_Monthly_Spend,
    sum(case when ecommerce_customer_churn_data.Discount_Usage_Percentage is null then 1 else 0 end) as missing_Discount_Usage_Percentage,
    sum(case when ecommerce_customer_churn_data.Customer_Support_Calls is null then 1 else 0 end) as missing_Customer_Support_Calls,
    sum(case when ecommerce_customer_churn_data.Satisfaction_Score is null then 1 else 0 end) as missing_Satisfaction_Score,
    sum(case when ecommerce_customer_churn_data.Is_Churn is null then 1 else 0 end) as missing_Is_Churn
from ecommerce_customer_churn_data;

# 查看Churn 字段的原始分布
select Is_Churn,
       COUNT(*) as cnt
from ecommerce_customer_churn_data
group by Is_Churn order by Is_Churn;


# 留存 vs 流失对比
SELECT
    Is_Churn,
    COUNT(*) AS 客户数,
    AVG(Monthly_Logins) AS 平均月登录次数,
    AVG(App_Usage_Time_Min) AS 平均使用时长_分钟,
    AVG(Monthly_Spend) AS 平均月消费_美元,
    AVG(Customer_Support_Calls) AS 平均客服呼叫次数,
    AVG(Satisfaction_Score) AS 平均满意度评分
FROM ecommerce_customer_churn_data
GROUP BY Is_Churn;

# 验证呼叫次数越高,流失率 ----- 划分次数,看各次数的流失率
select
    case
        when Customer_Support_Calls = 0 then '0次'
        when Customer_Support_Calls = 1 then '1次'
        when Customer_Support_Calls = 2 then '2次'
        when Customer_Support_Calls BETWEEN 3 and 4 then '3-4次'
        else '5次以上'
    end as call_group,
    count(*) 客户数,
    sum(Is_Churn) 流失客户数,
    round(avg(Is_Churn), 4) 流失率
from ecommerce_customer_churn_data
group by call_group
order by
    case call_group
        WHEN '0次' THEN 1
        WHEN '1次' THEN 2
        WHEN '2次' THEN 3
        WHEN '3-4次' THEN 4
        ELSE 5
    end;