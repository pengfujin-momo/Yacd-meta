import os
import requests
import shutil
import tempfile
import time
import zipfile
from datetime import datetime, timezone, timedelta

# 替换为您自己的值
repo = 'MetaCubeX/Yacd-meta'
download_url = 'https://github.com/MetaCubeX/yacd/archive/gh-pages.zip'
meta_dir_name = 'Yacd-meta-gh-pages'
target_directory = 'ui'

sleep_time = int(os.environ.get('SLEEP_TIME', '300'))
github_token = os.environ.get('GITHUB_TOKEN', '')

if github_token:
    # 创建包含 Authorization 头的 headers 字典, 值为 'token <your_github_token_here>'。
    headers = {'Authorization': f'token {github_token}'}
else:
    headers = {}

last_commit_sha, last_update_time = '', ''

while True:
    try:
        # 从 GitHub API 获取最新提交 SHA
        response = requests.get(f'https://api.github.com/repos/{repo}/commits', headers=headers)
        commit_sha = response.json()[0]['sha']

    except Exception as e:
        print(f'[{datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")}] 无法获取最新提交 SHA: {e}')
        commit_sha = ''

    # 检查自上次检查以来是否有提交 SHA 发生变化
    if commit_sha != last_commit_sha:
        print(f'[{datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")}] 仓库 {repo} 有更新！正在下载最新版本...')

        try:
            # 下载 zip 文件
            response = requests.get(download_url)
            with open('yacd.zip', 'wb') as f:
                f.write(response.content)
            print(f'[{datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")}] 成功下载最新版本！')

            # 将文件提取到临时目录
            with tempfile.TemporaryDirectory() as tmpdir:
                with zipfile.ZipFile('yacd.zip', 'r') as zip_ref:
                    zip_ref.extractall(path=tmpdir)

                extracted_dir = os.path.join(tmpdir, meta_dir_name)

                if not os.path.exists(extracted_dir):
                    raise FileNotFoundError('未找到提取的目录')
                
                # 删除ui文件夹下文件
                if os.path.exists(target_directory):
                    target_dir = os.path.abspath(target_directory)
                    for filename in os.listdir(target_dir):
                        file_path = os.path.join(target_dir, filename)
                        try:
                            if os.path.isfile(file_path) or os.path.islink(file_path):
                                os.unlink(file_path)
                            elif os.path.isdir(file_path):
                                shutil.rmtree(file_path)
                        except Exception as e:
                            print(f'[{datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")}] 删除"{file_path}"时发生错误: {e}')
                

                for file in os.listdir(extracted_dir):
                    shutil.move(os.path.join(extracted_dir, file), os.path.join(target_directory, file))
                print(f'[{datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")}] 成功更新本地版本！')

        except Exception as e:
            print(f'[{datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")}] 在下载和提取最新版本期间发生错误: {e}')

        else:
            # 更新上一个提交 SHA 和更新时间戳
            last_commit_sha = commit_sha
            last_update_time = datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')

            # print(f'[{datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")}] 最新版本的"{repo}"已保存到"{target_directory}"目录中。')
            print(f'[{datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")}] 最新提交 SHA: {last_commit_sha}')
            print(f'[{datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")}] 更新时间: {last_update_time}')


        finally:
            # 清理任何临时文件或目录
            if os.path.exists('yacd.zip'):
                os.remove('yacd.zip')
                # print(f'[{datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")}] 删除临时"yacd.zip"文件。')
            if os.path.exists(extracted_dir):
                shutil.rmtree(extracted_dir)
                # print(f'[{datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")}] 删除临时提取的目录。')


            # 等待一段时间后再次检查
            # print(f'[{datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")}] 已完成更新，下一次检查将在{sleep_time}秒后进行...')
            time.sleep(sleep_time)
            

    else:
        # 没有更新，等待一段时间后再次检查
        # print(f'[{datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")}] 没有发现更新，下一次检查将在{sleep_time}秒后进行...')
        time.sleep(sleep_time)
