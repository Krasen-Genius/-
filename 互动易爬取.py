"""
    这个代码用于爬取深证互动易的
    投资者问与答
    如果想爬取不同的时间范围
    请更改83&84行的开始与结束时间
"""
import requests
import time
import json
import csv
import re
from datetime import datetime, timedelta

def generate_timestamp():
    """生成当前的 Unix 时间戳，转换为秒级。用于API请求中防止缓存。"""
    return int(time.time())

def clean_text(text):
    """
    清洗文本数据，以适应CSV格式。
    替换内嵌的换行符和双引号，并使用正则表达式去除多余的空格。
    """
    text = text.replace('\n', ' ').replace('\r', ' ')
    text = re.sub(r'\s+', ' ', text)  # 将连续的空格替换为单个空格
    text = text.replace('"', '""')  # 转义CSV中的双引号
    return text.strip()

def make_post_request(start_date, end_date):
    url = "https://irm.cninfo.com.cn/newircs/index/search"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }

    with open('互动易ask&answer.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
        # Include pageNo and totalPage in the header
        writer.writerow(['Stock Code', 'Company Short Name', 'Main Content', 'Attached Content', 'Attached Author', 'Package Date', 'Page No', 'Total Pages'])

        for current_date in date_range(start_date, end_date):
            page_no = 1
            has_more_pages = True
            while has_more_pages:
                data = {
                    '_t': generate_timestamp(),
                    'pageNo': page_no,
                    'pageSize': 10,
                    'searchTypes': '11',
                    'beginDate': current_date.strftime("%Y-%m-%d 00:00:00"),
                    'endDate': current_date.strftime("%Y-%m-%d 23:59:59"),
                    'highLight': True
                }
                response = requests.post(url, headers=headers, data=data)
                if response.status_code == 200:
                    response_data = json.loads(response.text)
                    total_pages = response_data['totalPage']  # Get the total pages from the response
                    if response_data['results']:
                        for item in response_data['results']:
                            writer.writerow([
                                item.get('stockCode', 'N/A'),
                                item.get('companyShortName', 'N/A'),
                                clean_text(item.get('mainContent', 'N/A')),
                                clean_text(item.get('attachedContent', 'N/A')),
                                clean_text(item.get('attachedAuthor', 'N/A')),
                                item.get('packageDate', 'N/A'),
                                page_no,  # Add pageNo to each row
                                total_pages  # Add totalPage to each row
                            ])
                        if page_no >= total_pages:
                            has_more_pages = False
                        else:
                            page_no += 1
                    else:
                        has_more_pages = False
                else:
                    print("Failed to fetch data:", response.status_code)
                    break

def date_range(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

start_date = datetime(2023, 8, 20)
end_date = datetime(2024, 4, 30)  # Adjust as needed

make_post_request(start_date, end_date)

print("过程完成！")
