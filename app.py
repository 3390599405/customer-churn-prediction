import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="ChurnGuard", layout="wide", initial_sidebar_state="collapsed")

# ═══════════════════════════════ CSS ═══════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600;700&display=swap');

    * { font-family: 'Space Grotesk', system-ui, sans-serif; color: #e2e2f0; }
    .stApp {
        background: linear-gradient(160deg, #0b0a1a 0%, #141430 45%, #1e1e3a 100%) !important;
    }

    h1, h2, h3, h4 { font-family: 'Space Grotesk', sans-serif !important; font-weight: 700 !important; letter-spacing: -.02em; }

    /* ── Hero 区域（带光晕 halo）── */
    .hero {
        position: relative; overflow: hidden;
        background: linear-gradient(135deg, rgba(120,80,255,.10) 0%, rgba(80,120,255,.06) 100%);
        border: 1px solid rgba(120,80,255,.15);
        padding: 2.5rem 2rem; border-radius: 20px; text-align: center; margin-bottom: 2rem;
    }
    .hero::before {
        content: ''; position: absolute; top: -50%; left: 50%; translate: -50% 0;
        width: 500px; height: 500px;
        background: radial-gradient(circle, rgba(120,80,255,.15) 0%, transparent 70%);
        pointer-events: none;
    }
    .hero h1 { font-size: 2.6rem; margin: 0; position: relative; }
    .hero p { font-size: 1rem; opacity: .5; margin-top: .4rem; position: relative; }

    /* ── 通用卡片 ── */
    .card {
        background: rgba(255,255,255,.035); border: 1px solid rgba(255,255,255,.06);
        border-radius: 14px; padding: 1.5rem; margin-bottom: 1.25rem;
    }
    .card h3 { margin: 0 0 .2rem 0; color: #e0e0f0; font-size: 1.05rem; }
    .card .sub { font-size: .8rem; opacity: .4; margin-bottom: .8rem; }

    /* ── 结果卡片（顶部彩色状态条）── */
    .result-card {
        background: rgba(255,255,255,.035); border: 1px solid rgba(255,255,255,.06);
        border-radius: 14px; padding: 1.2rem; text-align: center; position: relative;
        overflow: hidden;
    }
    .result-card::before {
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    }
    .risk-high.result-card::before { background: linear-gradient(90deg, #f87171, #fb923c); }
    .risk-mid.result-card::before  { background: linear-gradient(90deg, #fbbf24, #f59e0b); }
    .risk-low.result-card::before  { background: linear-gradient(90deg, #34d399, #10b981); }
    .result-card .value {
        font-family: 'JetBrains Mono', monospace; font-size: 2rem; font-weight: 700;
    }
    .result-card .label { font-size: .75rem; opacity: .45; text-transform: uppercase; letter-spacing: 1px; }
    .risk-high .value { color: #f87171; }
    .risk-mid .value { color: #fbbf24; }
    .risk-low .value { color: #34d399; }

    /* ── 报告头部 ── */
    .report-header { border-left: 3px solid #a78bfa; padding-left: 1rem; margin-bottom: 1.2rem; }
    .report-header h2 { margin: 0; color: #f0f0ff; }
    .report-header .meta { font-size: .8rem; opacity: .4; }

    /* ── 表格 ── */
    table { width: 100%; border-collapse: collapse; font-size: .85rem; }
    th, td { padding: .5rem .7rem; text-align: left; border-bottom: 1px solid rgba(255,255,255,.05); }
    th { font-weight: 600; opacity: .45; font-size: .7rem; text-transform: uppercase; letter-spacing: .5px; }
    td { font-family: 'JetBrains Mono', monospace; font-size: .82rem; }
    td:first-child { font-family: 'Space Grotesk', sans-serif; }

    /* ── 输入框聚焦效果 ── */
    .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        font-family: 'JetBrains Mono', monospace !important;
    }
    .stNumberInput input:focus, .stSelectbox div[data-baseweb="select"]:focus-within {
        border-color: #7b6fff !important; box-shadow: 0 0 0 3px rgba(123,111,255,.15) !important;
    }
    .st-bb { border-color: rgba(255,255,255,.08); }

    /* ── 按钮 hover 光晕 ── */
    .stButton button {
        font-weight: 600 !important; border-radius: 10px !important;
        transition: all .25s ease !important;
    }
    .stButton button:hover {
        box-shadow: 0 0 30px rgba(120,80,255,.35), 0 4px 15px rgba(120,80,255,.2) !important;
        transform: translateY(-1px);
    }

    /* ── 徽章标签 ── */
    .badge {
        display: inline-block; font-size: .7rem; font-weight: 600;
        padding: 2px 10px; border-radius: 20px; letter-spacing: .3px;
    }
    .badge-red { background: rgba(248,113,113,.12); color: #f87171; }
    .badge-amber { background: rgba(251,191,36,.12); color: #fbbf24; }
    .badge-green { background: rgba(52,211,153,.12); color: #34d399; }

    /* ── 百分位小卡片 ── */
    .pctl-card {
        background: rgba(255,255,255,.035); border: 1px solid rgba(255,255,255,.06);
        border-radius: 12px; padding: .8rem .4rem; text-align: center;
        transition: transform .15s;
    }
    .pctl-card:hover { transform: translateY(-2px); }

    /* ── 财务估算表 ── */
    .fin-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: .5rem 0; border-bottom: 1px solid rgba(255,255,255,.05);
    }
    .fin-row:last-child { border-bottom: none; }
    .fin-row .fin-label { font-size: .85rem; opacity: .65; }
    .fin-row .fin-value { font-family: 'JetBrains Mono', monospace; font-weight: 600; }

    /* ── 风险因子进度条 ── */
    .risk-bar {
        background: rgba(255,255,255,.05); border-radius: 10px; height: 8px; overflow: hidden;
        margin: .35rem 0 .7rem 0;
    }
    .risk-bar-fill {
        height: 100%; border-radius: 10px;
        background: linear-gradient(90deg, #f87171, #fb923c);
    }
    .risk-bar-fill.med { background: linear-gradient(90deg, #fbbf24, #f59e0b); }
    .risk-bar-fill.low { background: linear-gradient(90deg, #34d399, #10b981); }

    /* ── 移动端 ── */
    @media (max-width: 768px) {
        .hero { padding: 1.5rem 1rem; }
        .hero h1 { font-size: 1.8rem; }
        .row-widget.stColumns { flex-direction: column !important; gap: .25rem !important; }
        .row-widget.stColumns > div { width: 100% !important; flex: none !important; }
        .card, .result-card { padding: 1rem; }
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════ 页面内容 ═══════════════════════════════

st.markdown("""
<div class="hero">
    <h1 style="background:linear-gradient(135deg,#a78bfa,#818cf8);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
        <span style="-webkit-text-fill-color:initial;">⚡</span> ChurnGuard
    </h1>
    <p>AI 智能客户流失预警系统 · 精准识别 · 分层干预 · 降低流失</p>
</div>
""", unsafe_allow_html=True)

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

@st.cache_data
def get_percentiles():
    pcts = {}
    for col in ['Monthly_Spend', 'Subscription_Duration_Months', 'Monthly_Logins',
                'App_Usage_Time_Min', 'Satisfaction_Score']:
        pcts[col] = df[col].describe(percentiles=[.1, .25, .5, .75, .9])
    return pcts

pcts = get_percentiles()

st.markdown('<div class="card"><h3>📋 客户信息录入</h3><div class="sub">请输入客户的基本行为数据</div>', unsafe_allow_html=True)
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

    # ════════════════════════════════════════
    # 📄 详细分析报告
    # ════════════════════════════════════════
    st.markdown("---")

    report_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.markdown(f"""
    <div class="report-header">
        <h2>📄 客户流失风险评估报告</h2>
        <div class="meta">报告生成时间：{report_time} ｜ 模型版本：v1.0（随机森林）</div>
    </div>
    """, unsafe_allow_html=True)

    # ── 1️⃣ 风险评分总览 ──
    st.markdown("### 1️⃣ 风险评分总览")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="result-card {risk_cls}"><div class="label">流失概率</div><div class="value">{prob:.1%}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="result-card {risk_cls}"><div class="label">预测结论</div><div class="value">{pred_label}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="result-card {risk_cls}"><div class="label">风险等级</div><div class="value">{risk_icon} {risk_label}</div></div>', unsafe_allow_html=True)
    health_score = max(0, min(100, int((1 - prob) * 100)))
    with c4:
        st.markdown(f'<div class="result-card {risk_cls}"><div class="label">健康度评分</div><div class="value">{health_score}<span style="font-size:1rem;font-family:Space Grotesk,sans-serif">/100</span></div></div>', unsafe_allow_html=True)

    # ── 2️⃣ 关键指标对比 ──
    st.markdown("### 2️⃣ 关键指标对比分析")
    st.markdown("将当前客户的关键指标与**留存客户均值**和**流失客户均值**进行对比，识别异常信号。")

    def badge_of(v, status):
        if "🔴" in status: return f'<span class="badge badge-red">{v}</span>'
        if "🟢" in status: return f'<span class="badge badge-green">{v}</span>'
        return f'<span class="badge badge-amber">{v}</span>'

    metrics_table = [
        ("💳 月消费金额", f"${spending:.0f}", f"${retained['Monthly_Spend'].mean():.0f}", f"${churned['Monthly_Spend'].mean():.0f}", "偏低" if spending < retained['Monthly_Spend'].mean() * 0.7 else "正常"),
        ("📆 订阅时长", f"{subscription}个月", f"{retained['Subscription_Duration_Months'].mean():.0f}个月", f"{churned['Subscription_Duration_Months'].mean():.0f}个月", "偏短" if subscription < retained['Subscription_Duration_Months'].mean() * 0.7 else "正常"),
        ("🔑 月登录次数", f"{logins}次", f"{retained['Monthly_Logins'].mean():.0f}次", f"{churned['Monthly_Logins'].mean():.0f}次", "偏低" if logins < retained['Monthly_Logins'].mean() * 0.7 else "正常"),
        ("📱 App使用时长", f"{app_usage}分钟", f"{retained['App_Usage_Time_Min'].mean():.0f}分钟", f"{churned['App_Usage_Time_Min'].mean():.0f}分钟", "偏少" if app_usage < retained['App_Usage_Time_Min'].mean() * 0.7 else "正常"),
        ("⭐ 满意度评分", f"{satisfaction}/5", f"{retained['Satisfaction_Score'].mean():.1f}/5", f"{churned['Satisfaction_Score'].mean():.1f}/5", "偏低" if satisfaction < 3 else "正常"),
        ("📞 客服呼叫次数", f"{support_calls}次", f"{retained['Customer_Support_Calls'].mean():.1f}次", f"{churned['Customer_Support_Calls'].mean():.1f}次", "偏高" if support_calls >= 4 else "正常"),
        ("🎫 折扣使用比例", f"{discount:.0%}", f"{retained['Discount_Usage_Percentage'].mean():.0%}", f"{churned['Discount_Usage_Percentage'].mean():.0%}", "偏高" if discount > 0.5 else "正常"),
        ("📅 距上次购买", f"{last_purchase}天", f"{retained['Last_Purchase_Days_Ago'].mean():.0f}天", f"{churned['Last_Purchase_Days_Ago'].mean():.0f}天", "偏长" if last_purchase > 15 else "正常"),
        ("📄 合同类型", "月合同" if contract_val else "年合同", "—", "—", "月合同" if contract_val else "年合同"),
    ]
    clr = {"正常": "badge-green", "偏低": "badge-red", "偏短": "badge-red", "偏少": "badge-red", "偏高": "badge-red", "偏长": "badge-red", "月合同": "badge-red", "年合同": "badge-green"}

    html = "<table><thead><tr><th>指标</th><th>当前客户</th><th>留存客户均值</th><th>流失客户均值</th><th>状态</th></tr></thead><tbody>"
    for r in metrics_table:
        badge_cls = clr.get(r[4], "badge-amber")
        html += f"<tr><td>{r[0]}</td><td><strong>{r[1]}</strong></td><td>{r[2]}</td><td>{r[3]}</td><td><span class='badge {badge_cls}'>{r[4]}</span></td></tr>"
    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)

    # ── 3️⃣ 风险因子诊断 ──
    st.markdown("### 3️⃣ 风险因子诊断")
    st.markdown("以下因子对该客户的流失风险贡献最大，按影响程度从高到低排序。")

    factors = [
        ("客服呼叫次数", support_calls / max(retained['Customer_Support_Calls'].mean(), 0.1), "呼叫越多风险越高"),
        ("距上次购买天数", last_purchase / max(retained['Last_Purchase_Days_Ago'].mean(), 1), "越久未购买越危险"),
        ("月消费金额", retained['Monthly_Spend'].mean() / max(spending, 1), "消费越低越危险"),
        ("订阅时长", retained['Subscription_Duration_Months'].mean() / max(subscription, 1), "订阅越短越危险"),
        ("月登录次数", retained['Monthly_Logins'].mean() / max(logins, 1), "登录越少越危险"),
        ("App使用时长", retained['App_Usage_Time_Min'].mean() / max(app_usage, 1), "使用越少越危险"),
        ("满意度评分", max(satisfaction, 1) / 5, "满意度越低越危险"),
        ("折扣依赖度", discount / max(retained['Discount_Usage_Percentage'].mean(), 0.01), "折扣依赖越高越危险"),
    ]
    if contract_val:
        factors.append(("合同类型（月合同）", 3.0, "月合同流失率显著更高"))

    factors.sort(key=lambda x: x[1], reverse=True)
    max_score = max(factors[0][1], 0.1)

    for i, (name, score, reason) in enumerate(factors[:5], 1):
        pct = min(score / max_score, 1.0)
        bar_cls = "" if pct > 0.7 else "med" if pct > 0.4 else "low"
        risk_tag = "高风险" if pct > 0.7 else "中风险" if pct > 0.4 else "低风险"
        tag_cls = "badge-red" if pct > 0.7 else "badge-amber" if pct > 0.4 else "badge-green"
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:.6rem;margin:.3rem 0">
            <strong style="font-size:.9rem;min-width:8rem;">#{i} {name}</strong>
            <span class="badge {tag_cls}">{risk_tag}</span>
            <span style="font-size:.78rem;opacity:.45;">{reason}</span>
        </div>
        <div class="risk-bar"><div class="risk-bar-fill {bar_cls}" style="width:{pct*100:.0f}%"></div></div>
        """, unsafe_allow_html=True)

    # ── 4️⃣ 同业百分位定位 ──
    st.markdown("### 4️⃣ 同业百分位定位")
    st.markdown("该客户在全体客户中的位置（百分位越高 = 表现越好）")

    percentile_items = [
        ("月消费金额", spending, df['Monthly_Spend']),
        ("订阅时长", subscription, df['Subscription_Duration_Months']),
        ("月登录次数", logins, df['Monthly_Logins']),
        ("App使用时长", app_usage, df['App_Usage_Time_Min']),
        ("满意度评分", satisfaction, df['Satisfaction_Score']),
    ]

    pcols = st.columns(5)
    for idx, (label, val, series) in enumerate(percentile_items):
        p = (series <= val).mean() * 100
        with pcols[idx]:
            color = "#34d399" if p > 50 else "#fbbf24" if p > 25 else "#f87171"
            st.markdown(f"""
            <div class="pctl-card">
                <div style="font-size:.68rem;opacity:.5;margin-bottom:.2rem;">{label}</div>
                <div style="font-size:1.8rem;font-weight:700;color:{color};font-family:'JetBrains Mono',monospace;">{p:.0f}</div>
                <div style="font-size:.65rem;opacity:.4;">高于 {p:.0f}% 的客户</div>
            </div>
            """, unsafe_allow_html=True)

    # ── 5️⃣ 雷达图 ──
    st.markdown("### 5️⃣ 客户画像可视化")
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
        '月登录次数': 'Monthly_Logins', 'App 使用时长': 'App_Usage_Time_Min', '满意度评分': 'Satisfaction_Score'
    }
    for name, lo, hi, _ in radar_metrics:
        col = cols_map[name]
        avg_retained.append(round((retained[col].mean() - lo) / (hi - lo), 3))
        avg_churned.append(round((churned[col].mean() - lo) / (hi - lo), 3))
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(r=this_val + [this_val[0]], theta=cats + [cats[0]],
        name='当前客户', fill='toself', line=dict(color='#a78bfa', width=2.5), marker=dict(size=6, color='#a78bfa')))
    fig_radar.add_trace(go.Scatterpolar(r=avg_retained + [avg_retained[0]], theta=cats + [cats[0]],
        name='留存客户平均', fill='toself', line=dict(color='#34d399', width=2, dash='dot'), opacity=0.7))
    fig_radar.add_trace(go.Scatterpolar(r=avg_churned + [avg_churned[0]], theta=cats + [cats[0]],
        name='流失客户平均', fill='toself', line=dict(color='#f87171', width=2, dash='dot'), opacity=0.7))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1.05], tickvals=[0, .25, .5, .75, 1],
                                   tickfont=dict(size=10, color='#888')),
                   bgcolor='rgba(0,0,0,0)', gridshape='circular'),
        legend=dict(orientation='h', yanchor='bottom', y=-0.25, font=dict(size=12, color='#aaa')),
        height=420, margin=dict(l=60, r=60, t=20, b=60),
        paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#ccc', size=11),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # ── 6️⃣ 个性化干预方案 ──
    st.markdown("### 6️⃣ 个性化干预方案")

    action_col1, action_col2 = st.columns([1, 1])
    with action_col1:
        if prob >= 0.7:
            if contract == "月合同":
                st.markdown("""
                <div style="background:rgba(248,113,113,.08);border:1px solid rgba(248,113,113,.15);border-radius:12px;padding:1rem;margin-bottom:.8rem;">
                    <strong style="color:#f87171;">🔴 最高优先级 — 立即干预</strong>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("""
                - 📞 **专属客服回访**：48 小时内电话联系
                - 🎫 **大额优惠券**：发送 20% 折扣券 + 免运费
                - 📱 **推送个性化推荐**：基于历史购买记录
                """)
            else:
                st.markdown("""
                <div style="background:rgba(248,113,113,.08);border:1px solid rgba(248,113,113,.15);border-radius:12px;padding:1rem;margin-bottom:.8rem;">
                    <strong style="color:#f87171;">🔴 最高优先级 — 立即干预</strong>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("""
                - 📞 **客户成功经理对接**：提前沟通续约
                - 🎁 **VIP 专属权益**：赠送额外服务包
                - 📊 **使用情况审查**：排查未充分利用的功能
                """)
        elif prob >= 0.3:
            st.markdown("""
            <div style="background:rgba(251,191,36,.08);border:1px solid rgba(251,191,36,.15);border-radius:12px;padding:1rem;margin-bottom:.8rem;">
                <strong style="color:#fbbf24;">🟡 中等优先级 — 预防维护</strong>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            - 🎯 **精准推送**：基于偏好推荐相关商品
            - 👑 **VIP 福利提醒**：告知可用积分/权益
            - 📧 **定期关怀邮件**：保持品牌粘性
            """)
        else:
            st.markdown("""
            <div style="background:rgba(52,211,153,.08);border:1px solid rgba(52,211,153,.15);border-radius:12px;padding:1rem;margin-bottom:.8rem;">
                <strong style="color:#34d399;">🟢 低优先级 — 常规维护</strong>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            - ✅ **维持现状**：当前满意度表现良好
            - 📬 **常规推送**：保持正常营销触达
            - 📈 **月度监控**：定期检查指标变化
            """)

    with action_col2:
        if prob >= 0.5:
            annual_value = int(spending * 12)
            recovery = int(spending * 12 * 0.3)
            st.markdown("""
            <div style="background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.06);border-radius:12px;padding:1rem 1.2rem;">
                <div style="font-weight:600;margin-bottom:.6rem;font-size:.9rem;">💰 财务影响估算</div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="fin-row"><span class="fin-label">若不干预流失概率</span><span class="fin-value" style="color:#f87171;">{prob:.0%}</span></div>
            <div class="fin-row"><span class="fin-label">预估客户年价值</span><span class="fin-value" style="color:#a78bfa;">${annual_value}</span></div>
            <div class="fin-row"><span class="fin-label">干预后留存提升</span><span class="fin-value" style="color:#34d399;">约 30%</span></div>
            <div class="fin-row"><span class="fin-label">预期挽回价值</span><span class="fin-value" style="color:#fbbf24;font-size:1.1rem;">${recovery}</span></div>
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            annual_value = int(spending * 12)
            st.markdown("""
            <div style="background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.06);border-radius:12px;padding:1rem 1.2rem;">
                <div style="font-weight:600;margin-bottom:.6rem;font-size:.9rem;">💰 客户价值概览</div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="fin-row"><span class="fin-label">流失风险</span><span class="fin-value" style="color:#34d399;">低风险</span></div>
            <div class="fin-row"><span class="fin-label">预估客户年价值</span><span class="fin-value" style="color:#a78bfa;">${annual_value}</span></div>
            <div class="fin-row"><span class="fin-label">建议策略</span><span class="fin-value" style="color:#34d399;">常规维护</span></div>
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.caption("报告由 ChurnGuard AI 引擎自动生成 ｜ 基于随机森林 + SMOTE 模型，AUC=0.90")
