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

    with open('crawler_stock_test4.csv', mode='a', newline='', encoding='utf-8-sig') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        existing_titles = get_existing_product_titles('crawler_stock_test4.csv')
        # Write header if the file is empty
        if file.tell() == 0:
            writer.writeheader()
    
        current_page = 1
        browser = webdriver.Chrome()
        try:
            url_with_page = base_url.format(current_page)
            browser.get(url_with_page)
            pagination_test = browser.find_element(By.CLASS_NAME, 'ant-pagination')
            pagination_num = int(pagination_test.find_elements(By.CLASS_NAME, "ant-pagination-item")[0].text)
            # print("Page Total:", pagination_num)
            # print(pagination_test)
            # pagination_num = 3
        except Exception as e:
            print("lỗi")
        while True:
            
            print("Page index:",current_page)

            try : 
                browser.get(url_with_page)
                pagination = browser.find_element(By.CLASS_NAME, 'ant-pagination')
                pagination_num = (pagination.find_elements(By.CLASS_NAME, "ant-pagination-item")[-1].text)
                print("Page Total:",pagination_num) 
            except Exception as e:
                print(e)

            if current_page > (int(pagination_num)) : 
                print("Reached the last page")
                break     
            time.sleep(5)

            products = browser.find_elements(By.CSS_SELECTOR, "[data-qa-locator='product-item']")
            
            listProductLink = []
            for product in products:
                outerHtml = product.get_attribute("outerHTML")
                productLink = re.search(r'href="(.*?)"', outerHtml).group(1)
                listProductLink.append(productLink)

            
            for productLink in listProductLink:
                print("DEBUG: " + productLink)

                try:
                    browser.get("https://" + productLink)
                except:
                    browser.get("https://www.lazada.vn/products" + productLink)

                time.sleep(2)  
                browser.execute_script("window.scrollTo(0, document.body.scrollHeight*0.8);")
                time.sleep(8)  
                
                try:
                    # basic information
                    productTitle = browser.find_element(By.CLASS_NAME, "pdp-mod-product-badge-title").text
                    if(is_product_seen(productTitle, existing_titles)):
                        print('Product is already in rows')
                        continue
                    else : 

                        productBrand = browser.find_element(By.CLASS_NAME, "pdp-product-brand__brand-link").text
                        productEvaluation = browser.find_element(By.CLASS_NAME, "pdp-review-summary__link").text
                        productPrice = browser.find_element(By.CSS_SELECTOR, ".pdp-price_type_normal").text
                        productPrice = re.match(r'^[\d|\.|\,]+', productPrice).group()

                        try:
                            productRegularPrice_element = browser.find_element(By.CLASS_NAME, "pdp-price_type_deleted")
                            productRegularPrice = productRegularPrice_element.text
                        except NoSuchElementException:
                            productRegularPrice = 0

                        try:
                            DiscountPercent_element = browser.find_element(By.CLASS_NAME, "pdp-product-price__discount")
                            DiscountPercent = DiscountPercent_element.text
                        except NoSuchElementException:
                            DiscountPercent = 0
                        
                        productImage = browser.find_element(By.CLASS_NAME, "pdp-mod-common-image").get_attribute("src")
                        
                        try :
                            expand_button = browser.find_element(By.CLASS_NAME, "pdp-view-more-btn")
                            ActionChains(browser).move_to_element(expand_button).perform()
                            time.sleep(4) 
                            expand_button.click()
                            time.sleep(4) 
                        except : 
                            pass
                        # expand more information
                        detail_container = browser.find_element(By.CLASS_NAME, "detail-content")
                        span_tags = detail_container.find_elements(By.TAG_NAME, "span")
                        span_texts = []  
                        for span in span_tags:
                            span_text = span.text.strip()
                            span_texts.append(span_text)

                        detail_texts = [text for text in span_texts if text.strip()]

                        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(6) 
                        
                        specification_container = browser.find_element(By.CLASS_NAME, "pdp-mod-specification")
                        li_tags = specification_container.find_elements(By.TAG_NAME, "li")      

                        specifications = {}
                        for li_tag in li_tags:
                            title_element = li_tag.find_element(By.CLASS_NAME, "key-title")
                            value_element = li_tag.find_element(By.CLASS_NAME, "key-value")

                            title = title_element.text.strip()
                            value = value_element.text.strip()
                            if title in headers:
                                specifications[title] = value
                            else :
                                headers.append(title)
                                specifications[title] = value

                        Product_score_average = browser.find_element(By.CLASS_NAME, "score-average").text
                        
                        print(current_page)
                        row_data = {
                            'Product Title': productTitle,
                            'Brand': productBrand,
                            'Price': productPrice,
                            'Regular Price':productRegularPrice,
                            'Discount %': DiscountPercent,
                            'Image': productImage,
                            'Product Evaluation' : productEvaluation ,
                            'Product_score_average': Product_score_average,
                            **specifications 
                        }
                        writer.writerow(row_data)
                        print('done')
                        time.sleep(3)
                except NoSuchElementException:
                    print("Error: Product information not found")
            current_page += 1
            time.sleep(2)
    browser.quit()
def get_existing_product_titles(filename):
    existing_titles = set()
    with open(filename, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            existing_titles.add(row['Product Title'])
    return existing_titles

def is_product_seen(product_title, existing_titles):
    if product_title in existing_titles:
        return True
    else:
        return False

