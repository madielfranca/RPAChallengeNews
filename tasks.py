import time
from RPA.Browser.Selenium import Selenium
from selenium.webdriver.common.keys import Keys
from robocorp.tasks import task
from RPA.Robocorp.WorkItems import WorkItems

from util import (
    set_month_range,
    write_csv_data,
    replace_date_with_hour,
    download_image_from_url,
    check_for_dolar_sign,
    check_phrases,
    create_image_folder,
    get_all_files_from_folder,
)

browser_lib = Selenium()

def close_browser() -> None:
    browser_lib.close_browser()

def open_website(url: str) -> None:
    browser_lib.open_available_browser(url)
    browser_lib.maximize_browser_window()
    time.sleep(5)
    terms_accept = '//*[@id="fides-button-group"]/div[2]/button[2]'
    is_term_button = browser_lib.does_page_contain_button(terms_accept)
    if is_term_button:
        browser_lib.click_button(locator=terms_accept)

def begin_search(search_phrase: str) -> None:
    try:        
        time.sleep(5)
        section = '//*[@id="app"]/div[2]/div/header/section[1]/div[1]/div/button'
        browser_lib.click_element(section)

        field_xpath = "//input[@placeholder='SEARCH']"
        browser_lib.input_text(locator=field_xpath, text=search_phrase)
        go_button_xpath = "//button[@type='submit']"
        browser_lib.click_button_when_visible(locator=go_button_xpath)

    except ValueError as e:
        raise f"Error on execution of begin_search -> {e}"

def select_category(categorys) -> None:
    if len(categorys) == 0:
        return
    for value in categorys:
        try:
            section_drop_btn = "//div[@data-testid='section']/button[@data-testid='search-multiselect-button']"
            browser_lib.click_button_when_visible(locator=section_drop_btn)
            sections_list = "//*[@data-testid='section']//li"
            browser_lib.wait_until_page_contains_element(locator=sections_list)
            section = f"//input[@data-testid='DropdownLabelCheckbox' and contains(@value, '{value}')]"
            browser_lib.click_element(section)

        except:
            print(f"Category not found")

def sort_newest_news(list_value="newest") -> None:
    try:
        sort_dropdow_btn = "//select[@data-testid='SearchForm-sortBy']"
        browser_lib.select_from_list_by_value(sort_dropdow_btn, list_value)

    except ValueError as e:
        raise f"Error on execution of sort_newest_news -> {e}"

def set_date_range(number_of_months: int) -> None:
    try:
        date_button = "//button[@data-testid='search-date-dropdown-a']"
        browser_lib.click_button_when_visible(locator=date_button)
        specific_dates_button = "//button[@value='Specific Dates']"
        browser_lib.click_button_when_visible(locator=specific_dates_button)
        input_date_range_start = "//input[@id='startDate']"
        input_date_range_end = "//input[@id='endDate']"
        date_start, date_end = set_month_range(number_of_months)
        browser_lib.input_text(input_date_range_start, date_start)
        browser_lib.input_text(input_date_range_end, date_end)
        browser_lib.click_button_when_visible(locator=date_button)

    except ValueError as e:
        raise f"Error on execution of data range -> {e}"

def load_all_news():
    show_more_button = "//button[normalize-space()='Show More']"
    while browser_lib.does_page_contain_button(show_more_button):
        try:
            browser_lib.wait_until_page_contains_element(
                locator=show_more_button
            )
            browser_lib.scroll_element_into_view(locator=show_more_button)
            browser_lib.click_button_when_visible(show_more_button)
        except:
            print("Page show more button done")

def get_element_value(path: str) -> str:
    if browser_lib.does_page_contain_element(path):
        return browser_lib.get_text(path)
    return ""

def get_image_value(path: str) -> str:
    if browser_lib.does_page_contain_element(path):
        return browser_lib.get_element_attribute(path, "src")
    return ""

def load_all_news() -> None:
    show_more_button = "//button[@data-testid='search-show-more-button']"
    while browser_lib.does_page_contain_button(show_more_button):
        try:
            browser_lib.wait_until_page_contains_element(
                locator=show_more_button
            )
            time.sleep(1)
            browser_lib.click_element(show_more_button)
        except:
            print("Page show more button done")

def get_element_value(path: str) -> str:
    if browser_lib.does_page_contain_element(path):
        return browser_lib.get_text(path)
    return ""

def get_image_value(path: str) -> str:
    if browser_lib.does_page_contain_element(path):
        return browser_lib.get_element_attribute(path, "src")
    return ""

def extract_website_data(search_phrase: str) -> None:
    load_all_news()
    element_list = "//ol[@data-testid='search-results']/li[@data-testid='search-bodega-result']"
    news_list_elements = browser_lib.get_webelements(element_list)
    extracted_data = []
    for value in range(1, len(news_list_elements) + 1):
        date = replace_date_with_hour(
            get_element_value(f"{element_list}[{value}]//span[@data-testid]")
        )
        title = get_element_value(f"{element_list}[{value}]//h4")
        description = get_element_value(f"{element_list}[{value}]//a/p")
        image = download_image_from_url(
            get_image_value(f"{element_list}[{value}]//img")
        )

        is_title_dolar = check_for_dolar_sign(title)
        is_description_dolar = check_for_dolar_sign(description)
        phrases_count = check_phrases(text_pattern=search_phrase, text=title)

        extracted_data.append(
            [
                title,
                date,
                description,
                image,
                is_title_dolar,
                is_description_dolar,
                check_phrases(
                    text_pattern=search_phrase,
                    text=description,
                    count=phrases_count,
                ),
            ]
        )
    write_csv_data(extracted_data)
@task
def main() -> None:
    try:
        create_image_folder()
        wi = WorkItems()
        wi.get_input_work_item()
        url = wi.get_work_item_variable("url")
        search_phrase = wi.get_work_item_variable("search_phrase")
        category = wi.get_work_item_variable("category")
        number_of_months = wi.get_work_item_variable("number_of_months")
        open_website(url=url)
        begin_search(search_phrase=search_phrase)
        select_category(categorys=category)
        sort_newest_news()
        set_date_range(number_of_months)
        extract_website_data(search_phrase)
        wi.add_work_item_file("./news_output.xlsx", "RESULT_EXCEL.xlsx")
        files = get_all_files_from_folder()
        wi.create_output_work_item(files=files, save=True)
        wi.create_output_work_item(files="./news_output.xlsx", save=True)

    finally:
        close_browser()


if __name__ == "__main__":
    main()
