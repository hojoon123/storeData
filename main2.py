from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
import os
import json

# 파일 저장 함수
def save_to_json(data, *path_parts):
    """
    데이터를 JSON 파일로 저장.
    path_parts: 디렉토리 경로 구성에 사용될 매개변수들
    """
    # 디렉토리 경로 구성
    directory_path = os.path.join(*path_parts[:-1])  # 마지막 항목 제외
    file_name = f"{path_parts[-1]}.json"  # 마지막 항목을 파일 이름으로 사용

    # 디렉토리 생성 (존재하지 않을 경우)
    os.makedirs(directory_path, exist_ok=True)

    # 파일 경로 생성
    file_path = os.path.join(directory_path, file_name)

    # JSON 데이터 저장
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    print(f"데이터가 {file_path}에 저장되었습니다.")


# iframe 전환 함수
def switch_to_iframe(iframe_id):
    """특정 iframe으로 전환"""
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, iframe_id))
    )
    driver.switch_to.frame(iframe_id)

def switch_to_default():
    """기본 DOM으로 복귀"""
    driver.switch_to.default_content()

def search_store(store_name):
    """음식점 검색"""
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input.input_search'))
    )
    search_box.send_keys(store_name)  # 검색어 입력
    search_box.send_keys(Keys.RETURN)  # Enter 키 입력으로 검색


def load_all_list_items():
    """스크롤을 끝까지 내려 모든 li 태그 로드"""
    scroll_container = driver.find_element(By.XPATH, '//*[@id="_pcmap_list_scroll_container"]')
    prev_height = -1

    while True:
        # 현재 스크롤 높이
        current_height = driver.execute_script("return arguments[0].scrollHeight", scroll_container)

        # 스크롤 끝까지 내리기
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_container)
        time.sleep(1)  # 스크롤 대기

        # 스크롤 끝까지 도달했는지 확인
        if current_height == prev_height:
            break
        prev_height = current_height

    # 모든 li 태그 가져오기
    list_items = driver.find_elements(By.XPATH, '//*[@id="_pcmap_list_scroll_container"]/ul/li')
    return list_items

def scroll_into_view(xpath):
    """요소를 화면 중앙으로 스크롤"""
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    time.sleep(1)  # 스크롤 후 대기

def extract_store_details():
    """가게 상세 정보를 추출"""
    switch_to_default()
    switch_to_iframe("entryIframe")

    store_name = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="_title"]/div/span[1]'))
    ).text

    store_location = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="app-root"]/div/div/div/div[5]/div/div[2]/div[1]/div/div[1]/div/a/span[1]'))
    ).text

    menu_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="app-root"]/div/div/div/div[4]/div/div/div/div/a[2]'))
    )
    menu_button.click()
    time.sleep(1)  # 페이지 전환 대기

    menu_data = extract_menu_details()

    # 기본 DOM으로 복귀
    switch_to_default()
    switch_to_iframe("searchIframe")

    return {
        "store_name": store_name,
        "store_location": store_location,
        "menu": menu_data
    }

def click_button_until_end(button_xpath, cooldown=1):
    """버튼을 끝날 때까지 클릭"""
    while True:
        try:
            # 버튼 클릭
            button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, button_xpath))
            )
            button.click()
            time.sleep(cooldown)  # 쿨타임
        except TimeoutException:
            #버튼이 없으면 반복 종료
            break

def extract_menu_details():
    """메뉴 정보를 추출"""
    more_button_xpath = '//*[@id="app-root"]/div/div/div/div[6]/div[2]/div[1]/div[2]/div/a'
    ul_xpath = '//*[@id="app-root"]/div/div/div/div[5]/div[2]/div[1]/div/ul'

    click_button_until_end(more_button_xpath)

    menu_items = driver.find_elements(By.XPATH, f'{ul_xpath}/li')
    menu_data = []

    for i, item in enumerate(menu_items, start=1):
        try:
            img_src = item.find_element(By.CLASS_NAME, "place_thumb").find_element(By.TAG_NAME, "img").get_attribute("src")
            menu_name = item.find_element(By.XPATH, f'{ul_xpath}/li[{i}]/a/div[2]/div[1]/div/span[1]').text
            additional_info = item.find_element(By.XPATH, f'{ul_xpath}/li[{i}]/a/div[2]/div[2]/div').text
            price = item.find_element(By.XPATH, f'{ul_xpath}/li[{i}]/a/div[2]/div[3]/em').text

            menu_data.append({
                "img_src": img_src,
                "menu_name": menu_name,
                "additional_info": additional_info,
                "price": price
            })
        except Exception as e:
            print(f"메뉴 {i} 추출 중 오류 발생: {e}")
            continue

    return menu_data

def click_next_page():
    """다음 페이지로 이동"""
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="app-root"]/div/div[2]/div[2]/a[7]'))
        )
        next_button.click()
        time.sleep(2)
    except TimeoutException:
        print("다음 페이지 없음")
        raise

def scrape_restaurant_data(*search_terms):
    """
    음식점 데이터를 검색어 기준으로 크롤링하고 JSON으로 저장.
    search_terms: 검색어와 디렉토리 경로를 구성할 매개변수
    """
    try:
        # 검색어 구성
        search_query = " ".join(search_terms)
        print(f"검색어: {search_query}")

        # 네이버 지도 접속
        driver.get('https://map.naver.com/')
        search_store(search_query)

        # 검색 결과 iframe으로 전환
        switch_to_iframe("searchIframe")

        # 데이터 저장용 리스트
        extracted_data = []

        while True:
            list_items = load_all_list_items()

            for i, item in enumerate(list_items, start=1):
                item_xpath = f'//*[@id="_pcmap_list_scroll_container"]/ul/li[{i}]//a'
                store = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, item_xpath))
                )
                store.click()

                # 상세 정보 추출
                store_details = extract_store_details()
                extracted_data.append(store_details)

            try:
                click_next_page()
            except:
                print("마지막 페이지 도달")
                break

        # 디렉토리에 JSON 저장
        save_to_json(extracted_data, *search_terms)

    except Exception as e:
        print("에러 발생:", e)

    finally:
        driver.quit()



# 실행 예시
if __name__ == "__main__":
    # 크롬 브라우저 실행
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # 검색어와 디렉토리 경로 구성
    scrape_restaurant_data("전라남도", "목포시", "음식점")