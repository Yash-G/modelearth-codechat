# codechat

# RAG Pipeline Documentation

The RAG pipeline processes files from a local repository (e.g., `ModelEarth/localsite`) by chunking them using **Tree-sitter**, embedding chunks with **OpenAI’s `text-embedding-3-small`**, and storing them in **Pinecone VectorDB** with metadata (`repo_name`, `file_path`, `file_type`, `chunk_type`, `line_range`, `content`).

Users query via a **frontend**, where an **AWS Lambda backend** embeds the question, searches Pinecone for relevant chunks, queries **Gemini (`gemini-1.5-flash`)** for answers, and returns results to the frontend.

**GitHub Actions** syncs the VectorDB by detecting PR merges, pulling changed files, re-chunking, re-embedding, and updating Pinecone. This enables a scalable Q&A system for codebase and documentation queries.

---

## TODO

- Chunk, Embed, Store in VectorDB - **NextJS repos** (`AnythingLLM`, `DataFlow`, `feed`, `swiper`)
- Chunk, Embed, Store in VectorDB - **JAM Stack repos** (`Team`, `Project`, `Localsite`) - Lokesh
- Chunk, Embed, Store in VectorDB - **RealityStream** colab and repo, and `cloud/run` folder
- Chunk, Embed, Store in VectorDB - **SQL/IO repos** (`profile`, `exiobase`, `io`, `useeio.js`, `useeio-widgets`, `useeio-widgets-without-react`, `useeiopy`, `useeio_api`, `useeio`, `useeior`, `useeio-state`, `useeio-json`)
- Chunk, Embed, Store in VectorDB - **Python Pipeline Repos** (`data-pipeline`, `community-data`, `community-timelines`, `community-zipcodes`, `community-forecasting`, first 5 CSV rows)
- Set Up Frontend Chat Page using CLI or Prepare a prompt
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

**Note** : 
- Update the ingestion pipeline to include appropriate chunking logic.
- Update this table accordingly to reflect the new file type, category, strategy, and embedding logic.
---

## Front End

Use **Claude Code CLI** to generate a chat admin interface in the `codechat` repo with a prompt.

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
