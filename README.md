<p align="center">
  <!-- TODO: Draw a terrible logo in MS Paint. A dog yelling WUPFF maybe? -->
  <img src="md_contents/logo.png" alt="WUPFF Logo - Needs Improvement" width="150"/>
</p>

<h1 align="center">WUPFF!</h1>

<p align="center">
  <em>"Did Ryan send you another WUPFF?"</em>
</p>
<p align="center">
  You know WUPHF from The Office? Ryan's billion-dollar idea that crashed faster than... well, faster than most of Ryan's ideas? I kinda built it. In Python. It's called WUPFF now. It takes your message and SHOUTS IT EVERYWHERE. Because sometimes, subtlety is overrated. (And because it was funny to try.)
  
<p align="center">
  <img src="md_contents/michael_sgtm.gif" alt="Alternate text" width="200"/>
</p>


</p>

---

## 🔑 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

> "Wupff" is a parody/inspired concept based on the fictional WUPHF.com from The Office (U.S.).  
> This project is not affiliated with NBC/Universal in any way.

---

## What The Heck Does It *Do*?



<p align="center">
  <!-- TODO: Replace this text with a seizure-inducing GIF of the script running -->
  <em>Why tell you. When I can show you(I just sent my self a Wupff!)</em>
  <br>
  <img src="md_contents/demo.gif" alt="WUPFF Demo GIF - It's Alive... Mostly" width="600"/>
  <!-- <video width="320" height="240" controls>
    <source src="md_contents/demo.mp4" type="video/mp4">
  </video>
 -->

<p align="center">
  <img src="md_contents/ryan_iluv_it.gif" alt="Alternate text" width="200"/>
</p>

</p>

You type message. You type target. You hit Enter. WUPFF tries to do this:

*   **📧 Email:** Slams into their inbox. Subject: PANIC!
*   **📱 SMS:** Sends SMS via Twilio with a 🐶 emoji (non-negotiable). Might or might not work depending on your country’s telecom regulations. Requires proper setup, funds, and number verification for trial accounts.
*   **🐦 X (Twitter):** Posts *publicly* from *your* account, tagging your victim target. Good luck scrubbing that later!
*   **💬 Telegram:** DMs them (or a group) via a Telegram Bot you gotta create first.
*   **💻 Terminal:** An ASCII dog appears ON YOUR SCREEN and yells until you submit by pressing Enter.
*   **💾 Virtual Printer:** Saves a `.txt` file Wupff printout.

It's a joke! A coding exercise! A monument to a terrible idea from a great show! Don't take it *too* seriously. Unless...?

---

## Make Your WUPFFs Weirder: Character Modes!

Why be normal when you can be... *them*?

*   `--mode Schrute`

    <img src="md_contents/schrute.gif" alt="Alternate text" width="200"/>

*   `--mode Kelly`
  
    <img src="md_contents/kelly.gif" alt="Alternate text" width="200"/>

*   `--mode Michael`
  
    <img src="md_contents/micheal.gif" alt="Alternate text" width="200"/>

---

## How to Unleash This Thing ( Get Started )

Need Python 3.

1.  **Get Code:**
    ```bash
    git clone https://github.com/Mahendranath-Porandla/wupff.git
    cd wupff
    ```

2.  **Virtual Env:** (Don't be like Kevin skipping steps with the chili.)
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Windows: .\venv\Scripts\activate
    ```
    *(`(venv)` should be visible. Feel the power.)*

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **THE `.env` FILE - Set up with your API keys**
    *   API keys live here. Keep 'em secret, keep 'em safe.
    *   Copy .env.example to create a .env file, then add your API keys as needed.

---

## `.env` - API keys

Fill these in `.env`.

*   **Email:** `EMAIL_SENDER_ADDRESS` (your email), `EMAIL_SENDER_PASSWORD` (**NOT your real password.** Use a 16-digit **App Password** from Google if using Gmail + 2FA).

 
*   **SMS (Twilio):** `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER` (like `+1...`). Trial accounts need verified numbers & struggle internationally. Costs money. High chance of failure = Authentic Ryan Howard experience.


*   **X (Twitter):** Needs FIVE keys: `X_API_KEY`, `X_API_SECRET_KEY`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET`, `X_BEARER_TOKEN`. Get from X Dev Portal. App needs **Read and Write** permission. Still getting `403 Forbidden` errors? **Regenerate Access Token/Secret** *after* saving permissions. Yes, again. It's like whack-a-mole.


*   **Telegram:** `TELEGRAM_BOT_TOKEN` (from `@BotFather`), `TELEGRAM_CHAT_ID` (target chat ID - can be obtained from `@useinfobot`).


*   **Defaults (`--target ALL`):** `DEFAULT_TARGET_EMAIL`, `DEFAULT_TARGET_PHONE`, `DEFAULT_TARGET_X`, `TELEGRAM_CHAT_ID`.
---

## Running WUPFF!

From your terminal (with `(venv)` active, remember?):

```bash
python3 wupff.py '<Your earth-shattering message>' --target <victim_identifier> --mode <vibe>
```
`<victim_identifier>`
```Email: 'pam.beesly@dundermifflin.com'

SMS (E.164 Format ONLY!): '+15705551234'

X (Twitter): '@XYZ12345'

Telegram (Use Chat ID): 'telegram:123456789'

All Defaults (from .env): 'ALL'

```
Example:

```bash
python3 wupff.py 'You have been Wupffed!' --target ALL --mode Normal
```