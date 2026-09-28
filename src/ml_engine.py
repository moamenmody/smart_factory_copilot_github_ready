# -*- coding: utf-8 -*-
"""
Smart Industrial ML Engine - Outlier Identification & Root Cause Analysis.
"""
import pandas as pd
import numpy as np
from database import load_meter_telemetry_df

def compute_incremental_consumption(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.sort_values(by=['MeterName', 'LocalTimestamp'])
    df['Delta_kWh'] = df.groupby('MeterName')['Cumulative_kWh'].diff()
    return df

def run_ml_diagnostics(meter_name: str = None) -> dict:
    df = load_meter_telemetry_df(meter_name)
    if df.empty:
        return {"status": "no_data", "findings": [], "recommendations": []}

    df = compute_incremental_consumption(df)
    diagnosed_issues = []

    for name, group in df.groupby('MeterName'):
        valid_deltas = group['Delta_kWh'].dropna()
        if len(valid_deltas) < 5:
            continue

        # 1. Negative Drop (Rollover / Reset)
        neg_events = group[group['Delta_kWh'] < 0]
        if not neg_events.empty:
            for _, row in neg_events.iterrows():
                diagnosed_issues.append({
                    "meter_name": name,
                    "issue_type": "NEGATIVE_CONSUMPTION_DROP",
                    "severity": "CRITICAL",
                    "timestamp": str(row['LocalTimestamp']),
                    "observed_value": float(row['Delta_kWh']),
                    "root_cause": (
                        "هبوط سالب حاد في القراءة التراكمية. ينتج عن إعادة تشغيل الحساس (Sensor Reset)، "
                        "أو انقطاع مؤقت في اتصال البوابة (Counter Rollover)."
                    ),
                    "recommendation": (
                        f"فحص كابل RS485 وتغذية العداد {name} وتفعيل فلتر رفض السالب في الـ Gateway."
                    )
                })

        # 2. Extreme Consumption Surges (Z-Score > 3.0)
        pos_deltas = valid_deltas[valid_deltas >= 0]
        if len(pos_deltas) > 5:
            mean = pos_deltas.mean()
            std = pos_deltas.std()
            if std > 0:
                z_scores = (group['Delta_kWh'] - mean) / std
                surges = group[(z_scores > 3.0) & (group['Delta_kWh'] > 0)]
                for _, row in surges.iterrows():
                    diagnosed_issues.append({
                        "meter_name": name,
                        "issue_type": "HIGH_ENERGY_SURGE",
                        "severity": "HIGH",
                        "timestamp": str(row['LocalTimestamp']),
                        "observed_value": float(row['Delta_kWh']),
                        "root_cause": (
                            f"قفزة مفاجئة في الاستهلاك ({row['Delta_kWh']:.1f} kWh مقابل متوسط متوقع {mean:.1f} kWh)."
                        ),
                        "recommendation": (
                            f"فحص المحركات المتصلة بلوحة {name} ومراجعة حرارة الكابلات لتفادي التحميل الزائد."
                        )
                    })

        # 3. Idle Standby Power
        mean_rate = pos_deltas.mean() if len(pos_deltas) > 0 else 0
        if name in ["Yutaka", "MC850HYD3", "PressService"] and mean_rate > 20.0:
            diagnosed_issues.append({
                "meter_name": name,
                "issue_type": "IDLE_STANDBY_POWER_LOSS",
                "severity": "MEDIUM",
                "observed_value": round(mean_rate, 2),
                "root_cause": (
                    f"الماكينة تستهلك طاقة خاملة عالية (~{mean_rate:.1f} kWh/cycle) أثناء فترات التوقف أو فواصل الورديات."
                ),
                "recommendation": (
                    f"تطبيق نظام الإطفاء التلقائي (Auto-Sleep / Power Saving Mode) لوحدات الهيدروليك في ماكينة {name} بعد 10 دقائق من التوقف."
                )
            })

    if diagnosed_issues:
        unique_recs = list({issue['recommendation'] for issue in diagnosed_issues})
    else:
        unique_recs = ["كافة قراءات العدادات تعمل ضمن النطاق الهندسي الطبيعي."]

    return {
        "status": "analyzed",
        "total_issues": len(diagnosed_issues),
        "issues": diagnosed_issues,
        "recommendations": unique_recs
    }
