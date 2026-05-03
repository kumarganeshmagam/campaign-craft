import asyncio
from typing import Dict, Any


async def run_agent(input_data: Dict[str, Any], queue=None) -> Dict[str, Any]:
    """Format combined campaign data into a human-readable structure.

    Accepts keys like `plan`, `usecases`, `contacts`, `content` and returns
    a dict with `formatted_text` (markdown/plain) and `sections` for structured
    consumption by the frontend.
    """
    if queue:
        await queue.put({"type": "progress", "agent": "StrategyFormatterAgent", "message": "Formatting campaign data..."})

    # small delay to simulate work
    await asyncio.sleep(0.15)

    plan = input_data.get("plan") or {}
    usecases = input_data.get("usecases") or {}
    contacts = input_data.get("contacts") or {}
    content = input_data.get("content") or {}

    # Build a readable markdown-style summary
    title = plan.get("overview") or f"Campaign"
    md_lines = [f"# {title}", ""]

    # Plan section
    if plan:
        md_lines.append("## Plan Overview")
        if plan.get("timeline"):
            md_lines.append("### Timeline")
            for t in plan.get("timeline", []):
                md_lines.append(f"- Week {t.get('week')}: {', '.join(t.get('activities', []))}")
        if plan.get("channels"):
            md_lines.append("")
            md_lines.append("**Channels:** " + ", ".join(plan.get("channels", [])))
        md_lines.append("")

    # Use cases
    uc_list = usecases.get("use_cases") if isinstance(usecases, dict) else None
    if uc_list:
        md_lines.append("## Use Cases")
        for uc in uc_list:
            md_lines.append(f"- **{uc.get('title')}** — {uc.get('summary')} (Value: {uc.get('value_prop')})")
        md_lines.append("")

    # Contacts
    contacts_list = contacts.get("contacts") if isinstance(contacts, dict) else None
    if contacts_list:
        md_lines.append("## Target Contacts")
        for c in contacts_list:
            md_lines.append(f"- {c.get('name')} — {c.get('role')} @ {c.get('company')} — {c.get('contact_link')}")
        md_lines.append("")

    # Content
    if content:
        md_lines.append("## Generated Content")
        # emails
        emails = content.get("emails") if isinstance(content, dict) else None
        if emails:
            md_lines.append("### Emails")
            for e in emails:
                md_lines.append(f"- To: {e.get('to')} | Subject: {e.get('subject')}")
                md_lines.append("```")
                md_lines.append(e.get('body') or "")
                md_lines.append("```")
        dms = content.get("dms") if isinstance(content, dict) else None
        if dms:
            md_lines.append("")
            md_lines.append("### DMs")
            for d in dms:
                md_lines.append(f"- {d}")
        md_lines.append("")

    md_text = "\n".join(md_lines)

    formatted = {
        "formatted_text": md_text,
        "sections": {
            "plan": plan,
            "usecases": usecases,
            "contacts": contacts,
            "content": content,
        }
    }

    if queue:
        await queue.put({"type": "progress", "agent": "StrategyFormatterAgent", "message": "Formatting complete."})

    return formatted
