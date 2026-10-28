==============================================================
  TECHXFLUENCE AI - RAG CHATBOT  (Streamlit + FREE Gemini API)
  Windows + VS Code setup guide (Tanglish)
==============================================================

IDHU ENNA?
----------
Neenga kelvi kettaa:
  1. App, data/ folder-la irukkura TechXfluence website content-ah search pannum (Retrieval - BM25).
  2. Best matching sections-ah Gemini-ku anuppum (Augmented).
  3. Gemini andha content-ah mattum vechu answer ezhudhum (Generation).
  4. Answer-oda "Sources" (website link / file name) kaattum.
Ollama VENDAM. Paid plan VENDAM - free Gemini API key mattum podhum.
Answer knowledge base-la illana:
  "I couldn't find that information in the available TechXfluence resources.
   Please contact the official team."

FILES
-----
app.py                     -> Streamlit UI
rag_engine.py              -> Knowledge load + search + prompt
gemini_llm.py              -> Gemini API (free)
ingest_website.py          -> Website-la irundhu content download
data/company_knowledge.txt -> Main knowledge file
requirements.txt           -> Packages (streamlit, requests, beautifulsoup4, pypdf)
run_windows.bat            -> Double-click start (optional)
.streamlit/secrets.toml.example -> API key vekkura example


==============================================================
RESOURCE UPLOAD
==============================================================
  - Sidebar-la PDF, TXT, MD, JSON resources upload pannalaam.
  - RAG search uploaded resources-la mattum nadakkum; data/ folder content use aagadhu.
  - Answer-kku keezha "Sources used" -la file peyar / section kaattum.
  - Uploaded resources browser session-kku mattum; refresh panna thirumba upload pannanum.
  - Scanned/image PDF-la selectable text illana adhai read panna mudiyaadhu.

==============================================================
A) PC-LA RUN PANNA (WINDOWS + VS CODE)
==============================================================
STEP 1: Python install (3.10+) - https://www.python.org/downloads/
        Installer-la "Add python.exe to PATH" TICK pannu.
        Check:  python --version

STEP 2: ZIP extract pannu -> VS Code -> File -> Open Folder -> TechXfluence_AI

STEP 3: Terminal-la:
        python -m venv .venv
        .venv\Scripts\activate
        pip install -r requirements.txt
   (PowerShell "scripts disabled" error na:
        Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned )

STEP 4: FREE GEMINI KEY
        https://aistudio.google.com/apikey -> Create API key. (Card vendam.)
        Key-ah yaarukkum share pannadha. Code-la / GitHub-la podaadha.

STEP 5: KEY SET PANNU (3 vazhi - edhavadhu onnu)
   Vazhi 1 (easy - app-la irundhe):
        App open panni, sidebar-la "Gemini API key" box-la key-ah paste pannu.
        Model dropdown-la model select pannu (list API-la irundhu varum).
        "Test" click panni green "ready" vandha ready.
        "Save" click panna .streamlit/secrets.toml-la save aagum (next time paste vendaam).
   Vazhi 2 (terminal-kku mattum):
        $env:GEMINI_API_KEY="ungal-key"
   Vazhi 3 (permanent):
        .streamlit\secrets.toml.example-ah copy panni  secrets.toml nu rename pannu.
        Ullla  GEMINI_API_KEY = "ungal-key"  nu maathu.
        GEMINI_MODEL = "gemini-3.5-flash-lite" nu set pannu.
        Key-ah chat-la paste pannadha; .streamlit/secrets.toml GitHub-ku upload pannaadha.

STEP 6: START
        streamlit run app.py
        Browser-la http://localhost:8501 open aagum.
        Sidebar-la "gemini-3.5-flash-lite ready" nu green-a varanum.
        (Illana run_windows.bat double-click pannalaam.)
        Stop: Ctrl + C

STEP 7: WEBSITE CONTENT ADD PANNA
   Option A: data/company_knowledge.txt-la website content already irukku.
   Option B: python ingest_website.py        -> data/website_content.txt create aagum.
             python ingest_website.py --url https://www.techxfluence.com/membership
   Option C: Kai-la copy-paste. data/company_knowledge.txt kadaisila:
          === SECTION: Partners ===
          SOURCE: https://www.techxfluence.com/partners
          (copy panna text)
        illana:  python ingest_website.py --add "Partners" "text" --source https://...
   Unmaiyana info mattum add pannu. Price/date/phone invent pannadha.
   Add panna apram sidebar-la "Reload knowledge" click pannu.

SAMPLE QUESTIONS
   - What services does TechXfluence offer?
   - What are the membership plans and prices?
   - How can I host an event?
   - What job roles are open?
   - Who is the president of USA?   (-> "couldn't find" nu varanum)


==============================================================
B) FREE ONLINE DEPLOY (STREAMLIT COMMUNITY CLOUD)
==============================================================
1) GitHub repo create pannu. App folder-la (app.py irukkura folder) terminal:
     git init -b main
     git add .
     git commit -m "TechXfluence AI RAG chatbot"
   Browser-la GitHub new repo create panni, appuram:
     git remote add origin https://github.com/<username>/<repo>.git
     git push -u origin main
   .streamlit/secrets.toml push aagadhu (.gitignore block pannum) - API key safe.
   Repo root-la app.py irukkanum.
2) https://share.streamlit.io -> Create app -> repo, branch = main,
   Main file path = app.py
3) Advanced settings -> Python version = 3.12 -> Secrets box-la paste pannu:
        GEMINI_API_KEY = "ungal-key"
        GEMINI_MODEL = "gemini-3.5-flash-lite"
4) Deploy click. Sidebar-la green "ready" varanum.
   Cloud-la "Save" button velai seiyaadhu (filesystem read-only) - Secrets-la mattum set pannu.
   Free tier-la oru model-ku ~20 questions/day; limit mudinjaa sidebar-la vera model select pannu.


==============================================================
COMMON ERRORS + FIX
==============================================================
1) 'python' is not recognized      -> Python reinstall, "Add to PATH" tick. VS Code restart.
2) 'streamlit' is not recognized   -> .venv\Scripts\activate ; pip install -r requirements.txt
                                      illana: python -m streamlit run app.py
3) Sidebar "Gemini not ready - No GEMINI_API_KEY set"
                                   -> Key set pannala. Step 5 paar (Cloud-la: Secrets). Save panni reboot.
4) "Gemini rejected the API key"   -> Key thappu / extra space. Puthu key create pannu.
5) "Free Gemini limit reached"     -> Free limit. 1 nimisham wait pannu.
   "free daily limit ... used up"   -> Andha model-ku 20 questions/day mudinjadhu.
                                      Sidebar-la vera model select pannu (ovvoru model-kum thani quota).
6) "Gemini model not found"        -> GEMINI_MODEL = "gemini-3.5-flash-lite" set pannu.
7) "Cannot reach Google"           -> Internet / VPN / firewall check pannu.
8) ModuleNotFoundError: gemini_llm / rag_engine (Cloud)
                                   -> Andha file GitHub-la illa. Ellaa files-um upload pannu, reboot app.
   ModuleNotFoundError: requests / streamlit (PC)
                                   -> venv active-a?  pip install -r requirements.txt
9) Cloud-la sidebar "No knowledge found in the data/ folder"
                                   -> data/company_knowledge.txt GitHub-la illa. Repo-la data folder + file upload pannu, reboot app.
9b) Always "I couldn't find that information..." 
                                   -> Kelvi words knowledge file-la illa. Vera maari kelu, illana
                                      data/company_knowledge.txt-la info add pannu.
10) ingest_website.py "[fail]"     -> Internet check. JavaScript page na Option C use pannu.
11) Port 8501 already in use       -> streamlit run app.py --server.port 8502

TIPS
----
  - Strict/loose search maatha: rag_engine.py top-la MIN_COVERAGE, TOP_K, MIN_SCORE.
  - Synonyms add: rag_engine.py SYNONYMS dictionary.
  - Colours maatha: app.py CSS block (--cyan, --purple, --navy).
  - Private documents data/ folder-la podaadha. API key code-la hardcode pannala.

All the best! 🚀
