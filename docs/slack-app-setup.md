# Slack App Setup

[日本語版](slack-app-setup_ja.md)

## 1. Create the App

Go to https://api.slack.com/apps and click "Create New App" → "From scratch".

## 2. Configure Bot Token Scopes

"OAuth & Permissions" → "Bot Token Scopes" → add the following:

| Scope | Purpose |
|---|---|
| `app_mentions:read` | Receive mentions |
| `chat:write` | Send messages |
| `channels:history` | Read public channel history |
| `groups:history` | Required for private channels (optional) |

## 3. Enable Socket Mode

"Socket Mode" → Enable Socket Mode → generate an App-Level Token.

- Token Name: any (e.g. `socket-token`)
- Scope: `connections:write`
- Save the generated `xapp-...` token

## 4. Configure Event Subscriptions

"Event Subscriptions" → Enable Events → "Subscribe to bot events" → add `app_mention`.

## 5. Install to Workspace

"OAuth & Permissions" → "Install to Workspace".  
Save the generated Bot User OAuth Token (`xoxb-...`).

---

## Token Types — Common Source of Confusion

This library uses exactly two tokens:

| Environment variable | Prefix | Where to find it |
|---|---|---|
| `SLACK_BOT_TOKEN` | `xoxb-...` | "OAuth & Permissions" → "Bot User OAuth Token" |
| `SLACK_APP_TOKEN` | `xapp-...` | "Basic Information" → "App-Level Tokens" |

### If you see `xoxe.xoxp-...`

That is a User Token with Token Rotation enabled — not the Bot Token. The Bot Token is on a separate row of the same page.  
If Token Rotation is not needed, disable it under "OAuth & Permissions" → "Advanced". It is unnecessary for personal use.
