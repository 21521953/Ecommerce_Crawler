from flask import Flask, render_template, request
import csv
import time
from scrape import scrape_data

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('crawler_user.html')

@app.route('/result', methods=['POST'])
def result():
    base_url = request.form['base_url'] + '&page={}'
    scraped_data = scrape_data(base_url)
    headers = scraped_data[0].keys() if scraped_data else []  # Lấy headers từ cột đầu tiên của dữ liệu
    time.sleep(10)  # Đợi 10 giây
    return render_template('crawler_result.html', data=scraped_data, headers=headers)


    

if __name__ == "__main__":
    app.run(debug=True)
