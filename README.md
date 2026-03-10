# slagent

A command-line tool for Slack using the Web API with a User Token.

Search messages, check mentions, post to channels, read threads, and more — all from your terminal.

[日本語版 README](README_ja.md)

## Installation

### Download pre-built binary (recommended)

Download the latest binary from the [Releases](https://github.com/myfinder/slagent-cli/releases) page.

| Platform | File |
|----------|------|
| Linux (x86_64) | `slagent-linux-amd64` |
| macOS (Intel) | `slagent-darwin-amd64` |
| macOS (Apple Silicon) | `slagent-darwin-arm64` |

```bash
# Example: macOS Apple Silicon
curl -LO https://github.com/myfinder/slagent-cli/releases/latest/download/slagent-darwin-arm64
chmod +x slagent-darwin-arm64
mv slagent-darwin-arm64 /usr/local/bin/slagent
```

### Install from source

```bash
git clone https://github.com/myfinder/slagent-cli.git
cd slagent-cli
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Setup

### 1. Create a Slack App

1. Go to [Slack API: Your Apps](https://api.slack.com/apps) and create a new app
2. Under **OAuth & Permissions**, add the following **User Token Scopes**:
   - `search:read` — Search messages
   - `chat:write` — Post messages
   - `channels:read` — List public channels
   - `groups:read` — List private channels
   - `channels:history` — Read public channel history
   - `groups:history` — Read private channel history
3. Install the app to your workspace
4. Copy the **User OAuth Token** (`xoxp-...`)

### 2. Set the environment variable

```bash
export SLACK_USER_TOKEN=xoxp-your-token-here
```

## Usage

```
slagent [COMMAND] [OPTIONS]
```

### Commands

#### search — Search messages

```bash
slagent search "deployment error"
slagent search "meeting notes" -n 5
slagent search "bug report" --sort score
```

| Option | Description |
|--------|-------------|
| `-n, --count` | Number of results (default: 10) |
| `--sort` | Sort by `score` or `timestamp` (default: `timestamp`) |

#### mentions — Show recent mentions

```bash
slagent mentions
slagent mentions -n 20
```

| Option | Description |
|--------|-------------|
| `-n, --count` | Number of results (default: 10) |

#### post — Post a message

```bash
slagent post "#general" "Hello from slagent!"
slagent post C01ABCD2EFG "Thread reply" --thread-ts 1234567890.123456
```

| Option | Description |
|--------|-------------|
| `--thread-ts` | Thread timestamp to reply to |

Channel can be specified as `#channel-name` or a channel ID.

#### thread — Read a thread

```bash
slagent thread "#general" 1234567890.123456
slagent thread C01ABCD2EFG 1234567890.123456 -n 100
```

| Option | Description |
|--------|-------------|
| `-n, --count` | Max replies to fetch (default: 50) |

#### history — Show recent messages in a channel

```bash
slagent history "#general"
slagent history "#random" -n 50
```

| Option | Description |
|--------|-------------|
| `-n, --count` | Number of messages (default: 20) |

#### channels — List channels you belong to

```bash
slagent channels
slagent channels --all
```

| Option | Description |
|--------|-------------|
| `--all` | Include archived channels |

## License

MIT
