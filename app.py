import streamlit as st
import pandas as pd
import numpy as np
import joblib

st.set_page_config(page_title="客户流失预测", layout="wide", initial_sidebar_state="collapsed")

# 手机端自适应 CSS
st.markdown("""
<style>
    /* 移动端适配 */
    @media (max-width: 768px) {
        .stMainBlockContainer { padding: 1rem 0.5rem !important; }
        .row-widget.stColumns { flex-direction: column !important; gap: 0.3rem !important; }
        .row-widget.stColumns > div { width: 100% !important; flex: none !important; }
        div[data-testid="column"] { width: 100% !important; min-width: 100% !important; }
        .st-emotion-cache-1jicfl2 { padding: 1rem 0.5rem !important; }
        h1 { font-size: 1.5rem !important; }
        h2, h3 { font-size: 1.1rem !important; }
        div[data-testid="metric-container"] { padding: 0.5rem !important; }
    }
    /* 卡片风格 */
    div[data-testid="metric-container"] {
        background: #f0f2f6; border-radius: 10px; padding: 1rem; text-align: center;
    }
    .st-emotion-cache-1r4qj8v { padding: 1rem 0.5rem; }
    @media (prefers-color-scheme: dark) {
        div[data-testid="metric-container"] { background: #262730; }
    }
</style>
""", unsafe_allow_html=True)

st.title("🛒 电商客户流失风险预测")
st.markdown("输入客户信息，预测流失概率并获取干预建议")

@st.cache_resource
def load_model():
    data = joblib.load('churn_model.pkl')
    return data['model'], data['scaler'], data['feature_columns']

model, scaler, feature_cols = load_model()

col1, col2, col3 = st.columns(3)

with col1:
    age = st.number_input("年龄", 18, 70, 35)
    subscription = st.number_input("订阅月数", 1, 60, 12)
    logins = st.number_input("月登录次数", 1, 30, 10)
    last_purchase = st.number_input("距上次购买天数", 0, 90, 10)

with col2:
    app_usage = st.number_input("App使用时长(分钟)", 1.0, 70.0, 20.0)
    spending = st.number_input("月消费金额($)", 10.0, 2000.0, 100.0)
    discount = st.number_input("折扣使用比例", 0.0, 1.0, 0.2)
    support_calls = st.number_input("客服呼叫次数", 0, 10, 1)

with col3:
    satisfaction = st.number_input("满意度评分", 1, 5, 4)
    contract = st.selectbox("合同类型", ["Monthly", "Annual"])

if st.button("🚀 预测流失风险", type="primary", use_container_width=True):
    input_data = pd.DataFrame([[age, subscription, logins, last_purchase,
                                app_usage, spending, discount, support_calls,
                                satisfaction, 1 if contract == "Monthly" else 0]],
                              columns=feature_cols)

    scaled = scaler.transform(input_data)
    prob = model.predict_proba(scaled)[0, 1]

    st.markdown("---")
    st.subheader("预测结果")

    res_col1, res_col2, res_col3 = st.columns(3)
    res_col1.metric("流失概率", f"{prob:.1%}")
    pred_label = "⚠️ 流失" if prob >= 0.3 else "✅ 未流失"
    res_col2.metric("预测结果", pred_label)
    if prob >= 0.7:
        risk = "🔴 高风险"
    elif prob >= 0.3:
        risk = "🟡 中风险"
    else:
        risk = "🟢 低风险"
    res_col3.metric("风险等级", risk)

    st.markdown("---")
    st.subheader("📋 干预建议")
    if prob >= 0.7:
        if contract == "Monthly":
            st.error("**优先干预**：高风险月合同客户，建议专属客服回访 + 大额优惠券")
        else:
            st.error("**优先干预**：高风险年合同客户，建议提前沟通续约问题")
    elif prob >= 0.3:
        st.warning("**预防维护**：建议推送个性化推荐或VIP福利，防止降级")
    else:
        st.success("**常规维护**：保持当前满意度即可")

    st.markdown("---")
    st.subheader("📊 主要流失驱动因素")
    st.markdown("""
    - 📞 客服呼叫次数 ≥ 4 → 流失率超 **50%**
    - 📅 距上次购买 > 15天 + 订阅 ≤ 3个月 → **高危画像**
    - 📄 月合同客户流失率显著高于年合同
    """)
