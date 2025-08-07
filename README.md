# CodeChat

## RAG Pipeline Documentation

The RAG pipeline processes files from a local repository (e.g., `modelearth/localsite`) by chunking them using **Tree-sitter**, embedding chunks with 

**OpenAI’s `text-embedding-3-small`**, and storing them in **Pinecone VectorDB** with metadata (`repo_name`, `file_path`, `file_type`, `chunk_type`, `line_range`, `content`).  Get $5 in credits, you won't need them all.

Users will query via a **frontend**, where an **AWS Lambda backend** embeds the question, searches Pinecone for relevant chunks, queries 

**Gemini (`gemini-1.5-flash`)** for answers, and returns results to the frontend.

**GitHub Actions** syncs the VectorDB by detecting PR merges, pulling changed files, re-chunking, re-embedding, and updating Pinecone. This enables a scalable Q&A system for codebase and documentation queries.

Add your 3 keys to .env and run to test the RAG process (Mac version):
Claude will install: python-dotenv pinecone-client openai google-generativeai

Windows PC

	python -m venv env
	env\Scripts\activate.bat

Mac/Linux

	python3 -m venv env
	source env/bin/activate

Start

	python rag_query_test.py

Or start Claude

	npx @anthropic-ai/claude-code


## ModelEarth webroot (MAIN RAG)

<a href="http://localhost:3001/" style="float:right">Runs on port 3001</a>

Fork the [modelearth webroot](https://github.com/modelearth/modelearth/) and run the [local install steps with Claude](https://model.earth/modelearth/).  
This webroot is a fork of Anything LLM NextJS with modelearth repos as submoduoles.

| Name | Repository | Description |
|------|------------|-------------|
| [codechat](../codechat/) | [github.com/modelearth/codechat](https://github.com/modelearth/codechat) | Code chat interface development |
| [home](../home/) | [github.com/modelearth/home](https://github.com/modelearth/home) | Everybody's Home Page |
| [localsite](../localsite/) | [github.com/modelearth/localsite](https://github.com/modelearth/localsite) | Core CSS / JS utilities, timeline, tabulator |
| [team](../team/) | [github.com/modelearth/team](https://github.com/modelearth/team) | Rust REST API for Azure |
| [realitystream](../realitystream/) | [github.com/modelearth/realitystream](https://github.com/modelearth/realitystream) | ML Run Models Colab) |
| [cloud](../cloud/) | [github.com/modelearth/cloud](https://github.com/modelearth/cloud) | Flask hosting of colabs |
| [feed](../feed/) | [github.com/modelearth/feed](https://github.com/modelearth/feed) | FeedPlayer video/gallery |
| [swiper](../swiper/) | [github.com/modelearth/swiper](https://github.com/modelearth/swiper) | UI swiper components |
| [comparison](../comparison/) | [github.com/modelearth/comparison](https://github.com/modelearth/comparison) | Trade Flow tools |
| [projects](../projects/) | [github.com/modelearth/projects](https://github.com/modelearth/projects) | Overview and TODOs |
<br>

## MaterialScience webroot

<a href="http://localhost:8888/" style="float:right">Runs on port 8888</a>

These repos focus on material science, environmental impact, and supply chain analysis tools.

| Name | Repository | Description |
|------|------------|-------------|
| [MaterialScience](../MaterialScience/) | [github.com/modelearth/MaterialScience](https://github.com/modelearth/MaterialScience) | MaterialScience webroot |
| [products](../products/) | [github.com/modelearth/products](https://github.com/modelearth/products) | Products frontend and python |
| [products-data](../products-data/) | [github.com/modelearth/products-data](https://github.com/modelearth/products-data) | Products data output |
| [profile](../profile/) | [github.com/modelearth/profile](https://github.com/modelearth/profile) | Profile frontend analysis |
| [exiobase](../exiobase/) | [github.com/modelearth/exiobase](https://github.com/modelearth/exiobase) | Trade flow output to .csv and SQL |
| [io](../io/) | [github.com/modelearth/io](https://github.com/modelearth/io) | Input-output analysis |
| [useeio.js](../useeio.js/) | [github.com/modelearth/useeio.js](https://github.com/modelearth/useeio.js) | JavaScript footprint tools |
| [useeio-widgets](../useeio-widgets/) | [github.com/USEPA/useeio-widgets](https://github.com/USEPA/useeio-widgets) | USEEIO React widgets |
| [useeio-widgets-without-react](../useeio-widgets-without-react/) | [github.com/modelearth/useeio-widgets-without-react](https://github.com/modelearth/useeio-widgets-without-react) | USEEIO widgets without React |
| [useeiopy](../useeiopy/) | [github.com/USEPA/useeiopy](https://github.com/USEPA/useeiopy) | Python USEEIO library |
| [useeio_api](../useeio_api/) | [github.com/USEPA/useeio_api](https://github.com/USEPA/useeio_api) | USEEIO REST API |
| [useeio](../useeio/) | [github.com/USEPA/useeio](https://github.com/USEPA/useeio) | Core USEEIO model |
| [useeior](../useeior/) | [github.com/USEPA/useeior](https://github.com/USEPA/useeior) | R package for USEEIO |
| [useeio-state](../useeio-state/) | [github.com/modelearth/useeio-state](https://github.com/modelearth/useeio-state) | State-level USEEIO data |
| [useeio-json](../useeio-json/) | [github.com/modelearth/useeio-json](https://github.com/modelearth/useeio-json) | USEEIO JSON data |
| [mario](../mario/) | [github.com/modelearth/mario](https://github.com/modelearth/mario) | Multi-regional input-output |
| [localsite](../localsite/) | [github.com/modelearth/localsite](https://github.com/modelearth/localsite) | Core CSS / JS utilities, timeline, tabulator |
| [team](../team/) | [github.com/modelearth/team](https://github.com/modelearth/team) | Rust REST API for Azure |

<br>

## PartnerTools webroot

<a href="http://localhost:8887/" style="float:right">Runs on port 8887</a>

Starter webroot for submodule additions based on prompter choices and config setting.

| Name | Repository | Description |
|------|------------|-------------|
| [webroot](../PartnerTools) | [github.com/modelearth/webroot](https://github.com/modelearth/PartnerTools) | PartnerTools webroot |
| [team](../team/) | [github.com/modelearth/team](https://github.com/modelearth/team) | Rust REST API for Azure |
| [localsite](../localsite/) | [github.com/modelearth/localsite](https://github.com/modelearth/localsite) | Core CSS / JS utilities, timeline, tabulator |
| [feed](../feed/) | [github.com/modelearth/feed](https://github.com/modelearth/feed) | FeedPlayer video/gallery |
| [swiper](../swiper/) | [github.com/modelearth/swiper](https://github.com/modelearth/swiper) | UI swiper components |
| [comparison](../comparison/) | [github.com/modelearth/comparison](https://github.com/modelearth/comparison) | Trade Flow tools |
| [products](../products/) | [github.com/modelearth/projects](https://github.com/modelearth/projects) | Overview and TODOs |
<br>

## Data-Pipeline - static output

These output repos may be pulled into local webroots during data processing, but we avoid committing these as a submodules in the webroots due to their large size. The static data in these repos is pulled directly through Github Pages and the Cloudflare CDN.

| Name | Repository | Description |
|------|------------|-------------|
| [data-pipeline](../data-pipeline/) | [github.com/modelearth/data-pipeline](https://github.com/modelearth/data-pipeline) | Python data processing pipeline |
| [community-data](../community-data/) | [github.com/modelearth/community-data](https://github.com/modelearth/community-data) | Community-level data outputs |
| [community-timelines](../community-timelines/) | [github.com/modelearth/community-timelines](https://github.com/modelearth/community-timelines) | Timeline data for communities |
| [community-zipcodes](../community-zipcodes/) | [github.com/modelearth/community-zipcodes](https://github.com/modelearth/community-zipcodes) | ZIP code level community data |
| [community-forecasting](../community-forecasting/) | [github.com/modelearth/community-forecasting](https://github.com/modelearth/community-forecasting) | Forecasting frontend (legacy) |
| [dataflow](../dataflow/) | [github.com/modelearth/dataflow](https://github.com/modelearth/dataflow) | Data flow NextJS UX |

<br>

## TODO

- Chunk, Embed, Store in VectorDB - **Modelearth repos** (listed above and in [modelearth/submodules.jsx](https://github.com/modelearth/modelearth)) - Lokesh
- Chunk, Embed, Store in VectorDB - **Team JAM Stack with Rust API and Azure** (`team`) 
- Chunk, Embed, Store in VectorDB - **IO repos** (`exiobase/tradeflow`, `profile`, `io`, `useeio.js`, `useeio-widgets`, `useeio-widgets-without-react`, `useeiopy`, `useeio_api`, `useeio`, `useeior`, `useeio-state`, `useeio-json`)
- Chunk, Embed, Store in VectorDB - **Python Pipeline and output repos** (`data-pipeline`, `community-data`, `community-timelines`, `community-zipcodes`, `community-forecasting`)
- Reuse pages in our [Modelearth](https://model.earth/modelearth/) fork of AnythingLLM for Chat Page starters
- Write AWS Lambda Backend (embed queries, fetch from Pinecone, and query Gemini)
- Sync VectorDB with PRs (GitHub Actions on PR merges)

---

## More Context

**Chunk, Embed, Store** – check out `rag_ingestion_pipeline.ipynb`

- I have used Tree-sitter for chunking; explore better strategies if available
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

---

## Front End

Reuse pages in our [Modelearth](https://model.earth/modelearth/) fork of AnythingLLM for Chat Page starters

Use **Claude Code CLI** to create new chat admin interfaces in the `codechat` repo.

---

## Backend

Write a Lambda function in Python (`lambda_function.py`) using the AWS free tier (1M requests/month) to handle user queries for the RAG pipeline. The logic should:

1. Embed the query with OpenAI’s `text-embedding-3-small` using `OPENAI_API_KEY` from environment variables  
2. Query Pinecone’s `repo-chunks` for top-5 chunks or the matching percentage  
3. Send context and query to **Gemini (`gemini-1.5-flash`)** using `GOOGLE_API_KEY`  
4. Return the answer to the frontend

Deploy in AWS Lambda with `PINECONE_API_KEY` in environment variables.

---

## VectorDB Sync

GitHub sync — develop a solution for how we can sync the PR to the vector DB.  
My solution is: we are having the `file_path` in the metadata, right? So whenever the PR is merged, we will replace all vectors related to that file with the updated file vectors.  
We are doing this in GitHub Actions, so chunking should be lightweight.

For the initial load, we used Tree-sitter. But try to figure out that if the PR is a Python file, then we only build Tree-sitter Python and chunk it.  
Embedding would obviously be OpenAI’s small model since it's lightweight.

---

## Future Enhancements

Now we set up 5 RAG training filesets, which we'll combine as agents to support broader questions about the entire system.  
Filesets 1, 2, and 3 can optionally be grouped into the same RAG, depending on overlap and use case.  
Each RAG will handle a specific part of the system, and combining them lets us scale to system-level Q&A across multiple domains.
