# coding:utf-8
import json
import os

from bs4 import BeautifulSoup

import PostgresUtils
import pdfkit


def search_article():
    sql = 'select * from test_tb_article'
    return sql


def search_comment():
    sql = 'select * from test_tb_comment'
    return sql


html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
</head>
<body>
<h1>{title}</h1>
<p>{text}</p>
</body>
</html>
"""


def extract_(total_dict_):
    total_htmls = []

    for item_dicts in total_dict_:
        item_dict = item_dicts.get('item_dict')
        print('item_dict---')
        print(item_dict)

        if 'content_text' in item_dict:
            text = item_dict['content_text']
        if 'title' in item_dict:
            soup_ = BeautifulSoup(html_template, 'html.parser')
            title = item_dict['title']
            time = item_dict['time']
            content_url = item_dict['content_url']

            time_tag = soup_.new_tag('p')
            soup1 = BeautifulSoup(html_template, 'html.parser')
            new_div_tag = soup1.new_tag("div")
            new_div_tag["class"] = "time"
            new_div_tag["color"] = "red"
            new_div_tag["font-size"] = "24px"

            time_tag.insert(0, new_div_tag)
            new_div_tag.string = time
            soup_.body.append(time_tag)
            html_time = str(soup_)
            html = html_time.format(title=title, text=text)

            soup_1 = BeautifulSoup(html, 'html.parser')
            content_url_tag = soup_1.new_tag('p')
            soup2 = BeautifulSoup(html, 'html.parser')
            new_div_tag2 = soup2.new_tag("div")
            new_div_tag2["class"] = "content_url"
            new_div_tag2.string = content_url
            content_url_tag.insert(0, new_div_tag2)
            soup_1.body.append(content_url_tag)
            html_content_url = str(soup_1)
            html = html_content_url.format(title=title, text=text)
        else:
            title = item_dict['time']
            html = html_template.format(title=title, text=text)

        if 'img_url_list' in item_dict:
            img_url_list = item_dict['img_url_list']
            soup_ = BeautifulSoup(html, 'html.parser')
            for item_img in img_url_list:
                img_tag = soup_.new_tag('img', src=item_img)
                soup_.body.append(img_tag)
                html_img = str(soup_)
                html = html_img.format(title=title, text=text)
        if 'video_url_list' in item_dict:
            video_url_list = item_dict['video_url_list']
            soup_ = BeautifulSoup(html, 'html.parser')
            for item_video in video_url_list:
                video_tag = soup_.new_tag('video', href=item_video)
                soup_.body.append(video_tag)
                html_video = str(soup_)
                html = html_video.format(title=title, text=text)
        if 'reply_comment_list' in item_dict:
            soup_ = BeautifulSoup(html, 'html.parser')
            comment_tag = soup_.new_tag('comment')
            comment_tag.attrs = {'class': 'reply_comment_list'}
            n = 0
            reply_comment_list = item_dict['reply_comment_list']
            for reply_comment in reply_comment_list:
                item_reply_comment = reply_comment['reply_comment']
                # print('item_reply_comment---')
                # print(item_reply_comment)
                soup1 = BeautifulSoup(html, 'html.parser')
                new_div_tag = soup1.new_tag("p")
                new_div_tag["class"] = "content"
                comment_tag.insert(n, new_div_tag)
                new_div_tag.string = item_reply_comment
                n = n + 1
            soup_.body.append(comment_tag)
            html_comment = str(soup_)
            html = html_comment.format(title=title, text=text)
        total_htmls.append(html)
    return total_htmls
    pass


def parsing(data, comment):
    htmls_data = []
    for item_data in data:
        # html = []
        dict_ = {}
        #
        print('item_data-----')
        print(item_data)
        if item_data[5] == 49:  # 图文类型
            dict_.update({'time': str(item_data[7]) + ' ' + str(item_data[2])})

            content_text_list = item_data[6]
            if content_text_list is not None:
                content_text = content_text_list[0]['content']
                content_text_json = json.dumps(content_text, ensure_ascii=False)
                _content_text = content_text_json.replace('[', '').replace(']', '') \
                    .replace(r'\n', '').replace(r'"', '').replace(r',', '')
                print('_content_text---')
                print(_content_text)

                dict_.update({'content_text': str(_content_text)})
                dict_.update({'title': item_data[1]})
                dict_.update({'content_url': item_data[4]})

                content_img = content_text_list[1]
                content_img_list = content_img['content_img_list']
                if content_img_list:
                    dict_.update({'img_url_list': content_img_list})

                content_video = content_text_list[2]
                content_video_list = content_video['content_video_list']
                if content_video_list:
                    dict_.update({'video_url_list': content_video_list})

        else:  # 图片or 文本类型
            dict_.update({'time': str(item_data[7])})  # 添加time
            dict_.update({'content_text': str(item_data[3])})  # 添加text or img

        msg_id = item_data[0]
        for item_comment in comment:
            article_id = item_comment[0]
            if msg_id == article_id:
                html_comment = []
                comment_list = item_comment[2]
                for item_comment_list in comment_list:

                    nick_name = item_comment_list[1]['nick_name']
                    comment_content = item_comment_list[2]['comment_content']
                    comment_content_text = nick_name + ': ' + comment_content
                    reply_content = item_comment_list[3]['reply_content']
                    if item_data[2]:
                        reply_comment = comment_content_text + '\n' + str(item_data[2]) + ': ' + reply_content
                    else:
                        reply_comment = comment_content_text + '\n' + '__' + ': ' + reply_content
                    html_comment.append({'reply_comment': reply_comment})  # 添加每篇中的每条comment_text
                dict_.update({'reply_comment_list': html_comment})
                # print('dict_-------')
                # print(dict_)

        htmls_data.append({'item_dict': dict_})
    print('htmls_data============')
    print(htmls_data)
    return htmls_data
    pass


def fetch_all_data():
    postgres = PostgresUtils.Pgs(host='localhost', port='5432', db_name='wx_mps', user='postgres', password='123456')
    sql = search_article()
    sql_comment = search_comment()

    data = postgres.fetch_all(sql)
    print('data=======')
    print(data)
    # print(type(data))
    if data:
        comment = postgres.fetch_all(sql_comment)
        # print('comment=======')
        # print(comment)
        if comment:
            return data, comment
    pass


def save_as_pdf(total_htmls):
    html_files = []
    for index, html in enumerate(total_htmls):
        file = str(index) + ".html"
        html_files.append(file)
        with open(file, 'w', encoding='utf-8')as f:
            f.write(html)
    options = {
        "user-style-sheet": "test.css",
        "page-size": "Letter",
        "encoding": "UTF-8",
        "custom-header": [("Accept-Encoding", "gzip")],
        "outline-depth": 8,
    }
    try:
        path_wk = r'D:\Program Files\JetBrains\wkhtmltopdf\bin\wkhtmltopdf.exe'  # 安装位置
        config = pdfkit.configuration(wkhtmltopdf=path_wk)
        pdfkit.from_file(html_files, "wx_一叶孤城.pdf", options=options, configuration=config)
    except Exception as e:
        print(e)
    for file in html_files:
        os.remove(file)
    print("已制作电子书在当前目录")

    pass


if __name__ == "__main__":
    data, comment = fetch_all_data()
    htmls_data = parsing(data, comment)
    total_htmls = extract_(htmls_data)
    print('total_htmls---')
    print(total_htmls)
    save_as_pdf(total_htmls)
