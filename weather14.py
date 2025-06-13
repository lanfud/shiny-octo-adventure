
import requests
from bs4 import BeautifulSoup
import csv
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math


# ------------------- 数据爬取相关函数 -------------------
def getHTMLtext(url):
    """请求获得网页内容"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        print("成功访问")
        return r.text
    except Exception as e:
        print(f"访问错误: {e}")
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
    with open(file_name, 'w', errors='ignore', newline='') as f:  # 改为 'w' 覆盖模式而非 'a' 追加模式
        if day == 14:
            header = ['日期', '天气', '最低气温', '最高气温', '风向1', '风向2', '风级']
        else:
            header = ['小时', '温度', '风力方向', '风级', '降水量', '相对湿度']
        f_csv = csv.writer(f)
        f_csv.writerow(header)
        f_csv.writerows(data)


# ------------------- 数据可视化相关函数 -------------------
def tem_curve(data):
    """温度曲线绘制"""
    # 检查数据列名
    required_cols = ['日期', '最低气温', '最高气温']
    for col in required_cols:
        if col not in data.columns:
            print(f"错误: 缺少必要的列 '{col}'")
            return

    date = list(data['日期'])
    tem_low = [float(x) for x in data['最低气温']]  # 确保温度是数值类型
    tem_high = [float(x) for x in data['最高气温']]  # 确保温度是数值类型

    # 处理缺失值
    for i in range(0, len(tem_low)):
        if math.isnan(tem_low[i]):
            tem_low[i] = tem_low[i - 1] if i > 0 else sum(tem_low) / len(tem_low)
        if math.isnan(tem_high[i]):
            tem_high[i] = tem_high[i - 1] if i > 0 else sum(tem_high) / len(tem_high)

    tem_high_ave = sum(tem_high) / len(tem_high)  # 求平均高温
    tem_low_ave = sum(tem_low) / len(tem_low)  # 求平均低温

    tem_max = max(tem_high)
    tem_max_date = tem_high.index(tem_max)  # 求最高温度对应日期索引
    tem_min = min(tem_low)
    tem_min_date = tem_low.index(tem_min)  # 求最低温度对应日期索引

    x = range(1, len(date) + 1)
    plt.figure(figsize=(10, 6))
    plt.plot(x, tem_high, color='red', label='高温')  # 画出高温度曲线
    plt.scatter(x, tem_high, color='red')  # 点出每个时刻的温度点
    plt.plot(x, tem_low, color='blue', label='低温')  # 画出低温度曲线
    plt.scatter(x, tem_low, color='blue')  # 点出每个时刻的温度点

    plt.plot([1, len(date)], [tem_high_ave, tem_high_ave], c='black', linestyle='--')  # 画出平均温度虚线
    plt.plot([1, len(date)], [tem_low_ave, tem_low_ave], c='black', linestyle='--')  # 画出平均温度虚线
    plt.legend()
    plt.text(tem_max_date + 0.15, tem_max + 0.15, str(tem_max), ha='center', va='bottom', fontsize=10.5)  # 标出最高温度
    plt.text(tem_min_date + 0.15, tem_min + 0.15, str(tem_min), ha='center', va='bottom', fontsize=10.5)  # 标出最低温度
    plt.title('未来14天高温低温变化曲线图')
    plt.xlabel('未来天数/天')
    plt.ylabel('摄氏度/℃')
    plt.xticks(x, date, rotation=45)  # 设置x轴刻度为日期
    plt.tight_layout()  # 调整布局，防止标签重叠
    plt.show()


def change_wind(wind):
    """改变风向（将文字风向转为角度）"""
    angle_map = {
        "北风": 90, "南风": 270, "西风": 180, "东风": 360,
        "东北风": 45, "西北风": 135, "西南风": 225, "东南风": 315
    }
    return [angle_map.get(w, 0) for w in wind]  # 对未知风向返回0


def wind_radar(data):
    """风向雷达图"""
    # 检查数据列名
    required_cols = ['风向1', '风向2', '风级']
    for col in required_cols:
        if col not in data.columns:
            print(f"错误: 缺少必要的列 '{col}'")
            return

    wind1 = list(data['风向1'])
    wind2 = list(data['风向2'])
    wind_speed = list(data['风级'])
    wind1 = change_wind(wind1)
    wind2 = change_wind(wind2)

    degs = np.arange(45, 361, 45)
    temp = []
    for deg in degs:
        speed = []
        # 获取 wind_deg 在指定范围的风速平均值数据
        for i in range(0, len(wind1)):
            if wind1[i] == deg:
                speed.append(wind_speed[i])
            if wind2[i] == deg:
                speed.append(wind_speed[i])
        if len(speed) == 0:
            temp.append(0)
        else:
            temp.append(sum(speed) / len(speed))

    N = 8
    theta = np.arange(0, 2 * np.pi, 2 * np.pi / N)
    # 数据极径
    radii = np.array(temp)
    # 绘制极区图坐标系
    plt.figure(figsize=(8, 8))
    ax = plt.axes(polar=True)
    # 定义每个扇区的 RGB 值，x 越大，对应的颜色越接近蓝色
    colors = [(1 - x / max(radii) if max(radii) > 0 else 0.5,
               1 - x / max(radii) if max(radii) > 0 else 0.5, 0.5) for x in radii]
    bars = ax.bar(theta, radii, width=2 * np.pi / N, bottom=0.0, color=colors)
    # 添加风向标签
    wind_labels = ['东北', '东', '东南', '南', '西南', '西', '西北', '北']
    ax.set_xticks(theta)
    ax.set_xticklabels(wind_labels)
    plt.title('未来14天风级分布图', fontsize=15)
    plt.tight_layout()
    plt.show()


def weather_pie(data):
    """绘制天气饼图"""
    # 检查数据列名
    if '天气' not in data.columns:
        print("错误: 缺少必要的列 '天气'")
        return

    weather = list(data['天气'])
    dic_wea = {}
    for i in range(0, len(weather)):
        if weather[i] in dic_wea.keys():
            dic_wea[weather[i]] += 1
        else:
            dic_wea[weather[i]] = 1

    # 过滤掉频次为0的天气类型
    dic_wea = {k: v for k, v in dic_wea.items() if v > 0}

    if not dic_wea:
        print("错误: 没有有效的天气数据")
        return

    print(dic_wea)
    explode = [0.01] * len(dic_wea.keys())
    color = ['lightskyblue', 'silver', 'yellow', 'salmon', 'grey', 'lime', 'gold', 'red', 'green', 'pink']
    plt.figure(figsize=(8, 8))
    plt.pie(dic_wea.values(), explode=explode, labels=dic_wea.keys(), autopct='%1.1f%%',
            colors=color[:len(dic_wea)], shadow=True, startangle=90)
    plt.title('未来14天气候分布饼图')
    plt.axis('equal')  # 保证饼图是圆的
    plt.tight_layout()
    plt.show()


# ------------------- 主函数 -------------------
def main():
    # 解决中文显示问题
    plt.rcParams['font.sans-serif'] = ['SimHei']
    # 解决负号显示问题
    plt.rcParams['axes.unicode_minus'] = False

    # 爬取数据
    url1 = 'http://www.weather.com.cn/weather/101280701.shtml'  # 珠海7天天气
    url2 = 'http://www.weather.com.cn/weather15d/101280701.shtml'  # 珠海8-15天天气

    html1 = getHTMLtext(url1)
    if not html1:
        print("获取7天数据失败，程序退出")
        return

    data1, data1_7 = get_content(html1)  # data1: 逐小时数据, data1_7: 7天数据

    html2 = getHTMLtext(url2)
    if not html2:
        print("获取8-15天数据失败，仅使用7天数据进行可视化")
        data8_14 = []
    else:
        data8_14 = get_content2(html2)  # 8-15天数据

    # 保存数据
    if data1:
        write_to_csv('weather_hourly.csv', data1, day=1)  # 逐小时数据
        print(f"已保存逐小时数据到 weather_hourly.csv (共{len(data1)}条记录)")

    if data1_7 or data8_14:
        data14 = data1_7 + data8_14
        write_to_csv('weather_daily.csv', data14, day=14)  # 日汇总数据
        print(f"已保存日汇总数据到 weather_daily.csv (共{len(data14)}条记录)")

        # 读取日汇总数据进行可视化
        try:
            data_daily = pd.read_csv('weather_daily.csv', encoding='gb2312')
            print("\n数据预览:")
            print(data_daily.head())
            print(f"\n数据列名: {list(data_daily.columns)}")

            # 绘制图表
            tem_curve(data_daily)
            wind_radar(data_daily)
            weather_pie(data_daily)
        except Exception as e:
            print(f"读取或可视化数据时出错: {e}")
    else:
        print("没有有效的日汇总数据，无法进行可视化")


if __name__ == '__main__':
    main()