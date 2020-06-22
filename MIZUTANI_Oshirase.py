import requests
import json
import datetime
import locale
import schedule
import time
import jupyter

# LINE notify へのアクセス

# test用
access_token = 'BC9YMpFXnczc8SGjiC00WibBPj5ArfBz8hY3ENw8nVi'
# 水谷さんのお知らせ（お天気様）
access_token_tenki = 'Cm5Odan247i43KiPTsTn5TD7S5uQg46utH7LHrOZZNB'
# 水谷さんのお知らせ（ゴミ捨て）
access_token_gomi = 'zLNJh9UPDk9nk1C1eX51OKEnEgnXHoKhOjwjQicLjGP'


class LINE_notify:
    API_url = 'https://notify-api.line.me/api/notify'
    
    def __init__(self, access_token):
        self.__headers = {'Authorization': 'Bearer ' + access_token}
    
    def sent(self, message):
        payload = {'message': message}
        r = requests.post(LINE_notify.API_url, headers=self.__headers, params=payload)


def GOMISUTE():
    locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
    dt_now = datetime.datetime.now()
    w_list = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日']
    wd = dt_now.weekday()
    if wd == 2 or wd == 6:
        message = '明日は{0}の可燃ゴミの日です。ゴミ捨てを忘れずに！'.format(w_list[wd + 1])
    elif wd == 1:
        message = '明日は{0}の資源ゴミの日です。プラ類，紙包装類，ペットボトル，ビン，缶を捨てるの忘れないようにしよう！'.format(w_list[wd + 1])
    elif wd == 4:
        message = '明日は{0}です。第２{0}はダンボールを捨てる日です。捨てるときは7:50まで忘れずに捨てよう！'.format(w_list[wd + 1])
    return message

def forecast_API():
    # livedoor tenki_APIのデータ取得
    base_url = 'http://weather.livedoor.com/forecast/webservice/json/v1'
    payload = {'city': '230010'}  # 愛知県の天気
    response = requests.get(base_url, params=payload)  # ベースURL + クエリでGET
    json_data = json.loads(response.content)  # json_dataにレスポンスを辞書型で代入
    tenki_data = requests.get(base_url, params=payload).json()
    titile = format(json_data['title'])
    
    #
    date = []
    dateLabel = []
    telop = []
    tem_max = []
    tem_min = []
    
    for forecast in json_data['forecasts']:  # 'forecasts'内は配列になっているのでループ処理
        date.append(forecast['date'])  # 予報日(yyyy-mm-dd)
        dateLabel.append(forecast['dateLabel'])  # 予報日
        print('{0} ({1})'.format(date, dateLabel))  # 予報日の表示
        telop.append(forecast['telop'])
        print('{0}'.format(telop))
        t_max = forecast['temperature'].get('max')  # 'max'の値がnullの場合があるのでgetメソッド
        t_min = forecast['temperature'].get('min')  # 'min'の値がnullの場合があるのでgetメソッド
        if t_max is not None and t_min is not None:  # 'max', 'min'の値がNoneじゃなかった場合の処理
            tem_max.append('最高気温{0}℃'.format(t_max['celsius']))
            tem_min.append('最低気温{0}℃'.format(t_min['celsius']))
        else:
            tem_max.append("null")
            tem_min.append("null")
        print(tem_max, tem_min)

    message = '\n{0}\n{1}\n{2}\n{3}\n{4}\n{5}'.format(titile, date[1], dateLabel[1], telop[1], tem_max[1],tem_min[1])
    return message


def LINE1():  # LINE  message_tenki
    LINE_tenki = LINE_notify(access_token=access_token_tenki)
    message1 = forecast_API()
    if "雨" in message1:  # 特定の文字列が含まれるか  $$ in &&
        message1 = message1 + '\n' + "********************************"
        message1 = message1 + '\n' + "明日は雨予報です。傘を忘れずに！"
        message1 = message1 + '\n' + "********************************"
    LINE_tenki.sent(message1)


def LINE2():
    # LINE_message_gomisute
    LINE_gomi = LINE_notify(access_token=access_token_gomi)
    message2 = '\n' + GOMISUTE()
    LINE_gomi.sent(message2)


# maiin
# 毎日22時00分に実行
schedule.every().day.at("22:30").do(LINE1)
schedule.every().day.at("22:30").do(LINE2)

while True:
    schedule.run_pending()
    time.sleep(1)
