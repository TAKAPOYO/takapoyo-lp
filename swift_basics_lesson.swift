// ============================================
// Swift 基礎講座 for TAKA
// ============================================

import Foundation

// ============================================
// 1. Swiftとは？
// ============================================
/*
 Swift は Apple が開発した、iOS/macOS アプリを作るためのプログラミング言語です。

 特徴:
 - シンプルで読みやすい文法
 - 安全性が高い（型に厳しい）
 - 高速で動作する
 - Xcode（開発ツール）で使う

 このファイルを Xcode Playground で開くと、実際に動かせます！
*/

print("=== Swift 基礎講座スタート！ ===\n")

// ============================================
// 2. 変数と定数（var と let）
// ============================================
print("--- 2. 変数と定数 ---")

// let = 定数（後から変更できない）
let appName = "MyFirstApp"
print("アプリ名: \(appName)")
// appName = "NewApp"  // エラー！定数は変更できない

// var = 変数（後から変更できる）
var userScore = 0
print("最初のスコア: \(userScore)")
userScore = 100
print("更新後のスコア: \(userScore)")

/*
 使い分けのコツ:
 - 基本は let を使う（安全！）
 - 値が変わる必要がある時だけ var を使う
*/

// ============================================
// 3. 基本的なデータ型
// ============================================
print("\n--- 3. データ型 ---")

// Int（整数）
let age: Int = 25
let level = 10  // 型推論：自動で Int と判断される

// String（文字列）
let userName: String = "TAKA"
let greeting = "こんにちは"  // 日本語もOK！

// Double（小数）
let price: Double = 1200.50
let pi = 3.14159  // 自動で Double

// Bool（真偽値）
let isLoggedIn: Bool = true
let hasNotification = false

print("名前: \(userName), 年齢: \(age)")
print("価格: \(price)円")
print("ログイン中: \(isLoggedIn)")

// 文字列の結合
let message = userName + "さん、" + greeting + "！"
print(message)

// より便利な文字列補間
let detailMessage = "\(userName)さんはレベル\(level)です"
print(detailMessage)

// ============================================
// 4. 配列と辞書
// ============================================
print("\n--- 4. 配列と辞書 ---")

// 配列（Array）- 順番のあるリスト
var fruits = ["りんご", "バナナ", "オレンジ"]
print("果物リスト: \(fruits)")

// 配列の操作
fruits.append("ぶどう")  // 追加
print("追加後: \(fruits)")
print("最初の果物: \(fruits[0])")  // インデックスは0から
print("果物の数: \(fruits.count)")

// 空の配列を作成
var scores: [Int] = []
scores.append(85)
scores.append(92)
print("スコア: \(scores)")

// 辞書（Dictionary）- キーと値のペア
var userInfo: [String: String] = [
    "name": "TAKA",
    "job": "Developer",
    "city": "Tokyo"
]
print("ユーザー情報: \(userInfo)")

// 辞書の値を取得
if let job = userInfo["job"] {
    print("職業: \(job)")
}

// 辞書に追加
userInfo["hobby"] = "アプリ開発"
print("趣味追加後: \(userInfo)")

// ============================================
// 5. 条件分岐（if文、switch文）
// ============================================
print("\n--- 5. 条件分岐 ---")

// if 文
let score = 85

if score >= 90 {
    print("成績: 優秀！")
} else if score >= 70 {
    print("成績: 良好")
} else {
    print("成績: がんばろう")
}

// 複数条件
let temperature = 25
let isSunny = true

if temperature >= 20 && isSunny {
    print("お出かけ日和です！")
} else if temperature < 10 || !isSunny {
    print("暖かくして出かけましょう")
}

// switch 文（パターンマッチング）
let weatherCode = "sunny"

switch weatherCode {
case "sunny":
    print("天気: 晴れ ☀️")
case "cloudy":
    print("天気: 曇り ☁️")
case "rainy":
    print("天気: 雨 🌧️")
default:
    print("天気: 不明")
}

// 数値の範囲でswitch
let playerLevel = 15

switch playerLevel {
case 0...5:
    print("レベル: 初心者")
case 6...15:
    print("レベル: 中級者")
case 16...30:
    print("レベル: 上級者")
default:
    print("レベル: マスター！")
}

// ============================================
// 6. ループ（for-in, while）
// ============================================
print("\n--- 6. ループ ---")

// for-in ループ（配列）
print("果物を1つずつ表示:")
for fruit in fruits {
    print("- \(fruit)")
}

// 範囲でループ
print("\n1から5までカウント:")
for number in 1...5 {
    print(number, terminator: " ")
}
print()  // 改行

// インデックス付きループ
print("\nインデックス付き:")
for (index, fruit) in fruits.enumerated() {
    print("\(index + 1)番目: \(fruit)")
}

// while ループ
var countdown = 3
print("\nカウントダウン:")
while countdown > 0 {
    print(countdown)
    countdown -= 1
}
print("発射！🚀")

// repeat-while ループ（最低1回は実行される）
var attempts = 0
repeat {
    attempts += 1
    print("試行回数: \(attempts)")
} while attempts < 2

// ============================================
// 7. 関数の基本
// ============================================
print("\n--- 7. 関数 ---")

// 基本的な関数
func sayHello() {
    print("こんにちは！")
}

sayHello()

// 引数を受け取る関数
func greet(name: String) {
    print("こんにちは、\(name)さん！")
}

greet(name: "TAKA")

// 複数の引数
func introduce(name: String, age: Int) {
    print("\(name)です。\(age)歳です。")
}

introduce(name: "TAKA", age: 25)

// 戻り値がある関数
func add(a: Int, b: Int) -> Int {
    return a + b
}

let result = add(a: 5, b: 3)
print("5 + 3 = \(result)")

// より実用的な関数
func calculateDiscount(price: Double, discountRate: Double) -> Double {
    let discount = price * discountRate
    return price - discount
}

let finalPrice = calculateDiscount(price: 1000, discountRate: 0.2)
print("割引後の価格: \(finalPrice)円")

// デフォルト引数
func makeGreeting(name: String, emoji: String = "👋") -> String {
    return "\(emoji) Hello, \(name)!"
}

print(makeGreeting(name: "TAKA"))
print(makeGreeting(name: "TAKA", emoji: "🎉"))

// ============================================
// 8. オプショナル型の基礎
// ============================================
print("\n--- 8. オプショナル型 ---")

/*
 オプショナル型 = 「値があるかもしれないし、ないかもしれない」

 なぜ必要？
 - nil（値なし）を安全に扱うため
 - エラーやバグを防ぐため
*/

// 普通の変数（nilを入れられない）
var normalName: String = "TAKA"
// normalName = nil  // エラー！

// オプショナル変数（nilを入れられる）
var optionalName: String? = "TAKA"
optionalName = nil  // OK
print("オプショナル: \(String(describing: optionalName))")

// オプショナルの値を取り出す方法

// 1. if let（安全なアンラップ）
var userAge: Int? = 25

if let age = userAge {
    print("年齢は\(age)歳です")
} else {
    print("年齢が設定されていません")
}

// 2. guard let（早期リターン）
func checkUser(name: String?) {
    guard let validName = name else {
        print("名前がありません")
        return
    }
    print("ユーザー名: \(validName)")
}

checkUser(name: "TAKA")
checkUser(name: nil)

// 3. nil合体演算子（??）
var nickname: String? = nil
let displayName = nickname ?? "ゲスト"
print("表示名: \(displayName)")

// 4. オプショナルチェーン
struct User {
    var name: String
    var email: String?
}

let user: User? = User(name: "TAKA", email: "taka@example.com")
let emailLength = user?.email?.count
print("メールアドレスの文字数: \(String(describing: emailLength))")

// 実践例：辞書とオプショナル
let userSettings: [String: String] = [
    "theme": "dark",
    "language": "ja"
]

// 辞書の値はオプショナルで返ってくる
if let theme = userSettings["theme"] {
    print("テーマ: \(theme)")
}

let fontSize = userSettings["fontSize"] ?? "16"  // キーがなければデフォルト値
print("フォントサイズ: \(fontSize)")

// ============================================
// まとめ
// ============================================
print("\n=== Swift 基礎講座 完了！ ===")
print("""

今日学んだこと:
✓ 変数（var）と定数（let）の使い分け
✓ 基本のデータ型（Int, String, Bool, Double）
✓ 配列と辞書でデータをまとめる
✓ if と switch で条件分岐
✓ for と while でループ処理
✓ 関数で処理をまとめる
✓ オプショナル型で安全にnilを扱う

次のステップ:
→ SwiftUI でUI を作ってみよう！
→ 実際に簡単なアプリを作ってみよう！
""")
