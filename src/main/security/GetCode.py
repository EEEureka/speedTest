# 从路径打开文件， 导入其中的密码
def GetCode(code_file):
    with open(code_file, 'r') as f:
        code = f.readline()
    return code

if __name__ == '__main__':
    path = ""
    print(GetCode(path))
