import requests
from bs4 import BeautifulSoup
import csv
import json

def getHTMLtext(url):
    """请求获得网页内容"""
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        print("成功访问")
        return r.text
    except:
        print("访问错误")
        return ""

def get_content(html):
    """处理得到有用信息保存数据文件（1 - 7 天及当天数据）"""
    final = []
    bs = BeautifulSoup(html, "html.parser")
    body = bs.body
    data = body.find(name='div', attrs={'id': '7d'})
    data2 = body.find_all(name='div', attrs={'class': 'left-div'})
    text = data2[2].find('script').string
    text = text[text.index('=') + 1: -2]
    jd = json.loads(text)
    dayone = jd['od']['od2']
    final_day = []
    count = 0
    for i in dayone:
        temp = []
        if count <= 23:
            temp.append(i['od21'])
            temp.append(i['od22'])
            temp.append(i['od24'])
            temp.append(i['od25'])
            temp.append(i['od26'])
            temp.append(i['od27'])
            temp.append(i['od28'])
            final_day.append(temp)
            count = count + 1
    # 爬取 7 天的数据
    ul = data.find('ul')
    li = ul.find_all('li')
    i = 0
    for day in li:
        if i < 7 and i > 0:
            temp = []
            date = day.find('h1').string
            date = date[date.index('日') + 1:]
            temp.append(date)
            inf = day.find_all('p')
            temp.append(inf[0].string)
            tem_low = inf[1].find('i').string
            if inf[1].find('span') is None:
                tem_high = None
            else:
                tem_high = inf[1].find('span').string
            temp.append(tem_low[:-1])
            if tem_high:
                if tem_high[-1] == '℃':
                    temp.append(tem_high[:-1])
                else:
                    temp.append(tem_high)
            wind = inf[2].find_all('span')
            for j in wind:
                temp.append(j['title'])
            wind_scale = inf[2].find('i').string
            index1 = wind_scale.index('级')
            temp.append(int(wind_scale[index1 - 1:index1]))
            final.append(temp)
        i = i + 1
    return final_day, final

def get_content2(html):
    """处理得到有用信息保存数据文件（8 - 15 天数据）"""
    final = []
    bs = BeautifulSoup(html, "html.parser")
    body = bs.body
    data = body.find('div', {'id': '15d'})
    ul = data.find('ul')
    li = ul.find_all('li')
    i = 0
    for day in li:
        if i < 8:
            temp = []
            date = day.find('span', {'class': 'time'}).string
            date = date[date.index('（') + 1: -2]
            temp.append(date)
            weather = day.find('span', {'class': 'wea'}).string
            temp.append(weather)
            tem = day.find('span', {'class': 'tem'}).text
            temp.append(tem[tem.index('/') + 1: -1])
            temp.append(tem[:tem.index('/') - 1])
            wind = day.find('span', {'class': 'wind'}).string
            if '转' in wind:
                temp.append(wind[wind.index('转'):])
                temp.append(wind[wind.index('转') + 1:])
            else:
                temp.append(wind)
                temp.append(wind)
            wind_scale = day.find('span', {'class': 'wind1'}).string
            index1 = wind_scale.index('级')
            temp.append(int(wind_scale[index1 - 1:index1]))
            final.append(temp)
        i = i + 1
    return final

def write_to_csv(file_name, data, day=14):
    """保存为 csv 文件"""
    with open(file_name, 'a', errors='ignore', newline='') as f:
        if day == 14:
            header = ['日期', '天气', '最低气温', '最高气温', '风向1', '风向2', '风级']
        else:
            header = ['小时', '温度', '风力方向', '风级', '降水量', '相对湿度','空气质量']
        f_csv = csv.writer(f)
        f_csv.writerow(header)
        f_csv.writerows(data)

def main():
    """主函数"""
    print("Weather test")
    # 珠海 7 天天气（中国天气网）
    url1 = 'http://www.weather.com.cn/weather/101280701.shtml'
    # 珠海 8 - 15 天天气（中国天气网）
    url2 = 'http://www.weather.com.cn/weather15d/101280701.shtml'

    html1 = getHTMLtext(url1)
    data1, data1_7 = get_content(html1)

    html2 = getHTMLtext(url2)
    data8_14 = get_content2(html2)

    data14 = data1_7 + data8_14
    write_to_csv('weather14.csv', data14, day=14)
    write_to_csv('weather1.csv', data1, day=1)

if __name__ == '__main__':
    main()