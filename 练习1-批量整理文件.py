"""
练习 1：批量整理文件（零基础版）
================================
这个脚本做三件事：
  1. 扫描一个文件夹里的所有文件
  2. 按「扩展名」给它们分类（图片 / 文档 / 表格 / 代码 / 压缩包 / 其他）
  3. 把文件名改成规范格式：分类_序号_原扩展名，例如  图片_001_.jpg

【重点】默认是「预览模式」，只打印会做什么，不会真的改名。
       确认没问题后，加 --go 参数才会真的改名。
       这是脚本的第一条生存法则：破坏性操作前先能预览。

运行方法（在 VS Code 里按 Ctrl+F5，或在终端里）：
    python 练习1-批量整理文件.py              # 预览
    python 练习1-批量整理文件.py --go         # 真的改名

作者注：这是你的第一个"有用"的程序，不是玩具。
       第 6 天你要做的是——读懂它，然后自己加一个"按修改日期分类"的功能。
"""

import os
import sys
import shutil

# ---------- 0. Windows 中文显示修复 ----------
# 这台电脑的控制台是 UTF-8 码页，但 Python 默认按系统 GBK 输出中文，会显示成乱码。
# 下面 2 行让 Python 用 UTF-8 输出。照抄即可，第 2 周会讲 encoding 是什么。
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ---------- 1. 配置：把分类规则写成字典 ----------
# 字典的格式是 {键: 值}，这里 键=分类名，值=属于这个分类的扩展名列表
CATEGORIES = {
    "图片": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"],
    "文档": [".doc", ".docx", ".pdf", ".txt", ".md", ".ppt", ".pptx"],
    "表格": [".xls", ".xlsx", ".csv"],
    "代码": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c"],
    "压缩包": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "音视频": [".mp4", ".mp3", ".avi", ".mkv", ".wav", ".flac"],
}


def get_category(filename):
    """根据文件名（或扩展名）判断它属于哪个分类。"""
    # os.path.splitext 把 "photo.jpg" 拆成 ("photo", ".jpg")
    ext = os.path.splitext(filename)[1].lower()   # lower() 统一转小写，.JPG 也能识别
    for category, extensions in CATEGORIES.items():   # 遍历字典：category 是分类名
        if ext in extensions:
            return category
    return "其他"      # 都没匹配上，归到"其他"


def scan_folder(folder):
    """扫描文件夹，返回 [(文件名, 分类), ...] 这样的清单。"""
    if not os.path.isdir(folder):
        print(f"[错误] 文件夹不存在：{folder}")
        return []

    result = []
    for name in os.listdir(folder):                    # 列出文件夹里的所有名字
        full_path = os.path.join(folder, name)         # 拼出完整路径
        if os.path.isfile(full_path):                  # 只处理文件，跳过子文件夹
            result.append((name, get_category(name)))
    return result


def build_new_names(items, folder):
    """生成改名计划：返回 [(旧名, 新名), ...]。"""
    # 计数器：用来生成 001、002 这样的序号
    counters = {}
    plan = []

    for old_name, category in items:
        # 每个分类单独计数
        counters[category] = counters.get(category, 0) + 1
        seq = counters[category]

        ext = os.path.splitext(old_name)[1].lower()
        new_name = f"{category}_{seq:03d}_{old_name}"   # :03d 表示补零到 3 位

        # 防止新旧名字一样（比如原名已经规范）
        if new_name != old_name:
            plan.append((old_name, new_name))
    return plan


def print_plan(plan):
    """打印改名计划，让用户先看清楚。"""
    print("\n" + "=" * 64)
    print(f"共发现 {len(plan)} 个需要改名的文件：")
    print("=" * 64)
    for i, (old_name, new_name) in enumerate(plan, start=1):
        print(f"{i:>3}. {old_name}")
        print(f"     -> {new_name}")
    print("=" * 64)


def apply_plan(plan, folder):
    """真正执行改名。"""
    ok, fail = 0, 0
    for old_name, new_name in plan:
        old_path = os.path.join(folder, old_name)
        new_path = os.path.join(folder, new_name)
        try:
            shutil.move(old_path, new_path)    # 改名 = 移动到新名字
            ok += 1
        except Exception as e:                 # 出错不要让程序崩掉，记录后继续
            fail += 1
            print(f"[失败] {old_name} -> {new_name}：{e}")
    print(f"\n完成：成功 {ok} 个，失败 {fail} 个")


def summary(items):
    """统计每个分类各有几个文件。"""
    counts = {}
    for _, category in items:
        counts[category] = counts.get(category, 0) + 1
    print("\n分类统计：")
    for category, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {category:<6} {n:>3} 个")


def main():
    # ---------- 2. 取参数 ----------
    # sys.argv 是"命令行参数列表"：argv[0] 是脚本名，argv[1] 是第一个参数
    real_run = "--go" in sys.argv            # 有没有加 --go

    # 要整理哪个文件夹？默认用当前脚本所在的目录
    target = None
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            target = arg
    if target is None:
        target = os.path.dirname(os.path.abspath(__file__))    # 脚本自己所在的目录

    print(f"目标文件夹：{target}")
    print(f"运行模式：{'【真实改名】' if real_run else '【预览模式，不会改动任何文件】'}")

    # ---------- 3. 执行流程：扫描 -> 统计 -> 生成计划 -> （执行）----------
    items = scan_folder(target)
    if not items:
        print("没有找到可处理的文件。")
        return

    summary(items)
    plan = build_new_names(items, target)
    print_plan(plan)

    if not plan:
        print("\n所有文件名都已经是规范格式，无需改动。")
        return

    if real_run:
        confirm = input("\n确认要真的改名吗？输入 yes 继续：")
        if confirm.strip().lower() == "yes":
            apply_plan(plan, target)
        else:
            print("已取消。")
    else:
        print("\n这是预览模式。确认无误后，加 --go 参数运行即可真的改名。")
        print("例如：python 练习1-批量整理文件.py --go")


# 固定写法：只有"直接运行这个文件"时才执行 main()
# 被别的文件 import 时不会自动执行（第 2 周会讲为什么）
if __name__ == "__main__":
    main()
