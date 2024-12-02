import requests
import pandas as pd
import streamlit as st
from datetime import datetime
from .config import AirQualityConfig
from .utils import AirQualityUtils

class AirQualityAPI:
    """대기질 관련 API 통신 클래스"""
    
    @staticmethod
    def get_station_list_with_coords(city_name):
        url = 'http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc/getMsrstnList'
        params = {
            'serviceKey': AirQualityConfig.SERVICE_KEY,
            'returnType': 'json',
            'numOfRows': '700',
            'pageNo': '1',
            'ver': '1.0'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            result = response.json()
            items = result.get('response', {}).get('body', {}).get('items', [])
            
            stations = []
            for station in items:
                addr = station.get('addr', '')
                if (addr.startswith(city_name) or 
                    f"{city_name}시" in addr or 
                    f"{city_name}광역시" in addr):
                    stations.append({
                        'name': station['stationName'],
                        'addr': station['addr'],
                        'lat': float(station['dmX']),
                        'lon': float(station['dmY'])
                    })
            
            return sorted(stations, key=lambda x: x['name'])
            
        except Exception as e:
            st.error(f"측정소 정보를 불러올 수 없습니다: {e}")
            return []

    @staticmethod
    def get_air_quality_data(station_name):
        url = 'http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty'
        params = {
            'serviceKey': AirQualityConfig.SERVICE_KEY,
            'returnType': 'json',
            'numOfRows': '24',
            'pageNo': '1',
            'stationName': station_name,
            'dataTerm': 'DAILY',
            'ver': '1.0'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            result = response.json()
            items = result.get('response', {}).get('body', {}).get('items', [])
            
            if not items:
                return None
                
            df = pd.DataFrame(items)
            
            numeric_columns = ['pm10Value', 'pm25Value', 'o3Value', 'coValue', 'no2Value', 'so2Value']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
            df['dataTime'] = df['dataTime'].apply(AirQualityUtils.parse_datetime)
            df = df.dropna(subset=['dataTime'])
            df = df.sort_values('dataTime')
                
            return df
            
        except Exception as e:
            st.error(f"대기질 정보를 불러올 수 없습니다: {e}")
            return None

    @staticmethod
    def get_forecast_data():
        url = 'http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMinuDustFrcstDspth'
        params = {
            'serviceKey': AirQualityConfig.SERVICE_KEY,
            'returnType': 'json',
            'numOfRows': '100',
            'pageNo': '1',
            'searchDate': datetime.now().strftime("%Y-%m-%d"),
            'ver': '1.1'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            result = response.json()
            items = result.get('response', {}).get('body', {}).get('items', [])
            
            if not items:
                st.warning("예보 데이터가 없습니다.")
                return None
                
            forecast_data = []
            for item in items:
                try:
                    if 'informData' in item:
                        forecast_date = datetime.strptime(item['informData'], '%Y-%m-%d')
                        
                        grade_text = item.get('informGrade', '').replace('[', '').replace(']', '')
                        
                        forecast_data.append({
                            'date': forecast_date,
                            'forecast_text': grade_text,
                            'forecast_summary': item.get('informOverall', '정보 없음').replace('\n', ' ')
                        })
                except Exception as parse_error:
                    st.error(f"데이터 파싱 중 오류 발생: {parse_error}")
                    continue
            
            if not forecast_data:
                st.warning("파싱 가능한 예보 데이터가 없습니다.")
                return None
                
            return sorted(forecast_data, key=lambda x: x['date'])
            
        except Exception as e:
            st.error(f"예보 정보 처리 중 오류 발생: {e}")
            return None