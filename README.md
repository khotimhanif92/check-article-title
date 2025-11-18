AI-based Journal Title Checker - ready to deploy to Render / Railway (free tiers)

Files included:
- app.py (Flask app using sentence-transformers)
- requirements.txt
- Procfile

Quick deploy (Render - recommended for beginners):
1. Create a GitHub repo and upload these files.
2. Sign in to https://render.com and click 'New' -> 'Web Service'.
3. Connect your GitHub repo, select the branch, and deploy.
4. Render will install requirements and start the web service. After successful build you'll get a public URL.
5. In OJS, paste an iframe:
   <iframe src="YOUR_RENDER_URL" style="width:100%;height:700px;border:none"></iframe>

Notes:
- The model 'all-MiniLM-L6-v2' will be downloaded at first startup; build may take time.
- Free tiers may have memory and size limits. If deployment fails due to size, consider:
  * Using a lighter embedding approach (OpenAI embeddings - requires API key)
  * Hosting on a server with more memory (paid)