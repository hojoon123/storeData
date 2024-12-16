import csv
import os
import re
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config import *




LOG_DIR = r"C:\GitHub\storeData\output_restaurant"
LOG_FILE_PATH = os.path.join(LOG_DIR, "address_match_log.csv")
OLD_VERSION_LOG = os.path.join(LOG_DIR, "old_version_menu_log.csv")
NEW_VERSION_LOG = os.path.join(LOG_DIR, "new_version_menu_log.csv")

# 로그 파일 초기화(없으면 헤더 작성)
for log_file, version_header in [(OLD_VERSION_LOG, "old"), (NEW_VERSION_LOG, "new")]:
    if not os.path.exists(log_file):
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, mode="w", newline="", encoding="euc-kr") as file:
            writer = csv.writer(file)
            # version, business_num, store_name, store_location, loc_x, loc_y, expected_postcode, message, timestamp
            writer.writerow(["version", "business_num", "store_name", "store_location", "loc_x", "loc_y", "expected_postcode", "message", "Timestamp"])

if not os.path.exists(LOG_FILE_PATH):
    with open(LOG_FILE_PATH, mode="w", newline="", encoding="euc-kr") as file:
        writer = csv.writer(file)
        writer.writerow(["business_num","Match", "store_location_text", "expected_postcode", "store_location", "Timestamp"])

def log_match_result(match, store_location_text, expected_postcode, store_location, business_num):
    with open(LOG_FILE_PATH, mode="a", newline="", encoding="euc-kr") as file:
        writer = csv.writer(file)
        writer.writerow([business_num, match, store_location_text, expected_postcode, store_location, time.strftime("%Y-%m-%d %H:%M:%S")])

def log_menu_issue(version, business_num, store_name, store_location, loc_x, loc_y, expected_postcode, message):
    """메뉴 추출 중 오류나 불완전성 발생 시 로그 기록"""
    log_file = OLD_VERSION_LOG if version == "old" else NEW_VERSION_LOG
    with open(log_file, mode="a", newline="", encoding="euc-kr") as file:
        writer = csv.writer(file)
        writer.writerow([version, business_num, store_name, store_location, loc_x, loc_y, expected_postcode, message, time.strftime("%Y-%m-%d %H:%M:%S")])

def click_button_until_end(driver, button_xpath, cooldown=1):
    """버튼을 끝날 때까지 클릭"""
    while True:
        try:
            button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, button_xpath))
            )
            button.click()
            time.sleep(cooldown)
        except TimeoutException:
            break


def extract_menu_details(driver, business_num, store_name, store_location, loc_x, loc_y, expected_postcode):
    """메뉴 정보를 추출 - 구버전/신버전 판별 후 각기 다른 로직 적용"""

    # 구버전 XPath
    old_version_xpath = '//*[@id="app-root"]/div/div/div/div[6]/div[2]/div[1]/div'
    old_version_xpath2 = '//*[@id="app-root"]/div/div/div/div[5]/div[2]/div[1]/div'
    old_version_container = ''

    # 신버전 XPath (카테고리/리스트)
    new_version_category_xpath = '//*[@id="root"]/div[3]/div/div/div[1]'
    new_version_list_xpath = '//*[@id="root"]/div[3]/div/div/div[2]'

    # 버전3 XPATH
    version3_xapth = '//*[@id="app-root"]/div/div/div/div[6]/div'

    menu_data = []

    # 구버전 판별
    try:
        # 먼저 div6 확인
        old_version_container = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, old_version_xpath))
        )
    except TimeoutException:
        # div6이 없으면 div5 확인
        try:
            old_version_container = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, old_version_xpath2))
            )
        except TimeoutException:
            pass

    if old_version_container:
        print("구버전 메뉴판 구조 감지")
        menu_data = extract_old_version_menu(driver, old_version_container, business_num, store_name, store_location,
                                             loc_x, loc_y, expected_postcode)
        return menu_data
    # 신버전 판별
    try:
        # 카테고리 영역 확인
        new_version_category = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.XPATH, new_version_category_xpath))
        )
        new_version_list = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.XPATH, new_version_list_xpath))
        )
        if new_version_category and new_version_list:
            print("신버전 메뉴판 구조 감지")
            menu_data = extract_new_version_menu(driver, new_version_list_xpath, business_num, store_name, store_location, loc_x, loc_y, expected_postcode)
            return menu_data
    except TimeoutException:
        # 신버전 구조도 없음
        print("메뉴판 구조를 감지하지 못했습니다.")
        pass

    # 3. 버전3 처리
    try:
        version3_container = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, version3_xapth))
        )
        print("버전3 메뉴판 감지")
        menu_data = extract_version3_menu(driver, version3_container, business_num, store_name, store_location, loc_x,
                                          loc_y, expected_postcode)
        return menu_data
    except TimeoutException:
        print("버전3 메뉴판 감지 실패")

    # 어떤 구조도 감지 못한 경우
    print("메뉴판 없음 또는 인식 불가")
    log_menu_issue("new", business_num, store_name, store_location, loc_x, loc_y, expected_postcode,
                   "No menu panel detected (neither old nor new)")
    return menu_data

def extract_version3_menu(driver, version3_xpath, business_num, store_name, store_location, loc_x, loc_y, expected_postcode):
    """
    버전3 메뉴판 데이터 추출
    """
    menu_data = []

    try:
        # 카테고리 섹션 탐색
        categories = version3_xpath.find_elements(By.XPATH, ".//div[contains(@class, 'place_section gkWf3')]")
        for category_index, category in enumerate(categories, start=1):
            try:
                # 카테고리 제목 추출
                category_name = category.find_element(By.XPATH, ".//h2[contains(@class, 'place_section_header')]/div").text.strip()

                # 더보기 버튼 클릭 (있는 경우)
                try:
                    more_button = category.find_element(By.XPATH, ".//div[contains(@class, 'NSTUp')]/div/a")
                    more_button.click()
                    time.sleep(1)  # 버튼 클릭 후 로드 대기
                except NoSuchElementException:
                    pass  # 더보기 버튼이 없는 경우 무시

                # 메뉴 항목 추출
                menu_items = category.find_elements(By.XPATH, ".//div[contains(@class, 'place_section_content')]/ul/li")
                for item in menu_items:
                    try:
                        # 썸네일 추출
                        try:
                            img_elem = item.find_element(By.XPATH, "./a/div[1]/img")
                            img_src = img_elem.get_attribute("src") if img_elem else ""
                        except NoSuchElementException:
                            img_src = ""

                        # 메뉴명 추출
                        try:
                            menu_name = item.find_element(By.XPATH, "./a/div[2]/div[1]").text.strip()
                        except NoSuchElementException:
                            menu_name = ""

                        # 가격 추출
                        try:
                            price_elem = item.find_element(By.XPATH, "./a/div[2]/div[contains(@class, 'GXS1X')]")
                            price = price_elem.text.strip() if price_elem else ""
                        except NoSuchElementException:
                            price = ""

                        # 메뉴 항목 추가
                        menu_data.append({
                            "category": category_name,
                            "img_src": img_src,
                            "menu_name": menu_name,
                            "price": price
                        })
                    except Exception as e:
                        print(f"메뉴 항목 추출 중 오류 발생: {e}")
                        continue

            except Exception as e:
                print(f"카테고리 {category_index} 처리 중 오류 발생: {e}")
                continue

    except TimeoutException:
        print("버전3 메뉴판을 감지하지 못했습니다.")
        log_menu_issue("version3", business_num, store_name, store_location, loc_x, loc_y, expected_postcode, "Version 3 menu panel not detected")
        return []

    return menu_data

def extract_old_version_menu(driver, container_element, business_num, store_name, store_location, loc_x, loc_y, expected_postcode):
    """구버전 메뉴판 로직"""
    # 더보기 클릭

    click_button_until_end(driver, MORE_BUTTON_XPATH)

    # container_element 하위의 div[1]/ul 내 메뉴 아이템들 추출
    ul = container_element.find_element(By.XPATH, './ul')
    menu_items = ul.find_elements(By.XPATH, './li')

    menu_data = []
    if not menu_items:
        log_menu_issue("old", business_num, store_name, store_location, loc_x, loc_y, expected_postcode,
                       "No menu items in old_version")
        return menu_data

    for i, item in enumerate(menu_items, start=1):
        try:
            # 이미지 추출
            try:
                img_elem = item.find_element(By.XPATH, './a/div[1]/div/img')
                img_src = img_elem.get_attribute("src") if img_elem else ""
            except:
                img_src = ""

            # 메뉴명
            menu_name = item.find_element(By.XPATH, './a/div[2]/div[1]/div/span[1]').text
            # 가격
            price = ""
            try:
                # 우선 기본적인 클래스 이름으로 찾기 시도
                price_elem = item.find_element(By.XPATH, "./a/div[2]//div[contains(@class, 'GXS1X')]")
                price = price_elem.text.strip() if price_elem else ""

            except NoSuchElementException:
                # 기본 클래스가 없을 경우 div[2] 아래 자식 div 개수 확인 후 적절한 div 선택
                try:
                    div2_elem = item.find_element(By.XPATH, "./a/div[2]")  # div[2] 가져오기
                    child_divs = div2_elem.find_elements(By.XPATH, "./div")  # 자식 div 요소 리스트

                    if len(child_divs) == 3:  # 설명글 포함 시 div[3]에 가격 존재
                        price_elem = child_divs[2]  # 세 번째 div
                        price = price_elem.text.strip() if price_elem else ""
                    elif len(child_divs) == 2:  # 설명글 없음, div[2]에 가격 존재
                        price_elem = child_divs[1]  # 두 번째 div
                        price = price_elem.text.strip() if price_elem else ""
                    else:
                        print("가격 정보를 담고 있는 div 구조를 확인할 수 없습니다.")
                except Exception:
                    print(f"가격 추출 실패")

            menu_data.append({
                "category": "",
                "img_src": img_src,
                "menu_name": menu_name,
                "price": price
            })
        except Exception as e:
            # 메뉴 한 개 추출 실패 -> 로그 남기고 계속
            error_msg = f"Old version menu {i}"
            print(f"구버전 메뉴 {i} 추출 중 오류 발생: {e}")
            log_menu_issue("old", business_num, store_name, store_location, loc_x, loc_y, expected_postcode, error_msg)
            continue

    if not menu_data:
        # 모든 메뉴 추출 실패했거나 없음
        log_menu_issue("old", business_num, store_name, store_location, loc_x, loc_y, expected_postcode,
                       "Extracted zero menu items in old_version")
    return menu_data


def extract_new_version_menu(driver, list_xpath, business_num, store_name, store_location, loc_x, loc_y, expected_postcode):
    """
    신버전 메뉴판 로직:
    1) 카테고리 버튼들을 찾는다.
    2) 각 카테고리를 클릭하여 해당 메뉴 리스트를 로드한다.
    3) 메뉴 리스트 영역(div[2]) 안에 있는 모든 order_list_area(ul) 내의 li 아이템을 추출한다.
    4) 각 li에서 img, 메뉴명, 가격을 가져온다.

    사용자가 제시한 예:
    - order_list_area ul 아래에 li들이 메뉴
    - li 예시 XPATH:
      img   : ./div/a/div[1]/span/img
      title : ./div/a/div[2]/div[1]
      price : ./div/a/div[2]/div[4]

    ※ 실제 페이지 구조에 따라 XPath 조정 필요
    """

    menu_data = []

    # eat_here_xpath = '//*[@id="root"]/div[2]/div/div[1]/div/div[2]/div/a[2]'
    # try:
    #     eat_here_button = WebDriverWait(driver, 2).until(
    #         EC.element_to_be_clickable((By.XPATH, eat_here_xpath))
    #     )
    #     if eat_here_button:
    #         eat_here_button.click()
    #         time.sleep(2)  # 버튼 클릭 후 페이지 갱신 대기
    #         print("먹고갈게요 버튼 클릭 완료")
    # except TimeoutException:
    #     # 먹고갈게요 버튼 없음 - 무시
    #     pass

    # 2. list_xpath 하위 구조 탐색
    # list_xpath: '//*[@id="root"]/div[3]/div/div/div[2]'
    # 여기서 order_list_wrap, order_list_wrap store_delivery를 모두 찾는다.
    # 이들은 각각 별도의 메뉴 섹션(카테고리 그룹)을 나타낸다.
    wrap_xpath = f"{list_xpath}//div[contains(@class, 'order_list_wrap')]"

    # order_list_wrap 및 store_delivery div들 찾기
    wrap_divs = driver.find_elements(By.XPATH, wrap_xpath)
    if not wrap_divs:
        print("order_list_wrap 요소 없음 - 메뉴 없음 처리")
        log_menu_issue("new", business_num, store_name, store_location, loc_x, loc_y, expected_postcode,
                       "No order_list_wrap found")
        return menu_data
    extracted_any = False

    # 3. 각 wrap_div 안의 order_list_inner 탐색
    for wrap_index, wrap_div in enumerate(wrap_divs, start=1):
        inner_divs = wrap_div.find_elements(By.XPATH, ".//div[contains(@class, 'order_list_inner')]")
        if not inner_divs:
            continue

        for inner_index, inner in enumerate(inner_divs, start=1):

            # order_list_tit 에서 카테고리 제목 추출
            category_name = ""
            try:
                title_span = inner.find_element(By.XPATH,
                                                ".//div[contains(@class, 'order_list_tit')]/span[@class='title']")
                category_name = title_span.text.strip()
            except NoSuchElementException:
                print(f"inner_div {inner_index}: Category title 없음")

            # order_list_area (ul) 찾기
            try:
                menu_ul = inner.find_element(By.XPATH, ".//ul[contains(@class, 'order_list_area')]")
            except NoSuchElementException:
                print(f"inner_div {inner_index}: menu_ul 없음")
                continue

            # li.order_list_item 추출
            menu_items = menu_ul.find_elements(By.XPATH, "./li[contains(@class, 'order_list_item')]")
            if not menu_items:
                print(f"inner_div {inner_index}: 메뉴 아이템 없음")
                continue


            # 각 메뉴 아이템에서 img, name, price 추출
            for item_index, item in enumerate(menu_items, start=1):
                try:
                    # 이미지 (옵션)
                    img_src = ""
                    try:
                        img_elem = item.find_element(By.XPATH, "./div/a//div[@class='info_img']//img")
                        if img_elem:
                            img_src = img_elem.get_attribute("src")
                    except NoSuchElementException:
                        print(f"메뉴 {item_index}: 이미지 없음")

                    # 메뉴명
                    menu_name = ""
                    try:
                        menu_name_elem = item.find_element(By.XPATH, "./div/a//div[@class='info_detail']//div[@class='tit']")
                        if menu_name_elem:
                            menu_name = menu_name_elem.text.strip()
                    except NoSuchElementException:
                        print(f"메뉴 이름 없음")

                    # 가격
                    price = ""
                    try:
                        price_elem = item.find_element(By.XPATH, "./div/a//div[@class='info_detail']//div[@class='price']")
                        if price_elem:
                            price = price_elem.text.strip()
                    except NoSuchElementException:
                        print(f"메뉴 {item_index}: 가격 없음")

                    # 메뉴 정보 저장
                    menu_data.append({
                        "category": category_name,
                        "img_src": img_src,
                        "menu_name": menu_name,
                        "price": price
                    })
                    extracted_any = True
                except Exception as e:
                    error_msg = f"New version menu {category_name}"
                    log_menu_issue("new", business_num, store_name, store_location, loc_x, loc_y, expected_postcode,
                                   error_msg)

    if not extracted_any:
        log_menu_issue("new", business_num, store_name, store_location, loc_x, loc_y, expected_postcode,
                       "No menu items extracted in new_version")

    return menu_data

def go_to_home_tab(driver):
    try:
        home_tab_xpath = '//*[@id="app-root"]/div/div/div/div[4]/div/div/div/div/a[contains(@title, "tpj9w _tab-menu")]'
        home_tab = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, home_tab_xpath))
        )
        home_tab.click()
        time.sleep(2)

    except TimeoutException:
        pass

def extract_full_details_if_matched(driver, switch_to_iframe_func, switch_to_default_func, expected_postcode, business_num, loc_x, loc_y):
    """
    주소를 먼저 확인하고, 주소가 일치하면 메뉴 정보를 추출.
    주소 불일치 or 메뉴 없음 시 None 반환.
    """
    # 우선 주소만 추출 위해 entryIframe 진입
    switch_to_default_func(driver)
    switch_to_iframe_func(driver, "entryIframe")

    go_to_home_tab(driver)

    store_name = WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.XPATH, STORE_NAME_XPATH))
    ).text
    home_button = WebDriverWait(driver, TIMEOUT).until(
        EC.element_to_be_clickable((By.XPATH, HOME_BUTTON))
    )
    time.sleep(2)
    home_button.click()

    print(store_name)

    # 주소 버튼 클릭
    try:
        location_button = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, STORE_LOCATION_XPATH_BUTTON))
        )
        time.sleep(2)
        location_button.click()
        print(location_button.text)

    except TimeoutException:
        print("주소 정보 버튼 없음")
        switch_to_default_func(driver)
        switch_to_iframe_func(driver, "searchIframe")
        return None

    # 우편번호(고유 텍스트) 추출
    store_location_text = WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.XPATH, STORE_LOCATION_XPATH))
    ).text

    # 정규식을 사용해 숫자만 추출
    store_location_text = "".join(re.findall(r"\d+", store_location_text))
    print(store_location_text)

    # 주소 추출
    store_location = WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.XPATH, STORE_LOCATION_XPATH_BUTTON))
    ).text

    print(store_location_text, expected_postcode)
    # 정확 일치 비교
    match = (store_location_text == expected_postcode)

    # 로그 기록
    log_match_result(match, expected_postcode, store_location_text, store_location, business_num)


    if not match:
        print("주소 불일치")
        print(match, expected_postcode, store_location_text, store_location)
        # 주소 불일치
        switch_to_default_func(driver)
        switch_to_iframe_func(driver, "searchIframe")
        return None

        # 주소 일치 시 메뉴탭 클릭
    try:
        print("주소 일치 -> 메뉴 탭 클릭")
        # 메뉴바 영역
        menu_bar = WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="app-root"]/div/div/div/div[4]/div/div/div/div'))
        )
        # "메뉴"라는 텍스트가 포함된 a 태그를 찾아 클릭
        menu_tab = menu_bar.find_element(By.XPATH, './/a[span[contains(text(), "메뉴")]]')
        menu_tab.click()
        time.sleep(1)  # 페이지 전환 대기
        print("메뉴 탭 클릭 완료")
    except (TimeoutException, NoSuchElementException):
        # 메뉴 버튼 없음 = 메뉴 정보 없는 곳 -> 폐업 취급
        print("메뉴 버튼 없음 -> 폐업 처리")
        switch_to_default_func(driver)
        switch_to_iframe_func(driver, "searchIframe")
        return 400

    # 메뉴 추출
    menu_data = extract_menu_details(driver, business_num, store_name, store_location, loc_x, loc_y, expected_postcode)

    # 메뉴가 없으면 폐업 처리
    if not menu_data:
        switch_to_default_func(driver)
        switch_to_iframe_func(driver, "searchIframe")
        return 401

    details = {
        "store_name": store_name,
        "store_location": store_location,
        "loc_x": loc_x,
        "loc_y": loc_y,
        "menu": menu_data
    }

    # 기본 DOM으로 복귀
    switch_to_default_func(driver)
    switch_to_iframe_func(driver, "searchIframe")
    return details

def click_next_page(driver):
    """다음 페이지로 이동"""
    try:
        next_button = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, NEXT_PAGE_XPATH))
        )
        next_button.click()
        time.sleep(2)
    except TimeoutException:
        print("다음 페이지 없음")
        raise
