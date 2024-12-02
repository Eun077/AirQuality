class AirQualityConfig:
    """대기질 등급 및 상수 설정 클래스"""
    PM10_GRADES = [
        (0, 30, '좋음', '#4575B4', '😊'),
        (31, 80, '보통', '#74ADD1', '🙂'),
        (81, 150, '나쁨', '#F46D43', '😷'),
        (151, 999, '매우나쁨', '#D73027', '😨')
    ]

    PM25_GRADES = [
        (0, 15, '좋음', '#4575B4', '😊'),
        (16, 35, '보통', '#74ADD1', '🙂'),
        (36, 75, '나쁨', '#F46D43', '😷'),
        (76, 999, '매우나쁨', '#D73027', '😨')
    ]

    SERVICE_KEY = 'FaewPSwluv5leL1CYQYPl+wLIOxQwbQRMpYdZKQuMrwAcQa4JWfvMGY8/+FMvPnL3T0afVCZlzIF8v+zspXi8Q=='