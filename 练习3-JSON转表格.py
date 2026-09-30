"""
练习 3：JSON 转表格（零基础版）
================================
这个脚本做三件事：
  1. 如果没有示例数据，自动生成一份嵌套的 orders.json
  2. 读取 JSON（里面有嵌套的字典和列表）
  3. 把嵌套结构「拍平」成一张表，导出为 CSV

【为什么练这个】
   接口返回的数据、日志、配置文件几乎都是 JSON，而且大多是嵌套的。
   把嵌套数据拍平成表格，是数据分析和做模型输入的第一步。
   第 14 周做 RAG 时你会再次用到这套思路。

运行方法：
    python 练习3-JSON转表格.py
"""

import json
import csv
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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, "orders.json")
CSV_FILE = os.path.join(BASE_DIR, "订单表.csv")

# 示例数据：注意它是"嵌套"的——每个订单里有 customer（字典）和 items（列表）
SAMPLE = {
    "shop": "校园便利店",
    "updated": "2026-09-29",
    "orders": [
        {
            "order_id": "A1001",
            "customer": {"name": "张三", "level": "普通", "city": "南京"},
            "items": [
                {"sku": "牛奶", "qty": 2, "price": 5.5},
                {"sku": "面包", "qty": 1, "price": 8.0},
            ],
            "paid": True,
        },
        {
            "order_id": "A1002",
            "customer": {"name": "李四", "level": "会员", "city": "南京"},
            "items": [
                {"sku": "矿泉水", "qty": 12, "price": 2.0},
            ],
            "paid": False,
        },
        {
            "order_id": "A1003",
            "customer": {"name": "王五", "level": "会员", "city": "杭州"},
            "items": [
                {"sku": "咖啡", "qty": 3, "price": 15.0},
                {"sku": "蛋糕", "qty": 2, "price": 22.0},
            ],
            "paid": True,
        },
    ],
}


def make_sample():
    """没有数据文件就自动生成一份。"""
    if os.path.exists(JSON_FILE):
        print(f"[跳过] 已存在：{JSON_FILE}")
        return
    # ensure_ascii=False 让中文按原样保存，而不是变成 \u4e2d 这种转义
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(SAMPLE, f, ensure_ascii=False, indent=2)
    print(f"[生成] 已创建示例数据：{JSON_FILE}")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)          # json.load 把文本变成 Python 的字典/列表


def flatten_orders(data):
    """
    把嵌套的订单数据拍平成一张表。
    思路：一个订单有多个商品，那就让每个商品占一行（这叫"明细粒度的表"）。
    """
    rows = []
    shop = data.get("shop", "")

    for order in data.get("orders", []):
        customer = order.get("customer", {})      # 取嵌套的 customer 字典
        items = order.get("items", [])            # 取嵌套的 items 列表

        # 算这个订单的总金额：把每件商品的 数量 x 单价 加起来
        total = sum(it.get("qty", 0) * it.get("price", 0) for it in items)

        for it in items:
            rows.append({
                "店铺": shop,
                "订单号": order.get("order_id", ""),
                "客户": customer.get("name", ""),
                "会员等级": customer.get("level", ""),
                "城市": customer.get("city", ""),
                "是否付款": "已付款" if order.get("paid") else "未付款",
                "商品": it.get("sku", ""),
                "数量": it.get("qty", 0),
                "单价": it.get("price", 0),
                "小计": round(it.get("qty", 0) * it.get("price", 0), 2),
                "订单总额": round(total, 2),
            })
    return rows


def print_preview(rows, n=5):
    if not rows:
        print("没有数据。")
        return
    headers = list(rows[0].keys())
    print("\n表格预览（前 %d 行）：" % min(n, len(rows)))
    print(" | ".join(headers))
    print("-" * 90)
    for r in rows[:n]:
        print(" | ".join(str(r[h]) for h in headers))


def simple_stats(rows):
    """顺手做个统计，让你看到"表格化之后能干什么"。"""
    if not rows:
        return
    print("\n简单统计：")
    print(f"  订单数（去重）：{len(set(r['订单号'] for r in rows))}")
    print(f"  明细行数：{len(rows)}")
    print(f"  总销售额：{sum(r['小计'] for r in rows):.2f} 元")

    # 按城市汇总销售额
    by_city = {}
    for r in rows:
        by_city[r["城市"]] = by_city.get(r["城市"], 0) + r["小计"]
    print("  按城市销售额：")
    for city, amount in sorted(by_city.items(), key=lambda x: -x[1]):
        print(f"    {city}：{amount:.2f} 元")


def save_csv(rows, path):
    if not rows:
        return
    headers = list(rows[0].keys())
    # utf-8-sig 让 Excel 直接双击打开也不乱码
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n[输出] 已导出表格：{path}")


def main():
    make_sample()
    data = load_json(JSON_FILE)

    print(f"[读取] 店铺：{data.get('shop')}，原始订单数：{len(data.get('orders', []))}")

    rows = flatten_orders(data)
    print_preview(rows)
    simple_stats(rows)
    save_csv(rows, CSV_FILE)


if __name__ == "__main__":
    main()
