# -*- coding: utf-8 -*-
"""
Industry 4.0 - Industrial Safety & Security Guardrails.
Multi-Layered Protection System:
1. Input Prompt Gatekeeper (Blocks destructive/malicious requests before LLM/SQL).
2. SQL Engine Validator (Enforces Read-Only SELECT/WITH and prevents query chaining).
3. Output Response Filter (Scans LLM output against destructive syntax).
"""
import re
from typing import Tuple

DESTRUCTIVE_PROMPT_PATTERNS = [
    r'\bdrop\b', r'\bdelete\b', r'\btruncate\b', r'\bwipe\b', r'\bformat\b',
    r'\bkill\b', r'\bshutdown\b', r'\balter\s+database\b', r'\balter\s+table\b',
    r'\binsert\s+into\b', r'\bupdate\b', r'\bexec\b', r'\bexecute\b',
    r'امسح', r'احذف', r'مسح', r'حذف', r'تدمير', r'فرمت', r'تفريغ', r'ازالة', r'إزالة',
    r'تعديل جدول', r'تعديل قاعدة', r'تعديل الداتا', r'اسقاط', r'إسقاط'
]

FORBIDDEN_SQL_KEYWORDS = [
    "DROP", "DELETE", "TRUNCATE", "UPDATE", "INSERT", 
    "ALTER", "CREATE", "EXEC", "EXECUTE", "MERGE", "GRANT", 
    "REVOKE", "BACKUP", "RESTORE", "SHUTDOWN", "KILL"
]

def inspect_user_prompt(prompt: str) -> Tuple[bool, str]:
    """Layer 1: Input Gatekeeper."""
    p = prompt.strip().lower()
    for pattern in DESTRUCTIVE_PROMPT_PATTERNS:
        if re.search(pattern, p, re.IGNORECASE):
            security_alert = (
                "⛔ **تنبيه أمني صناعي — تم حظر هذا الطلب بواسطة صمام الأمان (Industrial Guardrail)**\n\n"
                "النظام يعمل في **وضع القراءة والتحليل الهندسي فقط (Strict Read-Only Analytical Mode)**:\n\n"
                "- 🚫 **ممنوع قطعيّاً**: تنفيذ، أو صياغة، أو توفير خطوات لأي أوامر تعديلية أو تخريبية "
                "(مثل `DROP DATABASE`, `DELETE`, `TRUNCATE`, `ALTER`).\n"
                "- 🛡️ **سياسة الحماية**: قواعد بيانات وسجلات المصانع ومؤشرات الطاقة محمية ومؤمنة ضد الحذف أو التعديل.\n"
                "- 💡 **المصرح به فقط**: استعلامات القراءة (SELECT)، كشف الشذوذ (ML Anomaly Detection)، وحسابات الأداء (OEE)."
            )
            return False, security_alert
            
    return True, ""

def inspect_sql_query(sql_query: str) -> Tuple[bool, str]:
    """Layer 2: SQL Engine Validator."""
    clean_sql = sql_query.strip()
    clean_sql = re.sub(r"^```[a-zA-Z]*\s*", "", clean_sql)
    clean_sql = re.sub(r"\s*```$", "", clean_sql).strip()
    upper_sql = clean_sql.upper()
    
    for kw in FORBIDDEN_SQL_KEYWORDS:
        if re.search(r'\b' + kw + r'\b', upper_sql):
            return False, f"Security Policy Violation: Forbidden SQL command '{kw}' is strictly prohibited."
            
    if not (upper_sql.startswith("SELECT") or upper_sql.startswith("WITH")):
        return False, "Security Policy: Only read-only SELECT or WITH queries are permitted."
        
    statements = [s.strip() for s in clean_sql.split(";") if s.strip()]
    if len(statements) > 1:
        for stmt in statements:
            stmt_upper = stmt.upper()
            if not (stmt_upper.startswith("SELECT") or stmt_upper.startswith("WITH")):
                return False, "Security Policy: Multiple chained SQL statements are not allowed."

    return True, clean_sql

def sanitize_llm_output(output_text: str) -> str:
    """Layer 3: Output Response Filter."""
    dangerous_output_patterns = [
        r'DROP\s+DATABASE\s+\[?[a-zA-Z0-9_]+\]?',
        r'DROP\s+TABLE\s+\[?[a-zA-Z0-9_\.]+\]?',
        r'TRUNCATE\s+TABLE\s+\[?[a-zA-Z0-9_\.]+\]?',
        r'DELETE\s+FROM\s+\[?[a-zA-Z0-9_\.]+\]?'
    ]
    sanitized = output_text
    for pat in dangerous_output_patterns:
        sanitized = re.sub(pat, "[BLOCKED DESTRUCTIVE COMMAND]", sanitized, flags=re.IGNORECASE)
    return sanitized
