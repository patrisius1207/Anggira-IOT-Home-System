"""
google_auth.py — Jalankan SEKALI untuk login Google Calendar.
Setelah login, token disimpan di google_token.json dan auto-refresh oleh anggira.py.

Cara pakai:
1. Buka https://console.cloud.google.com
2. Buat project baru (atau pakai yang ada)
3. Enable Google Calendar API
4. Buat OAuth 2.0 Client ID → pilih "Desktop App"
5. Download credentials → salin client_id dan client_secret
6. Set environment variable:
   export GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
   export GOOGLE_CLIENT_SECRET="your-client-secret"
   (atau isi langsung di bawah untuk testing)
7. Jalankan: python google_auth.py
8. Buka URL yang muncul di browser, login, copy kode
9. Paste kode ke terminal
"""

import urllib.request
import urllib.parse
import json
import os
from datetime import datetime, timedelta, timezone

# Isi langsung jika tidak pakai env variable
CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
TOKEN_FILE = os.environ.get('GOOGLE_TOKEN_FILE', 'google_token.json')

# Scope yang dibutuhkan
SCOPES = "https://www.googleapis.com/auth/calendar"

def get_auth_url():
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
        'response_type': 'code',
        'scope': SCOPES,
        'access_type': 'offline',
        'prompt': 'consent'  # Paksa dapat refresh_token
    }
    url = "https://accounts.google.com/o/oauth2/auth?" + urllib.parse.urlencode(params)
    return url

def exchange_code_for_token(auth_code):
    data = urllib.parse.urlencode({
        'code': auth_code.strip(),
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
        'grant_type': 'authorization_code'
    }).encode()

    req = urllib.request.Request(
        'https://oauth2.googleapis.com/token',
        data=data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )

    with urllib.request.urlopen(req, timeout=15) as r:
        token_data = json.loads(r.read().decode())

    # Tambahkan expiry timestamp
    expires_in = token_data.get('expires_in', 3600)
    token_data['token_expiry'] = (
        datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    ).isoformat()

    return token_data

def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("❌ GOOGLE_CLIENT_ID dan GOOGLE_CLIENT_SECRET belum diset!")
        print("Set env variable atau edit file ini langsung.")
        return

    print("=" * 60)
    print("🔐 Google Calendar OAuth2 Login")
    print("=" * 60)
    print()
    print("1. Buka URL berikut di browser:")
    print()
    print(get_auth_url())
    print()
    print("2. Login dengan akun Google kamu")
    print("3. Izinkan akses Calendar")
    print("4. Copy kode yang muncul")
    print()

    auth_code = input("Paste kode di sini: ").strip()

    print("\nMengambil token...")
    token_data = exchange_code_for_token(auth_code)

    if 'access_token' not in token_data:
        print(f"❌ Gagal dapat token: {token_data}")
        return

    if 'refresh_token' not in token_data:
        print("⚠️  Tidak dapat refresh_token! Coba hapus akses app di Google Account lalu ulangi.")
        return

    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_data, f, indent=2)

    print(f"✅ Token berhasil disimpan ke '{TOKEN_FILE}'")
    print("Sekarang anggira.py bisa akses Google Calendar kamu!")
    print()

    # Test akses
    print("Testing akses ke Calendar...")
    try:
        access_token = token_data['access_token']
        req = urllib.request.Request(
            "https://www.googleapis.com/calendar/v3/users/me/calendarList?maxResults=5",
            headers={'Authorization': f'Bearer {access_token}'}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            result = json.loads(r.read().decode())

        calendars = result.get('items', [])
        print(f"✅ Berhasil! Ditemukan {len(calendars)} kalender:")
        for cal in calendars:
            print(f"   - {cal.get('summary', '?')} ({cal.get('id', '?')})")
    except Exception as e:
        print(f"❌ Test gagal: {e}")

if __name__ == "__main__":
    main()