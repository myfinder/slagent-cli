# slagent

Slack Web API を User Token で利用するコマンドラインツールです。

メッセージの検索、メンションの確認、チャンネルへの投稿、スレッドの閲覧などをターミナルから操作できます。

[English README](README.md)

## インストール

### ビルド済みバイナリをダウンロード（推奨）

[Releases](https://github.com/myfinder/slagent-cli/releases) ページから最新のバイナリをダウンロードできます。

| プラットフォーム | ファイル |
|----------------|---------|
| Linux (x86_64) | `slagent-linux-amd64` |
| macOS (Apple Silicon) | `slagent-darwin-arm64` |

```bash
# 例: macOS Apple Silicon
curl -LO https://github.com/myfinder/slagent-cli/releases/latest/download/slagent-darwin-arm64
chmod +x slagent-darwin-arm64
mv slagent-darwin-arm64 /usr/local/bin/slagent
```

### ソースからインストール

```bash
git clone https://github.com/myfinder/slagent-cli.git
cd slagent-cli
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## セットアップ

### 1. Slack App の作成

1. [Slack API: Your Apps](https://api.slack.com/apps) から新しいアプリを作成
2. **OAuth & Permissions** で以下の **User Token Scopes** を追加:
   - `search:read` — メッセージ検索
   - `chat:write` — メッセージ投稿
   - `channels:read` — パブリックチャンネル一覧
   - `groups:read` — プライベートチャンネル一覧
   - `channels:history` — パブリックチャンネル履歴の閲覧
   - `groups:history` — プライベートチャンネル履歴の閲覧
3. ワークスペースにアプリをインストール
4. **User OAuth Token** (`xoxp-...`) をコピー

### 2. 環境変数の設定

```bash
export SLACK_USER_TOKEN=xoxp-your-token-here
```

## 使い方

```
slagent [COMMAND] [OPTIONS]
```

### コマンド一覧

#### search — メッセージ検索

```bash
slagent search "デプロイ エラー"
slagent search "議事録" -n 5
slagent search "バグ報告" --sort score
```

| オプション | 説明 |
|-----------|------|
| `-n, --count` | 取得件数 (デフォルト: 10) |
| `--sort` | ソート順: `score` または `timestamp` (デフォルト: `timestamp`) |

#### mentions — 自分へのメンションを表示

```bash
slagent mentions
slagent mentions -n 20
```

| オプション | 説明 |
|-----------|------|
| `-n, --count` | 取得件数 (デフォルト: 10) |

#### post — メッセージを投稿

```bash
slagent post "#general" "slagent からこんにちは！"
slagent post C01ABCD2EFG "スレッドへの返信" --thread-ts 1234567890.123456
```

| オプション | 説明 |
|-----------|------|
| `--thread-ts` | 返信先のスレッドタイムスタンプ |

チャンネルは `#channel-name` またはチャンネル ID で指定できます。

#### thread — スレッドを読む

```bash
slagent thread "#general" 1234567890.123456
slagent thread C01ABCD2EFG 1234567890.123456 -n 100
```

| オプション | 説明 |
|-----------|------|
| `-n, --count` | 取得するリプライの最大数 (デフォルト: 50) |

#### history — チャンネルの直近メッセージを表示

```bash
slagent history "#general"
slagent history "#random" -n 50
```

| オプション | 説明 |
|-----------|------|
| `-n, --count` | 取得件数 (デフォルト: 20) |

#### channels — 所属チャンネル一覧を表示

```bash
slagent channels
slagent channels --all
```

| オプション | 説明 |
|-----------|------|
| `--all` | アーカイブ済みチャンネルも含める |

## リリース

GitHub Actions によりリリースが自動化されています。バージョンタグを push すると、Linux / macOS 向けのスタンドアロンバイナリがビルドされ、GitHub Release に添付されます。

### 新しいリリースの作成手順

1. `pyproject.toml` と `slagent.py`（`@click.version_option`）のバージョンを更新
2. 変更をコミット
3. タグを作成して push:

```bash
git tag v0.1.0
git push origin v0.1.0
```

4. GitHub Actions が自動的に以下を実行:
   - Linux (amd64)、macOS (Intel)、macOS (Apple Silicon) 向けのスタンドアロンバイナリをビルド
   - バイナリと SHA256 チェックサムを添付した GitHub Release を作成
   - コミット履歴からリリースノートを自動生成

5. 完了後、[Releases](https://github.com/myfinder/slagent-cli/releases) ページからバイナリをダウンロードできます

### ビルドターゲット

| バイナリ | プラットフォーム |
|---------|----------------|
| `slagent-linux-amd64` | Linux x86_64 |
| `slagent-darwin-arm64` | macOS Apple Silicon |

## ライセンス

MIT
