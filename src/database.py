# -*- coding: utf-8 -*-
"""
Database Connection Manager (Dual-Engine: MS SQL Server / SQLite Fallback).
"""
import sqlite3
import pandas as pd
from config import get_mssql_connection_string, SQLITE_DB_PATH

def get_db_connection():
    """Returns active connection: pyodbc (MS SQL Server) or fallback (sqlite3)."""
    try:
        import pyodbc
        conn_str = get_mssql_connection_string()
        conn = pyodbc.connect(conn_str, timeout=3)
        return conn, "MSSQL"
    except Exception:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        return conn, "SQLITE"

def execute_safe_query(sql_query: str) -> dict:
    """Executes read-only SQL query and returns standardized dictionary result."""
    conn, engine_type = get_db_connection()
    try:
        clean_query = sql_query
        if engine_type == "SQLITE":
            clean_query = clean_query.replace("dbo.", "")
            
        cursor = conn.cursor()
        cursor.execute(clean_query)
        cols = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        data = [dict(zip(cols, row)) for row in rows]
        conn.close()
        return {
            "status": "success",
            "engine": engine_type,
            "row_count": len(data),
            "columns": cols,
            "data": data[:100]
        }
    except Exception as e:
        if conn: conn.close()
        return {
            "status": "error",
            "engine": engine_type,
            "error": str(e),
            "sql": sql_query
        }

def load_meter_telemetry_df(meter_name: str = None) -> pd.DataFrame:
    """Loads clean time-series telemetry data into a pandas DataFrame."""
    conn, engine_type = get_db_connection()
    query = """
    SELECT 
        m.EnergyName AS MeterName,
        m.EnergyID,
        m.DepartmentID,
        t.TagName,
        r.NodeID,
        r.NodeValue AS Cumulative_kWh,
        r.LocalTimestamp
    FROM dbo.EnergyMeterReadings r
    INNER JOIN dbo.EnergyMeterTags t ON r.NodeID = t.NodeID
    INNER JOIN dbo.EnergyMeters m ON t.EnergyMeterID = m.EnergyID
    """
    if meter_name:
        query += f" WHERE m.EnergyName = '{meter_name}'"
    query += " ORDER BY m.EnergyName, r.LocalTimestamp ASC;"
    
    try:
        if engine_type == "SQLITE":
            query = query.replace("dbo.", "")
        df = pd.read_sql_query(query, conn)
    except Exception:
        query_clean = query.replace("dbo.", "")
        df = pd.read_sql_query(query_clean, conn)
        
    conn.close()
    df['LocalTimestamp'] = pd.to_datetime(df['LocalTimestamp'])
    return df
