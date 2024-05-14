from flask import Flask, render_template, request
import threading
from crawlers.scrape import crawler_data 
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('crawler_user.html')

@app.route('/result', methods=['POST'])
def result():
    base_url = request.form['base_url'] + '&page={}'

    scraped_data = []
    result_header = []

    def fetch_data():
        nonlocal scraped_data
        nonlocal result_header
        try:
            scraped_data = crawler_data(base_url)
            if scraped_data : 
                result_header = list(scraped_data[0].keys()) 
        except Exception as e:
            print(f"An error occurred: {e}")

    t = threading.Thread(target=fetch_data)
    t.start()
    t.join()  # Wait for the thread to finish

    return render_template('crawler_result.html', data=scraped_data, headers=result_header)

if __name__ == "__main__":
    app.run(debug=True)
