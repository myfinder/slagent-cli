#!/usr/bin/env python3
"""slagent - Slack CLI tool using Web API with User Token."""

import os
import sys
import time

import click
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def get_client():
    token = os.environ.get("SLACK_USER_TOKEN")
    if not token:
        click.echo("Error: SLACK_USER_TOKEN environment variable is not set.", err=True)
        sys.exit(1)
    return WebClient(token=token)


def resolve_channel(client, channel_name):
    """Resolve channel name or ID to channel ID."""
    if channel_name.startswith("C") and len(channel_name) >= 9:
        return channel_name
    name = channel_name.lstrip("#")
    cursor = None
    while True:
        resp = client.conversations_list(
            types="public_channel,private_channel",
            limit=200,
            cursor=cursor,
        )
        for ch in resp["channels"]:
            if ch["name"] == name:
                return ch["id"]
        cursor = resp.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break
    click.echo(f"Error: channel '{channel_name}' not found.", err=True)
    sys.exit(1)


def format_ts(ts):
    """Format Slack timestamp to human-readable."""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(ts)))


def get_permalink(client, channel, ts):
    try:
        resp = client.chat_getPermalink(channel=channel, message_ts=ts)
        return resp["permalink"]
    except SlackApiError:
        return None


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """slagent - Slack CLI powered by Web API."""
    pass


# ---------- search ----------

@cli.command()
@click.argument("query")
@click.option("-n", "--count", default=10, help="Number of results (default: 10)")
@click.option("--sort", type=click.Choice(["score", "timestamp"]), default="timestamp")
def search(query, count, sort):
    """Search messages in Slack."""
    client = get_client()
    try:
        resp = client.search_messages(query=query, count=count, sort=sort)
    except SlackApiError as e:
        click.echo(f"Error: {e.response['error']}", err=True)
        sys.exit(1)

    matches = resp["messages"]["matches"]
    if not matches:
        click.echo("No results found.")
        return

    click.echo(f"Found {resp['messages']['total']} results (showing {len(matches)}):\n")
    for m in matches:
        channel_name = m.get("channel", {}).get("name", "?")
        user = m.get("username", m.get("user", "?"))
        ts = format_ts(m["ts"])
        text = m.get("text", "")
        permalink = m.get("permalink", "")
        click.echo(f"#{channel_name}  {user}  {ts}")
        click.echo(f"  {text[:200]}")
        if permalink:
            click.echo(f"  {permalink}")
        click.echo()


# ---------- mentions ----------

@cli.command()
@click.option("-n", "--count", default=10, help="Number of results (default: 10)")
def mentions(count):
    """Show recent threads where you are mentioned."""
    client = get_client()
    try:
        auth = client.auth_test()
        user_id = auth["user_id"]
    except SlackApiError as e:
        click.echo(f"Error: {e.response['error']}", err=True)
        sys.exit(1)

    query = f"<@{user_id}>"
    try:
        resp = client.search_messages(query=query, count=count, sort="timestamp")
    except SlackApiError as e:
        click.echo(f"Error: {e.response['error']}", err=True)
        sys.exit(1)

    matches = resp["messages"]["matches"]
    if not matches:
        click.echo("No recent mentions found.")
        return

    click.echo(f"Recent mentions ({len(matches)}):\n")
    for m in matches:
        channel_name = m.get("channel", {}).get("name", "?")
        user = m.get("username", m.get("user", "?"))
        ts = format_ts(m["ts"])
        text = m.get("text", "")
        permalink = m.get("permalink", "")
        click.echo(f"#{channel_name}  {user}  {ts}")
        click.echo(f"  {text[:200]}")
        if permalink:
            click.echo(f"  {permalink}")
        click.echo()


# ---------- post ----------

@cli.command()
@click.argument("channel")
@click.argument("text")
@click.option("--thread-ts", default=None, help="Thread timestamp to reply to")
def post(channel, text, thread_ts):
    """Post a message to a channel. CHANNEL can be #name or channel ID."""
    client = get_client()
    channel_id = resolve_channel(client, channel)
    kwargs = {"channel": channel_id, "text": text}
    if thread_ts:
        kwargs["thread_ts"] = thread_ts
    try:
        resp = client.chat_postMessage(**kwargs)
        click.echo(f"Posted to #{channel} (ts: {resp['ts']})")
    except SlackApiError as e:
        click.echo(f"Error: {e.response['error']}", err=True)
        sys.exit(1)


# ---------- thread ----------

@cli.command()
@click.argument("channel")
@click.argument("thread_ts")
@click.option("-n", "--count", default=50, help="Max replies to fetch (default: 50)")
def thread(channel, thread_ts, count):
    """Read a thread by channel and thread timestamp."""
    client = get_client()
    channel_id = resolve_channel(client, channel)
    try:
        resp = client.conversations_replies(
            channel=channel_id, ts=thread_ts, limit=count
        )
    except SlackApiError as e:
        click.echo(f"Error: {e.response['error']}", err=True)
        sys.exit(1)

    messages = resp["messages"]
    if not messages:
        click.echo("No messages found in thread.")
        return

    click.echo(f"Thread ({len(messages)} messages):\n")
    for m in messages:
        user = m.get("user", "?")
        ts = format_ts(m["ts"])
        text = m.get("text", "")
        click.echo(f"  {user}  {ts}")
        click.echo(f"    {text[:300]}")
        click.echo()


# ---------- channels ----------

@cli.command()
@click.option("--all", "show_all", is_flag=True, help="Include archived channels")
def channels(show_all):
    """List channels you belong to."""
    client = get_client()
    results = []
    cursor = None
    while True:
        try:
            resp = client.users_conversations(
                types="public_channel,private_channel",
                exclude_archived=not show_all,
                limit=200,
                cursor=cursor,
            )
        except SlackApiError as e:
            click.echo(f"Error: {e.response['error']}", err=True)
            sys.exit(1)
        results.extend(resp["channels"])
        cursor = resp.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break

    results.sort(key=lambda c: c["name"])
    for ch in results:
        prefix = "[archived] " if ch.get("is_archived") else ""
        private = "[private] " if ch.get("is_private") else ""
        click.echo(f"  {prefix}{private}#{ch['name']}  ({ch['id']})")
    click.echo(f"\nTotal: {len(results)} channels")


# ---------- history ----------

@cli.command()
@click.argument("channel")
@click.option("-n", "--count", default=20, help="Number of messages (default: 20)")
def history(channel, count):
    """Show recent messages in a channel."""
    client = get_client()
    channel_id = resolve_channel(client, channel)
    try:
        resp = client.conversations_history(channel=channel_id, limit=count)
    except SlackApiError as e:
        click.echo(f"Error: {e.response['error']}", err=True)
        sys.exit(1)

    messages = resp["messages"]
    if not messages:
        click.echo("No messages found.")
        return

    messages.reverse()
    for m in messages:
        user = m.get("user", "?")
        ts = format_ts(m["ts"])
        text = m.get("text", "")
        thread_count = m.get("reply_count", 0)
        thread_info = f" [{thread_count} replies]" if thread_count else ""
        click.echo(f"  {user}  {ts}{thread_info}")
        click.echo(f"    {text[:300]}")
        click.echo()


if __name__ == "__main__":
    cli()
