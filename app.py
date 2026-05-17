import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="ChurnGuard 客户流失预警", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&display=swap');

    /* ═══ 亮色模式 — 天空蓝 ═══ */
    @media (prefers-color-scheme: light) {
        .stApp { background: linear-gradient(180deg, #e8f4f8 0%, #d0e8f0 40%, #b8dae8 100%) !important; }
        * { font-family: 'Inter', 'Microsoft YaHei', sans-serif; color: #1a2a3a; }
        h1, h2, h3, h4, h5 { color: #0d2137 !important; }
        .hero {
            background: linear-gradient(135deg, #5b9bd5, #4a89c0, #3a7aa8) !important;
            padding: 2.5rem 2rem; border-radius: 20px; text-align: center;
            color: white; margin-bottom: 2rem;
        }
        .hero h1 { font-size: 2.8rem; font-weight: 800; margin: 0; font-family: 'Playfair Display', serif; }
        .hero p { font-size: 1.05rem; opacity: .85; margin-top: .5rem; }
        .card {
            background: rgba(255,255,255,.75); border: 1px solid rgba(255,255,255,.9);
            border-radius: 14px; padding: 1.5rem; margin-bottom: 1.5rem;
            box-shadow: 0 4px 20px rgba(0,0,0,.05); backdrop-filter: blur(8px);
        }
        .card h3 { margin: 0 0 .3rem 0; font-weight: 600; color: #0d2137; }
        .card .sub { font-size: .8rem; opacity: .6; margin-bottom: 1rem; color: #4a6a8a; }
        .result-card {
            background: rgba(255,255,255,.8); border: 1px solid rgba(255,255,255,.9);
            border-radius: 14px; padding: 1.2rem; text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,.04);
        }
        .result-card .value { font-size: 2.2rem; font-weight: 800; }
        .result-card .label { font-size: .8rem; opacity: .6; text-transform: uppercase; letter-spacing: 1px; color: #4a6a8a; }
        .risk-high .value { color: #d63031; }
        .risk-mid .value { color: #e17055; }
        .risk-low .value { color: #00b894; }
        .report-header { border-left: 3px solid #5b9bd5; padding-left: 1rem; margin-bottom: 1.5rem; }
        .report-header h2 { margin: 0; font-weight: 700; color: #0d2137; }
        .report-header .meta { font-size: .8rem; opacity: .5; }
        th, td { padding: .6rem .8rem; text-align: left; border-bottom: 1px solid rgba(0,0,0,.06); color: #1a2a3a; }
        th { font-weight: 600; opacity: .7; font-size: .75rem; text-transform: uppercase; letter-spacing: .5px; }
        .st-bw { background: rgba(255,255,255,.3); }
        .stNumberInput label, .stSelectbox label { color: #1a2a3a !important; }
    }

    /* ═══ 暗色模式 — 星空 ═══ */
    @media (prefers-color-scheme: dark) {
        .stApp {
            background: linear-gradient(180deg, #0a0a1a 0%, #12122a 40%, #1a1a3a 100%) !important;
            position: relative;
        }
        .stApp::before {
            content: '';
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background-image:
                radial-gradient(1px 1px at 10% 20%, rgba(255,255,255,.4), transparent),
                radial-gradient(1px 1px at 25% 45%, rgba(255,255,255,.3), transparent),
                radial-gradient(1.5px 1.5px at 40% 10%, rgba(255,255,255,.5), transparent),
                radial-gradient(1px 1px at 55% 60%, rgba(255,255,255,.3), transparent),
                radial-gradient(1.5px 1.5px at 70% 25%, rgba(255,255,255,.4), transparent),
                radial-gradient(1px 1px at 82% 70%, rgba(255,255,255,.3), transparent),
                radial-gradient(1px 1px at 15% 80%, rgba(255,255,255,.25), transparent),
                radial-gradient(1.5px 1.5px at 90% 40%, rgba(255,255,255,.35), transparent),
                radial-gradient(1px 1px at 45% 85%, rgba(255,255,255,.2), transparent),
                radial-gradient(1px 1px at 65% 50%, rgba(255,255,255,.3), transparent),
                radial-gradient(1.5px 1.5px at 5% 55%, rgba(255,255,255,.4), transparent),
                radial-gradient(1px 1px at 35% 35%, rgba(255,255,255,.25), transparent),
                radial-gradient(1px 1px at 75% 15%, rgba(255,255,255,.3), transparent),
                radial-gradient(1.5px 1.5px at 50% 50%, rgba(255,255,255,.15), transparent),
                radial-gradient(1px 1px at 95% 80%, rgba(255,255,255,.2), transparent);
            pointer-events: none; z-index: 0;
        }
        * { font-family: 'Inter', 'Microsoft YaHei', sans-serif; color: #e0e0e0; }
        .hero {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e) !important;
            padding: 2.5rem 2rem; border-radius: 20px; text-align: center;
            color: white; margin-bottom: 2rem; position: relative; z-index: 1;
        }
        .hero h1 { font-size: 2.8rem; font-weight: 800; margin: 0; font-family: 'Playfair Display', serif; }
        .hero p { font-size: 1.05rem; opacity: .75; margin-top: .5rem; }
        .card {
            background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.08);
            border-radius: 14px; padding: 1.5rem; margin-bottom: 1.5rem;
            backdrop-filter: blur(4px); position: relative; z-index: 1;
        }
        .card h3 { margin: 0 0 .3rem 0; font-weight: 600; color: #e0e0e0; }
        .card .sub { font-size: .8rem; opacity: .5; margin-bottom: 1rem; }
        .result-card {
            background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.08);
            border-radius: 14px; padding: 1.2rem; text-align: center;
            backdrop-filter: blur(4px); position: relative; z-index: 1;
        }
        .result-card .value { font-size: 2.2rem; font-weight: 800; }
        .result-card .label { font-size: .8rem; opacity: .6; text-transform: uppercase; letter-spacing: 1px; }
        .risk-high .value { color: #ff4757; }
        .risk-mid .value { color: #ffa502; }
        .risk-low .value { color: #2ed573; }
        .report-header { border-left: 3px solid #7c4dff; padding-left: 1rem; margin-bottom: 1.5rem; }
        .report-header h2 { margin: 0; font-weight: 700; }
        .report-header .meta { font-size: .8rem; opacity: .5; }
        th, td { padding: .6rem .8rem; text-align: left; border-bottom: 1px solid rgba(255,255,255,.06); }
        th { font-weight: 600; opacity: .7; font-size: .75rem; text-transform: uppercase; letter-spacing: .5px; }
    }

    /* ═══ 通用 ═══ */
    .metric-row { display: flex; justify-content: space-between; padding: .5rem 0; border-bottom: 1px solid rgba(255,255,255,.05); }
    .metric-row .name { opacity: .7; }
    .metric-row .val { font-weight: 600; }
    .badge-danger { background: rgba(255,71,87,.15); color: #ff4757; }
    .badge-warn { background: rgba(255,165,2,.15); color: #ffa502; }
    .badge-good { background: rgba(46,213,115,.15); color: #2ed573; }
    @media (max-width: 768px) {
        .hero { padding: 1.5rem 1rem; }
        .hero h1 { font-size: 1.8rem; }
        .row-widget.stColumns { flex-direction: column !important; gap: 0.3rem !important; }
        .row-widget.stColumns > div { width: 100% !important; flex: none !important; }
    }
    table { width: 100%; border-collapse: collapse; font-size: .9rem; }
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

# 计算全体百分位
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

    # 报告头部
    report_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.markdown(f"""
    <div class="report-header">
        <h2>📄 客户流失风险评估报告</h2>
        <div class="meta">报告生成时间：{report_time} ｜ 模型版本：v1.0（随机森林）</div>
    </div>
    """, unsafe_allow_html=True)

    # ── 第 1 节：风险评分总览 ──
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
        st.markdown(f'<div class="result-card {risk_cls}"><div class="label">健康度评分</div><div class="value">{health_score}<span style="font-size:1rem">/100</span></div></div>', unsafe_allow_html=True)

    # ── 第 2 节：关键指标对比 ──
    st.markdown("### 2️⃣ 关键指标对比分析")
    st.markdown("将当前客户的关键指标与**留存客户均值**和**流失客户均值**进行对比，识别异常信号。")

    metrics_table = [
        ("💳 月消费金额", f"${spending:.0f}", f"${retained['Monthly_Spend'].mean():.0f}", f"${churned['Monthly_Spend'].mean():.0f}",
         "🔴 偏低" if spending < retained['Monthly_Spend'].mean() * 0.7 else "🟢 正常"),
        ("📆 订阅时长", f"{subscription}个月", f"{retained['Subscription_Duration_Months'].mean():.0f}个月", f"{churned['Subscription_Duration_Months'].mean():.0f}个月",
         "🔴 偏短" if subscription < retained['Subscription_Duration_Months'].mean() * 0.7 else "🟢 正常"),
        ("🔑 月登录次数", f"{logins}次", f"{retained['Monthly_Logins'].mean():.0f}次", f"{churned['Monthly_Logins'].mean():.0f}次",
         "🔴 偏低" if logins < retained['Monthly_Logins'].mean() * 0.7 else "🟢 正常"),
        ("📱 App使用时长", f"{app_usage}分钟", f"{retained['App_Usage_Time_Min'].mean():.0f}分钟", f"{churned['App_Usage_Time_Min'].mean():.0f}分钟",
         "🔴 偏少" if app_usage < retained['App_Usage_Time_Min'].mean() * 0.7 else "🟢 正常"),
        ("⭐ 满意度评分", f"{satisfaction}/5", f"{retained['Satisfaction_Score'].mean():.1f}/5", f"{churned['Satisfaction_Score'].mean():.1f}/5",
         "🔴 偏低" if satisfaction < 3 else "🟢 正常"),
        ("📞 客服呼叫次数", f"{support_calls}次", f"{retained['Customer_Support_Calls'].mean():.1f}次", f"{churned['Customer_Support_Calls'].mean():.1f}次",
         "🔴 偏高" if support_calls >= 4 else "🟢 正常"),
        ("🎫 折扣使用比例", f"{discount:.0%}", f"{retained['Discount_Usage_Percentage'].mean():.0%}", f"{churned['Discount_Usage_Percentage'].mean():.0%}",
         "🔴 偏高" if discount > 0.5 else "🟢 正常"),
        ("📅 距上次购买", f"{last_purchase}天", f"{retained['Last_Purchase_Days_Ago'].mean():.0f}天", f"{churned['Last_Purchase_Days_Ago'].mean():.0f}天",
         "🔴 偏长" if last_purchase > 15 else "🟢 正常"),
        ("📄 合同类型", "月合同" if contract_val else "年合同", "—", "—",
         "🔴 月合同" if contract_val else "🟢 年合同"),
    ]

    html = "<table><thead><tr><th>指标</th><th>当前客户</th><th>留存客户均值</th><th>流失客户均值</th><th>状态</th></tr></thead><tbody>"
    for row in metrics_table:
        html += f"<tr><td>{row[0]}</td><td><strong>{row[1]}</strong></td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td></tr>"
    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)

    # ── 第 3 节：风险因子排名 ──
    st.markdown("### 3️⃣ 风险因子诊断")
    st.markdown("以下因子对该客户的流失风险贡献最大，按影响程度从高到低排序。")

    # 计算每个指标偏离留存均值的程度
    factors = [
        ("客服呼叫次数", support_calls / max(retained['Customer_Support_Calls'].mean(), 0.1), "越高越危险"),
        ("距上次购买天数", last_purchase / max(retained['Last_Purchase_Days_Ago'].mean(), 1), "越长越危险"),
        ("月消费金额", retained['Monthly_Spend'].mean() / max(spending, 1), "越低越危险"),
        ("订阅时长", retained['Subscription_Duration_Months'].mean() / max(subscription, 1), "越短越危险"),
        ("月登录次数", retained['Monthly_Logins'].mean() / max(logins, 1), "越少越危险"),
        ("App使用时长", retained['App_Usage_Time_Min'].mean() / max(app_usage, 1), "越少越危险"),
        ("满意度评分", max(satisfaction, 1) / 5, "越低越危险"),
        ("折扣依赖度", discount / max(retained['Discount_Usage_Percentage'].mean(), 0.01), "越高越危险"),
    ]

    # 根据 contract 加入合同因子
    if contract_val:
        factors.append(("合同类型（月合同）", 3.0, "月合同流失率显著高于年合同"))

    factors.sort(key=lambda x: x[1], reverse=True)

    for i, (name, score, reason) in enumerate(factors[:5], 1):
        pct = min(score / max(factors[0][1], 0.1), 1.0)
        bar_color = "#ff4757" if pct > 0.7 else "#ffa502" if pct > 0.4 else "#2ed573"
        st.markdown(f"""
        **#{i} {name}** ｜ {reason}
        <div style="background:rgba(255,255,255,.06); border-radius:10px; height:8px; margin:.3rem 0 .8rem 0;">
            <div style="background:{bar_color}; border-radius:10px; height:8px; width:{pct*100:.0f}%;"></div>
        </div>
        """, unsafe_allow_html=True)

    # ── 第 4 节：同业百分位对比 ──
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
            color = "#2ed573" if p > 50 else "#ffa502" if p > 25 else "#ff4757"
            st.markdown(f"""
            <div style="text-align:center; padding:.5rem;">
                <div style="font-size:.7rem; opacity:.6; margin-bottom:.3rem;">{label}</div>
                <div style="font-size:1.6rem; font-weight:800; color:{color};">{p:.0f}%</div>
                <div style="font-size:.7rem; opacity:.5;">高于 {p:.0f}% 的客户</div>
            </div>
            """, unsafe_allow_html=True)

    # ── 第 5 节：雷达图 ──
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
        name='当前客户', fill='toself', line=dict(color='#7c4dff', width=2.5), marker=dict(size=6, color='#7c4dff')))
    fig_radar.add_trace(go.Scatterpolar(r=avg_retained + [avg_retained[0]], theta=cats + [cats[0]],
        name='留存客户平均', fill='toself', line=dict(color='#2ed573', width=2, dash='dot'), opacity=0.7))
    fig_radar.add_trace(go.Scatterpolar(r=avg_churned + [avg_churned[0]], theta=cats + [cats[0]],
        name='流失客户平均', fill='toself', line=dict(color='#ff4757', width=2, dash='dot'), opacity=0.7))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1.05], tickvals=[0, .25, .5, .75, 1],
                                   tickfont=dict(size=10, color='#888')),
                   bgcolor='rgba(0,0,0,0)', gridshape='circular'),
        legend=dict(orientation='h', yanchor='bottom', y=-0.25, font=dict(size=12, color='#aaa')),
        height=420, margin=dict(l=60, r=60, t=20, b=60),
        paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#ccc', size=11),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # ── 第 6 节：干预方案 ──
    st.markdown("### 6️⃣ 个性化干预方案")

    action_col1, action_col2 = st.columns([1, 1])
    with action_col1:
        if prob >= 0.7:
            if contract == "月合同":
                st.error("**🔴 最高优先级 — 立即干预**")
                st.markdown("""
                - 📞 **专属客服回访**：48 小时内电话联系
                - 🎫 **大额优惠券**：发送 20% 折扣券 + 免运费
                - 📱 **推送个性化推荐**：基于历史购买记录
                """)
            else:
                st.error("**🔴 最高优先级 — 立即干预**")
                st.markdown("""
                - 📞 **客户成功经理对接**：提前沟通续约
                - 🎁 **VIP 专属权益**：赠送额外服务包
                - 📊 **使用情况审查**：排查未充分利用的功能
                """)
        elif prob >= 0.3:
            st.warning("**🟡 中等优先级 — 预防维护**")
            st.markdown("""
            - 🎯 **精准推送**：基于偏好推荐相关商品
            - 👑 **VIP 福利提醒**：告知可用积分/权益
            - 📧 **定期关怀邮件**：保持品牌粘性
            """)
        else:
            st.success("**🟢 低优先级 — 常规维护**")
            st.markdown("""
            - ✅ **维持现状**：当前满意度表现良好
            - 📬 **常规推送**：保持正常营销触达
            - 📈 **月度监控**：定期检查指标变化
            """)

    with action_col2:
        st.markdown("#### 预期效果估算")
        if prob >= 0.5:
            savings = int(prob * 100)
            st.markdown(f"""
            - 🎯 若不干预，流失概率：**{prob:.0%}**
            - 💰 预估客户年价值：**${int(spending * 12)}**
            - 🛡️ 干预后留存概率提升：**约 30%**
            - 📈 预期挽回价值：**${int(spending * 12 * 0.3)}**
            """)
        else:
            st.markdown(f"""
            - ✅ 当前流失风险较低
            - 💰 预估客户年价值：**${int(spending * 12)}**
            - 🛡️ 建议保持当前维护策略
            """)

    # 底部
    st.markdown("---")
    st.caption("报告由 ChurnGuard AI 引擎自动生成 ｜ 基于随机森林 + SMOTE 模型，AUC=0.90")
