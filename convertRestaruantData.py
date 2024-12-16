import pandas as pd
from pyproj import Proj, Transformer

# 좌표 변환 설정 (EPSG:5174 -> EPSG:4326)
transformer = Transformer.from_crs("EPSG:5174", "EPSG:4326", always_xy=True)

# CSV 파일 읽기
file_path = r"C:\Users\rhzn5\Downloads\07_24_04_P_CSV\fulldata_filtered.csv"
output_path = r"C:\Users\rhzn5\Downloads\07_24_04_P_CSV\fulldata_converted.csv"
data = pd.read_csv(file_path, encoding="euc-kr")

# 좌표 변환 함수 정의
def convert_coordinates(x, y):
    if pd.notnull(x) and pd.notnull(y):
        lng, lat = transformer.transform(x, y)
        return lat, lng
    return None, None

# 변환 수행
data[['위도', '경도']] = data.apply(
    lambda row: convert_coordinates(row['좌표정보(x)'], row['좌표정보(y)']), axis=1, result_type='expand'
)

# 기존 x, y 컬럼 제거
data.drop(columns=['좌표정보(x)', '좌표정보(y)'], inplace=True)

# 결과 저장
data.to_csv(output_path, encoding="euc-kr", index=False)
print(f"변환된 데이터를 '{output_path}'에 저장했습니다.")
