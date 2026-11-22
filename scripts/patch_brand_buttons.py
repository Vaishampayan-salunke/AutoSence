html_path = 'V:/BDT/frontend/dist/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_block = """                    <div class="text-[11px] text-slate-400 space-y-1">
                        <div>Total Reviews: <strong class="text-slate-200">${b.total_reviews}</strong></div>
                        <div class="truncate">Catalog: <span class="text-cyan-300">${b.models_list.join(', ')}</span></div>
                    </div>
                `;"""

new_block = """                    <div class="text-[11px] text-slate-400 space-y-1">
                        <div>Total Reviews: <strong class="text-slate-200">${b.total_reviews}</strong></div>
                        <div class="truncate">Catalog: <span class="text-cyan-300">${b.models_list.join(', ')}</span></div>
                    </div>
                    <div class="pt-2 flex gap-1.5 border-t border-slate-800/80">
                        <button onclick="openEvidenceModal('brand', '${b.brand.replace(/'/g, \"\\\\'\")}')" class="flex-1 py-1.5 bg-cyan-950/80 hover:bg-cyan-900 text-cyan-300 border border-cyan-800/60 rounded-xl text-xs font-bold transition flex items-center justify-center space-x-1 shadow-sm" title="View exact review evidence behind this brand">
                            <span>🔍 Inspect Evidence</span>
                        </button>
                        <button onclick="switchView('models'); filterModelsByBrand('${b.brand.replace(/'/g, \"\\\\'\")}');" class="px-3 py-1.5 bg-navy-900 hover:bg-slate-800 text-slate-300 rounded-xl text-xs font-semibold border border-slate-700 transition" title="Drill into vehicle models">
                            Models &rarr;
                        </button>
                    </div>
                `;"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("[SUCCESS] Injected Evidence & Model Drill-Down buttons into Brand cards.")
else:
    print("[ERROR] Could not find target brand block.")
