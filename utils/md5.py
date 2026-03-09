import os
import hashlib
import config.settings as config

def check_md5(md5_str: str) -> bool:
    """ 检查传入的 md5 字符串是否已经被处理过了
    如果已经存在返回 True 否则返回 False
    """

    # 检查保存 md5 字符串的文件已存在
    # 未存在说明第一次传入，创建文件并返回 False
    # 如果 md5 字符串已存在返回 True
    if not os.path.exists(config.md5_file_path):
        open(config.md5_file_path, 'w', encoding='utf-8').close()
        return False
    else:
        with open(config.md5_file_path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                line = line.strip()
                if md5_str == line:
                    return True
            return False

def save_md5(md5_str: str):
    """ 将传入的 md5 字符串记录到文件内保存 """
    with open(config.md5_file_path, 'a', encoding='utf-8') as f:
        f.write(md5_str + "\n")

def get_string_md5(input_str: str, encoding='utf-8') -> str:
    """ 将传入的字符串转换为 md5 字符串 """

    # 将字符串转换为字节数组
    str_bytes = input_str.encode(encoding=encoding)
    # 获取 md5 字符串
    md5_str = hashlib.md5(str_bytes).hexdigest()
    return md5_str
