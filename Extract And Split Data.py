import pandas as pd

# 경로 설정
fulldata_path = r"C:\Users\rhzn5\Downloads\07_24_04_P_CSV\filtered_excluded.csv"
end_store_log_path = r"C:\GitHub\storeData\output_restaurant\end_store_log.csv"
error_log_path = r"C:\GitHub\storeData\output_restaurant\error_log.csv"
output_path_included = r"C:\Users\rhzn5\Downloads\07_24_04_P_CSV\filtered_included.csv"
output_path_excluded = r"C:\Users\rhzn5ㅂ\Downloads\07_24_04_P_CSV\filtered_excluded.csv"

# 추가되는 부분: '이건 진짜 모르는 에러다' 데이터 저장 경로
output_path_unknown_error = r"C:\Users\rhzn5\Downloads\07_24_04_P_CSV\filtered_error_case.csv"

# 데이터 로드
fulldata_df = pd.read_csv(fulldata_path, encoding="euc-kr")
end_store_log_df = pd.read_csv(end_store_log_path, encoding="euc-kr")
error_log_df = pd.read_csv(error_log_path, encoding="euc-kr")

# 도로명우편번호에서 소수점 제거
fulldata_df["도로명우편번호"] = fulldata_df["도로명우편번호"].astype(str).str.split('.').str[0]

# 데이터 타입 변환
fulldata_df["번호"] = fulldata_df["번호"].astype(str)
end_store_log_df["Business_Num"] = end_store_log_df["Business_Num"].astype(str)
error_log_df["Business_Num"] = error_log_df["Business_Num"].astype(str)

# 성공 처리된 Business_Num 추출
successful_business_nums = set(end_store_log_df["Business_Num"].unique())

# '검색 결과 없음', '우편번호 불일치', '메뉴 버튼 없음' 조건에 해당하는 Business_Num 추출
excluded_error_messages = [
    "검색 결과 없음 또는 첫 번째 가게 접근 불가 ",
    "우편번호 불일치",
    "메뉴 버튼 없음"
]
failed_business_nums = set(
    error_log_df[error_log_df["Error_Message"].isin(excluded_error_messages)]["Business_Num"].unique()
)

np_error_messages = [
    "이건 진짜 모르는 에러다",
    "메뉴 조회 실패 or 없음"
    ]


# 추가: '이건 진짜 모르는 에러다' + 메뉴 조회 실패 에 해당하는 Business_Num 추출
unknown_error_nums = set(
    error_log_df[error_log_df["Error_Message"].isin(np_error_messages)]["Business_Num"].unique()
)

# 포함된 데이터에 해당하는 Business_Num (성공 + 실패 조건)
included_business_nums = successful_business_nums.union(failed_business_nums)

# 디버깅용 출력
print(f"성공 처리된 Business_Num 개수: {len(successful_business_nums)}")
print(f"제외 조건에 해당하는 Business_Num 개수: {len(failed_business_nums)}")
print(f"전체 포함된 Business_Num 개수: {len(included_business_nums)}")
print(f"미지의 에러(이건 진짜 모르는 에러다) Business_Num 개수: {len(unknown_error_nums)}")

# 포함된 데이터: 성공 + 실패 데이터 모두 포함
included_data = fulldata_df[fulldata_df["번호"].isin(included_business_nums)]

# 제외된 데이터: 성공 + 실패를 제외한 나머지
excluded_data = fulldata_df[~fulldata_df["번호"].isin(included_business_nums)]

# unknown_error_nums에 해당하는 데이터는 excluded_data 중에서 추출
filtered_error_case = excluded_data[excluded_data["번호"].isin(unknown_error_nums)]

# unknown_error_nums에 해당하는 데이터는 excluded에서 제거
excluded_data = excluded_data[~excluded_data["번호"].isin(unknown_error_nums)]

# 디버깅용 출력
print(f"포함된 데이터 개수: {len(included_data)}")
print(f"제외된 데이터 개수 (미지의 에러 제외 전): {len(excluded_data) + len(filtered_error_case)}")
print(f"미지의 에러 데이터 개수: {len(filtered_error_case)}")
print(f"제외된 데이터 개수 (미지의 에러 제외 후): {len(excluded_data)}")

# 파일로 저장
included_data.to_csv(output_path_included, index=False, encoding="euc-kr")
excluded_data.to_csv(output_path_excluded, index=False, encoding="euc-kr")

# 미지의 에러 데이터 & 메뉴 조회 없음 데이터 저장
filtered_error_case.to_csv(output_path_unknown_error, index=False, encoding="euc-kr")

print(f"포함된 데이터는 {output_path_included}에 저장되었습니다.")
print(f"제외된 데이터는 {output_path_excluded}에 저장되었습니다.")
print(f"미지의 에러 데이터는 {output_path_unknown_error}에 저장되었습니다.")