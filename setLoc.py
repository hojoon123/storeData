import os
import json

# 입력 txt 경로 리스트
input_paths = [
    r"C:\GitHub\storeData\output\서울_EXTRACTED.txt",         # 서울특별시
    r"C:\GitHub\storeData\output\부산_EXTRACTED.txt",         # 부산광역시
    r"C:\GitHub\storeData\output\대구_EXTRACTED.txt",         # 대구광역시
    r"C:\GitHub\storeData\output\인천_EXTRACTED.txt",         # 인천광역시
    r"C:\GitHub\storeData\output\광주_EXTRACTED.txt",         # 광주광역시
    r"C:\GitHub\storeData\output\대전_EXTRACTED.txt",         # 대전광역시
    r"C:\GitHub\storeData\output\울산_EXTRACTED.txt",         # 울산광역시
    r"C:\GitHub\storeData\output\세종_EXTRACTED.txt",         # 세종특별자치시
    r"C:\GitHub\storeData\output\경기_EXTRACTED.txt",         # 경기도
    r"C:\GitHub\storeData\output\강원특별자치도_EXTRACTED.txt", # 강원특별자치도
    r"C:\GitHub\storeData\output\충북_EXTRACTED.txt",         # 충청북도
    r"C:\GitHub\storeData\output\충남_EXTRACTED.txt",         # 충청남도
    r"C:\GitHub\storeData\output\전북특별자치도_EXTRACTED.txt", # 전북특별자치도
    r"C:\GitHub\storeData\output\전남_EXTRACTED.txt",         # 전라남도
    r"C:\GitHub\storeData\output\경북_EXTRACTED.txt",         # 경상북도
    r"C:\GitHub\storeData\output\경남_EXTRACTED.txt",         # 경상남도
    r"C:\GitHub\storeData\output\제주_EXTRACTED.txt"          # 제주특별자치도
]

# 출력 경로 설정
output_base_dir = r"C:\GitHub\storeData\output2"
os.makedirs(output_base_dir, exist_ok=True)

# 최소단위로 인정할 행정구역 접미사
MINIMAL_UNITS = ('동', '읍', '면')
EXCLUDED_UNITS = ('리',)  # 제외할 단위

def insert_hierarchy(root_dict, hierarchy_list):
    """
    계층 구조에 따라 root_dict에 데이터를 삽입하는 함수.
    hierarchy_list 예) ["경기도","수원시","장안구","파장동"]
    """
    current = root_dict
    for i, part in enumerate(hierarchy_list):
        is_last = (i == len(hierarchy_list) - 1)

        # 리 단위 제외
        if is_last and any(part.endswith(ex) for ex in EXCLUDED_UNITS):
            # 해당 라인 추가하지 않음
            return

        if is_last:
            # 마지막 토큰 처리
            if any(part.endswith(unit) for unit in MINIMAL_UNITS):
                # 동/읍/면일 경우 리프노드
                if part not in current:
                    current[part] = {}
            else:
                # 마지막이지만 읍/면/동이 아닐 경우도 dict로
                if part not in current:
                    current[part] = {}
        else:
            # 중간 단위
            if part not in current:
                current[part] = {}
            current = current[part]

# 각 파일 별로 JSON 생성
for file_path in input_paths:
    # 파일명에서 지역명 추출 (예: "서울_EXTRACTED.txt" -> "서울")
    base_name = os.path.basename(file_path)
    region_name = base_name.replace("_EXTRACTED.txt", "")

    hierarchy_dict = {}

    with open(file_path, 'r', encoding='euc-kr', errors='replace') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # 공백 기준 split
            parts = line.split()
            insert_hierarchy(hierarchy_dict, parts)

    # 지역명으로 된 json 파일 출력
    output_json_path = os.path.join(output_base_dir, f"{region_name}.json")
    with open(output_json_path, 'w', encoding='utf-8') as out:
        json.dump(hierarchy_dict, out, ensure_ascii=False, indent=4)

    print("JSON 변환 완료:", output_json_path)
