html_path = 'V:/BDT/frontend/dist/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

pos1 = content.find('function renderEvidenceContent(data, filter) {')
old_head = """function renderEvidenceContent(data, filter) {
            document.getElementById('evidence-total-count').innerText = data.total_reviews.toLocaleString();
            document.getElementById('evidence-pos-count').innerText = data.sentiment_counts.positive.toLocaleString();
            document.getElementById('evidence-neu-count').innerText = data.sentiment_counts.neutral.toLocaleString();
            document.getElementById('evidence-neg-count').innerText = data.sentiment_counts.negative.toLocaleString();"""

new_head = """function renderEvidenceContent(data, filter) {
            if (!data) return;
            const totalCount = (typeof data.total_reviews === 'number') ? data.total_reviews : (data.evidence_reviews ? data.evidence_reviews.length : 0);
            const posCount = (data.sentiment_counts && typeof data.sentiment_counts.positive === 'number') ? data.sentiment_counts.positive : 0;
            const neuCount = (data.sentiment_counts && typeof data.sentiment_counts.neutral === 'number') ? data.sentiment_counts.neutral : 0;
            const negCount = (data.sentiment_counts && typeof data.sentiment_counts.negative === 'number') ? data.sentiment_counts.negative : 0;

            const elTotal = document.getElementById('evidence-total-count');
            if (elTotal) elTotal.innerText = totalCount.toLocaleString();
            const elPos = document.getElementById('evidence-pos-count');
            if (elPos) elPos.innerText = posCount.toLocaleString();
            const elNeu = document.getElementById('evidence-neu-count');
            if (elNeu) elNeu.innerText = neuCount.toLocaleString();
            const elNeg = document.getElementById('evidence-neg-count');
            if (elNeg) elNeg.innerText = negCount.toLocaleString();"""

if old_head in content:
    content = content.replace(old_head, new_head)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("[SUCCESS] Patched renderEvidenceContent safety checks.")
else:
    print("[ERROR] Could not find old_head.")
