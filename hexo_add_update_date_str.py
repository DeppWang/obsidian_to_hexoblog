import os
import re
UPDATE_DATE_REGEX = re.compile(r"\nupdate_date:\s(.*)\n")
STR_FORMAT_DATETIME = '%Y-%m-%d %H:%M:%S'
STR_FORMAT_DATETIME2 = '%a %b %d %H:%M:%S %Y %z'


def add_update_date(file_path, update_date):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    # lines = input_text.split('\n')
    update_line = f'update_date: {update_date}\n'
    lines.insert(4, update_line)
    # return '\n'.join(lines)
    with open(file_path, 'w') as f:
        f.writelines(lines)


FORMAT_DATETIME = "{:%Y-%m-%d %H:%M:%S}"
if __name__ == "__main__":
    import subprocess
    import datetime
    # Replace with the path to your file and the Git repository root directory
    repo_dir = "/Users/yanjie/GitHub/HexoBlog/source/_posts/"
    for file_name in os.listdir(repo_dir):
        file_path = os.path.join(repo_dir, file_name)
        if os.path.isdir(file_path) or os.path.splitext(file_name)[1] != ".md":
            continue
        try:
          with open(file_path, 'r') as f:
              print(file_path)
              content = f.read()
              date_result = UPDATE_DATE_REGEX.findall(content)
        except Exception as e:
            print(e)
            continue
        if len(date_result) != 0:
            continue
        # Run the Git command to get the last commit date for the file
        git_log_result = subprocess.run(["git", "log", "-1", "--format=%cd", "--",
                                        file_path], cwd=repo_dir, capture_output=True)
        # Decode the output and extract the date and time string
        git_last_commit_date_str = git_log_result.stdout.decode().strip()
        print(git_last_commit_date_str)
        dt = datetime.datetime.strptime(git_last_commit_date_str, STR_FORMAT_DATETIME2)
        file_git_last_commit_date = dt.strftime(STR_FORMAT_DATETIME)
        add_update_date(file_path, file_git_last_commit_date)
