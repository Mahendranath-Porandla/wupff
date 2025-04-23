import typer
import os
import random
import time
import smtplib
import sqlite3
import tweepy
import requests

from datetime import datetime
from dotenv import load_dotenv
from art import text2art, tprint # For ASCII art
from pyfiglet import Figlet # For specific font rendering
from email.mime.text import MIMEText # For email formatting
from twilio.rest import Client # For Twilio SMS API
from twilio.base.exceptions import TwilioRestException # For Twilio errors
from tweepy.errors import TweepyException # For Tweepy/X errors

# Load environment variables from .env file
load_dotenv()

# --- Constants ---
DB_FILE = "wupff_log.db" # Changed filename

# --- Character Mode Data ---
SCHRUTE_FACTS = [
    "FACT: Bears eat beets.",
    "FACT: Identity theft is not a joke, Jim! Millions of families suffer every year!",
    "WARNING: Failure to comply may necessitate a full shunning.",
    "REMINDER: The F&B committee has dibs on the good donuts.",
    "FACT: Tardiness is a gateway to anarchy.",
    "FACT: Schrute Farms approves punctuality."
]
KELLY_COMMENTS = [
    "OMG, like, you HAVE to see this!",
    "This is, like, the most important thing EVER.",
    "Seriously, stop whatever you're doing and look at this. TTYL! xoxo",
    "Is Ryan gonna see this? Hi Ryan!",
]
MICHAEL_QUOTES = [
    "That's what she said!",
    "I declare BANKRUPTCY!",
    "Where are the TURTLES?!",
    "I'm not superstitious, but I am a little stitious.",
    "Bears. Beets. Battlestar Galactica.",
]

# --- Database Functions ---
def setup_database():
    """Creates the log database and table if they don't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wupff_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            message TEXT,
            target TEXT,
            mode TEXT,
            email_status TEXT,
            sms_status TEXT,
            x_status TEXT,
            terminal_status TEXT,
            print_status TEXT,
            telegram_status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_wupff_activity(timestamp, message, target, mode, results):
    """Logs the details of a sent WUPFF to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO wupff_log (timestamp, message, target, mode,
                                email_status, sms_status, x_status,
                                terminal_status, print_status, telegram_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp,
            message,
            target,
            mode.capitalize(),
            'Success' if results.get('email') else 'Fail/Skip',
            'Success' if results.get('sms') else 'Fail/Skip',
            'Success' if results.get('x_post') else 'Fail/Skip',
            'Success' if results.get('terminal') else 'Fail/Skip',
            'Success' if results.get('printout') else 'Fail/Skip',
            'Success' if results.get('telegram') else 'Fail/Skip'
        ))
        conn.commit()
        print("[LOG] WUPFF! activity recorded in database.")
    except Exception as e:
        print(f"[LOG] Failed to write to database: {e}")
    finally:
        conn.close()

# --- Channel Sending Functions ---
def send_email(target, subject, body, config):
    """Sends an email using SMTP credentials from config."""
    sender = config.get("EMAIL_SENDER_ADDRESS")
    password = config.get("EMAIL_SENDER_PASSWORD")
    host = config.get("EMAIL_HOST", "smtp.gmail.com")
    port = config.get("EMAIL_PORT", 587)

    if not sender or not password or not target:
        print("[EMAIL] Skipped: Missing sender credentials or target address.")
        return False

    print(f"[EMAIL] Attempting to send to {target} via {host}...")
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = target

    try:
        port_int = int(port)
        with smtplib.SMTP(host, port_int) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, target, msg.as_string())
        print(f"[EMAIL] Successfully sent to {target}")
        return True
    except smtplib.SMTPAuthenticationError:
        print("[EMAIL] Failed: Authentication error. Check email/password in .env (Use App Password for Gmail).")
        return False
    except Exception as e:
        print(f"[EMAIL] Failed to send: {e}")
        return False

def send_sms(target, message, config):
    """Sends an SMS using Twilio credentials from config."""
    account_sid = config.get("TWILIO_ACCOUNT_SID")
    auth_token = config.get("TWILIO_AUTH_TOKEN")
    twilio_number = config.get("TWILIO_PHONE_NUMBER")

    if not account_sid or not auth_token or not twilio_number or not target:
        print("[SMS] Skipped: Missing Twilio credentials or target number.")
        return False

    print(f"[SMS] Attempting to send to {target} via Twilio...")
    client = Client(account_sid, auth_token)
    try:
        message_body = f"{message} 🐶 - WUPFF" # Changed signature
        sms = client.messages.create(
            body=message_body,
            from_=twilio_number,
            to=target
        )
        print(f"[SMS] Successfully sent to {target} (SID: {sms.sid})")
        return True
    except TwilioRestException as e:
        print(f"[SMS] Failed: Twilio error - {e}") 
        return False
    except Exception as e:
        print(f"[SMS] Failed to send: {e}")
        return False

def send_telegram(target_chat_id, message, config):
    """Sends a message via the Telegram Bot API."""
    bot_token = config.get("TELEGRAM_BOT_TOKEN")

    if not bot_token or not target_chat_id:
        print("[TELEGRAM] Skipped: Missing Telegram Bot Token or Target Chat ID.")
        return False

    api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': target_chat_id,
        'text': f"🐶 WUPFF Alert! 🐶\n--------------------\n{message}",
    }

    print(f"[TELEGRAM] Attempting to send to Chat ID {target_chat_id}...")
    try:
        response = requests.post(api_url, data=payload, timeout=10)
        response.raise_for_status() # Check for HTTP errors

        response_data = response.json()
        if response_data.get("ok"):
            print(f"[TELEGRAM] Successfully sent to Chat ID {target_chat_id}")
            return True
        else:
            error_desc = response_data.get('description', 'Unknown API error')
            print(f"[TELEGRAM] Failed: API Error - {error_desc}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[TELEGRAM] Failed: Network/Request Error - {e}")
        return False
    except Exception as e:
        print(f"[TELEGRAM] Failed unexpectedly: {e}")
        return False

def post_to_x(target_handle_no_at, message, config):
    """Posts a tweet using Tweepy and X API credentials."""
    api_key = config.get("X_API_KEY")
    api_secret = config.get("X_API_SECRET_KEY")
    access_token = config.get("X_ACCESS_TOKEN")
    access_secret = config.get("X_ACCESS_TOKEN_SECRET")
    bearer_token = config.get("X_BEARER_TOKEN")

    if not api_key or not api_secret or not access_token or not access_secret or not bearer_token:
        print("[X POST] Skipped: X/Twitter API credentials incomplete.")
        return False

    print(f"[X POST] Attempting to post via X API...")
    try:
        client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret,
            wait_on_rate_limit=False
        )

        mention = f"@{target_handle_no_at}" if target_handle_no_at else ""
        tweet_text = f"{mention} WUPFF says: {message} #WUPFF" # Changed tag

        # Basic truncation
        max_len = 280
        if len(tweet_text) > max_len:
            tweet_text = tweet_text[:max_len-3] + "..."

        response = client.create_tweet(text=tweet_text)
        print(f"[X POST] Successfully posted tweet ID: {response.data['id']}")
        return True
    except TweepyException as e:
        print(f"[X POST] Failed: Tweepy API error - {e}")
        if "Rate limit exceeded" in str(e) or "429" in str(e):
             print("  (Rate limit likely hit!)")
        if "403 Forbidden" in str(e):
             print("  (Check App Permissions 'Read and Write' & Regenerate Access Tokens!)")
        return False
    except Exception as e:
        print(f"[X POST] Failed unexpectedly: {e}")
        return False

def display_terminal_popup(message):
    """Displays an ASCII art popup in the terminal."""
    print("\n" + "="*40)
    # Use a simple, reliable font
    tprint("WUPFF!", font="standard")
    # Simple ASCII dog
    print("   / \\__")
    print("  (    @\\___")
    print("  /         O")
    print(" /   (_____/")
    print("/_____/   U")
    print(f"\nMESSAGE: {message}")
    print("="*40)
    try:
        # Annoy loop
        for i in range(5):
             print(f"... WUPFF demands attention {'!'*(i+1)}")
             time.sleep(0.5)
        print("(Press Enter to dismiss...)")
        input() # Wait for user
    except KeyboardInterrupt:
        print("\n[WUPFF Silenced Unwillingly!]")
    return True

def create_virtual_printout(message, filename):
    """Generates a .txt file simulating a printout."""
    try:
        fig = Figlet(font='slant')
        header = fig.renderText('W U P F F') # Changed text

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = f"{header}\n"
        content += f"*** WUPFF OFFICIAL DOT-MATRIX PRINTOUT ***\n" # Changed text
        content += f"SENT: {timestamp}\n"
        content += f"{'='*40}\n\n"
        content += f"MESSAGE:\n{message}\n\n"
        content += f"{'='*40}\n*** END OF TRANSMISSION ***\n"

        with open(filename, "w") as file:
            file.write(content)
        print(f"[VIRTUAL PRINTER] Output saved to {filename}")
        return True
    except NameError:
        print("[VIRTUAL PRINTER] Failed: Figlet class likely not imported correctly.")
        return False
    except Exception as e:
        print(f"[VIRTUAL PRINTER] Failed to print: {e}")
        return False

# --- Typer App Definition ---
app = typer.Typer(help="WUPFF: Send messages annoyingly across multiple channels.")

# --- Initial Setup ---
setup_database()

@app.command()
def send(
    message: str = typer.Argument(..., help="The message to WUPFF."),
    target: str = typer.Option("ALL", "--target", "-t", help="Target: Email, Phone (+1...), X @handle, telegram:ID, or 'ALL'"),
    mode: str = typer.Option("Normal", "--mode", "-m", help="Mode: Normal, Schrute, Kelly, Michael"),
):
    """
    Sends a WUPFF notification. Annoyingly.
    """
    print(f"\n🐶 WUPFF INITIATED ({mode.capitalize()} Mode) 🐶")

    # Load config dictionary each time - ensures fresh env vars if changed
    config = {
        "EMAIL_SENDER_ADDRESS": os.getenv("EMAIL_SENDER_ADDRESS"),
        "EMAIL_SENDER_PASSWORD": os.getenv("EMAIL_SENDER_PASSWORD"),
        "EMAIL_HOST": os.getenv("EMAIL_HOST"),
        "EMAIL_PORT": os.getenv("EMAIL_PORT", 587),
        "TWILIO_ACCOUNT_SID": os.getenv("TWILIO_ACCOUNT_SID"),
        "TWILIO_AUTH_TOKEN": os.getenv("TWILIO_AUTH_TOKEN"),
        "TWILIO_PHONE_NUMBER": os.getenv("TWILIO_PHONE_NUMBER"),
        "X_API_KEY": os.getenv("X_API_KEY"),
        "X_API_SECRET_KEY": os.getenv("X_API_SECRET_KEY"),
        "X_ACCESS_TOKEN": os.getenv("X_ACCESS_TOKEN"),
        "X_ACCESS_TOKEN_SECRET": os.getenv("X_ACCESS_TOKEN_SECRET"),
        "X_BEARER_TOKEN": os.getenv("X_BEARER_TOKEN"),
        "DEFAULT_TARGET_EMAIL": os.getenv("DEFAULT_TARGET_EMAIL"),
        "DEFAULT_TARGET_PHONE": os.getenv("DEFAULT_TARGET_PHONE"),
        "DEFAULT_TARGET_X": os.getenv("DEFAULT_TARGET_X"),
        "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
        "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
    }

    original_message = message
    final_message = original_message
    mode_lower = mode.lower()
    command_target = target # Store original target for logging

    # --- Apply Character Modes ---
    if mode_lower == "schrute":
        fact = random.choice(SCHRUTE_FACTS)
        nl = '\n'
        final_message = f"{original_message} {nl*2} {fact}"
    elif mode_lower == "kelly":
        comment = random.choice(KELLY_COMMENTS)
        nl = '\n'
        final_message = f"{original_message} {nl*2} {comment}"
    elif mode_lower == "michael":
        michael_quote = random.choice(MICHAEL_QUOTES)
        nl = '\n'
        final_message = f"{original_message} {nl*2} {michael_quote}"
        

    # --- Target Handling ---
    activate_email, activate_sms, activate_x, activate_telegram = False, False, False, False
    final_target_email, final_target_phone, final_target_x_handle, final_target_telegram_chat_id = None, None, None, None

    target_lower = target.lower()

    if target_lower == "all":
        print("[Target] 'ALL' selected. Activating channels based on defaults in .env...")
        default_email = config.get("DEFAULT_TARGET_EMAIL")
        default_phone = config.get("DEFAULT_TARGET_PHONE")
        default_x_raw = config.get("DEFAULT_TARGET_X")
        default_telegram_chat_id = config.get("TELEGRAM_CHAT_ID") # Re-use main chat ID as default

        if default_email:
            final_target_email = default_email
            activate_email = True
            print(f"  - Email target (default): {final_target_email}")
        if default_phone:
            final_target_phone = default_phone
            activate_sms = True
            print(f"  - SMS target (default): {final_target_phone}")
        if default_x_raw:
            final_target_x_handle = default_x_raw[1:] if default_x_raw.startswith('@') else default_x_raw
            activate_x = True
            print(f"  - X target (default): @{final_target_x_handle}")
        if default_telegram_chat_id:
            final_target_telegram_chat_id = default_telegram_chat_id
            activate_telegram = True
            print(f"  - Telegram target (default): ChatID {final_target_telegram_chat_id}")

        if not (activate_email or activate_sms or activate_x or activate_telegram):
             print("  Warning: 'ALL' selected but no default targets found/configured in .env.")

    elif '@' in target and '.' in target:
        final_target_email = target
        activate_email = True
        print(f"[Target] Email identified: {final_target_email}")
    elif target.startswith('+'):
        # Basic validation might be good here in future
        final_target_phone = target
        activate_sms = True
        print(f"[Target] Phone identified: {final_target_phone}")
    elif target.startswith('@'):
        final_target_x_handle = target[1:]
        activate_x = True
        print(f"[Target] X Handle identified: @{final_target_x_handle}")
    elif target_lower.startswith("telegram:"):
        try:
            potential_chat_id = target.split(":", 1)[1]
            if potential_chat_id: # Ensure it's not empty
                final_target_telegram_chat_id = potential_chat_id
                activate_telegram = True
                print(f"[Target] Telegram Chat ID identified: {final_target_telegram_chat_id}")
            else:
                print("Warning: Telegram target specified but Chat ID is missing after 'telegram:'.")
        except IndexError:
             print("Warning: Invalid Telegram target format. Use 'telegram:CHAT_ID'.")
    else:
        print(f"Warning: Could not determine specific target type for '{target}'. Only running Terminal/Printer.")

    results = {} # Store success/failure of each channel

    # --- Execute Channels (Reordered for better flow) ---
    print("-" * 10 + " Sending WUPFFs " + "-" * 10) # Changed name

    # 1. Email
    if activate_email:
        subject = f"WUPFF ALERT: {mode.capitalize()} Mode!" # Changed name
        results["email"] = send_email(final_target_email, subject, final_message, config)
    else:
        # Print skip message only if 'ALL' wasn't the target OR if 'ALL' was target but no default email
        if target_lower != 'all' or not config.get("DEFAULT_TARGET_EMAIL"):
            print("[EMAIL] Channel not activated for this target.")
        results["email"] = False

    # 2. SMS
    if activate_sms:
        results["sms"] = send_sms(final_target_phone, final_message, config)
    else:
        if target_lower != 'all' or not config.get("DEFAULT_TARGET_PHONE"):
            print("[SMS] Channel not activated for this target.")
        results["sms"] = False

    # 3. X Post
    if activate_x:
        results["x_post"] = post_to_x(final_target_x_handle, final_message, config)
    else:
        if target_lower != 'all' or not config.get("DEFAULT_TARGET_X"):
            print("[X POST] Channel not activated for this target.")
        results["x_post"] = False

    # 4. Telegram
    if activate_telegram:
         results["telegram"] = send_telegram(final_target_telegram_chat_id, final_message, config)
    else:
         if target_lower != 'all' or not config.get("TELEGRAM_CHAT_ID"):
             print("[TELEGRAM] Channel not activated for this target.")
         results["telegram"] = False

    # 5. Virtual Printer (Always runs unless error)
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    print_filename = f"wupff_{timestamp_str}.txt" # Changed filename prefix
    results["printout"] = create_virtual_printout(final_message, print_filename)

    # --- NOW Display the blocking Terminal Pop-up ---
    # 6. Terminal Pop-up (Always runs unless error)
    results["terminal"] = display_terminal_popup(final_message)

    # --- Log results after all attempts ---
    print("-" * 10 + " WUPFF Complete " + "-" * 10) # Changed name

    # Log the activity using the original target specified by the user
    log_wupff_activity(
        timestamp=datetime.now(),
        message=final_message,
        target=command_target,
        mode=mode,
        results=results
    )

if __name__ == "__main__":
    app()