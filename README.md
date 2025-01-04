# storeData
 일반음식점 데이터 수집

# 주요 기능

- 자동 검색 및 추출: 사업체 이름, 주소 등의 정보를 이용하여 가게를 찾아 메뉴 데이터를 추출합니다.
- 다양한 페이지 버전 지원: 네이버 지도 메뉴 페이지의 구버전과 신버전을 모두 처리할 수 있습니다.
- 오류 로그 기록: 성공 및 오류를 자세히 기록합니다.
- JSON 출력: 추출된 메뉴 데이터를 구조화된 JSON 파일로 저장합니다.
- 유연한 입력 및 출력: 동적인 입력 파일 구성과 출력 디렉터리 관리를 지원합니다.

# 파일 구조

- main.py: 스크래핑 프로세스를 시작하는 메인 스크립트로, 재시도 로직 및 오류 처리를 포함합니다.
- scraper.py: 구버전 및 신버전 메뉴 페이지의 메뉴 추출을 포함한 핵심 스크래핑 로직입니다.
- utils.py: 브라우저 상호작용 및 데이터 저장을 위한 유틸리티 함수들을 포함합니다.
- config.py: 타임아웃, XPath 선택자 등 구성 상수를 정의합니다.
- getRestaurantData.py: 대용량 CSV 파일을 분할하고 전처리합니다.
- setRestaurantData.py: 영업 중인 사업체만 포함하도록 데이터를 필터링합니다.
- setLoc.py: 위치 데이터를 계층적으로 처리합니다.
- convertRestaurantData.py: 사업체 데이터를 필요한 형식으로 변환합니다.

# 설치

- 레포지토리 클론:
- git clone https://github.com/yourusername/selenium-menu-extractor.git
cd selenium-menu-extractor

- 필요한 Python 라이브러리 설치:
- pip install -r requirements.txt



# 로깅 및 추출 예시

![image](https://github.com/user-attachments/assets/0ead8d17-6292-4e59-bd81-d3073b0ceff8)
![image](https://github.com/user-attachments/assets/b70c5b61-f87f-4193-940e-7ec3db2a09c8)
![image](https://github.com/user-attachments/assets/e4651962-52cf-48ae-bc96-18cad62b620e)
![image](https://github.com/user-attachments/assets/98befe21-61ec-46e7-a04c-02527a532937)
![image](https://github.com/user-attachments/assets/c78eb29e-d2de-4a23-be38-2efe9fd5ddd9)



