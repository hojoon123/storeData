import os
import json

from selenium.webdriver import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from config import TIMEOUT, SEARCH_INPUT_XPATH


def save_to_json(data, *path_parts):
    """
    데이터를 JSON 파일로 저장.
    path_parts: 디렉토리 경로 구성에 사용될 매개변수들
    """
    *directory_parts, file_name = path_parts
    directory_path = os.path.join(*directory_parts)

    os.makedirs(directory_path, exist_ok=True)

    file_path = os.path.join(directory_path, f"{file_name}.json")

    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    print(f"데이터가 {file_path}에 저장되었습니다.")

def switch_to_iframe(driver, iframe_id):
    """특정 iframe으로 전환"""
    WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.ID, iframe_id))
    )
    driver.switch_to.frame(iframe_id)

def switch_to_default(driver):
    """기본 DOM으로 복귀"""
    driver.switch_to.default_content()

def search_store(driver, search_query):
    """음식점 검색"""

    search_box = WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, SEARCH_INPUT_XPATH))
    )
    search_box.click()
    search_box.send_keys(Keys.CONTROL + "a")  # 모든 텍스트 선택 (Windows/Linux)
    search_box.send_keys(Keys.DELETE)

    search_box.send_keys(search_query)
    search_box.send_keys(Keys.RETURN)  # Enter

def load_all_list_items(driver):
    """
    스크롤을 끝까지 내려 모든 li 태그 로드
    """
    scroll_container = WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="_pcmap_list_scroll_container"]'))
    )
    prev_height = -1

    while True:
        current_height = driver.execute_script("return arguments[0].scrollHeight", scroll_container)
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_container)
        # 스크롤 후 기다리기
        WebDriverWait(driver, 1).until(lambda d: True)
        if current_height == prev_height:
            break
        prev_height = current_height

    # 모든 li 태그 가져오기
    list_items = driver.find_elements(By.XPATH, '//*[@id="_pcmap_list_scroll_container"]/ul/li')
    return list_items
