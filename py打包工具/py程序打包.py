import os
import subprocess
import shutil
import random
import string
import typer

def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f'错误: {stderr.decode()}')
    else:
        print(stdout.decode())

def main(py_file: str = typer.Option(None, help="要打包的py文件")):
    if py_file is None:
        py_file = typer.prompt("输入要打包的py文件")

    # 导出项目的依赖包 处理UnicodeDecodeError: 'gbk' codec can't decode byte 0x80 in position 390: illegal multibyte sequence
    # https://blog.csdn.net/craftsman2020/article/details/132580431
    run_command('pipreqs ./ --encoding=utf-8-sig --force')

    # 创建一个随机的虚拟环境名称
    venv_name = ''.join(random.sample(string.ascii_letters + string.digits, 8))
    print(venv_name)
    run_command(f'python -m venv {venv_name}')

    # 激活虚拟环境
    os.environ['PATH'] = os.path.join(os.getcwd(), venv_name, 'Scripts') + ';' + os.environ['PATH']

    # 使用pip wheel下载和安装依赖包 放到 lib 目录下
    run_command('pip wheel -r requirements.txt -w lib')

    # 安装依赖包
    run_command('pip install -r requirements.txt')

    # 下载pyinstaller
    run_command('pip install pyinstaller')

    # 使用pyinstaller打包成一个exe
    run_command(f'pyinstaller -F {py_file}')

    # 删除虚拟环境
    shutil.rmtree(venv_name)

if __name__ == "__main__":
    typer.run(main)
