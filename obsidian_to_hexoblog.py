import datetime
import subprocess
import os
import re
HEXO_POST_PATH = "/home/runner/work/Obsidian/Obsidian/HexoBlog-Resp/source/_posts"
OBSIDIAN_PATH = "/home/runner/work/Obsidian/Obsidian/Obsidian-Resp"
FORMAT_DATETIME = "{:%Y-%m-%d %H:%M:%S}"
STR_FORMAT_DATETIME = '%Y-%m-%d %H:%M:%S'
STR_FORMAT_DATETIME2 = '%a %b %d %H:%M:%S %Y %z'
DATE_REGEX = re.compile(r"\ndate:\s(.*)\n")
ENGLISH_TITLE_REGEX = re.compile(r"\nenglish_title:\s(.*)\n")
OBSIDIAN_TO_HEXOBLOG_TAG = "Obsidian-to-HexoBlog-Tag"
 

def get_obsidian_tags(file_path):
    """获取 Obsidian 文章的 tag"""

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

    return [tag for tag in first_line.split('#') if tag]


def get_hexo_post_english_title_2_title():
    """获取 HexoBlog 所有文章的英文名与标题的对应关系"""

    hexo_post_english_title_2_title = {}
    for file_name in os.listdir(HEXO_POST_PATH):
        file_path = os.path.join(HEXO_POST_PATH, file_name)
        if os.path.isdir(file_path):
            continue
        with open(file_path, "r") as f:
            content = f.read()
        hexo_english_title = ENGLISH_TITLE_REGEX.findall(content)[0]
        hexo_post_english_title_2_title[hexo_english_title] = file_name
    return hexo_post_english_title_2_title


def is_need_post_hexo(post_article_path, english_title, file_path):
    """判断是否需要发布 HexoBlog"""

    create_time = FORMAT_DATETIME.format(datetime.datetime.fromtimestamp(os.path.getmtime(file_path)))
    # 如果 Obsidian 修改了标题，修改 HexoBlog 英文名同名文章的标题
    if not os.path.exists(post_article_path):
        english_title_2_title = get_hexo_post_english_title_2_title()
        if english_title in english_title_2_title:
            post_article_path_new = os.path.join(HEXO_POST_PATH, english_title_2_title[english_title])
            os.rename(post_article_path_new, post_article_path)

    # 如果 Obsidian 文件已经在 HexoBlog 中存在，判断 Obsidian 文件更新时间与 HexoBlog 的最后更新时间
    if os.path.exists(post_article_path):
        with open(post_article_path, "r") as f:
            content = f.read()
        date_result = DATE_REGEX.findall(content)
        create_time = date_result[0]
        # HexoBlog 最后更新时间
        update_time_str = date_result[1] if len(date_result) == 2 else date_result[0]
        hexo_update_time = datetime.datetime.strptime(update_time_str, STR_FORMAT_DATETIME)
        # Run the Git command to get the last commit date for the file
        git_log_result = subprocess.run(["git", "log", "-1", "--format=%cd", "--",
                                        file_path], cwd=OBSIDIAN_PATH, capture_output=True)
        # Decode the output and extract the date and time string
        git_last_commit_date_str = git_log_result.stdout.decode().strip()
        dt = datetime.datetime.strptime(git_last_commit_date_str, STR_FORMAT_DATETIME2)
        file_git_last_commit_date = dt.strftime(STR_FORMAT_DATETIME)
        # 如果 hexoblog 中 update_date 和 文件最后更新时间不相同，则需要更新
        print('file_git_last_commit_date: {}, hexo_update_time: {}', file_git_last_commit_date, hexo_update_time)
        return create_time, file_git_last_commit_date, not (file_git_last_commit_date != hexo_update_time)
    # 如果不存在，则需求发布到 HexoBlog
    return create_time, create_time, True


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
    tags = get_obsidian_tags(file_path=file_path)
    # 如果没有 Obsidian-to-HexoBlog-Tag 标签
    if OBSIDIAN_TO_HEXOBLOG_TAG not in tags:
        return
    print('has tag', file_path)
    english_title = tags[0]  # 第一个标签为英文名

    # 2、如果是，判断是否需要发布 HexoBlog
    post_article_path = os.path.join(HEXO_POST_PATH, file_name)
    create_time, update_time, is_need = is_need_post_hexo(post_article_path, english_title, file_path)
    if not is_need:
        return
    print('need post', file_path)
    # 3、更新 Hexo 文章
    update_hexo_article(tags, english_title, create_time, update_time, file_name, post_article_path, file_path)


def transf():
    file_list = os.listdir(OBSIDIAN_PATH)
    for file_name in file_list:
        file_path = os.path.join(OBSIDIAN_PATH, file_name)
        file_suffix = os.path.splitext(file_name)[1]  # 笔记后缀
        if file_suffix != '.md':
            continue
        if os.path.isdir(file_path):
            continue
        exec(file_name, file_path)


if __name__ == "__main__":
    transf()
