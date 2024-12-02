import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

class AirQualityUtils:
    """유틸리티 메서드 클래스"""
    @staticmethod
    def get_grade_info(value, grade_levels):
        if pd.isna(value):
            return '정보없음', '#808080', '❓'
        value = float(value)
        for min_val, max_val, grade, color, emoji in grade_levels:
            if min_val <= value <= max_val:
                return grade, color, emoji
        return '정보없음', '#808080', '❓'

    @staticmethod
    def parse_datetime(dt_str):
        try:
            if dt_str.endswith(" 24:00"):
                base_date = datetime.strptime(dt_str[:-6], "%Y-%m-%d")
                return base_date + timedelta(days=1)
            return datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        except Exception as e:
            st.error(f"날짜 파싱 오류: {dt_str} - {e}")
            return None