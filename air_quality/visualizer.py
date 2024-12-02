import streamlit as st
import folium
import plotly.express as px
from streamlit_folium import st_folium
from .api import AirQualityAPI
from .utils import AirQualityUtils
from .config import AirQualityConfig

class AirQualityVisualizer:
    """대기질 시각화 클래스"""
    @staticmethod
    def create_map(stations, selected_station_name):
        center_lat = stations[0]['lat']
        center_lon = stations[0]['lon']
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=11)
        
        for station in stations:
            icon_color = 'red' if station['name'] == selected_station_name else 'blue'
            
            folium.Marker(
                [station['lat'], station['lon']],
                popup=f"{station['name']}<br>{station['addr']}",
                tooltip=station['name'],
                icon=folium.Icon(color=icon_color)
            ).add_to(m)
        
        return m

    @staticmethod
    def display_air_quality_info(station_name):
        air_quality_data = AirQualityAPI.get_air_quality_data(station_name)
        
        if air_quality_data is not None and not air_quality_data.empty:
            latest_data = air_quality_data.iloc[0]
            
            st.subheader("현재 대기질 상태")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                pm10_grade, pm10_color, pm10_emoji = AirQualityUtils.get_grade_info(
                    latest_data['pm10Value'], AirQualityConfig.PM10_GRADES
                )
                AirQualityVisualizer._display_quality_card(
                    '미세먼지 (PM10)', 
                    latest_data['pm10Value'], 
                    pm10_grade, 
                    pm10_color, 
                    pm10_emoji
                )
            
            with col2:
                pm25_grade, pm25_color, pm25_emoji = AirQualityUtils.get_grade_info(
                    latest_data['pm25Value'], AirQualityConfig.PM25_GRADES
                )
                AirQualityVisualizer._display_quality_card(
                    '초미세먼지 (PM2.5)', 
                    latest_data['pm25Value'], 
                    pm25_grade, 
                    pm25_color, 
                    pm25_emoji
                )
            
            AirQualityVisualizer._display_statistics(air_quality_data)
        else:
            st.warning("선택한 측정소의 대기질 정보를 불러올 수 없습니다.")

    @staticmethod
    def _display_quality_card(title, value, grade, color, emoji):
        st.markdown(
            f"""
            <div style="padding: 1rem; border-radius: 0.5rem; background-color: {color}; color: white;">
                <h3 style="margin: 0;">{title} {emoji}</h3>
                <p style="font-size: 1.5rem; margin: 0;">{value} µg/m³</p>
                <p style="margin: 0;">{grade}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    @staticmethod
    def _display_statistics(air_quality_data):
        daily_avg = air_quality_data.agg({
            'pm10Value': 'mean', 'pm25Value': 'mean',
            'o3Value': 'mean', 'coValue': 'mean',
            'no2Value': 'mean', 'so2Value': 'mean'
        }).round(2)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 24시간 평균")
            st.markdown(f"미세먼지 (PM10): {daily_avg['pm10Value']} µg/m³")
            st.markdown(f"초미세먼지 (PM2.5): {daily_avg['pm25Value']} µg/m³")
            st.markdown(f"오존 (O3): {daily_avg['o3Value']} ppm")
        
        with col2:
            st.markdown("#### 최고/최저")
            st.markdown(f"PM10 최고: {air_quality_data['pm10Value'].max()} µg/m³")
            st.markdown(f"PM10 최저: {air_quality_data['pm10Value'].min()} µg/m³")
            st.markdown(f"PM2.5 최고: {air_quality_data['pm25Value'].max()} µg/m³")
            st.markdown(f"PM2.5 최저: {air_quality_data['pm25Value'].min()} µg/m³")
        
        st.subheader("📈 24시간 추이")
        fig_pm = px.line(air_quality_data, x='dataTime', y=['pm10Value', 'pm25Value'],
                       title='미세먼지 농도 변화',
                       labels={'value': '농도', 'dataTime': '시간'},
                       line_shape='linear')
        st.plotly_chart(fig_pm, use_container_width=True)
        
        with st.expander("상세 데이터 보기"):
            st.dataframe(air_quality_data)