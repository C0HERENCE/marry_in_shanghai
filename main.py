from flask import Flask, jsonify
import requests
import threading
import queue
from itertools import groupby

app = Flask(__name__, static_url_path='/', static_folder='./web/build')


def request_data(dept, code, q):
    for d in range(8, 25):
        cus_date = f'2023-05-{d:02}'
        r = requests.post(url="https://ywtb.sh.gov.cn/ac-product-net/mzReserveTime/query.do", json={
            'selectDate': cus_date,
            'organId': code,
            'applyId': ''
        }, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        j = r.json()
        for a in j["data"]:
            dateTime = f"{a['selectDate']} {a['dateTime']}"
            seats = f"{a['num']}/{a['seatNum']}"
            obj = {'dateTime': dateTime, 'dept': dept, 'seats': seats}
            q.put(obj)
        print("checking", dept, cus_date, "done")


@app.route("/data")
def get_data():
    depts = {
        "黄浦区婚姻（收养）登记处": "000310101",
        "上海市静安区婚姻（收养）登记中心": "000310106",
        "徐汇区婚姻收养登记中心": "000310104",
        "上海市普陀区婚姻收养登记中心": "000310107",
        "上海市浦东新区婚姻管理所（惠南镇）": "000310241",
        "上海市浦东新区婚姻管理所（浦东南路）": "000310115",
        "上海市松江区婚姻登记管理所": "000310117",
        "上海市奉贤区婚姻（收养）登记中心": "000310120",
        "上海市长宁区婚姻（收养）登记中心": "000310105",
        "宝山婚姻登记管理所": "000310113",
        "崇明区婚姻收养登记中心": "000310230",
        "上海市虹口区民政局": "000310109",
        "上海市嘉定区民政局婚姻登记处": "000310114",
        "金山区婚姻（收养）登记中心": "000310116",
        "闵行区婚姻（收养）登记中心": "000310112",
        "上海市青浦区婚姻登记管理中心": "000310118",
        "杨浦区婚姻（收养）登记中心": "000310110",
    }
    q = queue.Queue()
    threads = []
    for (dept, code) in depts.items():
        thread = threading.Thread(target=request_data, args=(dept, code, q))
        threads.append(thread)
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    arr = []
    while not q.empty():
        arr.append(q.get())
    response = {}
    for time, group in groupby(arr, lambda x: x['dateTime']):
        if time not in response.keys():
            response[time] = {}
        for dp in group:
            response[time][dp["dept"]] = dp["seats"]
    result = []
    for (time, obj) in response.items():
        obj['time'] = time
        result.append(obj)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
