# -*- coding: utf-8 -*-
"""
Safe Text-to-SQL Agent with Security Guardrails.
"""
from database import execute_safe_query
from guardrails import inspect_sql_query

def execute_text_to_sql(sql_query: str) -> dict:
    """Validates SQL via Layer 2 Guardrail then executes safely."""
    is_valid, validated_sql_or_error = inspect_sql_query(sql_query)
    if not is_valid:
        return {
            "status": "error",
            "error": validated_sql_or_error,
            "sql": sql_query
        }
        
    result = execute_safe_query(validated_sql_or_error)
    return result
