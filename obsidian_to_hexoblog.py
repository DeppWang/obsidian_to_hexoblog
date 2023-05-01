import datetime
import subprocess
import os
import re
# /home/runner/work/Obsidian/Obsidian/HexoBlog-Resp/source/_posts
HEXO_POST_PATH = "/home/runner/work/Obsidian/Obsidian/HexoBlog-Resp/source/_posts"
OBSIDIAN_PATH = "/home/runner/work/Obsidian/Obsidian/Obsidian-Resp"
FORMAT_DATETIME = "{:%Y-%m-%d %H:%M:%S}"
STR_FORMAT_DATETIME = '%Y-%m-%d %H:%M:%S'
DATE_REGEX = re.compile(r"\ndate:\s(.*)\n")
ENGLISH_TITLE_REGEX = re.compile(r"\nenglish_title:\s(.*)\n")
OBSIDIAN_TO_HEXOBLOG_TAG = "Obsidian-to-HexoBlog-Tag"


def is_hexo_article(file_path):
    """判断是否是需要发布 Hexo 的文章"""

    first_line = ""
    try:
        with open(file_path, 'r', encoding="utf-8") as f:
            first_line = f.readline().strip().replace(" ", "")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return [], False
    except Exception as e:
        print(f"Error opening/reading file: {e}")
        return [], False

    tags = [tag for tag in first_line.split('#') if tag]
    # 如果没有 Obsidian-to-HexoBlog-Tag 标签，跳过
    if "Obsidian-to-HexoBlog-Tag" not in tags:
        return tags, True
    return tags, False


def is_need_post_hexo(post_article_path, english_title, file_path):
    """判断是否需要发布 HexoBlog"""

    print(os.listdir(HEXO_POST_PATH))
    print(os.listdir("/home/runner/work/Obsidian/Obsidian"))
    with open(post_article_path, "r") as f:
        content = f.read()
    hexo_english_title = ENGLISH_TITLE_REGEX.findall(content)[0]
    create_time = FORMAT_DATETIME.format(datetime.datetime.fromtimestamp(os.path.getmtime(file_path)))
    # 如果 Obsidian 文件已经在 HexoBlog 中存在，判断 Obsidian 文件更新时间与 HexoBlog 的最后更新时间
    if os.path.exists(post_article_path) or english_title == hexo_english_title:
        date_result = DATE_REGEX.findall(content)
        create_time = date_result[0]
        # HexoBlog 最后更新时间
        update_time_str = date_result[1] if len(date_result) == 2 else date_result[0]
        hexo_update_time = datetime.datetime.strptime(update_time_str, STR_FORMAT_DATETIME)
        # Run the Git command to get the last commit date for the file
        git_log_result = subprocess.run(["git", "log", "-1", "--format=%cd", "--",
                                        file_path], cwd=OBSIDIAN_PATH, capture_output=True)
        print(git_log_result.stdout.decode())
        # Decode the output and extract the date and time string
        git_last_commit_date_str = git_log_result.stdout.decode().strip()
        print(git_last_commit_date_str)
        file_git_last_commit_date = datetime.datetime.strptime(git_last_commit_date_str, STR_FORMAT_DATETIME)
        return create_time, file_git_last_commit_date, file_git_last_commit_date != hexo_update_time
    return create_time, '', False


def update_hexo_article(tags, english_title, create_time, update_time, file_name,
                        post_article_path, file_path):
    """更新 Hexo 文章"""

    tags.remove("Obsidian-to-HexoBlog-Tag")
    tags.remove(tags[0])
    file_content = ""
    with open(file_path, 'r') as f:
        data = f.read().splitlines(True)
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
    title = os.path.splitext(file_name)[0]
    hexo_post_article_content = hexo_post_article.format(
        title=title, english_title=english_title, date=create_time,
        update_date=update_time, tags=tags, file_content=file_content)

    with open(post_article_path, 'w') as f:
        f.write(hexo_post_article_content)


def exec(file_name, file_path):
    """执行"""

    # 1、根据 tag 判断是否是需要发布 Hexo 的文章
    tags, is_hexo_article_flag = is_hexo_article(file_path=file_path)
    if not is_hexo_article_flag:
        return
    english_title = tags[0]  # 第一个标签为英文名

    # 2、如果是，判断是否需要发布 HexoBlog
    post_article_path = os.path.join(HEXO_POST_PATH, file_name)
    create_time, update_time, is_need = is_need_post_hexo(post_article_path, english_title, file_path)
    if not is_need:
        return

    # 2、如果需要，更新 Hexo 文章
    update_hexo_article(tags, english_title, create_time, update_time, file_name, post_article_path, file_path)


def transf():
    file_list = os.listdir(OBSIDIAN_PATH)
    for file_name in file_list:
        file_path = os.path.join(OBSIDIAN_PATH, file_name)
        if os.path.isdir(file_path):
            continue
        exec(file_name, file_path)


if __name__ == "__main__":
    transf()
