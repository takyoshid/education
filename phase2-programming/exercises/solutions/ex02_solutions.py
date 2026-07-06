"""
演習 02: 変数・データ型・演算子 — 模範解答
Python 3.12+ で実行可能
"""

import math


# ---- 問題 1: 型の確認 ----
print("=== 問題 1: 型の確認 ===")
values = [42, 3.14, "hello", True, None]
for v in values:
    print(f"  {v!r:10} -> {type(v).__name__}")


# ---- 問題 2: 演算結果の予測 ----
print("\n=== 問題 2: 演算結果 ===")
print(f"  17 // 5  = {17 // 5}")   # 3
print(f"  17 % 5   = {17 % 5}")    # 2
print(f"  -17 // 5 = {-17 // 5}")  # -4 (数直線上で小さい方向への切り捨て)
print(f"  2 ** 8   = {2 ** 8}")    # 256
print(f"  True+True+False = {True + True + False}")  # 2


# ---- 問題 3: 摂氏→華氏変換 ----
print("\n=== 問題 3: 摂氏→華氏変換 ===")
celsius = 100
fahrenheit = celsius * 9 / 5 + 32
print(f"  {celsius}°C は {fahrenheit}°F です")


# ---- 問題 4: 円の面積と円周 ----
print("\n=== 問題 4: 円の面積・円周 ===")
PI = 3.14159
radius = 5
area = PI * radius ** 2
circumference = 2 * PI * radius
print(f"  半径 {radius} の円: 面積 = {area:.2f}, 円周 = {circumference:.2f}")


# ---- 問題 5: BMI 計算 ----
print("\n=== 問題 5: BMI ===")
weight_kg = 70.0
height_m = 1.75
bmi = weight_kg / height_m ** 2

if bmi < 18.5:
    category = "低体重"
elif bmi < 25.0:
    category = "普通体重"
else:
    category = "肥満"

print(f"  BMI = {bmi:.1f} → {category}")


# ---- 問題 6: 参照モデルの確認 ----
print("\n=== 問題 6: 参照モデル ===")
x = 10
y = x
# x は新しい整数オブジェクト 20 を参照するよう付け替えられる
# y はまだ 10 を参照している
x = 20
print(f"  y = {y}")   # 10
# 解説: 整数はイミュータブル。x = 20 は x の参照先を変えるだけで
# 元の整数オブジェクト 10 には影響しない。y はそのまま 10 を参照し続ける。


# ---- 問題 7: 型変換エラーの修正 ----
print("\n=== 問題 7: 型変換 ===")
score = 95

# 方法 1: str() で変換
message = "あなたの点数は " + str(score) + " 点です"
print(f"  {message}")

# 方法 2: f 文字列(最も読みやすい)
message2 = f"あなたの点数は {score} 点です"
print(f"  {message2}")


# ---- 問題 8: 複合フォーマット ----
print("\n=== 問題 8: 複合フォーマット ===")
celsius2 = 36.5
weight2 = 65.0
height2 = 1.70

fahrenheit2 = celsius2 * 9 / 5 + 32
bmi2 = weight2 / height2 ** 2

print(f"  体温: {celsius2}°C = {fahrenheit2:.1f}°F")
print(f"  BMI: {bmi2:.1f}")


# ---- 問題 9: 浮動小数点の誤差 ----
print("\n=== 問題 9: 浮動小数点の誤差 ===")
result = 0.1 + 0.2
print(f"  0.1 + 0.2 = {result}")        # 0.30000000000000004
print(f"  == 0.3: {result == 0.3}")      # False

print(f"  isclose: {math.isclose(result, 0.3)}")   # True
# math.isclose のデフォルト相対誤差は 1e-9
# 絶対誤差で比較したい場合: math.isclose(result, 0.3, abs_tol=1e-9)
