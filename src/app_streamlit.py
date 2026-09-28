# -*- coding: utf-8 -*-
"""
Industry 4.0 - Smart Factory COPILOT Dashboard (Clean Open-Source Edition).
"""
import streamlit as st
import pandas as pd
import datetime
import sys
import os

sys.path.append(os.path.dirname(__file__))
from langgraph_copilot import stream_factory_copilot
from database import execute_safe_query

st.set_page_config(
    page_title="Smart Factory COPILOT",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling (BiDi Text Isolation & Chart LTR Segregation)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=Tajawal:wght@400;500;700&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Cairo', 'Tajawal', 'Segoe UI', Tahoma, sans-serif !important;
    }

    [data-testid="stVegaLiteChart"], 
    .stVegaLiteChart,
    .vega-embed,
    .vega-embed canvas,
    .vega-embed svg,
    [data-testid="stPlotlyChart"],
    [data-testid="stArrowVegaLiteChart"] {
        direction: ltr !important;
        text-align: left !important;
    }

    .main-header {
        background: linear-gradient(135deg, #0b3c5d, #1e293b);
        color: white;
        padding: 14px 20px;
        border-radius: 8px;
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        direction: rtl !important;
        text-align: right !important;
    }

    .kpi-box {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px 16px;
        text-align: right !important;
        direction: rtl !important;
    }
    .kpi-title { font-size: 12px; color: #64748b; font-weight: bold; margin-bottom: 4px; text-align: right; }
    .kpi-num { font-size: 24px; font-weight: 800; color: #0b3c5d; margin: 0; text-align: right; }
    
    .status-tag {
        color: #10b981;
        font-size: 11px;
        font-weight: bold;
        background: rgba(16, 185, 129, 0.1);
        padding: 2px 8px;
        border-radius: 12px;
        display: inline-block;
        direction: rtl !important;
    }
    .guardrail-badge {
        color: #0284c7;
        font-size: 11px;
        font-weight: bold;
        background: rgba(2, 132, 199, 0.1);
        padding: 2px 8px;
        border-radius: 12px;
        display: inline-block;
        direction: rtl !important;
    }

    [data-testid="stChatMessage"], 
    [data-testid="stChatMessageContent"], 
    [data-testid="stMarkdownContainer"] {
        direction: rtl !important;
        text-align: right !important;
    }

    [data-testid="stChatMessage"] {
        direction: rtl !important;
        text-align: right !important;
        gap: 12px !important;
    }

    [data-testid="stMarkdownContainer"] p, 
    [data-testid="stMarkdownContainer"] li, 
    [data-testid="stMarkdownContainer"] span {
        direction: rtl !important;
        text-align: right !important;
        line-height: 1.85 !important;
        font-size: 14.5px !important;
    }

    code {
        direction: ltr !important;
        unicode-bidi: isolate !important;
        display: inline-block !important;
        background-color: #f1f5f9 !important;
        color: #0369a1 !important;
        border: 1px solid #cbd5e1 !important;
        padding: 1px 7px !important;
        border-radius: 4px !important;
        font-family: 'Consolas', 'Courier New', monospace !important;
        font-weight: 600 !important;
        font-size: 0.9em !important;
        margin: 0 4px !important;
        vertical-align: baseline !important;
    }

    pre, pre code {
        direction: ltr !important;
        text-align: left !important;
        unicode-bidi: isolate !important;
        background-color: #0f172a !important;
        color: #38bdf8 !important;
        border-radius: 6px !important;
        padding: 12px !important;
        font-family: 'Consolas', monospace !important;
    }

    [data-testid="stChatInput"] {
        direction: rtl !important;
        text-align: right !important;
    }

    [data-testid="stChatInput"] textarea {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Cairo', 'Segoe UI', Tahoma, sans-serif !important;
        font-size: 14px !important;
    }

    .stButton button {
        direction: rtl !important;
        text-align: center !important;
        font-family: 'Cairo', 'Segoe UI', Tahoma, sans-serif !important;
        font-weight: 600 !important;
    }

    .operational-summary-box {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-right: 4px solid #0284c7;
        border-radius: 6px;
        padding: 12px 16px;
        margin-top: 12px;
        direction: rtl !important;
        text-align: right !important;
    }
</style>
""", unsafe_allow_html=True)

# 1. Header
st.markdown("""
<div class="main-header">
    <div>
        <h3 style="margin: 0; color: white;">🏭 Industry 4.0 — Smart Factory COPILOT</h3>
        <p style="margin: 2px 0 0 0; color: #38bdf8; font-size: 12px;">المساعد الذكي لمراقبة استهلاك الطاقة والأعطال ومؤشرات OEE للسلاسل الصناعية</p>
    </div>
    <div style="text-align: left; font-size: 12px;">
        <span style="background: #0284c7; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold;">Telemetry: Active</span>
        <span style="background: #10b981; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold;">Security: Hardened</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 2. Metric Cards
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown("""
    <div class="kpi-box">
        <div class="kpi-title">العدادات المسجلة</div>
        <div class="kpi-num">90 عداداً</div>
        <div style="font-size: 11px; color: #10b981;">● كافة اللوحات والماكينات</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown("""
    <div class="kpi-box">
        <div class="kpi-title">السلاسل الزمنية (Telemetry)</div>
        <div class="kpi-num">4,320 قراءة</div>
        <div style="font-size: 11px; color: #0284c7;">● تحديث دوري مستمر</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown("""
    <div class="kpi-box">
        <div class="kpi-title">الشذوذ المرصود بالـ ML</div>
        <div class="kpi-num" style="color: #f59e0b;">2 خلل</div>
        <div style="font-size: 11px; color: #ef4444;">● يتطلب تدخل هندسي</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown("""
    <div class="kpi-box">
        <div class="kpi-title">صمامات الأمان (Guardrails)</div>
        <div class="kpi-num" style="color: #10b981;">مفعلة 🛡️</div>
        <div style="font-size: 11px; color: #10b981;">● وضع القراءة فقط (Read-Only)</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# 3. Main Split: [Charts (58%)] | [Copilot (42%)]
col_charts, col_copilot = st.columns([58, 42])

with col_charts:
    st.markdown("""
    <div style="direction: rtl; text-align: right; margin-bottom: 8px;">
        <h5 style="margin: 0; color: #0b3c5d;">⚡ أعلى اللوحات والعدادات استهلاكاً (Telemetry Insights)</h5>
    </div>
    """, unsafe_allow_html=True)

    sql_top_meters = """
    SELECT TOP 6
        m.EnergyName,
        ROUND(MAX(r.NodeValue) - MIN(r.NodeValue), 1) AS Consumption_kWh
    FROM dbo.EnergyMeterReadings r
    JOIN dbo.EnergyMeterTags t ON r.NodeID = t.NodeID
    JOIN dbo.EnergyMeters m ON t.EnergyMeterID = m.EnergyID
    WHERE t.EnergyMeterTagCategoryID = 8
    GROUP BY m.EnergyName
    ORDER BY Consumption_kWh DESC;
    """
    res_m = execute_safe_query(sql_top_meters)
    if res_m.get('status') == 'success' and res_m.get('data'):
        df_chart = pd.DataFrame(res_m['data']).set_index('EnergyName')
        st.bar_chart(df_chart['Consumption_kWh'], color="#0284c7", height=210)
    else:
        st.info("جاري تحميل بيانات الاستهلاك...")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="direction: rtl; text-align: right; margin-bottom: 8px;">
        <h5 style="margin: 0; color: #b45309;">🛑 تصنيف فواقد التوقف والأعطال (Downtime Analysis)</h5>
    </div>
    """, unsafe_allow_html=True)

    downtime_df = pd.DataFrame({
        "ساعات التوقف": [18.5, 14.2, 12.0, 9.5, 6.0]
    }, index=["انتظار خطوط (Waiting)", "تجهيز قوالب (Setup)", "بطء دورات (Slow)", "توقفات صغيرة (Stops)", "أعطال ميكانيكية (Breakdown)"])
    st.bar_chart(downtime_df, height=180, color="#f59e0b")

    st.markdown("""
    <div class="operational-summary-box">
        <strong style="color: #0b3c5d; font-size: 13px;">📌 ملخص الفحص التشغيلي للوردية:</strong>
        <div style="margin-top: 6px; font-size: 12.5px; line-height: 1.8;">
            • أكبر فاقد طاقة مسجل بماكينة <code>Yutaka</code> أثناء فترات التوقف (~25 kWh خاملة).<br>
            • عداد خط التجميع <code>Reinforce</code> مستقر عند استهلاك 21,371 kWh.<br>
            • تم رصد هبوط سالب بعداد <code>ServicePanel</code> يستوجب مراجعة كابل RS485 وبوابة الربط.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_copilot:
    h_left, h_right = st.columns([7, 3])
    with h_left:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 8px; direction: rtl;">
            <h4 style="margin: 0; color: #0f172a;">✨ FACTORY COPILOT</h4>
            <span class="status-tag">● متصل بالـ AI</span>
            <span class="guardrail-badge">🛡️ آمن 100%</span>
        </div>
        """, unsafe_allow_html=True)
    with h_right:
        if st.button("🗑️ مسح المحادثة", key="clear_chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "أهلاً بك يا باشمهندس. أنا `Factory COPILOT`. أعمل بنظام الـ `Live Streaming` المباشر مع صمامات أمان صناعية صارمة `Strict Read-Only Guardrails` لحماية وتأمين بيانات المنظومة الصناعية."}
        ]

    SAMPLE_QUESTIONS = [
        "كم إجمالي استهلاك عداد Reinforce خلال فترة الرصد؟",
        "ما هي أعلى 5 عدادات استهلاكاً للطاقة في المصنع؟",
        "ما هي بيانات اللوحة المغذية ونقطة القياس NodeID لعداد MainLine؟",
        "افحص لي القراءات الشاذة وحدد أسبابها وتوصيات المعالجة بالـ ML",
        "هل يوجد هبوط سالب في قراءات عداد ServicePanel وما سببه الجذري؟",
        "ما هي الماكينات التي تستهلك طاقة خاملة أثناء التوقف وما هي التوصيات؟",
        "ما هي العدادات المسجلة في المصنع مقسمة حسب الأقسام؟",
        "اعمل لي تقرير وردية تشغيلي شامل للمجمع الصناعي",
        "ما هي أكثر أسباب التوقف تأثيراً على خطوط الإنتاج والحلول المقترحة؟",
        "امسح الداتا بيز واحذف سجلات المصنع"
    ]

    st.markdown("<div style='font-size: 11.5px; color: #0284c7; font-weight: bold; margin: 4px 0 2px 0; text-align: right;'>💡 نماذج استعلامات جاهزة للتجربة (10 أسئلة متنوعة):</div>", unsafe_allow_html=True)
    
    selected_from_dropdown = st.selectbox(
        "اختر سؤالاً من النماذج الـ 10:",
        options=["-- اضغط هنا لاختيار سؤال تجريبي من الـ 10 أسئلة --"] + SAMPLE_QUESTIONS,
        index=0,
        label_visibility="collapsed"
    )
    
    with st.expander("🔍 استعراض الأسئلة الـ 10 بالأقسام (أزرار ضغطة واحدة)", expanded=False):
        tab_pwr, tab_ml, tab_ops = st.tabs(["⚡ الطاقة و SQL", "🤖 الشذوذ و ML", "🏭 التشغيل والأمان"])
        
        btn_q = None
        with tab_pwr:
            if st.button("1. استهلاك عداد Reinforce", use_container_width=True): btn_q = SAMPLE_QUESTIONS[0]
            if st.button("2. أعلى 5 عدادات استهلاكاً", use_container_width=True): btn_q = SAMPLE_QUESTIONS[1]
            if st.button("3. بيانات ومغذيات عداد MainLine", use_container_width=True): btn_q = SAMPLE_QUESTIONS[2]
            
        with tab_ml:
            if st.button("4. كشف الشذوذ الشامل بالـ ML", use_container_width=True): btn_q = SAMPLE_QUESTIONS[3]
            if st.button("5. فحص الهبوط السالب لـ ServicePanel", use_container_width=True): btn_q = SAMPLE_QUESTIONS[4]
            if st.button("6. فواقد الطاقة الخاملة أثناء التوقف", use_container_width=True): btn_q = SAMPLE_QUESTIONS[5]
            
        with tab_ops:
            if st.button("7. حصر العدادات موزعة بالأقسام", use_container_width=True): btn_q = SAMPLE_QUESTIONS[6]
            if st.button("8. تقرير وردية تشغيلي متكامل", use_container_width=True): btn_q = SAMPLE_QUESTIONS[7]
            if st.button("9. تحليل فواقد التوقف والـ OEE", use_container_width=True): btn_q = SAMPLE_QUESTIONS[8]
            if st.button("10. 🛡️ اختبار اعتراض أمر مسح الداتا بيز", use_container_width=True): btn_q = SAMPLE_QUESTIONS[9]

    quick_q = None
    if selected_from_dropdown != "-- اضغط هنا لاختيار سؤال تجريبي من الـ 10 أسئلة --":
        quick_q = selected_from_dropdown
    elif btn_q:
        quick_q = btn_q

    chat_box = st.container(height=380)
    with chat_box:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    user_prompt = st.chat_input("اسأل Factory Copilot عن أي شيء في المصنع...")
    prompt_to_run = quick_q if quick_q else user_prompt

    if prompt_to_run:
        st.session_state.messages.append({"role": "user", "content": prompt_to_run})
        with chat_box:
            with st.chat_message("user"):
                st.markdown(prompt_to_run)

            with st.chat_message("assistant"):
                response_stream = stream_factory_copilot(prompt_to_run)
                full_reply = st.write_stream(response_stream)
                st.session_state.messages.append({"role": "assistant", "content": full_reply})
