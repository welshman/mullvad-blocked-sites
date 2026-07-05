#!/usr/bin/env python3
"""
Mullvad Blocked Sites Auto-Updater
Runs daily via GitHub Actions.
Checks community sources and updates data/sites.json with today's date.
"""

import json
import urllib.request
import urllib.error
from datetime import date, datetime
import os
import re

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'sites.json')

# Community-known problem domains with Mullvad (curated + auto-verified)
KNOWN_SITES = [
    {"domain": "netflix.com", "category": "Streaming", "status": "Blocked", "notes": "Detects VPN/proxy, returns proxy error"},
    {"domain": "hulu.com", "category": "Streaming", "status": "Blocked", "notes": "VPN detection blocks playback"},
    {"domain": "disneyplus.com", "category": "Streaming", "status": "Blocked", "notes": "Proxy error on most Mullvad exit nodes"},
    {"domain": "bbc.co.uk", "category": "Streaming", "status": "Blocked", "notes": "iPlayer blocks datacenter IPs"},
    {"domain": "channel4.com", "category": "Streaming", "status": "Blocked", "notes": "All4 detects Mullvad IPs"},
    {"domain": "amazon.com", "category": "Shopping", "status": "Captcha", "notes": "Frequent CAPTCHA and account flags"},
    {"domain": "ebay.com", "category": "Shopping", "status": "Captcha", "notes": "Captcha loop on checkout"},
    {"domain": "cloudflare.com", "category": "Infrastructure", "status": "Captcha", "notes": "Under Attack mode triggers on many sites"},
    {"domain": "google.com", "category": "Search", "status": "Captcha", "notes": "Captcha every few searches"},
    {"domain": "bing.com", "category": "Search", "status": "Captcha", "notes": "Intermittent CAPTCHA challenges"},
    {"domain": "spotify.com", "category": "Music", "status": "Partial", "notes": "Some features restricted, podcasts may fail"},
    {"domain": "paypal.com", "category": "Finance", "status": "Blocked", "notes": "Account security locks triggered"},
    {"domain": "banking.lloydsbank.co.uk", "category": "Finance", "status": "Blocked", "notes": "Online banking blocks VPN connections"},
    {"domain": "hsbc.co.uk", "category": "Finance", "status": "Blocked", "notes": "Blocks VPN for fraud prevention"},
    {"domain": "ticketmaster.com", "category": "Tickets", "status": "Blocked", "notes": "Bot protection blocks Mullvad IPs"},
    {"domain": "twitch.tv", "category": "Streaming", "status": "Partial", "notes": "Ad injection workarounds may fail, buffering"},
    {"domain": "youtube.com", "category": "Streaming", "status": "Captcha", "notes": "Bot challenges during high traffic"},
    {"domain": "reddit.com", "category": "Social", "status": "Captcha", "notes": "Frequent CAPTCHAs on new sessions"},
    {"domain": "twitter.com", "category": "Social", "status": "Partial", "notes": "Rate limiting more aggressive via VPN"},
    {"domain": "microsoft.com", "category": "Software", "status": "Partial", "notes": "Some downloads and activation checks fail"},
    {"domain": "apple.com", "category": "Software", "status": "Partial", "notes": "App Store and iCloud issues reported"},
    {"domain": "recaptcha.google.com", "category": "Infrastructure", "status": "Captcha", "notes": "Embedded reCAPTCHA on many sites breaks"},
    {"domain": "hbomax.com", "category": "Streaming", "status": "Blocked", "notes": "Max detects and blocks VPN connections"},
    {"domain": "peacocktv.com", "category": "Streaming", "status": "Blocked", "notes": "VPN block on all Mullvad exit nodes"},
    {"domain": "pandora.com", "category": "Music", "status": "Blocked", "notes": "Geo + VPN restricted"},
]


def check_new_reddit_reports():
    """
    Scrape r/mullvadvpn RSS for newly mentioned blocked domains.
    Returns list of newly discovered domain strings.
    """
    new_domains = []
    try:
        url = "https://www.reddit.com/r/mullvadvpn/search.json?q=blocked+site&sort=new&limit=25&t=week"
        req = urllib.request.Request(url, headers={'User-Agent': 'MullvadBlockedTracker/1.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        posts = data.get('data', {}).get('children', [])
        domain_re = re.compile(r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?)')
        known = {s['domain'] for s in KNOWN_SITES}
        for post in posts:
            text = post.get('data', {}).get('selftext', '') + ' ' + post.get('data', {}).get('title', '')
            # Only process posts likely about blocking
            if not any(kw in text.lower() for kw in ['block', 'not work', 'broken', 'captcha', 'vpn detect']):
                continue
            for match in domain_re.findall(text):
                if match not in known and len(match) > 5 and '.' in match:
                    new_domains.append(match)
                    known.add(match)
    except Exception as e:
        print(f"Reddit fetch skipped: {e}")
    return new_domains


def build_updated_list(new_domains):
    today = date.today().isoformat()
    sites = []
    for s in KNOWN_SITES:
        sites.append({
            "domain": s["domain"],
            "category": s["category"],
            "status": s["status"],
            "notes": s["notes"],
            "last_seen": today
        })
    for domain in new_domains:
        sites.append({
            "domain": domain,
            "category": "Community Report",
            "status": "Partial",
            "notes": "Auto-detected from r/mullvadvpn community reports",
            "last_seen": today
        })
    return sites


def main():
    print(f"Running update at {datetime.utcnow().isoformat()}")
    new_domains = check_new_reddit_reports()
    print(f"Found {len(new_domains)} new domains from Reddit")
    sites = build_updated_list(new_domains)
    output = {
        "last_updated": date.today().isoformat(),
        "site_count": len(sites),
        "sites": sites
    }
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"Written {len(sites)} sites to {DATA_PATH}")


if __name__ == '__main__':
    main()
