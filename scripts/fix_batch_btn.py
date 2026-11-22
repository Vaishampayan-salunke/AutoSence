"""
Fix executeBatchTest button event handling and also the button HTML to pass event.
"""
import re

path = "frontend/dist/index.html"
content = open(path, "r", encoding="utf-8").read()

# Fix 1: Update executeBatchTest button onclick to pass event
old_btn = 'onclick="executeBatchTest()"'
new_btn = 'onclick="executeBatchTest(event)"'
if old_btn in content:
    content = content.replace(old_btn, new_btn)
    print("Fixed: onclick passes event")

# Fix 2: Update the function signature to accept evt
old_fn_sig = "        async function executeBatchTest() {\n            const btn = event ? event.target : null;\n            if (btn) btn.innerText = \"Processing 25 Reviews in Parallel...\";"
new_fn_sig = "        async function executeBatchTest(evt) {\n            const btn = (evt && evt.currentTarget) ? evt.currentTarget : null;\n            if (btn) { btn.disabled = true; btn.innerText = 'Processing 25 Reviews in Parallel...'; }"
if old_fn_sig in content:
    content = content.replace(old_fn_sig, new_fn_sig)
    print("Fixed: executeBatchTest function signature + btn ref")
else:
    print("WARNING: executeBatchTest signature not found - checking partial match...")
    idx = content.find("async function executeBatchTest(")
    if idx >= 0:
        print(f"Found at index {idx}: {content[idx:idx+200]}")

# Fix 3: Update the finally btn restore to also re-enable
old_finally = "            if (btn) btn.innerText = \"Run 25-Review Batch Evaluation ⚡\";"
new_finally = "            if (btn) { btn.disabled = false; btn.innerText = 'Run 25-Review Batch Evaluation ⚡'; }"
if old_finally in content:
    content = content.replace(old_finally, new_finally)
    print("Fixed: finally block re-enables button")

open(path, "w", encoding="utf-8").write(content)
print("Done writing.")
