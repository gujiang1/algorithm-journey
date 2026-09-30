# 这 4 行是 Windows 中文显示修复，照抄即可（第 2 周会讲 encoding 是什么）
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

name = "吕吉帅"
print ("你好，" + name)
print ("从今天起我要开始学算法，第一天先跑通这一行")
print (1 + 1)