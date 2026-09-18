from __future__ import annotations

import json
import math
import os
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path


USER = "subean-choi"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "activity-lotus.svg"
COLORS = ["#E9D4D8", "#D8A7B1", "#F5F0E8"]


def fetch_events() -> list[dict]:
    token = os.environ.get("GITHUB_TOKEN")
    request = urllib.request.Request(
        f"https://api.github.com/users/{USER}/events/public?per_page=100",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "subean-choi-profile-activity",
        },
    )
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def counts_by_day(events: list[dict], days: int = 21) -> list[tuple[datetime, int]]:
    now = datetime.now(timezone.utc)
    floor = now.date() - timedelta(days=days - 1)
    counter: Counter[str] = Counter()
    for event in events:
        created_at = event.get("created_at")
        if not created_at:
            continue
        day = datetime.fromisoformat(created_at.replace("Z", "+00:00")).date()
        if day >= floor:
            counter[day.isoformat()] += 1
    return [
        (datetime.combine(floor + timedelta(days=i), datetime.min.time()), counter[(floor + timedelta(days=i)).isoformat()])
        for i in range(days)
    ]


def lotus_dot(x: float, y: float, count: int, index: int) -> str:
    radius = 7 + min(count, 8) * 2.1
    color = COLORS[index % len(COLORS)]
    opacity = 0.42 + min(count, 6) * 0.09
    petals = []
    if count:
        for petal in range(min(count, 6)):
            angle = (math.tau / max(min(count, 6), 1)) * petal
            px = x + math.cos(angle) * (radius + 6)
            py = y + math.sin(angle) * (radius + 6)
            petals.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{radius * .42:.1f}" ry="{radius * .18:.1f}" fill="{color}" opacity=".28" transform="rotate({math.degrees(angle):.1f} {px:.1f} {py:.1f})"/>')
    return "\n    ".join(
        [
            *petals,
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.1f}" fill="{color}" opacity="{opacity:.2f}"/>',
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{max(radius - 6, 3):.1f}" fill="#0D0D0D" opacity=".18"/>',
        ]
    )


def render(rows: list[tuple[datetime, int]]) -> str:
    max_count = max((count for _, count in rows), default=0)
    total = sum(count for _, count in rows)
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    dots = []
    labels = []
    wave = []
    for idx, (day, count) in enumerate(rows):
        x = 82 + idx * 51.5
        y = 148 - (0 if max_count == 0 else (count / max_count) * 44)
        dots.append(lotus_dot(x, y, count, idx))
        wave.append(f"{x:.1f},{y + 58:.1f}")
        if idx % 5 == 0 or idx == len(rows) - 1:
            labels.append(f'<text x="{x:.1f}" y="224" text-anchor="middle" fill="#F5F0E8" opacity=".54" font-size="11">{day.strftime("%m/%d")}</text>')

    return f'''<svg width="1200" height="260" viewBox="0 0 1200 260" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc">
  <title id="title">Activity rhythm</title>
  <desc id="desc">Custom lotus and wave view of recent public GitHub activity for {USER}.</desc>
  <rect width="1200" height="260" rx="8" fill="#0D0D0D"/>
  <text x="52" y="58" fill="#F5F0E8" font-family="Inter, Arial, sans-serif" font-size="22" font-weight="800" letter-spacing="4">ACTIVITY RHYTHM</text>
  <text x="52" y="88" fill="#D8A7B1" font-family="Inter, Arial, sans-serif" font-size="14" letter-spacing="2">public events: {total} / refreshed {updated}</text>
  <path d="M64 190 C 188 150, 260 230, 384 190 S 580 150, 704 190 S 900 230, 1136 184" stroke="#2A2023" stroke-width="18" stroke-linecap="round"/>
  <polyline points="{' '.join(wave)}" stroke="#E9D4D8" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" opacity=".74"/>
  <g font-family="Inter, Arial, sans-serif">
    {' '.join(dots)}
    {' '.join(labels)}
  </g>
  <text x="52" y="244" fill="#F5F0E8" opacity=".64" font-family="Inter, Arial, sans-serif" font-size="13" letter-spacing="2">bugs: being observed / karma: clean / one commit closer.</text>
</svg>
'''


def main() -> None:
    events = fetch_events()
    OUT.write_text(render(counts_by_day(events)), encoding="utf-8")


if __name__ == "__main__":
    main()
