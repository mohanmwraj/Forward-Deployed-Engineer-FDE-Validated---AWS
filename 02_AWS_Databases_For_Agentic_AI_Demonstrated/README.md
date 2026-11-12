# 🤖 AWS Databases for Agentic AI Demonstrated

> **Lab:** "AWS Databases for Agentic AI Demonstrated", one of the challenge sets for the AWS Partner FDE credential.
> **Theme:** build and troubleshoot the data layer behind an AI agent: Aurora PostgreSQL + pgvector and DynamoDB for agent access and memory, Bedrock Knowledge Bases for document retrieval, MCP servers for debugging agent ↔ database calls, and query tuning.
> **App:** *AnyCompany Insights* chat app (resource prefix `insightflow-`) · **Region:** `us-east-1` only · **Lab resources:** see *🔑 Lab resources* below
> **Started:** 12 Nov 2026 · **Status legend:** ✅ passed · 🟡 in progress · ⬜ not started · ⚠️ needs improvement
> **Back to:** [Vault index](../README.md)

---

## 🏆 Result: _pending_

| | |
|---|---|
| **Microcredential** | AWS Databases for Agentic AI Demonstrated |
| **Result** | 🟡 In progress |
| **Pass date** | _—_ |
| **Valid until** | _—_ (Lab 01 was valid for one year from the pass date) |
| **Renew / retake from** | _—_ |
| **Badge** | Claim it from the **Credly** email, then add it to the **AWS Skills Profile** |

_Add the result screenshot as `assets/00_exam_result.png` when I have it._

---

## 🔑 Lab resources (Solution Resources panel)

> ⚠️ **These values change with every lab launch.** The suffix (`b55df330` here), the account ID and the URLs are all new each time. Copy them again from the panel and don't reuse old ones.

| Output | Value (this launch) | HLD component |
|---|---|---|
| `ChatAppURL` | https://d1s22585v8e7wl.cloudfront.net | CloudFront web app: use it to check the whole flow after each fix |
| `APIEndpoint` (also `InsightFlowAPIEndpoint…`) | https://rg43bobdb8.execute-api.us-east-1.amazonaws.com/prod/ | API Gateway (Cognito authorizer) |
| `OrchestratorFunctionName` | `insightflow-agent-b55df330` | Lambda (LangGraph agent) |
| `AuroraToolFunctionName` | `insightflow-aurora-query-tool-b55df330` | Lambda (query customers), **D** |
| `KBRetrieveToolFunctionName` | `insightflow-kb-retrieve-tool-b55df330` | Lambda (kb-retrieve-tool) |
| `DynamoDBToolFunctionName` | `insightflow-dynamodb-tool-b55df330` | Not drawn as its own box. **Not** B: B's checkpointer runs inside the agent Lambda. Probably a DynamoDB data tool the agent calls |
| `DynamoDBMCPFunctionName` | `insightflow-dynamodb-mcp-server-b55df330` | Lambda (DynamoDB MCP Server), **C** |
| `AuroraMCPFunctionName` | `insightflow-aurora-mcp-server-b55df330` | Lambda (Aurora MCP Server), **G** |
| `AuroraClusterARN` | `arn:aws:rds:us-east-1:987347315034:cluster:insightflow-cluster-b55df330` | Amazon Aurora (pgvector), **A** |
| `AuroraAgentSecretARN` | `arn:aws:secretsmanager:us-east-1:987347315034:secret:insightflow/aurora-agent-creds-b55df330-lR5jK1` | Secrets Manager → Aurora, **E** |
| `DocsBucketName` | `insightflow-documents-b55df330` | S3 bucket → Knowledge Base ingestion, **F** |

**Not in the panel, but given on task cards:**
- **Database name:** `insightflow` *(Challenge A)*
- **Admin DB secret:** `insightflow/aurora-admin-creds`, used for DDL in the Query Editor *(Challenge A)*. The panel's `aurora-agent-creds` secret is the agent's own lower-privilege user.
- **DynamoDB tables:** `agent-state` (original, wrong key schema, so leave it) and **`agent-checkpoints`** (created in B: `PK`/`SK` String, TTL `ttl`, on-demand) *(Challenge B)*
- **Agent Lambda env vars:** `CHECKPOINT_TABLE_NAME`, `AWS_REGION_OVERRIDE`, `KEY_SCHEMA` (a decoy) *(Challenge B)*
- **DynamoDB MCP server:** env vars `AWS_REGION_OVERRIDE`, `TABLE_NAMES` (allow-list: `user-sessions`, `agent-checkpoints`). Tool catalog in the bundled `tool_definitions.json` (`describe_table`, `sample_items`, `analyze_access_patterns`, …). Table `user-sessions` is pre-built *(Challenge C)*

**Not in the panel. Find these in the console when a challenge needs them:**
- the DynamoDB table name(s)
- the Knowledge Base ID and data source
- the Cognito user pool

Each Lambda's logs are in CloudWatch log group `/aws/lambda/<function-name>`.

### Lab rules (from the panel)

- **Console only, and no application code.** The tools are the **RDS Query Editor**, **Lambda test events** and the chat app. Expect fixes to be configuration, SQL, environment variables or secret values, not code.
- **IAM is preconfigured, and I don't need to change IAM for any task.** If something says "access denied", look first at the **database layer** (PostgreSQL `GRANT`s and roles, what's in the secret) or at resource config, not at IAM policies.
- **Region `us-east-1` only.** Check it before every console action.
- **Ignore `dbqms:CreateQueryHistory` errors in the Query Editor.** They only affect saving query history. The statement still runs.
- The panel describes the work as *"repair its database connections"*, which suggests most challenges are broken connections between the agent's tools and Aurora/DynamoDB.

### Testing toolkit

| Tool | How | What it tells me |
|---|---|---|
| **RDS Query Editor** | RDS console → **Query editor** → cluster `insightflow-cluster-…` → *Connect with a Secrets Manager ARN* → secret → database `insightflow` | **Admin secret** (`insightflow/aurora-admin-creds`) for DDL fixes. **Agent secret** (`AuroraAgentSecretARN`) to see exactly what the agent is allowed to see. It needs the cluster's **RDS Data API** enabled ⚠️ |
| **Lambda test events** | Lambda → function → **Test** tab → event JSON → **Test** | Calls one tool or MCP server on its own, without going through the agent |
| **CloudWatch Logs** | `/aws/lambda/<function-name>` → latest log stream | The real error behind a vague chat reply |
| **Chat app** | Open `ChatAppURL`, ask a question that needs the repaired tool | The final end-to-end check |

---

## 🎯 Scope (from the AWS announcement, 29 Sep 2026)

> "Prove you can build and troubleshoot the data layer that powers agentic AI. You'll configure Amazon Aurora PostgreSQL and Amazon DynamoDB for agent access and memory, set up pgvector and Amazon Bedrock Knowledge Bases for document retrieval, configure MCP servers to debug agent database interactions, and optimize the agent's database queries."

**Services named:** Amazon Aurora PostgreSQL, Amazon DynamoDB, Amazon Bedrock, AWS Lambda, Amazon CloudWatch, AWS Secrets Manager.
**Format:** a hands-on, timed lab in a live AWS account. No multiple choice and no hints: "You either fix the problem or you don't." Free on AWS Skill Builder. The announcement gives no challenge count, duration or passing score.

| Skill in scope | What I expect to touch | Study guide coverage today |
|---|---|---|
| Aurora PostgreSQL for agent access | DB users/roles, Secrets Manager credentials, RDS Data API or JDBC, security groups | [10 Sources: Aurora & DynamoDB](../00_AWS_Data_Services_Study_Guide/10_Source_Systems_Aurora_PostgreSQL_And_DynamoDB.md) (as a lakehouse source only) |
| DynamoDB for agent memory | Key design for sessions/conversations, TTL, GSIs, IAM conditions | Same file, ETL angle only |
| pgvector | `vector` extension, embedding columns, HNSW / IVFFlat indexes, distance operators | ⬜ not yet. Will add a file when the first challenge uses it |
| Bedrock Knowledge Bases | Data source (S3) → chunking → embeddings → vector store (Aurora), sync jobs, retrieval | ⬜ not yet |
| MCP servers | MCP server config for the database, tools the agent calls, reading the traces | ⬜ not yet |
| Query optimisation | `EXPLAIN ANALYZE`, indexes, filtered vector search | ⬜ not yet |
| Lambda / CloudWatch / Secrets Manager | Agent action functions, logs, DB credentials | [09 Lambda](../00_AWS_Data_Services_Study_Guide/09_AWS_Lambda.md) · [00 Foundations](../00_AWS_Data_Services_Study_Guide/00_AWS_Foundations_IAM_Regions_CLI_CloudWatch_KMS.md) |

_As each challenge confirms which services it uses, I'll add a service deep dive to the study guide for any gap marked ⬜ and link it here._

---

## 🗺️ Lab architecture (HLD)

![AWS Databases for Agentic AI Demonstrated: high-level design](assets/00_architecture_hld.png)

The lettered circles on the diagram mark where each challenge happens. I'll confirm each row's focus when its task card arrives, as I did in Lab 01.

| Label | Component on the diagram | Data flow | Likely focus (confirm from the task card) |
|---|---|---|---|
| **A** | **Amazon Aurora (pgvector)**, where the *Query data* arrow comes in | Query-customers Lambda → SQL → Aurora; Knowledge Bases also stores its vectors here | Aurora/pgvector setup or query performance (indexes, `EXPLAIN`) |
| **B** | **Amazon DynamoDB**, on the *Save state* arrow | LangGraph agent Lambda → `DynamoDBSaver` checkpoints → DynamoDB | ✔️ **Confirmed:** new `agent-checkpoints` table (`PK`/`SK` String, TTL `ttl`, on-demand) + the agent Lambda's env vars |
| **C** | **AWS Lambda (DynamoDB MCP Server)** | Developers/DBAs → *Invoke tools* → MCP server → *Inspect tables* → DynamoDB | ✔️ **Confirmed:** Region + `TABLE_NAMES` env vars, `max_results` type and missing `analyze_access_patterns` in `tool_definitions.json` |
| **D** | **Lambda function (query customers)** | LangGraph agent → *Query customers* → this Lambda → *Query data* → Aurora; *Write logs* → CloudWatch | The agent's database tool: SQL, connection or credentials, logging |
| **E** | **Aurora ← AWS Secrets Manager**, on the *Get credentials* arrow | Secrets Manager → credentials → Aurora access | DB credentials: secret contents, rotation, who can read the secret |
| **F** | **S3 bucket → Amazon Bedrock Knowledge Bases**, on the *Ingest docs* arrow | Docs in S3 → ingest (sync) → chunk + embed → store vectors in Aurora | KB data source, sync/ingestion, the pgvector table KB writes to |
| **G** | **Lambda function (Aurora MCP Server)** | Developers/DBAs → *Invoke tools* → MCP server → *Query data* → Aurora | MCP server config so DBAs can debug the agent's SQL |

### The three paths through the diagram

```text
1. Request path (end users)
   End users → CloudFront (web app on S3) → /api → API Gateway (Cognito authorizer)
             → Lambda (LangGraph agent) ──┬─ Invoke model ──→ Amazon Bedrock (Nova Pro)
                                          ├─ Query customers → Lambda (query customers)  [D] → Aurora pgvector [A]
                                          ├─ Retrieve docs ──→ Lambda (kb-retrieve-tool) → Bedrock Knowledge Bases
                                          └─ Save state ─────→ DynamoDB  [B]
   Both tool Lambdas → Write logs → CloudWatch Logs

2. Knowledge ingestion path
   S3 bucket (docs) → Ingest docs → Bedrock Knowledge Bases [F] → Store vectors → Aurora pgvector [A]
   Secrets Manager → Get credentials → Aurora [E]

3. Developer / DBA debugging path (MCP)
   Developers/DBAs → Invoke tools → Lambda (DynamoDB MCP Server) [C] → Inspect tables → DynamoDB
   Developers/DBAs → Invoke tools → Lambda (Aurora MCP Server)   [G] → Query data     → Aurora
```

**Aurora is used by four things here:** the agent's SQL tool (D), the Knowledge Base's vector store (F), the Aurora MCP server (G) and Secrets Manager credentials (E). A wrong grant, secret or index on Aurora can affect several challenges at once.

**Other services on the HLD** (not in the announcement's list): CloudFront + S3 for the web app, API Gateway with a Cognito authorizer, Bedrock **Nova Pro** as the agent's model, and **LangGraph** as the agent framework running in Lambda.

---

## 📋 Challenge tracker

| # | Challenge | Key services | Status | Notes |
|---|---|---|---|---|
| A | Optimize the agent's product search queries | Aurora PostgreSQL, pgvector (operator ↔ opclass), B-tree composite index, EXPLAIN | 🟡 In progress | [Challenge_A](Challenge_A_Product_Search_pgvector_Operator_Class_And_Composite_Index.md) |
| B | Configure Amazon DynamoDB for agent memory | DynamoDB (new table `PK`/`SK` + TTL `ttl`, on-demand), Lambda env vars, LangGraph `DynamoDBSaver` | 🟡 In progress | [Challenge_B](Challenge_B_DynamoDB_Agent_Memory_LangGraph_Checkpointer_Table.md) |
| C | Configure the DynamoDB MCP server for state inspection | Lambda (env vars, Code tab, Deploy, test events), MCP `tool_definitions.json` (JSON Schema), DynamoDB DescribeTable | 🟡 In progress | [Challenge_C](Challenge_C_DynamoDB_MCP_Server_Region_Tables_Tool_Definitions.md) |
| D | _Query-customers tool Lambda_ | Lambda, Aurora, CloudWatch | ⬜ | |
| E | _Aurora credentials_ | Secrets Manager, Aurora | ⬜ | |
| F | _Knowledge Base ingestion_ | S3, Bedrock Knowledge Bases, Aurora pgvector | ⬜ | |
| G | _Aurora MCP server_ | Lambda, MCP, Aurora | ⬜ | |

_Rows A–G are placeholders keyed to the diagram labels. I'll rename each one when I see its task card._

Each challenge file uses the same layout as Lab 01: status checklist → task card → where it sits in the architecture → root cause → solution → mistakes & lessons → troubleshooting table → study notes (with self-test) → run log.

---

## 🧭 Folder layout

```text
02_AWS_Databases_For_Agentic_AI_Demonstrated/
├── README.md ................................. you are here (scope + HLD + tracker)
├── Challenge_A_Product_Search_pgvector_Operator_Class_And_Composite_Index.md
├── Challenge_B_DynamoDB_Agent_Memory_LangGraph_Checkpointer_Table.md
├── Challenge_C_DynamoDB_MCP_Server_Region_Tables_Tool_Definitions.md
├── Challenge_<X>_<Short_Title>.md ............ one file per challenge, added as I post them
└── assets/
    ├── 00_architecture_hld.png ............... shared architecture diagram
    ├── challenge_A/ .......................... screenshots for Challenge A
    ├── challenge_B/ .......................... screenshots for Challenge B
    ├── challenge_C/ .......................... screenshots for Challenge C
    └── challenge_<X>/ ........................ screenshots for each challenge
```

---

## 🔁 Carry-over from Lab 01 (likely to matter here too)

- **Edit ≠ live.** Lambda needs **Deploy**, and Bedrock agents need **Prepare** after changes (⚠️ check how the lab's agent is hosted). Knowledge Base data sources need a **Sync** before new documents are searchable.
- **Use the lab's preconfigured resources** (secrets, roles, clusters, saved queries) rather than creating new ones.
- **Read the success criteria literally.** If they name a function, table or index, the fix goes there.
- **Grant to the exact principal** that makes the call. IAM is preconfigured in this lab, so here that means the **PostgreSQL user stored in the secret** (`GRANT … TO <agent user>`), not an IAM role.
- **Fix the cause, then repair the damage** as two separate steps.

---

## 🧠 Lessons from this lab (running list)

- **Check who you're connected as before any DDL.** In PostgreSQL, `CREATE INDEX`, `CREATE OR REPLACE FUNCTION` and `ANALYZE` need **ownership**, not `GRANT`s. The panel's `AuroraAgentSecretARN` is the low-privilege **agent** user. DDL needs the **admin** secret (`insightflow/aurora-admin-creds`), whose ARN you copy from Secrets Manager. Run `SELECT current_user;` first. *(A)*
- **Read the index's operator class. Don't infer it from sample queries.** The index was `vector_cosine_ops` (needs `<=>`), while the function and the task's diagnostic queries used `<->`. Find it with `pg_indexes` / `pg_opclass` first, then make the operator match. *(A)*
- **The Query editor's "success" can hide a skip.** A non-owner's `ANALYZE` returns *success / no rows changed* without doing anything. *(A)*
