#!/usr/bin/env python3
"""
browser_use.py — Browser Use Cloud CLI Wrapper

A comprehensive CLI for the Browser Use Cloud API.
Runs AI-powered browser automation tasks with stealth browsers,
structured data extraction, session management, and more.

Requires: pip install browser-use-sdk
Requires: BROWSER_USE_API_KEY environment variable

Usage:
    python browser_use.py run "Search for latest AI news on TechCrunch"
    python browser_use.py extract "Get top 5 HN posts" --schema '{"items": [{"title": "str", "url": "str", "points": "int"}]}'
    python browser_use.py session create --proxy us
    python browser_use.py billing
"""

import asyncio
import argparse
import json
import os
import sys
import traceback
from typing import Optional

import httpx

# ─── Ensure SDK is available ────────────────────────────────────────
try:
    from browser_use_sdk import AsyncBrowserUse, SessionSettings
except ImportError:
    print(
        json.dumps(
            {"error": "browser-use-sdk not installed. Run: pip install browser-use-sdk"}
        )
    )
    sys.exit(1)

DEFAULT_OUTPUT_DIR = "/a0/tmp/downloads/browser-use"


# ═══════════════════════════════════════════════════════════════════
# DYNAMIC PYDANTIC SCHEMA BUILDER
# ═══════════════════════════════════════════════════════════════════


def build_pydantic_model(schema_dict: dict, model_name: str = "DynamicModel"):
    """
    Build a Pydantic BaseModel from a simplified JSON schema dict.

    Schema format (simplified):
        {"field": "str"}                    -> simple string field
        {"field": "int"}                    -> simple int field
        {"field": "float"}                  -> simple float field
        {"field": "bool"}                   -> simple bool field
        {"items": [{"title": "str", ...}]}  -> list of objects
        {"field": "str?"}                   -> optional string field

    Also accepts full Pydantic-style JSON schema with "properties" and "type".
    """
    from pydantic import BaseModel, create_model
    from typing import List, Optional as Opt

    type_map = {
        "str": str,
        "string": str,
        "int": int,
        "integer": int,
        "float": float,
        "number": float,
        "bool": bool,
        "boolean": bool,
    }

    def resolve_field(key, value):
        """Resolve a single field definition to (type, default)."""
        if isinstance(value, str):
            optional = value.endswith("?")
            base = value.rstrip("?")
            py_type = type_map.get(base.lower(), str)
            if optional:
                return (Opt[py_type], None)
            return (py_type, ...)
        elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
            inner_model = build_pydantic_model(value[0], f"{key.title()}Item")
            return (List[inner_model], ...)
        elif isinstance(value, dict):
            nested = build_pydantic_model(value, f"{key.title()}Nested")
            return (nested, ...)
        else:
            return (str, ...)

    fields = {}
    for key, value in schema_dict.items():
        fields[key] = resolve_field(key, value)

    return create_model(model_name, **fields)


# ═══════════════════════════════════════════════════════════════════
# CORE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════


async def download_output_files(
    client, task_id: str, output_files: list, output_dir: str
) -> list:
    """
    Download output files from a completed task to local disk.

    Args:
        client: AsyncBrowserUse client instance
        task_id: The task ID (used for subfolder naming)
        output_files: List of file objects with .id and .file_name attributes
        output_dir: Base directory to save files into

    Returns:
        List of dicts with file_id, file_name, and saved_to for each downloaded file.
    """
    try:
        task_prefix = task_id[:8]
        save_dir = os.path.join(output_dir, task_prefix)
        os.makedirs(save_dir, exist_ok=True)

        downloaded = []
        for file in output_files:
            try:
                file_id = str(file.id)
                file_info = await client.files.task_output(task_id, file_id)
                file_name = (
                    file_info.file_name
                    if hasattr(file_info, "file_name") and file_info.file_name
                    else file_id
                )
                async with httpx.AsyncClient(follow_redirects=True) as http:
                    resp = await http.get(file_info.download_url)
                    resp.raise_for_status()
                save_path = os.path.join(save_dir, file_name)

                with open(save_path, "wb") as f:
                    f.write(resp.content)

                downloaded.append(
                    {
                        "file_id": file_id,
                        "file_name": file_name,
                        "saved_to": save_path,
                    }
                )
            except Exception as e:
                print(
                    f"Warning: Failed to download file {getattr(file, 'id', '?')}: {e}",
                    file=sys.stderr,
                )

        return downloaded
    except Exception as e:
        print(f"Warning: Failed to download output files: {e}", file=sys.stderr)
        return []


async def run_task(args):
    """
    Run a browser automation task and return text output.
    """
    client = AsyncBrowserUse()
    kwargs = {"flash_mode": args.flash}

    if args.model:
        kwargs["llm"] = args.model
    if args.start_url:
        kwargs["start_url"] = args.start_url
    if args.session_id:
        kwargs["session_id"] = args.session_id
    if args.allowed_domains:
        kwargs["allowed_domains"] = args.allowed_domains
    if args.system_prompt:
        kwargs["system_prompt_extension"] = args.system_prompt
    if args.max_steps:
        kwargs["max_steps"] = args.max_steps
    if args.thinking:
        kwargs["thinking"] = True
    if args.judge:
        kwargs["judge"] = True
    if args.proxy:
        kwargs["session_settings"] = SessionSettings(proxy_country_code=args.proxy)

    # Handle secrets
    if args.secrets:
        secrets = {}
        for s in args.secrets:
            parts = s.split("=", 1)
            if len(parts) == 2:
                secrets[parts[0]] = parts[1]
        if secrets:
            kwargs["secrets"] = secrets

    if args.stream:
        print(json.dumps({"status": "starting", "task": args.task}))
        steps = []
        async for step in client.run(args.task, **kwargs):
            step_info = {
                "step": step.number if hasattr(step, "number") else None,
                "goal": step.next_goal if hasattr(step, "next_goal") else None,
                "url": step.url if hasattr(step, "url") else None,
            }
            steps.append(step_info)
            print(json.dumps({"status": "step", **step_info}))
        # After streaming, we don't get a final result object easily
        print(json.dumps({"status": "finished", "total_steps": len(steps)}))
    else:
        result = await client.run(args.task, **kwargs)
        output = {
            "status": "finished",
            "task_id": str(result.id),
            "task_status": str(result.status),
            "steps": len(result.steps) if result.steps else 0,
            "output": result.output
            if isinstance(result.output, str)
            else str(result.output),
        }
        if result.output_files:
            output["output_files"] = [str(f) for f in result.output_files]
        print(json.dumps(output, indent=2, default=str))

        # Auto-download output files if present
        if result.output_files:
            output_dir = args.output_dir if args.output_dir else DEFAULT_OUTPUT_DIR
            downloaded = await download_output_files(
                client, str(result.id), result.output_files, output_dir
            )
            if downloaded:
                print(json.dumps({"downloaded_files": downloaded}, indent=2))


async def extract_data(args):
    """
    Run a task with structured data extraction using a JSON schema.
    """
    client = AsyncBrowserUse()

    # Parse schema
    try:
        schema_dict = json.loads(args.schema)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON schema: {e}"}))
        return

    OutputModel = build_pydantic_model(schema_dict, "ExtractedData")

    kwargs = {"output_schema": OutputModel, "flash_mode": args.flash}

    if args.model:
        kwargs["llm"] = args.model
    if args.start_url:
        kwargs["start_url"] = args.start_url
    if args.session_id:
        kwargs["session_id"] = args.session_id
    if args.proxy:
        kwargs["session_settings"] = SessionSettings(proxy_country_code=args.proxy)
    if args.max_steps:
        kwargs["max_steps"] = args.max_steps
    if args.allowed_domains:
        kwargs["allowed_domains"] = args.allowed_domains

    result = await client.run(args.task, **kwargs)

    output = {
        "status": "finished",
        "task_id": str(result.id),
        "task_status": str(result.status),
        "steps": len(result.steps) if result.steps else 0,
    }

    # Extract structured data
    if result.output:
        if hasattr(result.output, "model_dump"):
            output["data"] = result.output.model_dump()
        elif hasattr(result.output, "dict"):
            output["data"] = result.output.dict()
        else:
            output["data"] = str(result.output)
    else:
        output["data"] = None

    print(json.dumps(output, indent=2, default=str))

    # Auto-download output files if present
    if hasattr(result, "output_files") and result.output_files:
        output_dir = args.output_dir if args.output_dir else DEFAULT_OUTPUT_DIR
        downloaded = await download_output_files(
            client, str(result.id), result.output_files, output_dir
        )
        if downloaded:
            print(json.dumps({"downloaded_files": downloaded}, indent=2))


async def session_create(args):
    """Create a new browser session."""
    client = AsyncBrowserUse()
    kwargs = {}
    if args.proxy:
        kwargs["proxy_country_code"] = args.proxy
    if args.profile_id:
        kwargs["profile_id"] = args.profile_id

    session = await client.sessions.create(**kwargs)
    print(
        json.dumps(
            {
                "session_id": str(session.id),
                "live_url": str(session.live_url)
                if hasattr(session, "live_url") and session.live_url
                else None,
            },
            indent=2,
        )
    )


async def session_stop(args):
    """Stop a browser session."""
    client = AsyncBrowserUse()
    await client.sessions.stop(args.session_id)
    print(json.dumps({"status": "stopped", "session_id": args.session_id}))


async def session_delete(args):
    """Delete a browser session."""
    client = AsyncBrowserUse()
    await client.sessions.delete(args.session_id)
    print(json.dumps({"status": "deleted", "session_id": args.session_id}))


async def session_share(args):
    """Create a shareable link for a session."""
    client = AsyncBrowserUse()
    share = await client.sessions.create_share(args.session_id)
    print(json.dumps({"share_url": str(share)}, indent=2, default=str))


async def billing_info(args):
    """Get account billing information."""
    client = AsyncBrowserUse()
    billing = await client.billing.account()
    print(
        json.dumps(
            {
                "name": billing.name,
                "total_credits_usd": billing.total_credits_balance_usd,
                "monthly_credits_usd": billing.monthly_credits_balance_usd,
                "additional_credits_usd": billing.additional_credits_balance_usd,
                "rate_limit": billing.rate_limit,
                "plan": billing.plan_info.plan_name if billing.plan_info else "Unknown",
            },
            indent=2,
        )
    )


async def list_profiles(args):
    """List all browser profiles."""
    client = AsyncBrowserUse()
    profiles = await client.profiles.list()
    items = []
    if hasattr(profiles, "items"):
        for p in profiles.items:
            items.append(
                {
                    "id": str(p.id) if hasattr(p, "id") else None,
                    "name": str(p.name) if hasattr(p, "name") else None,
                }
            )
    print(
        json.dumps(
            {
                "profiles": items,
                "total": profiles.total_items
                if hasattr(profiles, "total_items")
                else len(items),
            },
            indent=2,
        )
    )


async def list_browsers(args):
    """List active browser sessions."""
    client = AsyncBrowserUse()
    browsers = await client.browsers.list()
    items = []
    if hasattr(browsers, "items"):
        for b in browsers.items:
            items.append({"id": str(b.id) if hasattr(b, "id") else None})
    print(
        json.dumps(
            {
                "browsers": items,
                "total": browsers.total_items
                if hasattr(browsers, "total_items")
                else len(items),
            },
            indent=2,
        )
    )


# ═══════════════════════════════════════════════════════════════════
# CLI ARGUMENT PARSER
# ═══════════════════════════════════════════════════════════════════


def build_parser():
    parser = argparse.ArgumentParser(
        description="Browser Use Cloud CLI — AI-powered browser automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # ── run ─────────────────────────────────────────────────────
    p_run = subparsers.add_parser("run", help="Run a browser task (text output)")
    p_run.add_argument("task", help="Natural language task description")
    p_run.add_argument(
        "--model",
        "-m",
        help="LLM model (e.g. browser-use-2.0, browser-use-llm, o3, gemini-flash-latest, claude-sonnet-4-6)",
    )
    p_run.add_argument(
        "--start-url", "-u", help="Starting URL (saves navigation steps)"
    )
    p_run.add_argument("--session-id", "-s", help="Reuse an existing session")
    p_run.add_argument("--proxy", "-p", help="Proxy country code (e.g. us, gb, de, jp)")
    p_run.add_argument(
        "--allowed-domains", nargs="+", help="Restrict navigation to these domains"
    )
    p_run.add_argument(
        "--secrets", nargs="+", help="Domain credentials as domain=user:pass"
    )
    p_run.add_argument("--system-prompt", help="Custom system prompt extension")
    p_run.add_argument("--max-steps", type=int, help="Maximum steps (default: 100)")
    p_run.add_argument(
        "--flash", action="store_true", help="Enable flash mode (faster, less careful)"
    )
    p_run.add_argument(
        "--thinking", action="store_true", help="Enable extended reasoning"
    )
    p_run.add_argument(
        "--judge", action="store_true", help="Enable quality judge verification"
    )
    p_run.add_argument(
        "--stream", action="store_true", help="Stream step-by-step output"
    )
    p_run.add_argument(
        "--output-dir",
        "-o",
        default=None,
        help="Directory to save output files (default: /a0/tmp/downloads/browser-use)",
    )

    # ── extract ─────────────────────────────────────────────────
    p_ext = subparsers.add_parser(
        "extract", help="Extract structured data from a website"
    )
    p_ext.add_argument("task", help="Natural language extraction task")
    p_ext.add_argument(
        "--schema", "-S", required=True, help="JSON schema for output structure"
    )
    p_ext.add_argument("--model", "-m", help="LLM model")
    p_ext.add_argument("--start-url", "-u", help="Starting URL")
    p_ext.add_argument("--session-id", "-s", help="Reuse an existing session")
    p_ext.add_argument("--proxy", "-p", help="Proxy country code")
    p_ext.add_argument(
        "--allowed-domains", nargs="+", help="Restrict navigation to these domains"
    )
    p_ext.add_argument("--max-steps", type=int, help="Maximum steps")
    p_ext.add_argument("--flash", action="store_true", help="Flash mode")
    p_ext.add_argument(
        "--output-dir",
        "-o",
        default=None,
        help="Directory to save output files (default: /a0/tmp/downloads/browser-use)",
    )

    # ── session ─────────────────────────────────────────────────
    p_sess = subparsers.add_parser("session", help="Session management")
    sess_sub = p_sess.add_subparsers(dest="session_command")

    p_sc = sess_sub.add_parser("create", help="Create a new session")
    p_sc.add_argument("--proxy", "-p", help="Proxy country code")
    p_sc.add_argument("--profile-id", help="Browser profile ID")

    p_ss = sess_sub.add_parser("stop", help="Stop a session")
    p_ss.add_argument("session_id", help="Session ID to stop")

    p_sd = sess_sub.add_parser("delete", help="Delete a session")
    p_sd.add_argument("session_id", help="Session ID to delete")

    p_sh = sess_sub.add_parser("share", help="Create shareable link")
    p_sh.add_argument("session_id", help="Session ID to share")

    # ── billing ─────────────────────────────────────────────────
    subparsers.add_parser("billing", help="Show account billing info")

    # ── profiles ────────────────────────────────────────────────
    subparsers.add_parser("profiles", help="List browser profiles")

    # ── browsers ────────────────────────────────────────────────
    subparsers.add_parser("browsers", help="List active browser sessions")

    return parser


# ═══════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════


async def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if not os.environ.get("BROWSER_USE_API_KEY"):
        print(json.dumps({"error": "BROWSER_USE_API_KEY environment variable not set"}))
        sys.exit(1)

    try:
        if args.command == "run":
            await run_task(args)
        elif args.command == "extract":
            await extract_data(args)
        elif args.command == "session":
            if args.session_command == "create":
                await session_create(args)
            elif args.session_command == "stop":
                await session_stop(args)
            elif args.session_command == "delete":
                await session_delete(args)
            elif args.session_command == "share":
                await session_share(args)
            else:
                print(
                    json.dumps(
                        {
                            "error": "Unknown session command. Use: create, stop, delete, share"
                        }
                    )
                )
        elif args.command == "billing":
            await billing_info(args)
        elif args.command == "profiles":
            await list_profiles(args)
        elif args.command == "browsers":
            await list_browsers(args)
        else:
            parser.print_help()
    except Exception as e:
        print(json.dumps({"error": str(e), "traceback": traceback.format_exc()}))
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
