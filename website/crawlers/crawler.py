from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import csv
import re
import time

def crawler_data(base_url):
    headers = ['Product Title', 'Brand', 'Price', 'Regular Price', 'Discount %', 'Image', 'Product Evaluation',
               'Product_score_average', 'Thương hiệu', 'SKU', 'Dạng sản phẩm', 'Mẫu mã',
               'Phân loại thương hiệu', 'Công dụng', 'Ingredient', 'Loại da', 'Dạng sản phẩm', 'Định lượng',
               'Hạn sử dụng', 'Loại bảo hành', 'Xuất xứ', 'Loại đóng gói', 'Hướng dẫn sử dụng', 'Cỡ du lịch',
               'Số lô', 'Recommended Age', 'Delivery_Option_Instant', 'Thời gian bảo hành', 'Ngày sản xuất']
    data = []

    with open('crawler_stock_test3.csv', mode='a', newline='', encoding='utf-8-sig') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        existing_titles = get_existing_product_titles('crawler_stock_test2.csv')

        if file.tell() == 0:
            writer.writeheader()

        browser = webdriver.Chrome()
        current_page = 1

        while current_page <= int(page_num):
            url_with_page = base_url.format(current_page)
            try:
                browser.get(url_with_page)
            except Exception as e:
                print(f"Error accessing {url_with_page}: {e}")
                continue

            print("Page index:", current_page)
            time.sleep(5)

            products = browser.find_elements(By.CSS_SELECTOR, "[data-qa-locator='product-item']")
            listProductLink = [product.find_element(By.TAG_NAME, 'a').get_attribute('href') for product in products]

            for productLink in listProductLink:
                try:
                    browser.get(productLink)
                    time.sleep(2)
                    browser.execute_script("window.scrollTo(0, document.body.scrollHeight*0.7);")
                    time.sleep(8)

                    productTitle = browser.find_element(By.CLASS_NAME, "pdp-mod-product-badge-title").text
                    if is_product_seen(productTitle, existing_titles):
                        print('Product is already in rows')
                        continue

                    productBrand = browser.find_element(By.CLASS_NAME, "pdp-product-brand__brand-link").text
                    productEvaluation = browser.find_element(By.CLASS_NAME, "pdp-review-summary__link").text
                    productPrice = re.match(r'^[\d|\.|\,]+', browser.find_element(By.CSS_SELECTOR, ".pdp-price_type_normal").text).group()

                    try:
                        productRegularPrice = browser.find_element(By.CLASS_NAME, "pdp-price_type_deleted").text
                    except NoSuchElementException:
                        productRegularPrice = '0'

                    try:
                        DiscountPercent = browser.find_element(By.CLASS_NAME, "pdp-product-price__discount").text
                    except NoSuchElementException:
                        DiscountPercent = '0'

                    productImage = browser.find_element(By.CLASS_NAME, "pdp-mod-common-image").getAttribute("src")

                    try:
                        expand_button = browser.find_element(By.CLASS_NAME, "pdp-view-more-btn")
                        ActionChains(browser).move_to_element(expand_button).perform()
                        time.sleep(4)
                        expand_button.click()
                        time.sleep(4)
                    except NoSuchElementException:
                        pass

                    detail_container = browser.find_element(By.CLASS_NAME, "detail-content")
                    span_tags = detail_container.find_elements(By.TAG_NAME, "span")
                    span_texts = [span.text.strip() for span in span_tags]

                    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(6)

                    specification_container = browser.find_element(By.CLASS_NAME, "pdp-mod-specification")
                    li_tags = specification_container.find_elements(By.TAG_NAME, "li")

                    specifications = {li.find_element(By.CLASS_NAME, "key-title").text.strip(): li.find_element(By.CLASS_NAME, "key-value").text.strip() for li in li_tags}

                    for title, value in specifications.items():
                        if title not in headers:
                            headers.append(title)

                    Product_score_average = browser.find_element(By.CLASS_NAME, "score-average").text

                    row_data = {
                        'Product Title': productTitle,
                        'Brand': productBrand,
                        'Price': productPrice,
                        'Regular Price': productRegularPrice,
                        'Discount %': DiscountPercent,
                        'Image': productImage,
                        'Product Evaluation': productEvaluation,
                        'Product_score_average': Product_score_average,
                        **specifications
                    }

                    data.append(row_data)
                    writer.writerow(row_data)
                    print('done')
                    time.sleep(3)

                except NoSuchElementException:
                    print("Error: Product information not found")
                    continue

            current_page += 1
            time.sleep(2)

        browser.quit()
    return data

def get_existing_product_titles(filename):
    existing_titles = set()
    with open(filename, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            existing_titles.add(row['Product Title'])
    return existing_titles

def is_product_seen(product_title, existing_titles):
    return product_title in existing_titles
