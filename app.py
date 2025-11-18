from flask import Flask, request, jsonify, render_template_string
from sentence_transformers import SentenceTransformer, util
import torch

app = Flask(__name__)

JOURNALS = {
    "Jurnal Manajemen Kesehatan": {
        "scope": "Manajemen rumah sakit, kebijakan kesehatan, administrasi layanan kesehatan, sistem informasi manajemen rumah sakit, pembiayaan kesehatan, audit klinis, mutu dan keselamatan pasien.",
    },
    "Jurnal Abdimas JATIBARA": {
        "scope": "Pengabdian kepada masyarakat, pemberdayaan komunitas, inovasi teknologi tepat guna untuk masyarakat, evaluasi program keberlanjutan sosial dan kesehatan masyarakat.",
    },
}

SIMILARITY_THRESHOLD = 0.58

MODEL_NAME = 'all-MiniLM-L6-v2'
model = SentenceTransformer(MODEL_NAME)

journal_names = list(JOURNALS.keys())
scopes = [JOURNALS[name]['scope'] for name in journal_names]
scope_embeddings = model.encode(scopes, convert_to_tensor=True)

def check_title_against_scopes(title, top_k=3):
    title = title.strip()
    if not title:
        return {'error': 'Empty title'}
    title_emb = model.encode(title, convert_to_tensor=True)
    cos_scores = util.cos_sim(title_emb, scope_embeddings)[0]
    results = []
    for i, name in enumerate(journal_names):
        score = float(cos_scores[i].cpu().item())
        results.append({
            'journal': name,
            'score': score,
            'scope_snippet': JOURNALS[name]['scope'][:280] + ("..." if len(JOURNALS[name]['scope'])>280 else "")
        })
    results = sorted(results, key=lambda x: x['score'], reverse=True)
    best = results[0]
    recommendation = 'TIDAK SESUAI'
    if best['score'] >= SIMILARITY_THRESHOLD:
        recommendation = 'SESUAI'
    return {
        'title': title,
        'recommendation': recommendation,
        'best_match': best,
        'matches': results[:top_k]
    }

INDEX_HTML = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI Title Checker</title>
  <style>
    body { font-family: Arial, sans-serif; padding: 20px; max-width: 800px; margin: auto }
    input[type=text] { width: 100%; padding: 10px; font-size: 16px }
    button { padding: 10px 16px; font-size: 16px }
    .result { margin-top: 20px; padding: 16px; border-radius: 8px; background: #f6f6f6 }
    .score { font-weight: bold }
  </style>
</head>
<body>
  <h2>AI-based Cek Judul Jurnal</h2>
  <p>Masukkan judul artikel. Sistem akan memberi rekomendasi apakah judul sesuai dengan fokus/ruang lingkup jurnal.</p>
  <input id="titleInput" type="text" placeholder="Masukkan judul artikel... " />
  <p><button onclick="checkTitle()">Cek Judul</button></p>
  <div id="output"></div>

<script>
async function checkTitle(){
  const title = document.getElementById('titleInput').value;
  const output = document.getElementById('output');
  output.innerHTML = '<div class="result">Checking... please wait</div>';

  try{
    const res = await fetch('/api/check', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({title: title})
    });
    const data = await res.json();
    if (data.error){
      output.innerHTML = '<div class="result">Error: '+data.error+'</div>';
      return;
    }

    let html = '<div class="result">';
    html += '<div><strong>Rekomendasi:</strong> ' + data.recommendation + '</div>';
    html += '<div><strong>Judul:</strong> ' + data.title + '</div>';
    html += '<hr />';
    html += '<div><strong>Top Matches:</strong></div>';
    data.matches.forEach(m => {
      html += '<div style="margin-top:8px">';
      html += '<div><span class="score">' + (m.score.toFixed(3)) + '</span> — <em>' + m.journal + '</em></div>';
      html += '<div style="font-size:90%">' + m.scope_snippet + '</div>';
      html += '</div>';
    });
    html += '</div>';
    output.innerHTML = html;
  }catch(err){
    output.innerHTML = '<div class="result">Request failed: '+err.message+'</div>';
  }
}
</script>
</body>
</html>
'''

from flask import render_template_string
@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/api/check', methods=['POST'])
def api_check():
    data = request.get_json(force=True)
    title = data.get('title','').strip()
    if not title:
        return jsonify({'error':'No title provided'}), 400
    result = check_title_against_scopes(title, top_k=5)
    return jsonify(result)

@app.route('/health')
def health():
    return jsonify({'status':'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000')