import datetime
import os
import re
# /home/runner/work/Obsidian/Obsidian/HexoBlog-Resp/source/_posts
HEXO_POST_PATH = "HexoBlog-Resp/source/_posts"
OBSIDIAN_PATH = "Obsidian-Resp"
FORMAT_DATETIME = "{:%Y-%m-%d %H:%M:%S}"
STR_FORMAT_DATETIME = '%Y-%m-%d %H:%M:%S'
HEXO_HEAD_BLOCK_REGEX = re.compile(r"\ndate:\s(.*)\n")
OBSIDIAN_TO_HEXOBLOG_TAG = "Obsidian-to-HexoBlog-Tag"

def exec(file_name, file_path):
    # 1、判断是否需要替换
    post_article_path = os.path.join(HEXO_POST_PATH, file_name)

    # 如果不存在，新增
    # 如果存在，但时间更近，更新

    # 如果存在，并且本地时间小于等于时间，跳过
    if os.path.exists(post_article_path):
        with open(post_article_path, "r") as f:
            content = f.read()
        data_result = HEXO_HEAD_BLOCK_REGEX.findall(content)
        update_time_str = data_result[1] if len(data_result) == 2 else data_result[0]
        update_time = datetime.datetime.strptime(update_time_str, STR_FORMAT_DATETIME)
        file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
        if file_time <= update_time:
            return

    # 如果没有 Obsidian-to-HexoBlog-Tag 标签，跳过
    first_line = ""
    with open(file_path, 'r') as f:
        first_line = f.readline().strip().replace(" ", "")
    tags = [tag for tag in first_line.split('#') if tag]
    if "Obsidian-to-HexoBlog-Tag" not in tags:
        return

    # 2、替换
    tags.remove("Obsidian-to-HexoBlog-Tag")
    english_title = tags[0]  # 第一个标签为英文名
    tags.remove(tags[0])
    file_content = ""
    with open(file_path, 'r') as fin:
        data = fin.read().splitlines(True)
    file_content = "".join(data[1:])

    hexo_post_article = """---
title: {title}
english_title: {english_title}
date: {date}
update_date: {update_date}
tags: {tags}
---
{file_content}
    """

    create_time = data_result[0] if os.path.exists(post_article_path) else FORMAT_DATETIME.format(
        datetime.datetime.fromtimestamp(os.path.getmtime(file_path)))
    update_time = FORMAT_DATETIME.format(datetime.datetime.now())
    title = os.path.splitext(file_name)[0]
    hexo_post_article_content = hexo_post_article.format(title=title, english_title=english_title, date=create_time, 
                                                       update_date=update_time, tags=tags, file_content=file_content)


    with open(post_article_path, 'w') as f:
        f.write(hexo_post_article_content)


def transf():
    file_list = os.listdir(OBSIDIAN_PATH)
    for file_name in file_list:
        file_path = os.path.join(OBSIDIAN_PATH, file_name)
        if os.path.isdir(file_path):
            continue
        exec(file_name, file_path)


if __name__ == "__main__":
    transf()
