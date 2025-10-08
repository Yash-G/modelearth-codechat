<div class='titleflex'>
    <div>
    	<h1>CodeChat</h1>
		Scroll down for our RAG pipeline process and view our <a href="chat">chat interface</a>.
    </div>
    <a href="https://github.com/ModelEarth/codechat" target="codechat_github" class="github-link">
        <img src="../localsite/img/icon/github/github.png" alt="Codechat Repository">
    </a>
</div>

## Webroot

<a href="http://localhost:8887/" style="float:right">Runs on port 8887</a>

Our webroot repo loads these submodules, plus claude.md and [vector_sync.yml](https://github.com/ModelEarth/webroot/blob/main/.github/workflows/vector_sync.yml) - [Get Started](https://model.earth/webroot/)

| Name | Repository | Description |
|------|------------|-------------|
| [webroot](../) | [github.com/modelearth/webroot](https://github.com/modelearth/webroot) | PartnerTools webroot |
| [cloud](../cloud/) | [github.com/modelearth/cloud](https://github.com/modelearth/cloud) | Flask for python colabs |
| [codechat](../codechat/) | [github.com/modelearth/codechat](https://github.com/modelearth/codechat) | Chat RAG using Pinecone |
| [community-forecasting](../community-forecasting/) | [github.com/modelearth/community-forecasting](https://github.com/modelearth/community-forecasting) | Javascript-based ML with maps |
| [comparison](../comparison/) | [github.com/modelearth/comparison](https://github.com/modelearth/comparison) | Trade Flow data visualizations |
| [exiobase](../exiobase/) | [github.com/modelearth/comparison](https://github.com/modelearth/exiobase) | Trade data to CSV and SQL |
| [feed](../feed/) | [github.com/modelearth/feed](https://github.com/modelearth/feed) | FeedPlayer video/gallery |
| [home](../home/) | [github.com/modelearth/home](https://github.com/modelearth/home) | Everybody's Home Page |
| [io](../io/) | [github.com/modelearth/io](https://github.com/modelearth/io) | React Input-Output widgets for states |
| [localsite](../localsite/) | [github.com/modelearth/localsite](https://github.com/modelearth/localsite) | Core javacript utilities, tabulator |
| [products](../products/) | [github.com/modelearth/products](https://github.com/modelearth/products) | Building Transparency Product API |
| [profile](../profile/) | [github.com/modelearth/profile](https://github.com/modelearth/profile) | Footprint Reports for communities and industries |
| [projects](../projects/) | [github.com/modelearth/projects](https://github.com/modelearth/projects) | Overview and TODOs - Projects Hub |
| [realitystream](../realitystream/) | [github.com/modelearth/realitystream](https://github.com/modelearth/realitystream) | Run Models colab |
| [reports](../reports/) | [github.com/modelearth/realitystream](https://github.com/modelearth/reports) | Output from RealityStream colab |
| [swiper](../swiper/) | [github.com/modelearth/swiper](https://github.com/modelearth/swiper) | UI swiper component for FeedPlayer |
| [team](../team/) | [github.com/modelearth/team](https://github.com/modelearth/team) | Rust API for Azure and AI Insights |

<br><div class="floatRight" style="max-width:240px;"><a href="overview/img/flowchart.png"><img src="overview/img/flowchart.png" style="width:100%"></a></div>

Optional:

**Extra repos:** (forked and cloned into webroot) topojson, community, nisar, useeio-json, trade-data

**Inactive repos:** planet, earthscape, modelearth
<br>


## Data-Pipeline (static csv and json output for fast web reports)

These output repos may be pulled into local webroots during data processing, but we avoid committing these as a submodules in the webroots due to their large size. The static data in these repos is pulled directly through Github Pages and the Cloudflare CDN.

| Name | Repository | Description |
|------|------------|-------------|
| [data-pipeline](../data-pipeline/) | [github.com/modelearth/data-pipeline](https://github.com/modelearth/data-pipeline) | Python data processing pipeline |
| [trade-data](../trade-data/) | [github.com/modelearth/trade-data](https://github.com/modelearth/trade-data) | Tradeflow data outputs |
| [products-data](../products-data/) | [github.com/modelearth/products-data](https://github.com/modelearth/products-data) | Product impact profiles |
| [community-data](../community-data/) | [github.com/modelearth/community-data](https://github.com/modelearth/community-data) | Community-level data outputs |
| [community-timelines](../community-timelines/) | [github.com/modelearth/community-timelines](https://github.com/modelearth/community-timelines) | Timeline data for communities |
| [community-zipcodes](../community-zipcodes/) | [github.com/modelearth/community-zipcodes](https://github.com/modelearth/community-zipcodes) | ZIP code level community data |
| [community-forecasting](../community-forecasting/) | [github.com/modelearth/community-forecasting](https://github.com/modelearth/community-forecasting) | Forecasting frontend (legacy) |
| [dataflow](../dataflow/) | [github.com/modelearth/dataflow](https://github.com/modelearth/dataflow) | Data flow NextJS UX |

<br>

## RAG Pipeline Documentation

The RAG pipeline processes files from a local repository (e.g., `modelearth/localsite`) by chunking them using **Tree-sitter**, embedding chunks with 

**OpenAI’s `text-embedding-3-small`**, and storing them in **Pinecone VectorDB** with metadata (`repo_name`, `file_path`, `file_type`, `chunk_type`, `line_range`, `content`).  Get $5 in credits, you won't need them all.

Users will query via the [chat frontend](chat), where an **AWS Lambda backend** embeds the question, searches Pinecone for relevant chunks, queries 

**Gemini (`gemini-1.5-flash`)** for answers, and returns results to the frontend.

**GitHub Actions** syncs the VectorDB by detecting PR merges, pulling changed files, re-chunking, re-embedding, and updating Pinecone. This enables a scalable Q&A system for codebase and documentation queries.

Add your 3 keys to .env and run to test the RAG process (Mac version):

### Installing Dependencies

The `requirements.txt` file automatically installs these core packages and their dependencies:
- `python-dotenv` - Environment variable management
- `pinecone` - Vector database client  
- `openai` - OpenAI API client for embeddings
- `google-generativeai` - Gemini API client for responses
- Additional core dependencies: `certifi`, `typing-extensions`, `urllib3`, `requests`, `pydantic`, `anyio`

Windows PC

	python -m venv env
	env\Scripts\activate.bat
	pip install -r requirements.txt

Mac/Linux

	python3 -m venv env
	source env/bin/activate
	pip install -r requirements.txt

Start

	python rag_query_test.py

Or start Claude

	npx @anthropic-ai/claude-code

### AWS Lambda Deployment Issues

**Error: `Unable to import module 'lambda_function': no module named 'pydantic_core._pydantic_core'`**

This error occurs when deploying to AWS Lambda because `pydantic` (required by the OpenAI client) has compiled dependencies that may not be compatible with Lambda's runtime environment.

**Solutions:**

1. **Use Lambda Layers** (Recommended):
   ```bash
   # Create a layer with dependencies
   mkdir python
   pip install -r requirements.txt -t python/
   zip -r dependencies-layer.zip python/
   # Upload as Lambda Layer and attach to your function
   ```

2. **Platform-specific Installation**:
   ```bash
   # Install for Linux x86_64 (Lambda runtime)
   pip install -r requirements.txt --platform linux_x86_64 --only-binary=:all: -t package/
   ```

3. **Alternative: Use Docker for Lambda**:
   ```dockerfile
   FROM public.ecr.aws/lambda/python:3.11
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY lambda_function.py .
   CMD ["lambda_function.lambda_handler"]
   ```

4. **Lightweight Alternative**: Replace `pydantic`-heavy clients with `requests` for direct API calls to reduce dependency complexity.



## Projects

- Chunk, Embed, Store in VectorDB - **Webroot and submodules** (listed above and in [webroot/submodules.jsx](https://github.com/modelearth/webroot))
- Write AWS Lambda Backend (embed queries, fetch from Pinecone, and query Gemini)
- Sync VectorDB with PRs (GitHub Actions on PR merges)

---

## More Context

**Chunk, Embed, Store** – check out `rag_ingestion_pipeline.ipynb`

- We used Tree-sitter for chunking; explore better strategies if available
- Embedding using OpenAI `text-embedding-3-small` (dimension: 1536)
- Create a free Pinecone account and store embeddings with the metadata (`repo_name`, `file_path`, `file_type`, `chunk_type`, `line_range`, `content`)
- ✅ Ensure no file type is missed during chunking, embedding, or storing — any missing content could lead to loss of critical information


| File Type(s)                                     | Category        | Chunking Strategy                                 | What Gets Embedded                                     |
|--------------------------------------------------|------------------|---------------------------------------------------|--------------------------------------------------------|
| `.py`, `.js`, `.ts`, `.java`, `.cpp`, `.c`, `.cs`, `.go`, `.rb`, `.php`, `.rs`, `.swift`, `.kt`, `.scala` | Code            | Tree-sitter parse: functions, classes, methods     | Logical code blocks (function/class level)             |
| `.ipynb`                                         | Notebook         | Cell-based splitting (code + markdown)            | Each notebook cell and selected metadata               |
| `.html`                                          | HTML Markup      | Tree-sitter DOM-based: `<div>`, `<p>`, etc.       | Structural HTML segments by semantic tag               |
| `.xml`, `.xsd`, `.xsl`                           | XML Markup       | Tree-sitter DOM-based elements                    | Logical XML nodes or fallback 1K-char splits           |
| `.md`, `.txt`, `.rst`, `.adoc`, `.mdx`           | Markdown/Text    | Header-based (`#`, `##`, etc.)                    | Markdown sections and paragraphs                       |
| `.json`, `.yaml`, `.yml`, `.jsonl`               | Config/Data      | Recursive key-level splitting                     | Key-value chunks or JSON/YAML fragments                |
| `.csv`, `.tsv`, `.xls`, `.xlsx`, `.parquet`, `.feather`, `.h5`, `.hdf5` | Tabular Data | Preview: columns + sample rows                    | Column names and first few data rows                   |
| `.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`, `.psd`, `.bmp`, `.tiff` | Image Files     | Skipped from content chunking                     | Metadata summary only (file name/type)                 |
| `.woff`, `.woff2`, `.ttf`, `.otf`                | Fonts            | Skipped from content chunking                     | Metadata summary only                                  |
| `.map`, `.zip`, `.exe`, `.bin`, `.dll`, `.so`, `.o` | Binary         | Skipped from content chunking                     | Metadata summary only                                  |
| `.min.js`, `.min.css`, `.js.map`, `.css.map`     | Minified         | Skipped from content chunking                     | Metadata summary only                                  |
| `.pdf`, `.docx`, `.doc`, `.rtf`, `.odt`          | Documents        | Skipped from content chunking                     | Metadata summary only                                  |
| `.css`, `.scss`, `.sass`, `.less`                | Stylesheets      | Tree-sitter (style rules)                         | CSS rule blocks (selectors + declarations)             |
| Unknown extensions                               | Fallback         | Single string summary                             | Minimal metadata string (filename, path, ext)          |

**Note:**
- Update the ingestion pipeline to include appropriate chunking logic.
- Update this table accordingly to reflect the new file type, category, strategy, and embedding logic.


## Front End

Use **Claude Code CLI** to create new chat admin interfaces in the `codechat` repo.


## Backend

Write a Lambda function in Python (`lambda_function.py`) using the AWS free tier (1M requests/month) to handle user queries for the RAG pipeline. The logic should:

1. Embed the query with OpenAI’s `text-embedding-3-small` using `OPENAI_API_KEY` from environment variables  
2. Query Pinecone’s `repo-chunks` for top-5 chunks or the matching percentage  
3. Send context and query to **Gemini (`gemini-1.5-flash`)** using `GOOGLE_API_KEY`  
4. Return the answer to the frontend

Deploy in AWS Lambda with `PINECONE_API_KEY` in environment variables.


## VectorDB Sync

### Implementation & Usage

- Script: `codechat/vectordb_sync.py` (commit-range replay; supports A/M/D + rename)
- Workflow: `webroot/.github/workflows/vector_sync.yml` (runs on merges/pushes to `main`)

What it does
- Replays `BASE..HEAD` and expands changes into file-level A/M/D across the superproject and changed submodules.
- Handles renames by deleting the old path and indexing the new path (R → D old + M new).
- Add/Modify: pre-delete vectors for that `file_path`, then chunk → embed (OpenAI `text-embedding-3-small`) → upsert.
- Delete: remove vectors filtered by `repo_name` + `file_path`.
- Embeddings are content-only; `file_path` and other fields live in metadata so updates are precise and idempotent.

Secrets for VectorDB Sync (GitHub Actions)
1) In the webroot repo on GitHub, open Settings (top menu).
2) In the left sidebar under Security, select Secrets and variables > Actions.
3) Under Repository secrets, click New repository secret and add:
   - `PINECONE_API_KEY` (required)
   - `OPENAI_API_KEY` (required)
   - Optional serverless: `PINECONE_CLOUD=aws`, `PINECONE_REGION=us-east-1`
   - Optional classic: `PINECONE_ENV=us-west1-gcp`
   - Optional index: `PINECONE_INDEX=repo-chunks` (default)
4) (Optional) If you use Environments, click Manage environment secrets to scope secrets to an environment and add the same keys there.
5) Variables tab is for non‑secret values; do not place API keys there.

Local testing (real APIs; cleans up vectors)
- Ensure `codechat/.env` contains the keys above.
- Run: `python codechat/test_vectordb_sync.py`

Action logs and errors
- Actions → VectorDB Sync → open the run; expand the sync step to view logs.
- If errors occur, the workflow uploads `vector-sync-errors` (artifact with `codechat/.vector_sync_errors.jsonl`) and adds a summary to the job output.

