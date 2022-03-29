import os
import random
import time
from datetime import datetime
from sys import platform
from urllib.parse import urljoin

from dateutil import parser
from loguru import logger
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from settings import MMS_CREDENTIALS as CRED
from settings import WEBDRIVER_PATH, ROOT_DIR

r_time = round(random.uniform(1.6, 3.8), 1)
now = datetime.now()
DATE = "20-03-2022"
URL = r"https://mms.ua.energy"
data_path = "data"

prods = [
    "ENERGY_CENTRE - PROD",
    "EKO_ENERGY_PRO - PROD",
    "POHREB_SOLAR_LLC - PROD",
    "CITY_SOLAR_LLC - PROD",
    "SUN_CITY_PLUS - PROD",
    "PRIME_SUN_LLC - PROD",
    "BILASHKY_ENERGY - PROD",
    "SUN_VOLT - PROD",
    "UKRSPECSTROYPLUS - PROD",
    "INHULETS_ENERGO2 - PROD",
    "RENGY_ZAPORIZHZH - PROD",
]


def parse_date_str(date):
    return parser.parse(date)


def create_date_header(date):
    return dict(
        year=date.strftime("%Y"), month=date.strftime("%m"), day=date.strftime("%d")
    )


def get_driver(dir):
    logger.debug(f"Initializing driver")
    logger.debug(f"sys platform is: {platform}")
    logger.debug(f"driver path is: {WEBDRIVER_PATH}")
    if platform == "linux":
        options = Options()
        options.add_argument("--headless")
        options.add_argument(f"download.default_directory={os.path.abspath(data_path)}")
        driver = webdriver.Chrome(options=options, executable_path="./chromedriver")

    elif platform == "win32":
        options = webdriver.ChromeOptions()
        options.add_argument("headless")  # for debugging need comment it ###
        prefs = {"download.default_directory": str(ROOT_DIR.joinpath("data", dir))}
        options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(
            executable_path=WEBDRIVER_PATH, chrome_options=options
        )
    else:
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.maximize_window()
    driver.implicitly_wait(10)
    return driver


def get_sign_in_page(url, dir):
    url = urljoin(url, "/sign-in")
    driver = get_driver(dir)
    try:
        logger.debug(f"New connection to {url}...")
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.title_contains("Market Management System"))
        logger.debug(f"connection to {url} successful")
        return driver
    except Exception:
        logger.error("Can't open web page:", url)


def login(url, username, password, dir):
    page = get_sign_in_page(url, dir)
    try:
        WebDriverWait(page, 10).until(EC.title_contains("Market Management System"))
        logger.debug(f"Logging in...")
        time.sleep(r_time)

        page.find_element(
            by=By.XPATH, value='//*[@id="mat-expansion-panel-header-0"]/span'
        ).click()
        time.sleep(r_time)

        page.find_element(by=By.ID, value="mat-input-0").send_keys(username)
        time.sleep(r_time)

        page.find_element(by=By.ID, value="mat-input-1").send_keys(password)
        time.sleep(r_time)

        page.find_element(
            by=By.XPATH, value='//*[@id="cdk-accordion-child-0"]/div/div/button'
        ).click()
        time.sleep(r_time)

        WebDriverWait(page, 10).until(EC.title_contains("Market Management System"))
        logger.debug("Login Success")
        return page
    except Exception:
        logger.error("Can't login...")
        page.close()


def select_prod(page, prod):
    try:
        logger.debug(f"try to find prod selector")
        prod_selector = page.find_element(
            by=By.XPATH, value='//*[@id="navbar-top"]/div[2]/mms-company-role-selector'
        )
        prod_selector.click()
        cdk_overlay_panel = page.find_element(
            by=By.XPATH, value='//*[@id="cdk-overlay-0"]'
        )
        time.sleep(r_time)
        logger.debug(f"try to select {prod} element")
        for option in cdk_overlay_panel.find_elements(
            by=By.TAG_NAME, value="mat-option"
        ):
            if option.text == prod:
                option.click()
        time.sleep(r_time)
        return page
    except Exception:
        logger.error("Can't find selector")
        page.close()


def get_overview_page(page, url):
    url = urljoin(url, "/emfamily/BalAccountOverview.do")
    try:
        logger.debug(f"try to get {url} page")
        page.get(url)
        time.sleep(r_time)
        return page
    except Exception:
        logger.error(f"Can't get {url} page")
        page.close()


def switch_frame(page):
    try:
        logger.debug(f"try to swich frame...")
        page.switch_to.frame(
            page.find_element(
                by=By.CSS_SELECTOR,
                value="body > mms-root >"
                " mms-full-layout > "
                "mat-sidenav-container >"
                " mat-sidenav-content >"
                " div > mms-emfamily-component >"
                " div > mat-card >"
                " mat-card-content > iframe",
            )
        )
        return page
    except Exception:
        logger.error(f"Can't switch to frame")
        page.close()


def get_balance_groups(page):
    time.sleep(r_time)
    try:
        logger.debug(f"try to find groups")
        page.find_element(by=By.NAME, value="balanceGroupFilter").click()
        balance_group_selector = page.find_element(
            by=By.NAME, value="balanceGroupFilter"
        )
        return balance_group_selector
    except Exception:
        logger.error(f"Can't find groups")
        page.close()


def get_balance_groups_names(balance_group_selector):
    names = []
    for option in balance_group_selector.find_elements_by_tag_name("option"):
        if option.text != "*":
            names.append(option.text)
    return names


def select_balance_group(balance_group_selector, name):
    try:
        logger.debug(f"try to select {name} group")
        for option in balance_group_selector.find_elements_by_tag_name("option"):
            if option.text == name:
                option.click()
        time.sleep(r_time)
    except Exception:
        logger.error(f"Can't select balance group {name}")


def select_day(page, day):
    try:
        logger.debug(f"try to find day selector")
        page.find_element(by=By.NAME, value="dateTypeChooser.day").click()
        date_chooser_day = page.find_element(by=By.NAME, value="dateTypeChooser.day")
        logger.debug(f"try to set day selector")
        for option in date_chooser_day.find_elements(By.TAG_NAME, value="option"):
            if option.text == day:
                option.click()
        time.sleep(r_time)
        return page
    except Exception:
        logger.error(f"Can't select day selector {day}")
        page.close()


def select_month(page, month):
    try:
        logger.debug(f"try to find day selector")
        page.find_element(by=By.NAME, value="dateTypeChooser.month").click()
        date_chooser_month = page.find_element(
            by=By.NAME, value="dateTypeChooser.month"
        )
        logger.debug(f"try to set day selector")
        for option in date_chooser_month.find_elements(by=By.TAG_NAME, value="option"):
            if option.text == month:
                option.click()
        time.sleep(r_time)
        return page
    except Exception:
        logger.error(f"Can't select month selector {month}")
        page.close()


def select_year(page, year):
    try:
        logger.debug(f"try to find year selector")
        page.find_element(by=By.NAME, value="dateTypeChooser.year").click()
        date_chooser_year = page.find_element(by=By.NAME, value="dateTypeChooser.year")
        logger.debug(f"try to set day selector")
        for option in date_chooser_year.find_elements(by=By.TAG_NAME, value="option"):
            if option.text == year:
                option.click()
                time.sleep(r_time)
        return page
    except Exception:
        logger.error(f"Can't select year selector {year}")
        page.close()


def click_filter_button(page):
    time.sleep(r_time)
    try:
        logger.debug(f"try to find and click filter button")
        page.find_element(by=By.XPATH, value='//*[@id="filterButton"]').click()
        time.sleep(r_time + 2)
        return page
    except Exception:
        logger.error(f"Can't find filter button")
        page.close()


def click_choices_button(page):
    time.sleep(r_time)
    try:
        logger.debug(f"try to find and click choices button")
        page.find_element(
            by=By.XPATH,
            value="/html/body/div/div/form/div[8]" "/table/tbody/tr[3]/td[5]/a[1]",
        ).click()
        time.sleep(r_time)
        return page
    except Exception:
        logger.error(f"Can't find choices button")
        page.close()


def click_expand_group_button(page):
    time.sleep(r_time)
    try:
        logger.debug(f"try to find and click expand group button")
        page.find_element(
            by=By.XPATH, value="/html/body/div/div/form/div[10]/nobr/input[2]"
        ).click()
        time.sleep(r_time)
        return page
    except Exception:
        logger.error(f"Can't find expand group button")
        page.close()


def click_download_button(page):
    try:
        logger.debug(f"try to find and click download button")
        page.find_element(
            by=By.XPATH, value="/html/body/div/div/form/div[7]/div/input[1]"
        ).click()
        time.sleep(r_time)
        return page
    except Exception:
        logger.error(f"Can't find download button")
        page.close()


def click_back(page):
    try:
        logger.debug(f"try to find and click back button")
        page.find_element(by=By.XPATH, value="/html/body/div/div/form/div[4]/a").click()
        time.sleep(r_time)
        return page
    except Exception:
        logger.error(f"Can't find back button")
        page.close()


def main(p):
    main_page = login(URL, CRED.get("username"), CRED.get("password"), p)
    select_prod(main_page, p)
    time.sleep(r_time)
    overview_page = get_overview_page(main_page, URL)
    time.sleep(r_time)
    overview_page = switch_frame(overview_page)
    balance_group_selector = get_balance_groups(overview_page)
    balance_group_names = get_balance_groups_names(balance_group_selector)

    for group in balance_group_names:
        select_balance_group(balance_group_selector, group)
        date = create_date_header(parse_date_str(DATE))
        select_day(overview_page, date.get("day"))
        select_month(overview_page, date.get("month"))
        select_year(overview_page, date.get("year"))
        click_filter_button(overview_page)
        overview_page = click_choices_button(overview_page)
        overview_page = click_expand_group_button(overview_page)
        click_download_button(overview_page)
        click_back(overview_page)
        time.sleep(r_time)
        balance_group_selector = get_balance_groups(overview_page)
    overview_page.close()
    main_page.close()


if __name__ == "__main__":
    for p in prods:
        try:
            main(p)
        except Exception:
            time.sleep(10)
            main(p)
