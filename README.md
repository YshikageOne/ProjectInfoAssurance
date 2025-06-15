# ProjectInfoAssurance
for Designing UI, Use any or use QT designer.exe
for editing the database, use DB Browser for SQLite v3.13.1


Only Development serve not yet online,
but there is


🔐 ✅ Secure App Development Roadmap (Revised)
✅ Step 1/6 – API-Connected Login with Password Hashing ✔️ (DONE)
✅ Created Users table in SQLite

✅ Used werkzeug.security to hash passwords

✅ Set up /login and /register routes via Flask

✅ PyQt5 UI communicates with backend via requests.post

✅ Human-readable error prompts added

🔐 Step 2/6 – JWT Token Setup (Next Step)
Goal: On successful login, generate a signed JWT to prove identity.

⏱️ Time: 10–20 mins

Use PyJWT to issue token

Add JWT_SECRET, exp, and signature logic

Token returned to PyQt5 UI

Optional: Display or log the token (for dev/debug)

🔐 Step 3/6 – Token Usage in PyQt5
Goal: Store the JWT after login and include it in future requests

⏱️ Time: 20–30 mins

Store token in memory or .token file

Include it as a Bearer token in Authorization headers

Use for secured routes like /add, /update, /get-all

🔐 Step 4/6 – Secure JWT with AES and Blockchain Validation
Goal: Strengthen the token system

⏱️ Time: 1–2 hours (moderate complexity)

AES encryption: Encrypt token payload or sensitive user fields

Use pycryptodome or cryptography library

Blockchain option (one of these):

✔️ Log token metadata on a local/private chain

✔️ Validate JWTs via smart contract or blockchain ledger (optional)

📌 You can simulate blockchain logging using hash + append-only storage for demo

🌐 Step 5/6 – Hosting Flask API Online (Production Mode)
Goal: Run Flask where others can access it

⏱️ Time: 30 mins – 1 hour

✅ Option A: Use ngrok (easy for demo/presentations)

✅ Option B: Host Flask on Apache with mod_wsgi using XAMPP

✅ Option C: Use Flask deployment server like Gunicorn or Waitress with port forwarding

Ensure API is protected (no debug mode, CORS policy enabled)

🧪 Step 6/6 – Final Testing + Static Cleanup
Goal: Remove security holes and test

⏱️ Time: 30–45 mins

✅ Remove any static code that references hardcoded usernames/passwords

✅ Test expired token rejection

✅ Block invalid/altered tokens

✅ Handle broken connections gracefully

✅ Ensure database errors aren’t exposed to the user

🏁 By the End:
You will have a secured, non-static PyQt5 app that:

Authenticates via encrypted API

Uses JWT for session identity

(Optionally) validates token integrity with blockchain-like logging

Hosted securely and ready for presentation or deployment

Let me know when you're ready to continue with Step 2 and I’ll walk you through the actual code.
