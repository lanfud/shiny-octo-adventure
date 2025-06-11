import requests
from lxml import etree
import csv


# 定义方法
def getWeather(url):
    weather_info = []
    headers = {
        'Cookie': 'UserId=17492113410185356; Hm_lvt_7c50c7060f1f743bcccf8c150a646e90a=1749211341; '
                  'HMACCOUNT=54F2FF78AEECB908; Hm_lvt_5326a74bb3e3143580750a123a85e7a1=1749211410; '
                  'Hm_lpvt_5326a74bb3e3143580750a123a85e7a1=1749212779; '
                  'Hm_lpvt_7c50c7060f1f743bcccf8c150a646e90a=1749212779',
        'referer': 'https://lishi.tianqi.com/shanghai/201412.html',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
    }

    try:
        # 发起请求，接受响应数据
        response = requests.get(url=url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功

        # 数据预处理
        resp_html = etree.HTML(response.text)

        # 修正xpath表达式
        resp_list = resp_html.xpath("//ul[@class='thrui']/li")

        for li in resp_list:
            day_weather_info = {}

            # 日期
            date_text = li.xpath("./div[1]/text()")
            day_weather_info['date_time'] = date_text[0].split(' ')[0] if date_text else ""

            # 最高气温(处理摄氏度符号)
            high_text = li.xpath("./div[2]/text()")
            high = high_text[0] if high_text else ""
            day_weather_info['high'] = high.replace("°C", "")

            # 最低气温
            low_text = li.xpath("./div[3]/text()")
            low = low_text[0] if low_text else ""
            day_weather_info['low'] = low.replace("°C", "")

            # 天气
            weather_text = li.xpath("./div[4]/text()")
            day_weather_info['weather'] = weather_text[0] if weather_text else ""

            weather_info.append(day_weather_info)

    except Exception as e:
        print(f"获取天气数据时出错: {e}")

    return weather_info


q1q = []
for month in range(1,13):
    weather_time = '2014' +('0'+str(month) if month <10 else str(month))
    print(f"正在获取{weather_time}的天气数据...")
    url = f'https://Lishi.tianqi.com/shanghai/{weather_time}.html'
    weather = getWeather(url)
    #存储数据
    q1q.extend(weather) #使用extend而不是append，避免嵌套列表
    # 打印进度
    print(f"{weather_time}获取完成，共{len(weather)}条记录")

# 数据写入CSV
try:
    with open('weather_2014.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        # 写入列名
        writer.writerow(['日期', '最高气温', '最低气温', '天气'])

        # 写入数据
        for day_data in q1q:
            writer.writerow([
                day_data['date_time'],
                day_data['high'],
                day_data['low'],
                day_data['weather']
            ])

        print(f"数据已成功写入 weather_2014.csv, 共{len(q1q)}条记录")

except Exception as e:
    print(f"写入CSV文件时出错:{e}")