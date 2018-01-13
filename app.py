from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

import requests 
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
import random


import sys
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials as SAC

app = Flask(__name__)


line_bot_api = LineBotApi('Your_Line_Bot_Channel_access_token ')
handler = WebhookHandler('Your_Line_Bot_Channel secret ')

#電影
def movie():
    target_url = 'https://movies.yahoo.com.tw/'
    print('Start parsing movie ...')
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')   
    content = ""
    for index, data in enumerate(soup.select('div.movielist_info h1 a')):
        if index == 20:
            return content
        print("data：")
        print(index)
        print(data)        
        title = data.text
        link =  data['href']
        content += '{}\n{}\n'.format(title, link)
    return content
#新聞
def apple_news():
    target_url = 'https://tw.appledaily.com/new/realtime'
    print('Start parsing movie ...')
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')   
    content = []
    for index, data in enumerate(soup.select('div.item a')):
        if index == 20:           
            return content
    
        title = data.find('img')['alt']
        link =  data['href']
        link2 = 'https:'+ data.find('img')['data-src']
        content.append(title)
        content.append(link)
        content.append(link2)
        print("data：")
        print(content)   
    return content

@app.route("/", methods=['GET'])
def hello():
    return "Hello World!"

@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    print("Request body: " + body, "Signature: " + signature)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
       abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    #print(type(msg))
    msg = msg.encode('utf-8')  
    if event.message.text == "最新電影":
        a=movie()
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))
    if event.message.text == "你好":
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=event.message.text))
    elif event.message.text == "貼圖":
        print("貼圖get")
        line_bot_api.reply_message(event.reply_token,StickerSendMessage(package_id=1, sticker_id=2))
    elif event.message.text == "圖片":
        print("圖片get")
        line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url='圖片網址', preview_image_url='圖片網址'))
    elif event.message.text == "影片":
        line_bot_api.reply_message(event.reply_token,VideoSendMessage(original_content_url='影片網址', preview_image_url='預覽圖片網址'))
    elif event.message.text == "音訊":
        line_bot_api.reply_message(event.reply_token,AudioSendMessage(original_content_url='音訊網址', duration=100000))
    elif event.message.text == "位置":
        print("位置get")
        line_bot_api.reply_message(event.reply_token,LocationSendMessage(title='my location', address='Tainan', latitude=22.994821, longitude=120.196452))
    if event.message.text == "紀錄":
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="紀錄成功"))
        pass
        GDriveJSON = 'Json檔名.json'
        GSpreadSheet = 'Google試算表名稱'
        while True:
            try:
                scope = ['https://spreadsheets.google.com/feeds']
                key = SAC.from_json_keyfile_name(GDriveJSON, scope)
                gc = gspread.authorize(key)
                worksheet = gc.open(GSpreadSheet).sheet1
            except Exception as ex:
                print('無法連線Google試算表', ex)
                sys.exit(1)
            textt=""
            textt+=event.message.text
            if textt!="":
                worksheet.append_row((datetime.datetime.now(), textt))
                print('新增一列資料到試算表' ,GSpreadSheet)
                return textt         
    if event.message.text == "News":
        a=apple_news()
        g=[]
        h=[]
        n=[]    
        for i in range(0,len(a),3):   
            g.append(a[i])
            h.append(a[i+1])
            n.append(a[i+2])
        m=[] 
        x=['title','link','link2']
        m.append(g)
        m.append(h)
        m.append(n)
        dictionary = dict(zip(x,m))
        p=random.sample(range(12),3)
        Image_Carousel = TemplateSendMessage(
        alt_text='目錄 template',
        template=ImageCarouselTemplate(
        columns=[
            ImageCarouselColumn(
                image_url=dictionary['link2'][p[0]],
                action=URITemplateAction(
                    uri=dictionary['link'][p[0]],
                    label=dictionary['title'][p[0]][0:11]
                )
            ),
            ImageCarouselColumn(
                image_url=dictionary['link2'][p[2]],
                action=URITemplateAction(
                    uri=dictionary['link'][p[2]],
                    label=dictionary['title'][p[2]][0:11]
                )
            ),
            ImageCarouselColumn(
                image_url=dictionary['link2'][p[1]],
                action=URITemplateAction(
                uri=dictionary['link'][p[1]],
                label=dictionary['title'][p[1]][0:11]
                )
            )
            ]))
        line_bot_api.reply_message(event.reply_token,Image_Carousel)
    elif event.message.text == "樣板":
        print("TEST1")       
        buttons_template = TemplateSendMessage(
        alt_text='目錄 template',
        template=ButtonsTemplate(
            title='Template-樣板介紹',
            text='Template分為四種，也就是以下四種：',
            thumbnail_image_url='圖片網址',
            actions=[
                MessageTemplateAction(
                    label='Buttons Template',
                    text='Buttons Template'
                ),
                MessageTemplateAction(
                    label='Confirm template',
                    text='Confirm template'
                ),
                MessageTemplateAction(
                    label='Carousel template',
                    text='Carousel template'
                ),
                MessageTemplateAction(
                    label='Image Carousel',
                    text='Image Carousel'
                )
            ]
        )
    )
        line_bot_api.reply_message(event.reply_token, buttons_template)
    elif event.message.text == "Buttons Template":
        print("TEST")       
        buttons_template = TemplateSendMessage(
        alt_text='Buttons Template',
        template=ButtonsTemplate(
            title='這是ButtonsTemplate',
            text='ButtonsTemplate可以傳送text,uri',
            thumbnail_image_url='圖片網址',
            actions=[
                MessageTemplateAction(
                    label='ButtonsTemplate',
                    text='ButtonsTemplate'
                ),
                URITemplateAction(
                    label='VIDEO1',
                    uri='網址'
                ),
                PostbackTemplateAction(
                label='postback',
                text='postback text',
                data='postback1'
                )
            ]
        )
    )
        line_bot_api.reply_message(event.reply_token, buttons_template)
    elif event.message.text == "Carousel template":
        print("Carousel template")       
        Carousel_template = TemplateSendMessage(
        alt_text='目錄 template',
        template=CarouselTemplate(
        columns=[
            CarouselColumn(
                thumbnail_image_url='網址',
                title='this is menu1',
                text='description1',
                actions=[
                    PostbackTemplateAction(
                        label='postback1',
                        text='postback text1',
                        data='action=buy&itemid=1'
                    ),
                    MessageTemplateAction(
                        label='message1',
                        text='message text1'
                    ),
                    URITemplateAction(
                        label='uri1',
                        uri='網址'
                    )
                ]
            ),
            CarouselColumn(
                thumbnail_image_url='網址',
                title='this is menu2',
                text='description2',
                actions=[
                    PostbackTemplateAction(
                        label='postback2',
                        text='postback text2',
                        data='action=buy&itemid=2'
                    ),
                    MessageTemplateAction(
                        label='message2',
                        text='message text2'
                    ),
                    URITemplateAction(
                        label='連結2',
                        uri='網址'
                    )
                ]
            )
        ]
    )
    )
        line_bot_api.reply_message(event.reply_token,Carousel_template)
    elif event.message.text == "Confirm template":
        print("Confirm template")       
        Confirm_template = TemplateSendMessage(
        alt_text='目錄 template',
        template=ConfirmTemplate(
            title='這是ConfirmTemplate',
            text='這就是ConfirmTemplate,用於兩種按鈕選擇',
            actions=[                              
                MessageTemplateAction(
                    label='Y',
                    text='Y'
                ),
                MessageTemplateAction(
                    label='N',
                    text='N'
                )
            ]
        )
    )
        line_bot_api.reply_message(event.reply_token,Confirm_template)
    elif event.message.text == "Image Carousel":
        print("Image Carousel")       
        Image_Carousel = TemplateSendMessage(
        alt_text='目錄 template',
        template=ImageCarouselTemplate(
        columns=[
            ImageCarouselColumn(
                image_url='網址',
                action=PostbackTemplateAction(
                    label='postback1',
                    text='postback text1',
                    data='action=buy&itemid=1'
                )
            ),
            ImageCarouselColumn(
                image_url='網址',
                action=PostbackTemplateAction(
                    label='postback2',
                    text='postback text2',
                    data='action=buy&itemid=2'
                )
            )
        ]
    )
    )
        line_bot_api.reply_message(event.reply_token,Image_Carousel)
    return 'OK2'

if __name__ == "__main__":
    app.run(debug=True,port=80)
