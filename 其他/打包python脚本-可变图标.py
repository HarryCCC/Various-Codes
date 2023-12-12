import subprocess
import os
import shutil

def package_script(script_name, output_name):
    try:
        # 检查当前目录是否存在.ico文件
        icon_file = None
        for file in os.listdir():
            if file.endswith('.ico'):
                icon_file = file
                break

        # 创建pyinstaller命令
        pyinstaller_command = ["pyinstaller", "--onefile", "--name", output_name]

        # 如果找到.ico文件，添加到pyinstaller命令中
        if icon_file:
            pyinstaller_command.extend(["--icon", icon_file])

        pyinstaller_command.append(script_name)

        # 创建单一可执行文件
        subprocess.run(pyinstaller_command)
        
        # 移动可执行文件到当前目录
        os.rename(f"dist/{output_name}.exe", f"{output_name}.exe")

        # 删除生成的额外文件和目录
        os.remove(f"{output_name}.spec")
        shutil.rmtree("dist")
        shutil.rmtree("build")
        shutil.rmtree("__pycache__")

        print(f"Packaging {script_name} to {output_name}.exe is complete.")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    script_name = "全面加密.py"  # 你的 Python 脚本文件名
    output_name = "output"  # 输出的可执行文件名
    package_script(script_name, output_name)
