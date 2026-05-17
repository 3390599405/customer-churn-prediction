import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="ChurnGuard", layout="wide", initial_sidebar_state="collapsed")

# ── 顶部 Banner ──
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    * { font-family: 'Inter', sans-serif; }

    .hero {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        padding: 2.5rem 2rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    .hero h1 { font-size: 2.8rem; font-weight: 800; margin: 0; letter-spacing: -0.5px; }
    .hero p { font-size: 1.05rem; opacity: .75; margin-top: .5rem; }
    .card {
        background: rgba(255,255,255,.04);
        border: 1px solid rgba(255,255,255,.08);
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(4px);
    }
    .card h3 { margin-top: 0; font-weight: 600; font-size: 1.1rem; color: #e0e0e0; }
    .stNumberInput label, .stSelectbox label { font-weight: 500; font-size: 0.85rem; }

    /* 结果卡片 */
    .result-card {
        background: rgba(255,255,255,.04);
        border: 1px solid rgba(255,255,255,.08);
        border-radius: 14px;
        padding: 1.2rem;
        text-align: center;
        backdrop-filter: blur(4px);
    }
    .result-card .value { font-size: 2.2rem; font-weight: 800; }
    .result-card .label { font-size: .8rem; opacity: .6; text-transform: uppercase; letter-spacing: 1px; }

    .risk-high .value { color: #ff4757; }
    .risk-mid .value { color: #ffa502; }
    .risk-low .value { color: #2ed573; }

    /* 移动端适配 */
    @media (max-width: 768px) {
        .hero { padding: 1.5rem 1rem; }
        .hero h1 { font-size: 1.8rem; }
        .row-widget.stColumns { flex-direction: column !important; gap: 0.3rem !important; }
        .row-widget.stColumns > div { width: 100% !important; flex: none !important; }
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>⚡ ChurnGuard</h1><p>AI-powered customer churn prediction · Identify · Prioritize · Retain</p></div>', unsafe_allow_html=True)

# ── 加载模型 ──
@st.cache_resource
def load_model():
    data = joblib.load('churn_model.pkl')
    return data['model'], data['scaler'], data['feature_columns']

model, scaler, feature_cols = load_model()

# ── 特征重要性图表（始终显示）──
feat_names = feature_cols.copy()
# 把 Contract_Type_Monthly 显示为 Contract_Type
feat_labels = [n.replace('Contract_Type_Monthly', 'Contract Type') for n in feat_names]

importances = model.feature_importances_
imp_df = pd.DataFrame({'Feature': feat_labels, 'Importance': importances}).sort_values('Importance', ascending=True)

fig_importance = px.bar(
    imp_df, x='Importance', y='Feature', orientation='h',
    title='What Drives Churn?',
    text_auto='.0%',
    color='Importance', color_continuous_scale='viridis',
    height=400
)
fig_importance.update_layout(
    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
    font=dict(size=13), margin=dict(l=10, r=10, t=40, b=10),
    xaxis_title=None, yaxis_title=None,
    coloraxis_showscale=False
)
fig_importance.update_traces(textposition='outside', cliponaxis=False)

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

# ── 特征重要性图 ──
st.plotly_chart(fig_importance, use_container_width=True)

# ── 预测 ──
if st.button("🔮 Predict Churn Risk", type="primary", use_container_width=True):
    input_data = pd.DataFrame([[age, subscription, logins, last_purchase,
                                app_usage, spending, discount, support_calls,
                                satisfaction, 1 if contract == "Monthly" else 0]],
                              columns=feature_cols)
    scaled = scaler.transform(input_data)
    prob = model.predict_proba(scaled)[0, 1]

    # 风险等级
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

    # ── 仪表盘（速度表风格）──
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=prob * 100,
        number={'suffix': '%', 'font': {'size': 36, 'color': '#e0e0e0'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': '#555'},
            'bar': {'color': '#ff4757' if prob >= 0.7 else '#ffa502' if prob >= 0.3 else '#2ed573', 'thickness': 0.3},
            'bgcolor': 'rgba(0,0,0,0)',
            'borderwidth': 0,
            'steps': [
                {'range': [0, 30], 'color': 'rgba(46,213,115,.15)'},
                {'range': [30, 70], 'color': 'rgba(255,165,2,.12)'},
                {'range': [70, 100], 'color': 'rgba(255,71,87,.12)'}
            ],
            'threshold': {
                'line': {'color': 'white', 'width': 3},
                'thickness': 0.6,
                'value': prob * 100
            }
        }
    ))
    fig_gauge.update_layout(
        height=280,
        margin=dict(l=30, r=30, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#aaa', 'family': 'Inter'}
    )

    gcol1, gcol2 = st.columns([1, 1])
    with gcol1:
        st.plotly_chart(fig_gauge, use_container_width=True)

    with gcol2:
        st.markdown("#### Recommended Action")
        if prob >= 0.7:
            if contract == "Monthly":
                st.error("**Priority intervention** — High-risk monthly contract client. Assign dedicated support + substantial discount offer.")
            else:
                st.error("**Priority intervention** — High-risk annual contract client. Proactive renewal discussion recommended.")
        elif prob >= 0.3:
            st.warning("**Preventive care** — Push personalized recommendations or VIP benefits to prevent downgrade.")
        else:
            st.success("**Routine maintenance** — Keep current satisfaction levels. No urgent action needed.")

        st.markdown("#### Key Drivers")
        top3 = imp_df.tail(3)
        for _, r in top3.iterrows():
            st.markdown(f"- **{r['Feature']}** — {r['Importance']:.1%} contribution")
