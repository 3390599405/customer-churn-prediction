import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go

st.set_page_config(page_title="ChurnGuard 客户流失预警", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    * { font-family: 'Inter', 'Microsoft YaHei', sans-serif; }
    .hero {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        padding: 2.5rem 2rem; border-radius: 20px; text-align: center;
        color: white; margin-bottom: 2rem;
    }
    .hero h1 { font-size: 2.8rem; font-weight: 800; margin: 0; }
    .hero p { font-size: 1.05rem; opacity: .75; margin-top: .5rem; }
    .card {
        background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.08);
        border-radius: 14px; padding: 1.5rem; margin-bottom: 1.5rem;
        backdrop-filter: blur(4px);
    }
    .result-card {
        background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.08);
        border-radius: 14px; padding: 1.2rem; text-align: center;
        backdrop-filter: blur(4px);
    }
    .result-card .value { font-size: 2.2rem; font-weight: 800; }
    .result-card .label { font-size: .8rem; opacity: .6; text-transform: uppercase; letter-spacing: 1px; }
    .risk-high .value { color: #ff4757; }
    .risk-mid .value { color: #ffa502; }
    .risk-low .value { color: #2ed573; }
    @media (max-width: 768px) {
        .hero { padding: 1.5rem 1rem; }
        .hero h1 { font-size: 1.8rem; }
        .row-widget.stColumns { flex-direction: column !important; gap: 0.3rem !important; }
        .row-widget.stColumns > div { width: 100% !important; flex: none !important; }
    }
    .stApp { background: #0d0d1a; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>⚡ ChurnGuard</h1><p>AI 智能客户流失预警系统 · 精准识别 · 分层干预 · 降低流失</p></div>', unsafe_allow_html=True)

@st.cache_resource
def load_model():
    data = joblib.load('churn_model.pkl')
    return data['model'], data['scaler'], data['feature_columns']

model, scaler, feature_cols = load_model()

@st.cache_data
def load_data():
    df = pd.read_csv('ecommerce_customer_churn_data.csv')
    churned = df[df['Is_Churn'] == 1]
    retained = df[df['Is_Churn'] == 0]
    return df, churned, retained

df, churned, retained = load_data()

st.markdown('<div class="card"><h3>📋 客户信息录入</h3>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    age = st.number_input("年龄", 18, 70, 35)
    subscription = st.number_input("订阅月数", 1, 60, 12)
    logins = st.number_input("月登录次数", 1, 30, 10)
    last_purchase = st.number_input("距上次购买天数", 0, 90, 10)
with col2:
    app_usage = st.number_input("App 使用时长(分钟/天)", 1.0, 70.0, 20.0)
    spending = st.number_input("月消费金额($)", 10.0, 2000.0, 100.0)
    discount = st.number_input("折扣使用比例", 0.0, 1.0, 0.2)
    support_calls = st.number_input("近30天客服呼叫次数", 0, 10, 1)
with col3:
    satisfaction = st.number_input("满意度评分", 1, 5, 4)
    contract = st.selectbox("合同类型", ["月合同", "年合同"])
st.markdown('</div>', unsafe_allow_html=True)

if st.button("🔮 预测流失风险", type="primary", use_container_width=True):
    contract_val = 1 if contract == "月合同" else 0
    input_data = pd.DataFrame([[age, subscription, logins, last_purchase,
                                app_usage, spending, discount, support_calls,
                                satisfaction, contract_val]],
                              columns=feature_cols)
    scaled = scaler.transform(input_data)
    prob = model.predict_proba(scaled)[0, 1]

    if prob >= 0.7:
        risk_label, risk_cls = "高风险", "risk-high"
        risk_icon = "🔴"
    elif prob >= 0.3:
        risk_label, risk_cls = "中风险", "risk-mid"
        risk_icon = "🟡"
    else:
        risk_label, risk_cls = "低风险", "risk-low"
        risk_icon = "🟢"

    pred_label = "⚠️ 可能流失" if prob >= 0.3 else "✅ 相对稳定"

    st.markdown("---")
    st.markdown("### 📊 预测结果")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="result-card {risk_cls}"><div class="label">流失概率</div><div class="value">{prob:.1%}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="result-card {risk_cls}"><div class="label">预测结论</div><div class="value">{pred_label}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="result-card {risk_cls}"><div class="label">风险等级</div><div class="value">{risk_icon} {risk_label}</div></div>', unsafe_allow_html=True)

    # ── 雷达图 ──
    st.markdown("---")
    st.markdown("### 🎯 客户画像对比 — 与市场基准对标")

    radar_metrics = [
        ('月消费金额', min(df['Monthly_Spend']), max(df['Monthly_Spend']), spending),
        ('订阅时长', min(df['Subscription_Duration_Months']), max(df['Subscription_Duration_Months']), subscription),
        ('月登录次数', min(df['Monthly_Logins']), max(df['Monthly_Logins']), logins),
        ('App 使用时长', min(df['App_Usage_Time_Min']), max(df['App_Usage_Time_Min']), app_usage),
        ('满意度评分', 1, 5, satisfaction),
    ]

    cats, this_val, avg_retained, avg_churned = [], [], [], []

    for name, lo, hi, val in radar_metrics:
        cats.append(name)
        this_val.append(round((val - lo) / (hi - lo), 3))
    cols_map = {
        '月消费金额': 'Monthly_Spend', '订阅时长': 'Subscription_Duration_Months',
        '月登录次数': 'Monthly_Logins', 'App 使用时长': 'App_Usage_Time_Min',
        '满意度评分': 'Satisfaction_Score'
    }
    for name, lo, hi, _ in radar_metrics:
        col = cols_map[name]
        avg_retained.append(round((retained[col].mean() - lo) / (hi - lo), 3))
        avg_churned.append(round((churned[col].mean() - lo) / (hi - lo), 3))

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(r=this_val + [this_val[0]], theta=cats + [cats[0]],
                                        name='当前客户', fill='toself',
                                        line=dict(color='#7c4dff', width=2.5),
                                        marker=dict(size=6, color='#7c4dff')))
    fig_radar.add_trace(go.Scatterpolar(r=avg_retained + [avg_retained[0]], theta=cats + [cats[0]],
                                        name='留存客户平均', fill='toself',
                                        line=dict(color='#2ed573', width=2, dash='dot'),
                                        opacity=0.7))
    fig_radar.add_trace(go.Scatterpolar(r=avg_churned + [avg_churned[0]], theta=cats + [cats[0]],
                                        name='流失客户平均', fill='toself',
                                        line=dict(color='#ff4757', width=2, dash='dot'),
                                        opacity=0.7))

    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1.05], tickvals=[0, .25, .5, .75, 1],
                                   tickfont=dict(size=10, color='#888')),
                   bgcolor='rgba(0,0,0,0)', gridshape='circular'),
        legend=dict(orientation='h', yanchor='bottom', y=-0.25, font=dict(size=12, color='#aaa')),
        height=420, margin=dict(l=60, r=60, t=20, b=60),
        paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#ccc', size=11),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    gcol1, gcol2 = st.columns([1, 1])
    with gcol1:
        st.markdown("#### 💡 干预建议")
        if prob >= 0.7:
            if contract == "月合同":
                st.error("**优先干预** — 高风险月合同客户，建议专属客服回访 + 大额优惠券")
            else:
                st.error("**优先干预** — 高风险年合同客户，建议提前沟通续约问题")
        elif prob >= 0.3:
            st.warning("**预防维护** — 推送个性化推荐或 VIP 福利，防止降级")
        else:
            st.success("**常规维护** — 保持当前满意度即可")

    with gcol2:
        st.markdown("#### 🔍 关键发现")
        diffs = []
        for i, name in enumerate([m[0] for m in radar_metrics]):
            d = this_val[i] - avg_retained[i]
            diffs.append((name, d))
        diffs.sort(key=lambda x: x[1])
        worst = diffs[0]
        if worst[1] < -0.08:
            st.markdown(f"- ⚠️ **{worst[0]}** 显著低于留存客户均值")
        best = diffs[-1]
        if best[1] > 0.08:
            st.markdown(f"- ✅ **{best[0]}** 高于平均水平")
        st.markdown(f"- 📊 客户健康度评分 **{max(0, min(100, int((1 - prob) * 100)))}/100**")
