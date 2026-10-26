# Muse AI — Prototype v1

স্ক্রিনশটের ChatGPT লেআউটের মতো করে বানানো: উপরে রঙিন বড় Muse AI, বামে সাইডবার (Home / New chat / Projects / Recents), মাঝে চ্যাট, নিচে ইনপুট বক্সে + বাটন, উপরে ডানদিকে + Browser বাটন।

## চালানো (Windows)
1. Python ইনস্টল করো (Add Python to PATH টিক দাও)
2. এই ফোল্ডারে Command Prompt খুলে:
   ```
   pip install playwright
   playwright install chromium
   ```
3. `.env.example` কপি করে `.env` বানাও, ভেতরে তোমার OpenRouter Key পেস্ট করো (শুধু পিসিতে, চ্যাটে না)
4. চালাও:
   ```
   python main.py
   ```

## বাটনগুলো
- **+ Browser (উপরে ডানে) / + (ইনপুট বক্সে):** ডেডিকেটেড ব্রাউজার খুলবে। এই ব্রাউজার শুধু এজেন্টের কাজের জন্য, তোমার নিজের Chrome আলাদা থাকবে। প্রথমবার ওই ব্রাউজারে নিজে হাতে লগইন করবে, সেশন `muse_browser_profile` ফোল্ডারে সেভ থাকবে।
- **STOP:** ব্রাউজারের কাজ সাথে সাথে থামবে। আবার শুরু করতে + Browser চাপো।
- **চ্যাট:** লিখলে Qwen (OpenRouter) মাথা RULES.md নিয়ম মেনে উত্তর দেবে। এটা পুরো Muse না, আংশিক Muse — নিয়ম আর পদ্ধতি লোড করা আছে।

## সীমা (v1)
- v1-এ লাইভ Shopify এডিট নেই, শুধু চ্যাট + ডেডিকেটেড ব্রাউজার খোলা।
- EXE এখনো নেই — Windows-এ টেস্ট পাস হলে PyInstaller দিয়ে EXE বানানো যাবে, সেটা পরের ধাপ।
