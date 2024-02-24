'''
Author: zi.yang
Date: 2024-02-24 20:56:50
LastEditors: zi.yang
LastEditTime: 2024-02-24 21:26:32
Description: Common utils
FilePath: /sonar_bugfix_ai/utils/common.py
'''


def read_file(file_path):
    """读文件
    :param file_path: 文件路径
    :return: 读取成功返回 { "ok": True, "content": content }，否则返回 { "ok": False, "error": error }
    """

    try:
        with open(file_path, 'r') as file:
            content = file.read()
            return {"ok": True, "content": content}
    except FileNotFoundError:
        return {"ok": False, "error": f"文件读取失败：文件不存在 {file_path}"}
    except UnicodeDecodeError:
        return {"ok": False, "error": f"文件读取失败：文件编码错误 {file_path}"}
    except IsADirectoryError:
        return {"ok": False, "error": f"文件读取失败：读取对象时一个文件夹 {file_path}"}
    except Exception as e:
        return {"ok": False, "error": f"文件读取失败：{str(e)}"}


def write_file(file_path, content):
    """写文件
    :param file_path: 文件路径
    :param content: 写入内容
    :return: 写入成功返回 { "ok": True }，否则返回 { "ok": False, "error": error }
    """

    try:
        with open(file_path, 'w') as file:
            if isinstance(content, str):
                file.write(content)
            else:
                return {"ok": False, "error": "文件写入失败：写入的数据必须是一个字符串"}
            return {"ok": True}
    except FileNotFoundError:
        print(f"文件不存在：{file_path}")
        return {"ok": False, "error": f"文件写入失败：文件不存在 {file_path}"}
    except IsADirectoryError:
        print(f"文件夹：{file_path}")
        return {"ok": False, "error": f"文件写入失败：写入对象是一个文件夹 {file_path}"}
    except Exception as e:
        return {"ok": False, "error": f"文件写入失败： {str(e)}"}
