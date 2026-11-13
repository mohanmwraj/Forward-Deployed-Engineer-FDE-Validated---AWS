# ☁️ AWS Partner FDE Challenges Vault

> **Purpose:** working notes for the hands-on AWS Partner FDE challenges I need to pass to earn the credential. Each lab has its own folder. Inside it, each challenge gets one file: the task as given, the screenshots I took, the root cause, the fix that worked, mistakes I made along the way, and study notes for going deeper later.
> **Started:** 11 Nov 2026 · **Status legend:** ✅ passed · 🟡 in progress · ⬜ not started · ⚠️ needs improvement

---

## 🧪 Labs

| # | Lab | Focus | Challenges | Status |
|---|---|---|---|---|
| 01 | [AWS Data Lakehouse Demonstrated](01_AWS_Data_Lakehouse_Demonstrated/README.md) | Glue, Iceberg, Athena, Lake Formation, Firehose, Step Functions | A ✅ · B ✅ · C ✅ · D ✅ · E ✅ · F ✅ · G ⚠️ | ✅ **PASSED** 11 Nov 2026 · valid to 11 Nov 2027 · renew from 8 Aug 2027 |
| 02 | [AWS Databases for Agentic AI Demonstrated](02_AWS_Databases_For_Agentic_AI_Demonstrated/README.md) | Aurora PostgreSQL + pgvector, DynamoDB (agent memory), Bedrock Knowledge Bases, MCP servers, Lambda | A ✅ · B ✅ · C ✅ · D ✅ · E ✅ · F ✅ · G ✅ | ✅ **PASSED** 12 Nov 2026 · valid to 12 Nov 2027 · renew from 9 Aug 2027 |
| 03 | [AWS Agentic AI Demonstrated](03_AWS_Agentic_AI_Demonstrated/README.md) | Bedrock AgentCore (Runtime, Gateway, Memory), Guardrails, Cognito OAuth 2.0, OpenSearch Serverless KB, Lambda, VPC | A ✅ · B ✅ · C ✅ · D ✅ · E ✅ · F ✅ | ✅ **PASSED** 13 Nov 2026 · valid to 13 Nov 2027 · renew from ~10 Aug 2027 |
| 04 | [AWS Securing Agent Identities Demonstrated](04_AWS_Securing_Agent_Identities_Demonstrated/README.md) | AgentCore Identity (workload identities, inbound JWT / SigV4), IAM tag-based access control, Cognito scopes, EC2 + SSM (self-hosted agent), CloudTrail + CloudWatch audit | A 🟡 · B 🟡 · C 🟡 · D 🟡 · E 🟡 · F 🟡 | 🟡 in progress (started 13 Nov 2026) · 135 min |

_New labs are added as `05_<Lab_Name>/`, `06_<Lab_Name>/` and so on._

---

## 📘 Study guide (service reference)

**[00_AWS_Data_Services_Study_Guide](00_AWS_Data_Services_Study_Guide/README.md)** has one in-depth file per service used in the labs:
- S3, Apache Iceberg, Glue, Athena, Lake Formation, Data Firehose, EventBridge, Step Functions and Lambda
- IAM/CloudWatch foundations, and the source DBs (Aurora and DynamoDB)

Each file covers must-know facts, first principles, examples, troubleshooting, second-order thinking and a GCP mapping. The folder also has two end-to-end walkthroughs (one with 7 practice challenges), an exam cheat sheet with 35 practice questions, and a **[30-day voucher plan](00_AWS_Data_Services_Study_Guide/31_30_Day_Plan_For_FDE_Microcredentials.md)**.

---

## 🧭 Vault layout

```text
AWS_Partner_FDE_Challenges_Vault/
├── README.md ........................................ you are here (index of labs)
├── 00_AWS_Data_Services_Study_Guide/ ................ service deep dives, walkthroughs, cheat sheet, 30-day plan
├── 01_AWS_Data_Lakehouse_Demonstrated/
│   ├── README.md .................................... lab HLD + challenge tracker
│   ├── Challenge_A_Product_Catalog_Schema_Mismatch_And_Partitioning.md
│   ├── Challenge_B_Analytics_Query_Performance_Compaction_And_MOR.md
│   ├── Challenge_C_LF_Tag_Based_Access_Control_Data_Science_And_Intern.md
│   ├── Challenge_D_Firehose_Iceberg_Streaming_Upserts_And_Buffering.md
│   ├── Challenge_E_LF_Data_Cell_Filters_Marketing_And_Regional_Manager.md
│   ├── Challenge_F_Vendor_File_Pipeline_EventBridge_StepFunctions_Lambda.md
│   ├── Challenge_G_Orders_Ingest_Duplicates_And_Iceberg_Snapshot_Rollback.md
│   └── assets/
│       ├── 00_lakehouse_architecture_hld.png
│       ├── challenge_A/
│       ├── challenge_B/
│       ├── challenge_C/
│       ├── challenge_D/
│       ├── challenge_E/
│       ├── challenge_F/
│       └── challenge_G/
├── 02_AWS_Databases_For_Agentic_AI_Demonstrated/
│   ├── README.md .................................... result + resources + HLD + tracker
│   ├── Challenge_A_Product_Search_pgvector_Operator_Class_And_Composite_Index.md
│   ├── Challenge_B_DynamoDB_Agent_Memory_LangGraph_Checkpointer_Table.md
│   ├── Challenge_C_DynamoDB_MCP_Server_Region_Tables_Tool_Definitions.md
│   ├── Challenge_D_Aurora_Query_Tool_Least_Privilege_Secret_SSL_And_Summary_View.md
│   ├── Challenge_E_pgvector_Document_Embeddings_Table_HNSW_And_GIN_Indexes.md
│   ├── Challenge_F_Bedrock_Knowledge_Base_On_Aurora_S3_Data_Sources_Sync.md
│   ├── Challenge_G_Aurora_MCP_Server_Agent_Credentials_And_Explain_Query_Tool.md
│   └── assets/ .................................. HLD, exam result, challenge_<X>/ screenshots + code/
├── 03_AWS_Agentic_AI_Demonstrated/
│   ├── README.md .................................... result + resources + HLD + tracker
│   ├── Challenge_A_Bedrock_Guardrails_Content_Safety_Word_PII_Regex_Filters.md
│   ├── Challenge_B_Cognito_OAuth2_M2M_Client_Credentials_JWT_Authorizers.md
│   ├── Challenge_C_AgentCore_Gateway_Tool_Routing_GATEWAY_URL_Lambda_Targets.md
│   ├── Challenge_D_Bedrock_KB_OpenSearch_Serverless_KB_Specialist_Runtime_A2A.md
│   ├── Challenge_E_AgentCore_Memory_Strategies_Namespaces_MEMORY_ID.md
│   ├── Challenge_F_VPC_Networking_Interface_Endpoints_PrivateLink_Runtimes.md
│   └── assets/ .................................. HLD, challenge_<X>/ screenshots
└── 04_AWS_Securing_Agent_Identities_Demonstrated/
    ├── README.md .................................... brief + objectives + identity primer + tracker
    ├── Challenge_<X>_<Short_Title>.md ............... one per challenge, added as I go
    └── assets/
```

Every challenge file follows the same layout:

1. **Status checklist:** the success criteria, ticked off as each one passes
2. **Task card:** the screenshot of the task, plus a text copy
3. **Where it sits in the architecture**
4. **Root cause**
5. **Solution:** the steps and code that worked
6. **Mistakes & lessons:** screenshots of what went wrong and why
7. **Troubleshooting table**
8. **Study notes:** concepts to learn properly afterwards, with self-test questions
9. **Run log:** the actual error text and outputs I saw, filled in as I go

---

## 🧠 Lessons that apply across labs

- **Know where each piece of code runs.** Console SQL editors (Athena) run SQL only. PySpark goes in a Glue job script. *(Lakehouse A)*
- **Use the lab's preconfigured resources** (workgroups, roles, saved queries) instead of defaults like `primary`. *(Lakehouse A)*
- **Read the success criteria literally.** If they say a specific job must succeed, make the fix inside that job. *(Lakehouse A)*
- **When a command "has no effect", look at the settings that govern it** (thresholds, retention, quotas) before assuming the command is broken. *(Lakehouse B)*
- **Grant to the exact principal your console session uses.** Check the account menu, because federated and assumed role names often differ from what you'd expect. *(Lakehouse C)*
- **After editing a managed service's config (Firehose, etc.), wait for it to return to *Active* before you check.** *(Lakehouse D)*
- **Prefer allow-lists to deny-lists for sensitive data**, so new columns stay hidden by default. *(Lakehouse E)*
- **Code edits in managed consoles aren't live until you deploy or save** (Lambda **Deploy**, Step Functions **Save**, Glue **Save**). My first Challenge F check failed only because the Lambda wasn't deployed. There's a per-service table under *First-time console gotchas* in [Challenge F](01_AWS_Data_Lakehouse_Demonstrated/Challenge_F_Vendor_File_Pipeline_EventBridge_StepFunctions_Lambda.md). *(Lakehouse A, F)*
- **Fix the cause and repair the damage as two separate steps.** Fixing the job stops new bad data, and restoring a snapshot removes what's already there. Don't re-run the job between the restore and the check. *(Lakehouse G)*
- **Check which database user you are before DDL.** In PostgreSQL, schema changes need *ownership*, not GRANTs. Use the admin secret for DDL, and keep the agent secret read-only. *(Agentic DB A)*
- **Read the real config instead of guessing from examples.** The index opclass decides the vector operator, and the library's docs decide the table keys. Sample queries and `KEY_SCHEMA`-style hints can be decoys. *(Agentic DB A, B)*
- **Look for missing settings, not just wrong ones.** Add the secret ARN, remove the plaintext password, and fix decoy cluster or DB names. *(Agentic DB D)*
- **When a handler is available, read it.** It shows exact argument names, parsing (`split(",")` without strip), and errors returned under a green "Succeeded". *(Agentic DB C, G)*
- **Debug as the agent, never as admin.** Elevated debug credentials hide the permission bugs you are looking for. *(Agentic DB G)*
- **Scope what an AI agent can read.** Ingest only the folders it should quote. Expose views instead of raw tables, and use read-only roles. *(Agentic DB D, F)*
- **A field/value table in the task notes describes one item, not a list of items.** Count the items before saving, and keep notes like *"(type it exactly)"* out of the values. *(Agentic AI A)*
- **Check which creation path the console put you on.** AgentCore has a config-only **harness** and a **deploy-your-own-code** Runtime. Also, an `s3:PutObject` denial on a timestamped key means the console is trying to upload. Choose the *existing artifact* option. *(Agentic AI D)*
- **When several challenges edit one shared resource, check that earlier settings survive each save.** Five of the six Lab 03 challenges changed the same orchestrator runtime's env vars. *(Agentic AI A–F)*
