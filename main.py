import os
import csv
import time
from datetime import datetime

from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from urllib3.exceptions import ReadTimeoutError, HTTPError
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from scraper import extract_full_details_if_matched, click_next_page
from utils import switch_to_iframe, switch_to_default, search_store, load_all_list_items, save_to_json
from config import TIMEOUT, LIST_UL_XPATH
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

input_file = r"C:\Users\rhzn5\Downloads\07_24_04_P_CSV\filtered_excluded.csv"
output_directory = r"C:\GitHub\storeData\output_restaurant"
os.makedirs(output_directory, exist_ok=True)

log_file = os.path.join(output_directory, "error_log.csv")
end_file_path = os.path.join(output_directory, "end_store_log.csv")

# 로그 파일 초기화
if not os.path.exists(log_file):
    with open(log_file, mode="w", newline="", encoding="euc-kr") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Business_Num", "Business_Name", "Error_Message"])

if not os.path.exists(end_file_path):
    with open(end_file_path, mode="w", newline="", encoding="euc-kr") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Business_Num", "Business_Name", "Details"])

# 로그 함수
def log_error(business_num, business_name, message):
    """오류 로그 기록"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, mode="a", newline="", encoding="euc-kr") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, business_num, business_name, message])
    print(f"[{timestamp}] 번호: {business_num}, 사업장명: {business_name}, 오류: {message}")

def log_success(business_num, business_name, message):
    """성공 로그 기록"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(end_file_path, mode="a", newline="", encoding="euc-kr") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, business_num, business_name, message])
    print(f"[{timestamp}] 번호: {business_num}, 사업장명: {business_name}, 성공: {message}")


def handle_new_tab(driver, original_window, business_num, business_name):
    """
    새 창 또는 탭이 열렸는지 확인하고, 필요시 닫고 원래 창으로 돌아갑니다.
    """
    # 현재 모든 열린 창 가져오기
    current_windows = driver.window_handles

    # 새 창이 열렸는지 확인
    if len(current_windows) > 1:
        print(f"[{business_num}] {business_name} - 광고 또는 새 창이 감지됨")
        log_error(business_num, business_name, "광고 또는 새 창이 열렸음")

        # 새 창으로 전환
        for window in current_windows:
            if window != original_window:
                driver.switch_to.window(window)
                driver.close()  # 새 창 닫기
                print(f"[{business_num}] {business_name} - 새 창 닫음")

        # 원래 창으로 복귀
        driver.switch_to.window(original_window)

    return True
def is_network_error(driver):
    """
    네트워크 에러(404 등)를 감지하는 함수.
    """
    try:
        error_element = driver.find_element(By.XPATH, "//h1[contains(text(), '404') or contains(text(), '찾을 수 없습니다')]")
        return True if error_element else False
    except NoSuchElementException:
        return False

def scrape_by_business_name(driver, business_name, expected_postcode, address_jibun, business_num, loc_x, loc_y):
    """
    사업장명을 검색한 후, 검색 결과 목록을 페이지 단위로 순회.
    store_location이 주어진 주소와 일치하는 가게를 찾으면:
      - 메뉴 버튼 클릭, 메뉴 추출
      - 메뉴 없으면 폐업 처리(무시)
      - 메뉴 있으면 JSON 저장 후 True 반환
    찾지 못하면 False 반환.
    """
    switch_to_default(driver)

    # 소재지 검색 -> 사업장명 검색
    try:
        search_store(driver, address_jibun)
        time.sleep(2)

        search_store(driver, business_name)
        switch_to_iframe(driver, "searchIframe")

        try:
            # 첫 번째 가게 클릭
            first_item_xpath = f'{LIST_UL_XPATH}/li[1]//a'
            store_link = WebDriverWait(driver, TIMEOUT).until(
                EC.element_to_be_clickable((By.XPATH, first_item_xpath))
            )
            store_link.click()
            time.sleep(2)

            # 404 에러 감지
            if is_network_error(driver):
                log_error(business_num, business_name, "404 에러 또는 네트워크 문제 발생")
                return 0  # 재시도 필요

        except ElementClickInterceptedException:
            pass # 바로 entry로 진입하면 클릭이 안 됨

        except TimeoutException:
            log_error(business_num, business_name, "검색 결과 없음 또는 첫 번째 가게 접근 불가 ")
            return 2  # 정상 실패

        # entryIframe에서 세부 정보 추출
        details = extract_full_details_if_matched(
            driver, switch_to_iframe, switch_to_default, expected_postcode, business_num, loc_x, loc_y
        )

        if details:
            if details == 400:
                log_error(business_num, business_name, "메뉴 버튼 없음")
                return 2
            if details == 401:
                log_error(business_num, business_name, "메뉴 조회 실패 or 없음")
                return 2
            # 성공 시 JSON 저장
            file_name = business_num + '_' + details["store_name"]
            save_to_json(details, output_directory, file_name)
            log_success(business_num, business_name, "성공적으로 메뉴 추출 완료")
            return 1  # 성공
        else:
            log_error(business_num, business_name, "우편번호 불일치")
            return 2  # 정상 실패
    except ReadTimeoutError:
        log_error(business_num, business_name, "네트워크 타임아웃 발생")
        return 0  # 재시도 필요
    except HTTPError:
        log_error(business_num, business_name, f"HTTP 에러 발생")
        return 0  # 재시도 필요
    except:
        log_error(business_num, business_name, "이건 진짜 모르는 에러다")
        return 2  # 정상 실패


def scrape_with_retry(driver, business_name, expected_postcode, address_jibun, business_num, loc_x, loc_y):
    """
    특정 사업장 정보를 재시도 로직과 함께 처리.
    """
    original_window = driver.current_window_handle  # 작업 시작 시 현재 창 저장

    for attempt in range(MAX_RETRIES):
        print(f"[{business_num}] {business_name} - {attempt + 1}번째 시도")
        result = scrape_by_business_name(driver, business_name, expected_postcode, address_jibun, business_num, loc_x,
                                         loc_y)

        if result == 1:
            return True  # 성공
        elif result == 2:
            return False  # 정상 실패로 종료
        elif attempt < MAX_RETRIES - 1:  # 재시도 필요
            print(f"[{business_num}] {business_name} - 새로고침 후 재시도")
            driver.refresh()
            time.sleep(3)
        else:
            log_error(business_num, business_name, "최대 재시도 횟수 초과로 중단")
            return False

    handle_new_tab(driver, original_window, business_num, business_name)  # 광고 창 확인 및 처리
    return False

def create_driver():
    """Create and return a new Selenium driver instance."""
    chrome_options = Options()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-popup-blocking')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--enable-features=NetworkServiceInProcess')
    chrome_options.add_argument('--disable-application-cache')
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def restart_driver(driver):
    """Restart the Selenium driver."""
    print("드라이버 재시작 중...")
    driver.quit()
    time.sleep(2)
    return create_driver()


if __name__ == "__main__":
    MAX_RETRIES = 3
    RESTART_THRESHOLD = 50
    driver = create_driver()
    driver.get('https://map.naver.com/')

    try:
        operation_count = 0

        with open(input_file, 'r', encoding='euc-kr', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                business_name = row["사업장명"].strip()
                expected_postcode = row["도로명우편번호"].strip() if row["도로명우편번호"] else ""
                address_jibun = row["소재지전체주소"].strip() if row["소재지전체주소"] else ""
                loc_x = row["좌표정보(x)"].strip() if row["좌표정보(x)"] else ""
                loc_y = row["좌표정보(y)"].strip() if row["좌표정보(y)"] else ""

                business_num = row["번호"].strip()

                if not business_name or not expected_postcode:
                    log_error(business_num, business_name, "사업장명 또는 우편번호 누락")
                    continue

                scrape_with_retry(
                    driver, business_name, expected_postcode, address_jibun, business_num, loc_x, loc_y
                )
                operation_count += 1

                # Restart driver every RESTART_THRESHOLD operations
                if operation_count >= RESTART_THRESHOLD:
                    driver = restart_driver(driver)
                    driver.get('https://map.naver.com/')
                    operation_count = 0


    finally:
        driver.quit()
