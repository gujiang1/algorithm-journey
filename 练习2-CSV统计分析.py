"""
练习 2：CSV 数据统计分析（零基础版）
====================================
这个脚本做四件事：
  1. 如果没有示例数据，自动生成一份 students.csv
  2. 读取 CSV，统计人数、平均分、最高分、最低分
  3. 按条件筛选（比如"分数 >= 80 的学生"）
  4. 把统计结果写成新的 CSV

【关键知识点】CSV 就是"用逗号分隔的表格"，Excel 能直接打开。
   第 5 周做机器学习时，你 80% 的时间都在跟这种数据打交道。

运行方法：
    python 练习2-CSV统计分析.py
"""

import csv       # Python 自带的 CSV 读写工具，不用装任何东西
import os
import sys

# ---------- Windows 中文显示修复 ----------
# 这台电脑的控制台是 UTF-8 码页，但 Python 默认按系统 GBK 输出中文，会显示成乱码。
# 下面 2 行让 Python 用 UTF-8 输出。照抄即可，第 2 周会讲 encoding 是什么。
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# CSV 文件放在脚本旁边
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "students.csv")
REPORT_FILE = os.path.join(BASE_DIR, "统计结果.csv")

# 这是"示例数据"，用列表套列表表示：第一行是表头，后面每行是一条记录
SAMPLE_DATA = [
    ["姓名", "专业", "平时分", "期末分"],
    ["张三", "动物科学", 88, 91],
    ["李四", "动物科学", 56, 62],
    ["王五", "计算机", 92, 95],
    ["赵六", "计算机", 73, 68],
    ["钱七", "信息管理", 85, 79],
    ["孙八", "动物科学", 60, 58],
    ["周九", "信息管理", 95, 88],
    ["吴十", "计算机", 45, 52],
]


def make_sample_data():
    """如果数据文件不存在，就生成一份示例数据。"""
    if os.path.exists(DATA_FILE):
        print(f"[跳过] 已存在数据文件：{DATA_FILE}")
        return

    # newline="" 是 Windows 上写 CSV 的固定写法，避免每行多出空行
    # encoding="utf-8-sig" 让 Excel 打开时中文不乱码
    with open(DATA_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        for row in SAMPLE_DATA:
            writer.writerow(row)
    print(f"[生成] 已创建示例数据：{DATA_FILE}")


def read_data(path):
    """读取 CSV，返回字典列表，例如 [{'姓名': '张三', '期末分': '91'}, ...]"""
    rows = []
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)      # DictReader 把每行变成字典，用表头当键
        for row in reader:
            rows.append(row)
    return rows


def to_number(value):
    """把从 CSV 读到的字符串安全地转成数字。转不了就返回 0。"""
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def analyze(rows):
    """做统计，返回一个字典。"""
    if not rows:
        return {}

    finals = [to_number(r["期末分"]) for r in rows]        # 列表推导式：把每行的期末分取出来
    totals = [to_number(r["平时分"]) * 0.3 + to_number(r["期末分"]) * 0.7 for r in rows]   # 总评 = 平时30% + 期末70%

    stats = {
        "总人数": len(rows),
        "平均期末分": sum(finals) / len(finals),
        "最高期末分": max(finals),
        "最低期末分": min(finals),
        "平均总评": sum(totals) / len(totals),
        "及格人数": sum(1 for t in totals if t >= 60),      # 生成器 + sum：统计满足条件的个数
    }
    return stats


def print_stats(stats):
    print("\n" + "=" * 40)
    print("统计结果")
    print("=" * 40)
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key:<10} {value:.2f}")
        else:
            print(f"  {key:<10} {value}")


def filter_rows(rows, min_score=80):
    """筛选：期末分 >= min_score 的学生。"""
    return [r for r in rows if to_number(r["期末分"]) >= min_score]


def write_report(rows, stats, path):
    """把统计结果 + 筛选结果写成一份新的 CSV。"""
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)

        writer.writerow(["【统计结果】"])
        for key, value in stats.items():
            writer.writerow([key, round(value, 2) if isinstance(value, float) else value])

        writer.writerow([])                       # 空行分隔
        writer.writerow(["【期末分 80 分以上名单】"])
        writer.writerow(["姓名", "专业", "期末分"])
        for r in rows:
            writer.writerow([r["姓名"], r["专业"], r["期末分"]])

    print(f"\n[输出] 报告已写入：{path}")


def main():
    make_sample_data()

    rows = read_data(DATA_FILE)
    print(f"[读取] 共 {len(rows)} 条记录")

    stats = analyze(rows)
    print_stats(stats)

    top = filter_rows(rows, min_score=80)
    print(f"\n期末分 80 分以上：{len(top)} 人")
    for r in top:
        print(f"  {r['姓名']}（{r['专业']}）{r['期末分']} 分")

    write_report(rows, stats, REPORT_FILE)


if __name__ == "__main__":
    main()
