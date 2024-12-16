import csv

input_file = r"C:\Users\rhzn5\Downloads\07_24_04_P_CSV\fulldata_07_24_04_P_일반음식점.csv"
output_file = r"C:\Users\rhzn5\Downloads\07_24_04_P_CSV\fulldata_filtered.csv"

# 남길 컬럼들
columns_to_keep = [
    "번호",
    "개방서비스명",
    "소재지전체주소",
    "도로명전체주소",
    "도로명우편번호",
    "사업장명",
    "좌표정보(x)",
    "좌표정보(y)"
]

# euc-kr 인코딩으로 읽고, 쓰기 시에도 errors='replace'로 인코딩 불가 문자 대체
with open(input_file, 'r', encoding='euc-kr', errors='replace') as f_in, \
     open(output_file, 'w', encoding='euc-kr', errors='replace', newline='') as f_out:
    reader = csv.reader(f_in)
    writer = csv.writer(f_out)

    header = next(reader)
    # 각 열의 인덱스 파악
    col_index = {col: idx for idx, col in enumerate(header)}

    # 남길 열의 인덱스 리스트
    keep_indexes = [col_index[col] for col in columns_to_keep]

    # 필터링된 헤더 작성
    writer.writerow(columns_to_keep)

    # "영업상태명" 열 인덱스
    business_status_col = col_index["영업상태명"]

    for row in reader:
        # 영업상태명 확인
        status = row[business_status_col]
        # 폐업이 아닌 경우만 기록
        if status != "폐업":
            # 필요한 열만 추출
            filtered_row = [row[i] for i in keep_indexes]
            writer.writerow(filtered_row)

print("필터링 완료:", output_file)
