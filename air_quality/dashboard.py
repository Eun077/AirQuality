import streamlit as st
from datetime import datetime
from .api import AirQualityAPI
from .visualizer import AirQualityVisualizer
import folium
from streamlit_folium import st_folium

class AirQualityDashboard:
    """대시보드 메인 클래스"""
    @staticmethod
    def display_current_date_and_forecast():
        now = datetime.now()
        col1, col2 = st.columns([2, 3])
        
        with col1:
            st.markdown(f"### 📅 현재 시각")
            st.markdown(f"#### {now.strftime('%Y년 %m월 %d일 %H:%M')}")
        
        forecast_data = AirQualityAPI.get_forecast_data()
        
        if forecast_data:
            with col2:
                st.markdown("### 🔮 미세먼지 예보")
                st.markdown(f"**예보 요약:** {forecast_data[0]['forecast_summary']}")
        else:
            st.warning("예보 정보를 불러올 수 없습니다.")

    @staticmethod
    def run():
        st.set_page_config(page_title="실시간 대기질 정보", layout="wide")
        st.title("🌍 실시간 대기질")

        AirQualityDashboard.display_current_date_and_forecast()
        st.write("실시간 대기질 정보와 통계를 확인해보세요.")
        
        if 'selected_station' not in st.session_state:
            st.session_state.selected_station = None
        
        with st.sidebar:
            st.header("지역 선택")
            city_options = [
                "서울", "부산", "대구", "인천", "광주", "울산", "대전", "세종",
                "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"
            ]
            city_name = st.selectbox("도시를 선택하세요", city_options)
            
            stations = AirQualityAPI.get_station_list_with_coords(city_name)
            
            if stations:
                station_names = [s['name'] for s in stations]
                selected_station = st.selectbox(
                    "측정소를 선택하세요", 
                    station_names,
                    key="sidebar_station_select"
                )
                st.session_state.selected_station = selected_station
                st.info(f"선택된 측정소: {selected_station}")
            else:
                st.error(f"{city_name}에 해당하는 측정소를 찾을 수 없습니다.")
                st.stop()

        st.subheader("📍 측정소 위치")
        m = AirQualityVisualizer.create_map(stations, st.session_state.selected_station)
        map_data = st_folium(m, width=800, height=400, key="map")
        
        if map_data['last_clicked']:
            clicked_lat = map_data['last_clicked']['lat']
            clicked_lng = map_data['last_clicked']['lng']
            
            closest_station = min(
                stations,
                key=lambda x: abs(x['lat'] - clicked_lat) + abs(x['lon'] - clicked_lng)
            )
            st.session_state.selected_station = closest_station['name']
        
        if st.session_state.selected_station:
            AirQualityVisualizer.display_air_quality_info(st.session_state.selected_station)