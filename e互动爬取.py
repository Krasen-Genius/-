# import requests
# import re
# import csv
# f1 = open("e互动ask.csv",mode="w")
# csvwriter1 = csv.writer(f1)
# csvwriter1.writerow(["ask"])
# f2 = open("e互动answer.csv",mode="w")
# csvwriter2 = csv.writer(f2)
# csvwriter2.writerow(["answer"])
#
# url = 'https://sns.sseinfo.com/getNewDataFullText.do'
# obj_ask = re.compile(r'<div class="ask_ico index_ico".*?></div>.*?'
#                  r'<div class="m_feed_txt" id="m_feed_txt-(?P<id>.*?)">.*?:(?P<ask>.*?)</div>'
#                         r'.*?<span>(?P<date>.*?)</span>',re.S)
# obj_answer = re.compile(r'<div class="index_ico answer_ico"></div>.*?'
#                         r'<div class="m_feed_txt" id="m_feed_txt-(?P<id>.*?)">(?P<answer>.*?)</div>',re.S)
# for page in range(1,43):
#     dat={
#         'sdate': '2023-08-20',
#         'edate': '2023-08-21',
#         'keyword':'',
#         'type': '1',
#         'page': page,
#         'comId':'',
#     }
#
#     # send post request
#     resp=requests.post(url, data=dat)  # data is post only
#     result1 = obj_ask.finditer(resp.text)
#     result2 = obj_answer.finditer(resp.text)
#     for i1 in result1:
#         dic1 = i1.groupdict()
#         dic1["ask"] = dic1["ask"].strip()
#         csvwriter1.writerow(dic1.values())
#
#     for i2 in result2:
#         dic2 = i2.groupdict()
#         dic2["answer"] = dic2["answer"].strip()
#         csvwriter2.writerow(dic2.values())
# f1.close()
# f2.close()
# print("over!")
#         # print(i.group('question').strip())
#         # print(i.group('answer').strip())
#     # print(resp.text)  # transform the returned contents from terminal into json ==> dic


import requests
import re
import csv
from datetime import datetime, timedelta

"""
    这个代码用于爬取上证e互动的
    投资者问与答
    如果想爬取不同的时间范围
    请更改83&84行的开始与结束时间
"""
def clean_text(text):
    """清洗文本，移除换行符和不必要的空白字符，并处理特殊字符"""
    text = text.replace('\n', ' ').replace('\r', ' ')  # 移除换行和回车
    text = re.sub(r'\s+', ' ', text)  # 将连续的空白字符替换为单个空格
    return text.strip()

# 打开CSV文件并设置写入器
with open("e互动ask.csv", mode="w", newline='', encoding='utf-8') as f1, \
     open("e互动answer.csv", mode="w", newline='', encoding='utf-8') as f2:

    csvwriter1 = csv.writer(f1)
    csvwriter1.writerow(["id", "ask", "date"])

    csvwriter2 = csv.writer(f2)
    csvwriter2.writerow(["id", "answer"])

    # 定义正则表达式
    obj_ask = re.compile(r'<div class="ask_ico index_ico".*?></div>.*?'
                         r'<div class="m_feed_txt" id="m_feed_txt-(?P<id>\d+)">.*?:(?P<ask>.*?)</div>'
                         r'.*?<span>(?P<date>.*?)</span>', re.S)
    obj_answer = re.compile(r'<div class="index_ico answer_ico"></div>.*?'
                            r'<div class="m_feed_txt" id="m_feed_txt-(?P<id>\d+)">(?P<answer>.*?)</div>', re.S)

    # 定义日期范围
    start_date = datetime(2023, 8, 20)
    end_date = datetime(2024, 4, 30)
    current_date = start_date

    while current_date <= end_date:
        formatted_date = current_date.strftime("%Y-%m-%d")

        page = 1
        while True:
            dat = {
                'sdate': formatted_date,
                'edate': formatted_date,
                'keyword': '',
                'type': '1',
                'page': page,
                'comId': '',
            }
            resp = requests.post('https://sns.sseinfo.com/getNewDataFullText.do', data=dat)

            if 'm_feed_txt' in resp.text:  # 检查页面是否有数据
                result1 = obj_ask.finditer(resp.text)
                result2 = obj_answer.finditer(resp.text)

                has_result = False
                for i1 in result1:
                    has_result = True
                    dic1 = i1.groupdict()
                    dic1["ask"] = clean_text(dic1["ask"])
                    csvwriter1.writerow([dic1["id"], dic1["ask"], dic1["date"]])

                for i2 in result2:
                    has_result = True
                    dic2 = i2.groupdict()
                    dic2["answer"] = clean_text(dic2["answer"])
                    csvwriter2.writerow([dic2["id"], dic2["answer"]])

                if not has_result:
                    break
                page += 1
            else:
                break

        current_date += timedelta(days=1)

    print("过程完成！")
