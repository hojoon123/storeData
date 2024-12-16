import os

# TXT 파일 리스트
korea = [
    r"C:\Users\rhzn5\Downloads\대한민국\ACMM_ADMSECT_인천\ACMM_ADMSECT_28_202404.txt",
    r"C:\Users\rhzn5\Downloads\대한민국\ACMM_ADMSECT_서울\ACMM_ADMSECT_11_202404.txt",
    r"C:\Users\rhzn5\Downloads\대한민국\ACMM_ADMSECT_부산\ACMM_ADMSECT_26_202404.txt",
    r"C:\Users\rhzn5\Downloads\대한민국\ACMM_ADMSECT_충북\ACMM_ADMSECT_43_202404.txt",
    r"C:\Users\rhzn5\Downloads\대한민국\ACMM_ADMSECT_충남\ACMM_ADMSECT_44_202404.txt",
    r"C:\Users\rhzn5\Downloads\대한민국\ACMM_ADMSECT_전남\ACMM_ADMSECT_46_202404.txt",
    r"C:\Users\rhzn5\Downloads\대한민국\ACMM_ADMSECT_울산\ACMM_ADMSECT_31_202404.txt",
    r"C:\Users\rhzn5\Downloads\대한민국\ACMM_ADMSECT_세종\ACMM_ADMSECT_36_202404.txt",
    r"C:\Users\rhzn5\Downloads\대한민국\ACMM_ADMSECT_제주\ACMM_ADMSECT_50_202404.txt",
    r"C:\Users\rhzn5\Downloads\대한민국\ACMM_ADMSECT_전북특별자치도\ACMM_ADMSECT_52_202404.txt",
    r"C:\Users\rhzn5\Downloads\대한민국\ACMM_ADMSECT_대구\ACMM_ADMSECT_27_202404.txt",
    r"C:\Users\rhzn5\Downloads\대한민국\ACMM_ADMSECT_광주\ACMM_ADMSECT_29_202404.txt",
    r"C:\Users\rhzn5\Downloads\대한민국\ACMM_ADMSECT_대전\ACMM_ADMSECT_30_202404.txt",
    r"C:\Users\rhzn5\Downloads\대한민국\ACMM_ADMSECT_경기\ACMM_ADMSECT_41_202404.txt",
    r"C:\Users\rhzn5\Downloads\대한민국\ACMM_ADMSECT_전북\ACMM_ADMSECT_45_202310.txt",
    r"C:\Users\rhzn5\Downloads\대한민국\ACMM_ADMSECT_경북\ACMM_ADMSECT_47_202404.txt",
    r"C:\Users\rhzn5\Downloads\대한민국\ACMM_ADMSECT_경남\ACMM_ADMSECT_48_202404.txt",
    r"C:\Users\rhzn5\Downloads\대한민국\ACMM_ADMSECT_강원특별자치도\ACMM_ADMSECT_51_202404.txt"
]

# 현재 디렉토리에서 output 디렉토리 생성
output_directory = os.path.join(os.getcwd(), "output")
os.makedirs(output_directory, exist_ok=True)

for file_path in korea:
    # 부모 디렉토리명 추출 (예: "ACMM_ADMSECT_인천")
    parent_dir_name = os.path.basename(os.path.dirname(file_path))

    # "ACMM_ADMSECT_" 제거 후 지역명만 추출
    region_name = parent_dir_name.replace("ACMM_ADMSECT_", "")

    # 결과 파일명 지정
    output_file_path = os.path.join(output_directory, f"{region_name}_EXTRACTED.txt")

    with open(file_path, 'r', encoding='euc-kr') as infile, \
            open(output_file_path, 'w', encoding='euc-kr') as outfile:

        for line in infile:
            line = line.strip()
            # 헤더라인 건너뛰기
            if line.startswith("ADM_SECT_GBN"):
                continue

            parts = line.split('|')
            if len(parts) > 2:
                adm_sect_nm = parts[2].strip()
                if adm_sect_nm:
                    outfile.write(adm_sect_nm + "\n")
