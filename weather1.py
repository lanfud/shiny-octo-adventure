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
            temp.append(i['od21'])  # 小时
            temp.append(i['od22'])  # 温度
            temp.append(i['od24'])  # 风力方向
            temp.append(i['od25'])  # 风级
            temp.append(i['od26'])  # 降水量
            temp.append(i.get('od27', None))  # 相对湿度（可能缺失，用 get 处理）
            final_day.append(temp)
            count = count + 1
    # 爬取 7 天的数据（若需扩展可补充，当前主要用逐小时数据示例）
    return final_day


def write_to_csv(file_name, data, day=1):
    """保存为 csv 文件"""
    with open(file_name, 'w', errors='ignore', newline='') as f:
        if day == 1:
            header = ['小时', '温度', '风力方向', '风级', '降水量', '相对湿度']
        else:
            header = ['日期', '天气', '最低气温', '最高气温', '风向1', '风向2', '风级']
        f_csv = csv.writer(f)
        f_csv.writerow(header)
        f_csv.writerows(data)


# ------------------- 数据可视化相关函数 -------------------
def tem_curve(data):
    """温度曲线绘制（示例，若需调整适配数据列名）"""
    if '温度' not in data.columns:
        print("错误: 缺少 '温度' 列，无法绘制温度曲线")
        return
    hours = data['小时']
    temps = data['温度'].astype(float)
    plt.figure(figsize=(10, 6))
    plt.plot(hours, temps, color='red', label='温度曲线')
    plt.scatter(hours, temps, color='red')
    plt.title('温度变化曲线')
    plt.xlabel('小时')
    plt.ylabel('温度/℃')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()


def hum_curve(data):
    """相对湿度曲线绘制（需确保数据有 '相对湿度' 列）"""
    if '相对湿度' not in data.columns:
        print("错误: 缺少 '相对湿度' 列，无法绘制湿度曲线")
        return
    hours = data['小时']
    hums = data['相对湿度'].astype(float)
    plt.figure(figsize=(10, 6))
    plt.plot(hours, hums, color='blue', label='相对湿度曲线')
    plt.scatter(hours, hums, color='blue')
    plt.title('相对湿度变化曲线')
    plt.xlabel('小时')
    plt.ylabel('相对湿度/%')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()


def air_curve(data):
    """空气质量相关曲线（需补充逻辑，示例框架）"""
    # 需根据实际数据列名完善，比如假设存在 '空气质量' 列
    if '空气质量' not in data.columns:
        print("错误: 缺少 '空气质量' 列，无法绘制空气质量曲线")
        return
    hours = data['小时']
    air = data['空气质量']
    plt.figure(figsize=(10, 6))
    plt.plot(hours, air, color='green', label='空气质量曲线')
    plt.scatter(hours, air, color='green')
    plt.title('空气质量变化曲线')
    plt.xlabel('小时')
    plt.ylabel('空气质量指数')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()


def wind_radar(data):
    """风向雷达图"""
    if '风力方向' not in data.columns or '风级' not in data.columns:
        print("错误: 缺少 '风力方向' 或 '风级' 列，无法绘制风向雷达图")
        return
    wind = list(data['风力方向'])
    wind_speed = list(data['风级'].astype(float))
    # 风向转换
    for i in range(len(wind)):
        if wind[i] == "北风":
            wind[i] = 90
        elif wind[i] == "南风":
            wind[i] = 270
        elif wind[i] == "西风":
            wind[i] = 180
        elif wind[i] == "东风":
            wind[i] = 360
        elif wind[i] == "东北风":
            wind[i] = 45
        elif wind[i] == "西北风":
            wind[i] = 135
        elif wind[i] == "西南风":
            wind[i] = 225
        elif wind[i] == "东南风":
            wind[i] = 315
    degs = np.arange(45, 361, 45)
    temp = []
    for deg in degs:
        speed = []
        for i in range(len(wind)):
            if wind[i] == deg:
                speed.append(wind_speed[i])
        if len(speed) == 0:
            temp.append(0)
        else:
            temp.append(sum(speed) / len(speed))
    print(temp)
    N = 8
    theta = np.arange(0, 2 * np.pi, 2 * np.pi / 8)
    radii = np.array(temp)
    plt.axes(polar=True)
    colors = [(1 - x / max(radii), 1 - x / max(radii), 0.6) for x in radii]
    plt.bar(theta, radii, width=(2 * np.pi / N), bottom=0.0, color=colors)
    plt.title('一天风级图', x=0.2, fontsize=20)
    plt.show()


# ------------------- 温湿度相关性分析函数 -------------------
def calc_corr(a, b):
    """计算相关系数"""
    a_avg = sum(a) / len(a) if len(a) > 0 else 0
    b_avg = sum(b) / len(b) if len(b) > 0 else 0
    cov_ab = sum([(x - a_avg) * (y - b_avg) for x, y in zip(a, b)])
    sq_a = math.sqrt(sum([(x - a_avg) ** 2 for x in a]))
    sq_b = math.sqrt(sum([(x - b_avg) ** 2 for x in b]))
    if sq_a == 0 or sq_b == 0:
        return 0
    corr_factor = cov_ab / (sq_a * sq_b)
    return corr_factor


def corr_tem_hum(data):
    """温湿度相关性分析"""
    if '温度' not in data.columns or '相对湿度' not in data.columns:
        print("错误: 缺少 '温度' 或 '相对湿度' 列，无法分析温湿度相关性")
        return
    tem = data['温度'].astype(float).tolist()
    hum = data['相对湿度'].astype(float).tolist()
    plt.scatter(tem, hum, color='blue')
    plt.title('温湿度相关性分析图')
    plt.xlabel('温度/℃')
    plt.ylabel('相对湿度/%')
    corr = calc_corr(tem, hum)
    plt.text(20, 40, f"相关系数为: {corr:.2f}", fontdict={'size': 10, 'color': 'red'})
    plt.show()
    print(f"相关系数为: {corr:.2f}")


# ------------------- 主函数 -------------------
def main():
    # 解决中文显示问题
    plt.rcParams['font.sans-serif'] = ['SimHei']
    # 解决负号显示问题
    plt.rcParams['axes.unicode_minus'] = False

    # 爬取数据（以逐小时数据为例，可扩展）
    url = 'http://www.weather.com.cn/weather/101280701.shtml'  # 珠海天气示例
    html = getHTMLtext(url)
    if not html:
        print("数据爬取失败，程序退出")
        return

    data_hourly = get_content(html)
    if not data_hourly:
        print("未获取到有效数据，程序退出")
        return

    # 保存数据到 CSV
    write_to_csv('weather14.csv', data_hourly, day=1)
    print("数据已保存到 weather14.csv")

    # 读取数据
    try:
        data1 = pd.read_csv('weather14.csv', encoding='gb2312')
        print("\n数据预览:")
        print(data1.head())

        # 调用各可视化及分析函数
        tem_curve(data1)
        hum_curve(data1)
        air_curve(data1)
        wind_radar(data1)
        corr_tem_hum(data1)
    except Exception as e:
        print(f"数据处理或可视化出错: {e}")


if __name__ == '__main__':
        main()