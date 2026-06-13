# Discord Google Search Bot

Python 3.11+ 製の Discord Bot。Google Custom Search API と YouTube Data API を使った画像・動画・Web検索ができます。

---

## 必要なもの

| 項目 | 入手先 |
|------|--------|
| Discord Bot Token | [Discord Developer Portal](https://discord.com/developers/applications) |
| Discord Application ID | 同上 (General Information) |
| Google API Key | [Google Cloud Console](https://console.cloud.google.com/) → API & Services → Credentials |
| Google Custom Search Engine ID | [Programmable Search Engine](https://programmablesearchengine.google.com/) |
| YouTube Data API v3 Key | Google Cloud Console → YouTube Data API v3 を有効化 |

---

## セットアップ

### 1. ファイルを用意する

```bash
# このフォルダに移動
cd discord-bot

# .env ファイルを作成
copy .env.example .env        # Windows
cp .env.example .env          # Mac / Linux
```

`.env` を開いて各値を埋める:

```env
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_APPLICATION_ID=your_application_id_here
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_custom_search_engine_id_here
YOUTUBE_API_KEY=your_youtube_data_api_key_here
```

### 2. Python パッケージをインストール

```bash
pip install -r requirements.txt
```

### 3. Bot を起動

```bash
python bot.py
```

VSCode のターミナルで実行してください。起動すると以下のように表示されます:

```
Slash commands synced.
Logged in as YourBot#0000 (ID: 123456789)
------
```

---

## Google Cloud の設定手順

### Google API Key の取得

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. プロジェクトを作成 (または既存のものを選択)
3. 「API とサービス」→「ライブラリ」で以下を有効化:
   - **Custom Search API**
   - **YouTube Data API v3**
4. 「API とサービス」→「認証情報」→「認証情報を作成」→「API キー」

### Custom Search Engine ID の取得

1. [Programmable Search Engine](https://programmablesearchengine.google.com/) にアクセス
2. 「Add」で新規作成
3. 「Search the entire web」を有効にする
4. 「Image search」を有効にする
5. 作成後に表示される **Search engine ID** をコピー

---

## Discord Bot の設定

### Developer Portal での設定

1. [Discord Developer Portal](https://discord.com/developers/applications) でアプリを作成
2. 「Bot」タブ → Token を生成・コピー
3. 「General Information」→ Application ID をコピー
4. 「Bot」タブ → 「Privileged Gateway Intents」は全てオフでOK
5. 「OAuth2」→「URL Generator」で以下を選択:
   - Scopes: `bot`, `applications.commands`
   - Bot Permissions: `Send Messages`, `Embed Links`, `Read Message History`
6. 生成されたURLでBotをサーバーに招待

---

## コマンド一覧

| コマンド | 説明 |
|---------|------|
| `/set` | 現在のチャンネルをBot専用チャンネルに設定 (チャンネル管理権限が必要) |
| `/google_search [query] [mode]` | image / video / ai モードで検索 |
| `/google_image [query]` | 画像検索 + Back/Next ページネーション |
| `/google_video [query]` | YouTube動画検索 + Back/Next ページネーション |
| `/google_news [query]` | Googleニュース検索 |
| `/google_web [query]` | Google Web検索 |

### 表示内容

**画像検索の結果:**
- Image name と URL
- 画像埋め込み
- ソースサイト名
- 著作権ステータス (CC / Public Domain / 不明 など)
- Back / Next ボタン

**動画検索の結果:**
- Video name と YouTube URL
- サムネイル埋め込み (URLをクリックするとYouTubeに飛びます)
- チャンネル名
- Back / Next ボタン

---

## ファイル構成

```
discord-bot/
├── bot.py                  # エントリーポイント
├── requirements.txt        # 依存パッケージ
├── .env.example            # 環境変数テンプレート
├── .env                    # 実際の環境変数 (自分で作成・Git管理外)
├── cogs/
│   ├── settings.py         # /set コマンド・チャンネル管理
│   └── search.py           # 検索コマンド群・ページネーション
├── utils/
│   └── google_api.py       # Google / YouTube API ラッパー
└── data/
    └── channels.json       # チャンネル設定の保存先
```

---

## 注意事項

- Google Custom Search API の無料枠は **1日100クエリ** です。
- YouTube Data API v3 は **1日10,000ユニット** の無料枠があります。
- `.env` ファイルは絶対に Git にコミットしないでください。`.gitignore` に追加することを推奨します。
