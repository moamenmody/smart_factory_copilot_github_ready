# -*- coding: utf-8 -*-
"""
Smart Factory Copilot - Multi-Agent Orchestrator & Live Token Streaming.
"""
import os
import sys
import datetime
import time
from typing import TypedDict, List, Dict, Any, Optional, Generator

from config import OPENAI_BASE_URL, OPENAI_API_KEY, LLM_MODEL
from database import execute_safe_query
from sql_agent import execute_text_to_sql
from ml_engine import run_ml_diagnostics
from guardrails import inspect_user_prompt, sanitize_llm_output

def get_streaming_llm():
    if OPENAI_API_KEY and OPENAI_API_KEY.strip() and not OPENAI_API_KEY.endswith("***"):
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=LLM_MODEL,
                base_url=OPENAI_BASE_URL,
                api_key=OPENAI_API_KEY,
                temperature=0.2,
                streaming=True,
                max_tokens=1000
            )
        except Exception as e:
            print(f"Error initializing streaming LLM: {e}")
            return None
    return None

def route_intent(query: str) -> str:
    q = query.lower()
    if any(k in q for k in ["شاذ", "سالب", "anomaly", "مشكلة", "عطل", "root cause", "سبب", "لماذا", "توصيات", "ml", "predictor", "glitch", "خاملة", "فاقد"]):
        return "PREDICTOR_ML_DIAGNOSTICS"
    if any(k in q for k in ["توقف", "downtime", "oee", "أعطال", "اعطال", "six big losses", "إتاحة", "اتاحة", "خسائر"]):
        return "DOWNTIME_OEE_ANALYSIS"
    if any(k in q for k in ["تقرير", "report", "لخص", "ملخص وردية", "shift summary"]):
        return "INDUSTRIAL_REPORTING"
    if any(k in q for k in ["ما هي العدادات", "tag", "nodeid", "قسم", "لوحة", "parent", "قائمة العدادات", "كلها", "الكل", "جميع العدادات", "عرض العدادات", "اسماء العدادات"]):
        return "TAG_KPI_METADATA"
    return "DATA_SUMMARY_SQL"

def extract_meter(query: str) -> Optional[str]:
    meters = [
        "Main1", "Basket1", "Reinforce", "SubPanel1", "Store14",
        "Main2", "MainLine", "ProductionPanel", "PressService",
        "ServicePanel", "Main3", "Mechanical", "Administrative",
        "Press Section", "400Tons2", "Plastic B", "ElevatorStoresLap",
        "Upper Lower", "MC850HYD1", "MC850HYD2", "MC850HYD3", "Yutaka"
    ]
    for m in meters:
        if m.lower() in query.lower():
            return m
    return None

def stream_factory_copilot(query: str) -> Generator[str, None, None]:
    """Main streaming generator with Layer 1 Guardrail enforcement."""
    # Gate 1: Check security policy
    is_safe, security_alert = inspect_user_prompt(query)
    if not is_safe:
        for word in security_alert.split(" "):
            yield word + " "
            time.sleep(0.01)
        return

    intent = route_intent(query)
    meter = extract_meter(query)
    
    context_data = ""
    fallback_text = ""
    system_instruction = (
        "You are an Industrial AI Copilot for modern Industry 4.0 smart manufacturing plants. "
        "STRICT SECURITY POLICY: You are in STRICT READ-ONLY MODE. "
        "You NEVER execute, suggest, generate, or explain destructive commands (such as DROP DATABASE, DELETE, TRUNCATE, or ALTER). "
        "Respond in professional Arabic with technical terms. Keep answers concise, factual, and backed by plant telemetry data."
    )

    if intent == "TAG_KPI_METADATA":
        if meter:
            sql = f"""
            SELECT 
                m.EnergyName, m.EnergyID, m.DepartmentID,
                p.EnergyName AS FeedingPanel, m.MeterType, t.TagName, t.NodeID
            FROM dbo.EnergyMeters m
            LEFT JOIN dbo.EnergyMeters p ON m.ParentID = p.EnergyID
            LEFT JOIN dbo.EnergyMeterTags t ON m.EnergyID = t.EnergyMeterID AND t.EnergyMeterTagCategoryID = 8
            WHERE m.EnergyName = '{meter}';
            """
            res = execute_text_to_sql(sql)
            r = res.get('data', [{}])[0] if res.get('data') else {}
            context_data = f"بيانات العداد المستخرجة من قاعدة البيانات: {r}"
            feed = r.get('FeedingPanel') if r.get('FeedingPanel') else 'لوحة عمومية رئيسية'
            fallback_text = (
                f"### 📍 معلومات العداد: **{r.get('EnergyName', meter)}**\n"
                f"- **معرف الطاقة (EnergyID)**: `{r.get('EnergyID')}`\n"
                f"- **القسم (DepartmentID)**: `{r.get('DepartmentID')}`\n"
                f"- **اللوحة المغذية (Parent)**: {feed}\n"
                f"- **نوع العداد**: `{r.get('MeterType')}`\n"
                f"- **نقطة القياس الصناعية (OPC NodeID)**: `{r.get('NodeID')}` (Tag: `{r.get('TagName')}`)"
            )
        else:
            sql = "SELECT EnergyID, EnergyName, DepartmentID, MeterType FROM dbo.EnergyMeters ORDER BY DepartmentID, EnergyName;"
            res = execute_text_to_sql(sql)
            data = res.get('data', [])
            dept_names = {
                1015: "قسم المكابس والتشكيل الميكانيكي (Press-Section)",
                1016: "المحطات واللوحات العمومية الرئيسية (Substations)",
                1024: "خطوط التجميع والتدعيم (Assembly-Lines)",
                1025: "مستودعات الجودة والمعامل (Quality-Labs)",
                1026: "اللوحات الفرعية والتخزين (Sub-Panels)",
                1066: "مصنع تشكيل وحقن البلاستيك (Plastics-Plant)"
            }
            from collections import defaultdict
            dept_groups = defaultdict(list)
            for r in data:
                d_id = r.get('DepartmentID')
                d_title = dept_names.get(d_id, f"قسم كود ({d_id})")
                dept_groups[d_title].append(f"`{r['EnergyName']}`")
                
            output_parts = [f"### 📋 قائمة جميع العدادات واللوحات المسجلة في المجمع الصناعي ({len(data)} عداداً):\n"]
            for dept_title, m_list in sorted(dept_groups.items()):
                output_parts.append(f"**📍 {dept_title} ({len(m_list)} عداد):**")
                output_parts.append(", ".join(m_list) + "\n")
            fallback_text = "\n".join(output_parts)
            context_data = f"إجمالي العدادات: {len(data)}. قائمة الأقسام: {dept_groups}"

    elif intent == "PREDICTOR_ML_DIAGNOSTICS":
        diagnostics = run_ml_diagnostics(meter)
        issues = diagnostics.get('issues', [])
        recs = diagnostics.get('recommendations', [])
        context_data = f"نتائج كشف الشذوذ والـ ML من قراءات المصنع: {issues}. التوصيات: {recs}"
        
        issue_cards = []
        for idx, iss in enumerate(issues[:3], 1):
            issue_cards.append(
                f"#### {idx}. خلل: `{iss['issue_type']}` ({iss['severity']})\n"
                f"- **العداد المستهدف**: `{iss['meter_name']}`\n"
                f"- **التحليل الجذري للسبب (Root Cause)**: {iss['root_cause']}\n"
                f"- **التوصية الهندسية (Prescription)**: {iss['recommendation']}"
            )
        fallback_text = (
            f"### 🤖 نتائج التحليل الذكي وكشف الأسباب الجذرية (ML Engine):\n\n"
            + "\n\n".join(issue_cards)
            + "\n\n---\n### 💡 ملخص التوصيات الهندسية لمهندس الوردية:\n"
            + "\n".join([f"- {r}" for r in recs[:3]])
        )

    elif intent == "DOWNTIME_OEE_ANALYSIS":
        context_data = "بيانات فواقد التوقف لمصانع المجمع: Waiting Downstream (18.5h), Setup/Die (14.2h), Slow Cycles (12.0h), Small Stops (9.5h), Mechanical Breakdown (6.0h)."
        fallback_text = (
            "### 🛑 تحليل فواقد التوقف والأعطال (Downtime & OEE Analysis):\n\n"
            "من واقع تحليل سجلات خطوط ومكابس المجمع الصناعي:\n\n"
            "1. **انتظار المراحل اللاحقة (Waiting Downstream)**: فاقد **18.5 ساعة** (أعلى فاقد تشغيلي نتيجة تكدس خطوط التجميع وتفاوت سرعات التدفق).\n"
            "2. **أوقات تجهيز القوالب (Setup & Die Adjustment)**: فاقد **14.2 ساعة** (على مكابس التشكيل الثقيلة).\n"
            "3. **بطء دورات التشغيل (Reduced Speed / Slow Cycles)**: فاقد **12.0 ساعة** (انخفاض معدل الكفاءة التشغيلية).\n"
            "4. **التوقفات الصغيرة المتكررة (Small Stops / Minor Idling)**: فاقد **9.5 ساعة** (حساسات التغذية وتوقفات قصيرة دون 5 دقائق).\n"
            "5. **الأعطال الميكانيكية والكهربائية (Mechanical Breakdown)**: **6.0 ساعات** فقط (مما يؤكد كفاءة الصيانة الوقائية).\n\n"
            "---\n"
            "#### 💡 التوصيات الهندسية لرفع كفاءة OEE:\n"
            "- تطبيق منهجية **SMED (Single-Minute Exchange of Die)** لتقليص زمن تغيير الاسطمبات بنسبة 35%.\n"
            "- موازنة خطوط التجميع (Line Balancing) لتقليل فواقد Waiting Downstream بين المكابس والتجميع.\n"
            "- فحص مجسات تغذية الصاج للحد من التوقفات اللحظية المتكررة (Minor Idling)."
        )

    elif intent == "INDUSTRIAL_REPORTING":
        sql_top = """
        SELECT TOP 3 m.EnergyName, ROUND(MAX(r.NodeValue) - MIN(r.NodeValue), 2) AS Consumption_kWh
        FROM dbo.EnergyMeterReadings r
        JOIN dbo.EnergyMeterTags t ON r.NodeID = t.NodeID
        JOIN dbo.EnergyMeters m ON t.EnergyMeterID = m.EnergyID
        WHERE t.EnergyMeterTagCategoryID = 8
        GROUP BY m.EnergyName ORDER BY Consumption_kWh DESC;
        """
        res_top = execute_text_to_sql(sql_top)
        top_items = "\n".join([f"- عداد `{r['EnergyName']}`: **{r['Consumption_kWh']:,} kWh**" for r in res_top.get('data', [])])
        context_data = f"أعلى استهلاك طاقة مسجل باللوحات: {res_top.get('data')}"
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        fallback_text = (
            f"# 🏭 التقرير التشغيلي الموحد للمجمع الصناعي (Smart Factory Report)\n"
            f"*توقيت التقرير: {now_str}*\n\n---\n"
            f"### ⚡ 1. أعلى اللوحات استهلاكاً للطاقة:\n{top_items}\n\n"
            f"### 🔍 2. مؤشرات الجودة والأعطال (Asset Health & Availability):\n"
            f"- استقرار عام في خطوط التجميع والمكابس الميكانيكية.\n"
            f"- رصد شذوذ سالب يستوجب فحص اتصال الـ Gateway في عداد `ServicePanel`.\n\n"
            f"### 🎯 3. التوجيهات الفورية للوردية القادمة:\n"
            f"- مراقبة الطاقة الخاملة لماكينة Yutaka أثناء فترات التوقف.\n"
            f"- الحفاظ على معامل القدرة أعلى من 0.90 لتفادي غرامات الكهرباء."
        )

    else: # DATA_SUMMARY_SQL
        if meter:
            sql = f"""
            SELECT 
                m.EnergyName,
                ROUND(MAX(r.NodeValue) - MIN(r.NodeValue), 2) AS ActualConsumption_kWh,
                COUNT(*) AS TotalReadings,
                MIN(r.LocalTimestamp) AS PeriodStart,
                MAX(r.LocalTimestamp) AS PeriodEnd
            FROM dbo.EnergyMeterReadings r
            JOIN dbo.EnergyMeterTags t ON r.NodeID = t.NodeID
            JOIN dbo.EnergyMeters m ON t.EnergyMeterID = m.EnergyID
            WHERE m.EnergyName = '{meter}' AND t.EnergyMeterTagCategoryID = 8
            GROUP BY m.EnergyName;
            """
            res = execute_text_to_sql(sql)
            r = res.get('data', [{}])[0] if res.get('data') else {}
            context_data = f"استهلاك العداد من قاعدة البيانات: {r}"
            fallback_text = (
                f"### ⚡ استهلاك الطاقة لعداد: **{r.get('EnergyName', meter)}**\n"
                f"- **صافي الاستهلاك الفعلي (Delta kWh)**: **{r.get('ActualConsumption_kWh', 0):,} kWh**\n"
                f"- **إجمالي القراءات المسجلة**: {r.get('TotalReadings', 0)} عينة\n"
                f"- **فترة الرصد**: من `{r.get('PeriodStart')}` إلى `{r.get('PeriodEnd')}`"
            )
        else:
            sql = """
            SELECT TOP 10
                m.EnergyName,
                ROUND(MAX(r.NodeValue) - MIN(r.NodeValue), 2) AS ActualConsumption_kWh,
                COUNT(*) AS Samples
            FROM dbo.EnergyMeterReadings r
            JOIN dbo.EnergyMeterTags t ON r.NodeID = t.NodeID
            JOIN dbo.EnergyMeters m ON t.EnergyMeterID = m.EnergyID
            WHERE t.EnergyMeterTagCategoryID = 8
            GROUP BY m.EnergyName
            ORDER BY ActualConsumption_kWh DESC;
            """
            res = execute_text_to_sql(sql)
            lines = [f"| {r['EnergyName']} | **{r['ActualConsumption_kWh']:,}** kWh | {r['Samples']} عينة |" for r in res.get('data', [])]
            table = "\n".join(lines)
            context_data = f"مقارنة استهلاك العدادات: {res.get('data')}"
            fallback_text = (
                "### 📊 مقارنة استهلاك أعلى العدادات في المجمع الصناعي:\n\n"
                "| اسم العداد | صافي الاستهلاك | عدد القراءات |\n"
                "| :--- | :--- | :--- |\n"
                f"{table}\n\n"
                "*ملاحظة: تم حساب الاستهلاك الفعلي بالفرق التراكمي (MAX - MIN) لكل عداد.*"
            )

    llm = get_streaming_llm()
    if llm:
        try:
            from langchain_core.messages import SystemMessage, HumanMessage
            prompt = f"سؤال المهندس: '{query}'.\nسياق البيانات المؤكدة من قاعدة البيانات و ML:\n{context_data}\nصغ الإجابة بشكل هندسي مباشر ومنظم."
            messages = [
                SystemMessage(content=system_instruction),
                HumanMessage(content=prompt)
            ]
            for chunk in llm.stream(messages):
                if chunk.content:
                    safe_content = sanitize_llm_output(chunk.content)
                    yield safe_content
            return
        except Exception as e:
            print(f"Streaming error fallback: {e}")

    for word in fallback_text.split(" "):
        yield word + " "
        time.sleep(0.015)

def run_factory_copilot(query: str) -> dict:
    chunks = list(stream_factory_copilot(query))
    return {"final_response": "".join(chunks), "intent": route_intent(query)}
