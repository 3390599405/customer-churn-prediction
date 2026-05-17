import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go

st.set_page_config(page_title="ChurnGuard", layout="wide", initial_sidebar_state="collapsed")

# ── CSS ──
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .hero {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        padding: 2.5rem 2rem; border-radius: 20px; text-align: center;
        color: white; margin-bottom: 2rem;
    }
    .hero h1 { font-size: 2.8rem; font-weight: 800; margin: 0; letter-spacing: -0.5px; }
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
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>⚡ ChurnGuard</h1><p>AI-powered customer churn prediction · Identify · Prioritize · Retain</p></div>', unsafe_allow_html=True)

# ── 加载模型 + 数据 ──
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

# ── 输入区 ──
st.markdown('<div class="card"><h3>📋 Customer Profile</h3>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    age = st.number_input("Age", 18, 70, 35)
    subscription = st.number_input("Subscription (months)", 1, 60, 12)
    logins = st.number_input("Monthly Logins", 1, 30, 10)
    last_purchase = st.number_input("Days Since Last Purchase", 0, 90, 10)
with col2:
    app_usage = st.number_input("App Usage (min/day)", 1.0, 70.0, 20.0)
    spending = st.number_input("Monthly Spend ($)", 10.0, 2000.0, 100.0)
    discount = st.number_input("Discount Usage Rate", 0.0, 1.0, 0.2)
    support_calls = st.number_input("Support Calls (last 30d)", 0, 10, 1)
with col3:
    satisfaction = st.number_input("Satisfaction Score", 1, 5, 4)
    contract = st.selectbox("Contract Type", ["Monthly", "Annual"])
st.markdown('</div>', unsafe_allow_html=True)

# ── 预测 ──
if st.button("🔮 Predict Churn Risk", type="primary", use_container_width=True):
    input_data = pd.DataFrame([[age, subscription, logins, last_purchase,
                                app_usage, spending, discount, support_calls,
                                satisfaction, 1 if contract == "Monthly" else 0]],
                              columns=feature_cols)
    scaled = scaler.transform(input_data)
    prob = model.predict_proba(scaled)[0, 1]

    if prob >= 0.7:
        risk_label, risk_cls = "High Risk", "risk-high"
        risk_icon = "🔴"
    elif prob >= 0.3:
        risk_label, risk_cls = "Medium Risk", "risk-mid"
        risk_icon = "🟡"
    else:
        risk_label, risk_cls = "Low Risk", "risk-low"
        risk_icon = "🟢"

    pred_label = "At Risk ⚠️" if prob >= 0.3 else "Stable ✅"

    # ── 结果卡片 ──
    st.markdown("---")
    st.markdown("### 📊 Prediction Result")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="result-card {risk_cls}"><div class="label">Churn Probability</div><div class="value">{prob:.1%}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="result-card {risk_cls}"><div class="label">Prediction</div><div class="value">{pred_label}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="result-card {risk_cls}"><div class="label">Risk Level</div><div class="value">{risk_icon} {risk_label}</div></div>', unsafe_allow_html=True)

    # ── 雷达图 ──
    st.markdown("---")
    st.markdown("### 🎯 Customer Profile vs. Market Benchmarks")

    # 定义雷达指标：选取关键数值特征，统计流失/留存群体的均值
    radar_metrics = [
        ('Monthly Spend ($)', min(df['Monthly_Spend']), max(df['Monthly_Spend']), spending),
        ('Subscription (months)', min(df['Subscription_Duration_Months']), max(df['Subscription_Duration_Months']), subscription),
        ('Monthly Logins', min(df['Monthly_Logins']), max(df['Monthly_Logins']), logins),
        ('App Usage (min)', min(df['App_Usage_Time_Min']), max(df['App_Usage_Time_Min']), app_usage),
        ('Satisfaction Score', 1, 5, satisfaction),
    ]

    # 归一化 0-1
    cats = []
    this_val = []
    avg_retained = []
    avg_churned = []

    for name, lo, hi, val in radar_metrics:
        cats.append(name)
        this_val.append(round((val - lo) / (hi - lo), 3))
    for name, lo, hi, _ in radar_metrics:
        if name == 'Satisfaction Score':
            avg_retained.append(round((retained['Satisfaction_Score'].mean() - lo) / (hi - lo), 3))
            avg_churned.append(round((churned['Satisfaction_Score'].mean() - lo) / (hi - lo), 3))
        elif name == 'Monthly Spend ($)':
            avg_retained.append(round((retained['Monthly_Spend'].mean() - lo) / (hi - lo), 3))
            avg_churned.append(round((churned['Monthly_Spend'].mean() - lo) / (hi - lo), 3))
        elif name == 'Subscription (months)':
            avg_retained.append(round((retained['Subscription_Duration_Months'].mean() - lo) / (hi - lo), 3))
            avg_churned.append(round((churned['Subscription_Duration_Months'].mean() - lo) / (hi - lo), 3))
        elif name == 'Monthly Logins':
            avg_retained.append(round((retained['Monthly_Logins'].mean() - lo) / (hi - lo), 3))
            avg_churned.append(round((churned['Monthly_Logins'].mean() - lo) / (hi - lo), 3))
        elif name == 'App Usage (min)':
            avg_retained.append(round((retained['App_Usage_Time_Min'].mean() - lo) / (hi - lo), 3))
            avg_churned.append(round((churned['App_Usage_Time_Min'].mean() - lo) / (hi - lo), 3))

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(r=this_val + [this_val[0]], theta=cats + [cats[0]],
                                        name='This Customer', fill='toself',
                                        line=dict(color='#7c4dff', width=2.5),
                                        marker=dict(size=6, color='#7c4dff')))
    fig_radar.add_trace(go.Scatterpolar(r=avg_retained + [avg_retained[0]], theta=cats + [cats[0]],
                                        name='Retained Customers', fill='toself',
                                        line=dict(color='#2ed573', width=2, dash='dot'),
                                        opacity=0.7))
    fig_radar.add_trace(go.Scatterpolar(r=avg_churned + [avg_churned[0]], theta=cats + [cats[0]],
                                        name='Churned Customers', fill='toself',
                                        line=dict(color='#ff4757', width=2, dash='dot'),
                                        opacity=0.7))

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1.05], tickvals=[0, .25, .5, .75, 1],
                            tickfont=dict(size=10, color='#888')),
            bgcolor='rgba(0,0,0,0)',
            gridshape='circular'
        ),
        legend=dict(orientation='h', yanchor='bottom', y=-0.25, font=dict(size=12, color='#aaa')),
        height=420, margin=dict(l=60, r=60, t=20, b=60),
        paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#ccc', size=11),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # ── 雷达解读 ──
    gcol1, gcol2 = st.columns([1, 1])
    with gcol1:
        st.markdown("#### 💡 Recommended Action")
        if prob >= 0.7:
            if contract == "Monthly":
                st.error("**Priority intervention** — High-risk monthly contract client. Assign dedicated support + substantial discount offer.")
            else:
                st.error("**Priority intervention** — High-risk annual contract client. Proactive renewal discussion recommended.")
        elif prob >= 0.3:
            st.warning("**Preventive care** — Push personalized recommendations or VIP benefits to prevent downgrade.")
        else:
            st.success("**Routine maintenance** — Keep current satisfaction levels. No urgent action needed.")

    with gcol2:
        st.markdown("#### 🔍 Key Insights")
        # 找出客户偏离最大的指标
        diffs = []
        for i, name in enumerate([m[0] for m in radar_metrics]):
            d = this_val[i] - avg_retained[i]
            diffs.append((name, d))
        diffs.sort(key=lambda x: x[1])
        worst = diffs[0]
        if worst[1] < -0.08:
            st.markdown(f"- ⚠️ **{worst[0]}** is significantly below retained customers")
        best = diffs[-1]
        if best[1] > 0.08:
            st.markdown(f"- ✅ **{best[0]}** is above average — good sign")
        st.markdown(f"- 📊 Customer scores **{max(0, min(100, int((1 - prob) * 100)))}/100** vs. retained baseline")
