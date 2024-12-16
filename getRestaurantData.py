input_file = r"C:\Users\rhzn5\Downloads\07_24_04_P_CSV\fulldata_07_24_04_P_일반음식점.csv"
output_dir = r"C:\Users\rhzn5\Downloads\07_24_04_P_CSV\split_files"
lines_per_file = 100000  # 10만 줄 단위로 분할

import os

os.makedirs(output_dir, exist_ok=True)

file_count = 1
line_count = 0
out_file = None

try:
    with open(input_file, 'r', encoding='euc-kr', errors='replace') as f_in:
        for line in f_in:
            if line_count % lines_per_file == 0:
                # 새로운 출력 파일을 연다
                if out_file:
                    out_file.close()
                out_file_path = os.path.join(output_dir, f"split_{file_count:04d}.csv")
                out_file = open(out_file_path, 'w', encoding='euc-kr', errors='replace')
                print(f"{out_file_path} 생성 시작")
                file_count += 1
            out_file.write(line)
            line_count += 1

finally:
    if out_file:
        out_file.close()

print("파일 분할 완료!")
