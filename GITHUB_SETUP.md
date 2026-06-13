# GitHub へのpush手順

VSCode のターミナルで以下の順番に実行してください。

---

## 1. GitHubで空のリポジトリを作成

1. https://github.com/new にアクセス
2. Repository name を入力 (例: `discord-google-bot`)
3. Private / Public を選択
4. **README や .gitignore は追加しない** (空のリポジトリを作る)
5. 「Create repository」をクリック
6. 作成後に表示される URL をコピー (例: `https://github.com/あなたのユーザー名/discord-google-bot.git`)

---

## 2. discord-botフォルダをVSCodeで開く

ファイルをローカルにダウンロードし、VSCode で `discord-bot/` フォルダを開いてください。

---

## 3. ターミナルで以下を実行

```bash
# gitの初期化
git init

# ユーザー情報を設定 (初回のみ)
git config user.name "あなたの名前"
git config user.email "あなたのメールアドレス"

# ファイルをステージング
git add .

# コミット
git commit -m "Initial commit: Discord Google Search Bot"

# メインブランチ名を設定
git branch -M main

# リモートリポジトリを追加 (URLは自分のものに変更)
git remote add origin https://github.com/あなたのユーザー名/discord-google-bot.git

# push
git push -u origin main
```

---

## 4. GitHub Token での認証

push 時にユーザー名とパスワードを求められた場合:

- **Username**: GitHubのユーザー名
- **Password**: GitHubのパスワード**ではなく**、Personal Access Token を入力

### Token を使った URL で認証をスキップする方法

```bash
git remote set-url origin https://あなたのユーザー名:あなたのTOKEN@github.com/あなたのユーザー名/discord-google-bot.git
git push -u origin main
```

---

## 5. .env はpushされないことを確認

`.gitignore` に `.env` が含まれているので、**トークンや APIキーは自動的にpush対象外**になっています。

`git status` で `.env` が表示されないことを確認してから push してください。

---

## push後のフォルダ構成

```
discord-google-bot/         ← GitHubリポジトリ
├── bot.py
├── requirements.txt
├── .env.example            ← テンプレートのみpush (実際の.envはpushしない)
├── .gitignore
├── README.md
├── GITHUB_SETUP.md
├── cogs/
│   ├── settings.py
│   └── search.py
├── utils/
│   └── google_api.py
└── data/
    └── channels.json       ← .gitignoreで除外済み
```
