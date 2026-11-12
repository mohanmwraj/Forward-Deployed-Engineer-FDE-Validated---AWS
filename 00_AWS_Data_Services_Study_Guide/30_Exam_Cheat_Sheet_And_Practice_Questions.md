# 🎯 Exam Cheat Sheet & Practice Questions (AWS data lakehouse stack)

> **Use this for:** the last review before an FDE exam lab, and DEA-C01-style multiple-choice practice.
> **Covers:** S3 · Iceberg · Glue · Athena · Lake Formation · Firehose · EventBridge · Step Functions · Lambda · IAM/CloudWatch
> **As of:** Nov 2026 · ⚠️ = numbers or labels that change, so verify them in the docs before relying on them
> **Back to:** [Study guide index](README.md)

---

## ⭐ Part 1: Lab tactics (learned the hard way)

These cost me time or points in *AWS Data Lakehouse Demonstrated*. Check them every lab.

| # | Tactic | Why |
|---|---|---|
| 1 | **Read every task card first**, then start the **slowest** step (Glue job runs, Firehose updates, crawlers) before anything else | I ran out of time on Challenge G because its job runs came last |
| 2 | **Check the region** (top right) and **look up exact names**. Lab resources carry suffixes (`-7db76de0`) | Wrong region means empty consoles; guessed names don't match |
| 3 | **Athena: switch to the lab workgroup** (e.g. `anycompany-lakehouse`) | `primary` has no result location, and the saved queries live in the lab workgroup |
| 4 | **Athena = SQL only, one statement per run.** PySpark goes in the **Glue job script** | I pasted `spark.sql(...)` into Athena |
| 5 | **Edit ≠ live:** Lambda → **Deploy** · Glue / Step Functions → **Save** · Firehose → wait for **Active** | My Lambda fix failed Check because it wasn't deployed |
| 6 | **Read the hints in the scripts** (`# TODO`, `# HINT 1..4`). Adapt sample code to the script's own variable names | I pasted a generic template with the wrong names |
| 7 | **Success criteria are literal.** If they say "job X runs successfully", make the change *in job X* | The checker inspects that resource |
| 8 | **Check after each challenge**, not all at the end | You find mistakes while you still have time |
| 9 | **Don't re-run ingest jobs after a restore** unless the task asks | You'll re-add the duplicates you just removed |
| 10 | **Console confusing? Use CloudShell** (bottom-left of the console) with the CLI | Faster and deterministic |
| 11 | **Grant to the exact session role** shown in the account menu | Lake Formation grants are per principal |
| 12 | **New EventBridge console:** Event buses → `default` → **Rules**; use **Advanced builder** | "Scheduled rules (legacy)" is the wrong page |

---

## 🧭 Part 2: Service-selection decision tables

### Ingestion

| Need | Pick | Not this, because… |
|---|---|---|
| Stream → S3/Iceberg/Redshift with **no code**, minutes of latency OK | **Data Firehose** | Kinesis Data Streams needs consumers you write |
| Stream with **multiple consumers**, replay, ordering per shard, sub-second | **Kinesis Data Streams** | Firehose has no replay and only one destination per stream |
| Kafka API compatibility | **Amazon MSK** | Kinesis isn't Kafka |
| Database replication / CDC from RDS/Aurora/on-prem | **AWS DMS** (or zero-ETL ⚠️) | Glue JDBC is batch polling |
| Periodic batch pull from JDBC sources | **Glue job + JDBC connection** | Lambda has a 15-minute limit and no Spark |
| SaaS sources (Salesforce, etc.) | **Amazon AppFlow** ⚠️ | No custom code needed |
| React to a file landing in S3 | **S3 → EventBridge → Step Functions / Lambda** | Polling wastes money and adds latency |
| DynamoDB → lake | **Export to S3** (full/incremental), or **Streams** for near real time | Scanning the table burns read capacity |

### Transformation & compute

| Need | Pick | Not this, because… |
|---|---|---|
| Serverless Spark ETL, catalog-integrated | **Glue ETL job** | EMR means managing clusters |
| Huge or custom Spark/Hadoop, long-running clusters, full control | **EMR** (EC2 / Serverless / EKS) | Glue has less tuning control |
| Light per-file logic, < 15 min, small data | **Lambda** | Spark is overkill |
| SQL transform of lake data into new tables | **Athena CTAS / INSERT INTO / MERGE** | No cluster needed |
| Heavy BI on hot, structured data with joins and concurrency | **Redshift** | Athena is per-scan and less suited to dashboards at high concurrency |

### Orchestration & events

| Need | Pick | Not this, because… |
|---|---|---|
| Multi-step workflow with retries, branching, waiting on jobs | **Step Functions** (Standard) | Code-based retries are fragile |
| Very high volume, short (< 5 min) event processing | **Step Functions Express** | Standard is billed per state transition |
| Existing Airflow DAGs / complex dependency graphs | **MWAA** | Rewriting in ASL takes time |
| Simple Glue-only chains | **Glue workflows/triggers** | Fine, but limited to Glue |
| Cron / one-time schedules | **EventBridge Scheduler** | Scheduled *rules* are legacy |
| Route events by content to targets | **EventBridge rules** | SNS has limited filtering |
| Point-to-point source → filter → enrich → target | **EventBridge Pipes** | No glue Lambda needed |

### Query & serving

| Need | Pick |
|---|---|
| Ad-hoc SQL on S3, pay per query | **Athena** |
| Data warehouse, consistent low-latency BI | **Redshift** (+ Spectrum for S3) |
| Search / log analytics | **OpenSearch** |
| Dashboards | **QuickSight** (on Athena/Redshift) |

### Governance & security

| Need | Pick |
|---|---|
| Who can call which API | **IAM** (identity + resource policies) |
| Table/column grants for specific tables | **Lake Formation named-resource grants** |
| Scalable classification-based access (new tables auto-covered) | **LF-Tags (TBAC)** |
| Row-level / cell-level security | **LF data cell filters** |
| Share catalog tables across accounts | **Lake Formation + AWS RAM** (resource links) ⚠️ |
| Customer-managed encryption + audit | **SSE-KMS (CMK)** + **CloudTrail** |
| Find PII in S3 | **Amazon Macie** |

### Table format & layout

| Symptom / need | Pick |
|---|---|
| Updates/deletes/upserts on lake tables, ACID, time travel | **Apache Iceberg** |
| Many tiny files | **Compaction** (Athena OPTIMIZE / Spark rewrite_data_files) + bigger buffers |
| Too many snapshots / storage creep | **VACUUM / expire_snapshots** (keep enough for recovery) |
| Frequent upserts (CDC) | **Merge-on-read** + regular compaction |
| Read-heavy, rare updates | **Copy-on-write** |
| Hive table with many date partitions | **Partition projection** (Athena) |
| Query filter ≠ partition column | **Partition evolution** (Iceberg) |

---

## 🔑 Part 3: Keyword → service

| If the question says… | Think… |
|---|---|
| "serverless SQL", "query data in S3", "pay per query" | **Athena** |
| "near real-time", "no code", "deliver to S3 / Redshift / OpenSearch", "buffer" | **Firehose** |
| "convert JSON to Parquet in flight" | **Firehose record format conversion** (Glue schema) |
| "multiple consumers", "replay", "shards" | **Kinesis Data Streams** |
| "centralised permissions", "column-level", "row-level", "tag-based" | **Lake Formation** |
| "metadata", "schema", "table definitions", "Hive metastore" | **Glue Data Catalog** |
| "infer schema automatically" | **Glue crawler** (watch for wrong inferences) |
| "only process new files" in Glue | **Job bookmarks** |
| "data quality rules" | **Glue Data Quality (DQDL)** |
| "ACID", "time travel", "upsert", "schema evolution" on S3 | **Apache Iceberg** (or Hudi/Delta) |
| "too many small files" | **Compaction / OPTIMIZE** |
| "orchestrate", "retry with backoff", "wait for job to finish" | **Step Functions** (`.sync`) |
| "react when an object is created" | **S3 → EventBridge** (or S3 notifications → Lambda) |
| "run on a schedule" | **EventBridge Scheduler** |
| "short event-driven code" | **Lambda** |
| "cost control per team" in Athena | **Workgroups** + per-query scan limits |
| "audit who accessed" | **CloudTrail** (+ Lake Formation audit) |
| "encrypt with customer key" | **KMS (SSE-KMS)** |

---

## 🔢 Part 4: Numbers worth remembering (⚠️ verify all of these, since limits change)

| Service | Number |
|---|---|
| **Lambda** | Max timeout **15 min** · memory **128 MB – 10,240 MB** · `/tmp` up to **10 GB** · sync payload **6 MB** · async payload **256 KB** ⚠️ (may have increased) · default regional concurrency **1,000** (soft limit) |
| **Step Functions** | Standard: up to **1 year**, exactly-once, **25,000** history events · Express: up to **5 min**, at-least-once · payload **256 KiB** |
| **EventBridge** | Event size **256 KB** · **5 targets** per rule · default target retry **24 h / 185 attempts** |
| **Firehose** | Record ≤ **1,000 KiB** · `PutRecordBatch` ≤ **500 records / 4 MiB** · S3 buffer size **1–128 MiB**, interval **0–900 s** ⚠️ (default **5 MiB / 300 s**) |
| **S3** | Single PUT ≤ **5 GB** · multipart **10,000** parts, 5 MB–5 GB each · max object **50 TB** (raised from 5 TB in Dec 2025; older exam questions may still say 5 TB) · ~**3,500** write / **5,500** read requests per second **per prefix** · strong read-after-write consistency |
| **Athena** | **$5 per TB** scanned ⚠️, **10 MB** minimum per query · **one** SQL statement per execution · DML timeout **30 min** default (can be raised to 240) · ~**200** active DML queries in us-east-1 (soft limit) |
| **Glue** | 1 **DPU** = 4 vCPU + 16 GB · G.1X = 1 DPU, G.2X = 2 DPU · per-second billing, **1-min minimum** (Glue 2.0+) ⚠️ · Flex = cheaper, can be delayed |
| **Iceberg** | Legal type promotions: **int → long**, **float → double**, **decimal precision widen** · row-level deletes need **format v2** |
| **Athena Iceberg defaults** (checked Nov 2026) | `optimize_rewrite_data_file_threshold` **5** · `optimize_rewrite_delete_file_threshold` **2** · `vacuum_min_snapshots_to_keep` **1** · `vacuum_max_snapshot_age_seconds` **432000 (5 d)** · `vacuum_max_metadata_files_to_keep` **100** · VACUUM needs `s3:DeleteObject` or it silently deletes nothing |
| **Firehose → Iceberg** (checked Nov 2026) | Default operation **insert**. Upserts need operation = update via JQ or Lambda metadata · tables must be **v2** · retry duration 0–7200 s |

---

## 🧠 Part 5: The 12 traps that catch people

1. **Firehose to Iceberg without unique keys** only appends, so status updates become duplicates. *(D)*
2. **Retry ordering:** `States.ALL` must be **last and alone**.
3. **`.sync` vs no `.sync`:** without it, Step Functions only *starts* the Glue job and reports success immediately.
4. **Input transformer quoting:** strings get quotes around the placeholder (`"<key>"`).
5. **S3 → EventBridge needs the bucket toggle ON**, and **only new events** match.
6. **S3 event keys are URL-encoded.** Decode with `unquote_plus`.
7. **Lake Formation ≠ IAM.** IAM allow + no LF grant = *Insufficient Lake Formation permission(s)*.
8. **Changing LF-Tags needs ASSOCIATE** on the tag, even for admins. *(C)*
9. **Row filter strings are case-sensitive.** Check the actual values first. *(E)*
10. **Athena SET TBLPROPERTIES** only covers Athena-managed properties. `write.*.mode` and partition evolution need **Spark**. *(A, B)*
11. **Aggressive VACUUM destroys time travel and rollback.** *(B vs G)*
12. **Reading a whole prefix of full exports** multiplies the data. Scope by date or use MERGE. *(G)*

---

## 📝 Part 6: DEA-C01 domain map ⚠️

*(Weights from my memory of the exam guide. Verify on the official DEA-C01 page.)*

| Domain | ~Weight | Where in this guide |
|---|---|---|
| 1. Data Ingestion & Transformation | ~34% | 03 Glue, 06 Firehose, 07 EventBridge, 08 Step Functions, 09 Lambda, 10 Sources |
| 2. Data Store Management | ~26% | 01 S3, 02 Iceberg, 03 Glue Catalog, 04 Athena |
| 3. Data Operations & Support | ~22% | 00 Foundations (CloudWatch), troubleshooting tables, 08 Step Functions |
| 4. Data Security & Governance | ~18% | 00 IAM/KMS, 05 Lake Formation |

---

## 🧪 Part 7: Practice questions (35)

> Answer before you open the box. The explanations also cover **why the distractors are wrong**.

**Q1.** A retailer wants clickstream JSON events landed in S3 as Parquet within ~5 minutes, with no servers or custom consumers to manage. Which solution?
A) Kinesis Data Streams + Lambda that writes Parquet · B) **Amazon Data Firehose with record format conversion using a Glue table schema** · C) Glue streaming job reading from SQS · D) MSK Connect S3 sink
<details><summary>Answer</summary>B. Firehose buffers, converts JSON→Parquet using a Glue schema, and delivers to S3 with no code. A needs custom code. C: SQS isn't a native Glue streaming source here and it's more to operate. D needs an MSK cluster.</details>

**Q2.** Analysts want ad-hoc SQL over S3 data, paying only when they query. Which service?
A) Redshift provisioned · B) EMR with Presto · C) **Athena** · D) RDS
<details><summary>Answer</summary>C. Athena is serverless and charged per TB scanned. A and B mean always-on infrastructure. D isn't for S3 data.</details>

**Q3.** Marketing must query `customers` in Athena without `customer_email`, and regional managers should see only their region's rows. Least operational effort?
A) Create per-team views and S3 copies · B) **Lake Formation data cell filters granted per role** · C) IAM policies on S3 prefixes · D) Glue job that writes masked copies nightly
<details><summary>Answer</summary>B. Data cell filters give column and row security on one table, enforced in Athena. A and D duplicate data. C can't filter columns or rows inside files.</details>

**Q4.** A company has 400 tables and adds ~20 a week. Access depends on data classification (public/internal/pii) and zone. How should permissions scale?
A) Named-resource grants per table · B) **LF-Tags with tag-based grants (TBAC)** · C) Bucket policies per prefix · D) One IAM role per table
<details><summary>Answer</summary>B. Tag-based grants cover new tables automatically once they're tagged. A doesn't scale. C and D are coarse and hard to manage.</details>

**Q5.** An Iceberg table has thousands of tiny files and queries take 90 s. `OPTIMIZE ... BIN_PACK` "does nothing". Most likely cause?
A) Athena engine v2 · B) **`optimize_rewrite_data_file_threshold` is set too high** · C) Table is copy-on-write · D) Missing Lake Formation SELECT
<details><summary>Answer</summary>B. OPTIMIZE skips partitions with fewer candidate files than the threshold. Lower it (Challenge B). C doesn't stop compaction. D would cause an error, not a silent no-op.</details>

**Q6.** After a source column changes from INT to BIGINT, a Glue job appending to an Iceberg table fails on every run. Best fix?
A) Cast to int in the job · B) Recreate the table · C) **`ALTER TABLE ... ALTER COLUMN quantity TYPE bigint` (Spark)** · D) Switch to merge-on-read
<details><summary>Answer</summary>C. int→long is a legal metadata-only promotion. A risks overflow and corrupt data. B loses history. D is unrelated.</details>

**Q7.** Queries filter by `event_ts` date ranges, but the Iceberg table is partitioned by `customer_id`. What's the fix without rewriting existing data?
A) Create a new table · B) **`ADD PARTITION FIELD days(event_ts)` (partition evolution)** · C) Add a `dt` column and ask analysts to use it · D) Athena partition projection
<details><summary>Answer</summary>B. Iceberg partition evolution is metadata-only, and new writes use the new spec. Hidden partitioning means analysts keep filtering on `event_ts`. D applies to Hive tables.</details>

**Q8.** A faulty load committed 2 hours ago tripled the rows in an Iceberg table. Fastest recovery?
A) Reload from source · B) DELETE duplicates with a window function · C) **Roll back to the last good snapshot (`rollback_to_snapshot`)** · D) Restore S3 object versions
<details><summary>Answer</summary>C. Rollback is metadata-only and takes seconds. Confirm the snapshot first with `FOR VERSION AS OF`. A and B are slow. D doesn't understand table metadata (Challenge G).</details>

**Q9.** Each CSV uploaded under `incoming/` must be validated, then loaded with retries and failure notification. Which design?
A) Cron Lambda listing the bucket every minute · B) **S3 → EventBridge rule → Step Functions (Lambda validate → Glue `.sync` with Retry/Catch → SNS)** · C) Glue crawler hourly · D) S3 replication
<details><summary>Answer</summary>B. It's event-driven, orchestrated, and has error handling. A polls and is fragile. C only catalogs. D only copies (Challenge F).</details>

**Q10.** A Step Functions Task starts a Glue job, but the execution succeeds even when the job fails. Why?
A) Missing Retry · B) **The resource ARN lacks `.sync`** · C) The job has bookmarks enabled · D) Express workflow
<details><summary>Answer</summary>B. Without `.sync`, the task only calls StartJobRun and returns. `.sync` waits for the job and fails the state if the job fails.</details>

**Q11.** Saving a state machine fails with an error about `States.ALL`. Most likely?
A) States.ALL is deprecated · B) **States.ALL isn't the last retrier, or is combined with other errors** · C) Missing Catch · D) BackoffRate < 1
<details><summary>Answer</summary>B. ASL requires `States.ALL` to be alone in its `ErrorEquals` and in the last retrier or catcher.</details>

**Q12.** A developer fixed a Lambda in the console, but invocations still run the old logic. Why?
A) Cold start cache · B) **The change wasn't deployed** (or an alias still points to the old version) · C) The IAM role lacks permissions · D) The DLQ is full
<details><summary>Answer</summary>B. Console edits must be **deployed**. With versions and aliases, the alias must point to the new version.</details>

**Q13.** An EventBridge rule targets a state machine expecting `{"bucket":…, "key":…}`, but the state machine receives the full S3 event. Fix?
A) Add a Lambda to reshape · B) **Configure an input transformer** · C) Use SNS fan-out · D) Change the event pattern
<details><summary>Answer</summary>B. InputPathsMap extracts `$.detail.bucket.name` and `$.detail.object.key`, and InputTemplate builds the payload. A works but adds needless code.</details>

**Q14.** Firehose delivers order-status events to an Iceberg table, but each order appears 4–5 times. Fix?
A) Increase buffer size · B) **Configure unique keys (`order_id`) so updates upsert** · C) Enable dynamic partitioning · D) Convert to Parquet
<details><summary>Answer</summary>B. Without unique keys, Firehose appends every event (Challenge D). Also make sure the operation resolves to update ⚠️.</details>

**Q15.** Firehose creates a new tiny file every minute and queries get slower over time. Fix at the source?
A) Lower the buffer interval · B) **Raise the buffer interval/size** · C) Add a Lambda transform · D) Use Direct PUT
<details><summary>Answer</summary>B. Bigger buffers mean fewer, larger files. Pair it with compaction for what's already been written.</details>

**Q16.** A Glue job reprocesses every file in an S3 prefix on each daily run, creating duplicates. Two valid fixes?
A) **Enable job bookmarks** · B) **Scope the read path to the run date** · C) Increase DPUs · D) Use a crawler
<details><summary>Answer</summary>A and B. Bookmarks skip files already processed, and a date-scoped path reads only one day. MERGE on a key also prevents duplicates (Challenge G).</details>

**Q17.** A Hive-style table in Athena has years of daily partitions, and query planning is slow because of partition metadata. Fix?
A) MSCK REPAIR TABLE daily · B) **Partition projection** · C) More workers · D) Convert to CSV
<details><summary>Answer</summary>B. Projection computes partitions from configuration instead of reading them from the catalog. A adds even more partitions to the metadata.</details>

**Q18.** The finance team's Athena dashboards occasionally scan 5 TB by mistake. How do you cap spend per query and per team?
A) IAM condition keys · B) **Separate workgroups with per-query and per-workgroup data usage limits** · C) S3 lifecycle · D) Redshift WLM
<details><summary>Answer</summary>B. Workgroups carry scan-limit controls and their own result location.</details>

**Q19.** Running a query in Athena shows "Before you run your first query, you need to set up a query result location in Amazon S3." The lab provided a workgroup. Best action?
A) Edit the primary workgroup · B) **Switch to the lab's workgroup** · C) Create a new bucket · D) Use the CLI
<details><summary>Answer</summary>B. The lab workgroup already has a result location and the saved queries.</details>

**Q20.** A Glue job using a JDBC connection to Aurora fails with connection timeouts. The DB is healthy. Likely cause?
A) Wrong Glue version · B) **The security group lacks a self-referencing inbound rule (or the subnet has no route)** · C) Missing bookmarks · D) Athena workgroup
<details><summary>Answer</summary>B. Glue ENIs in the VPC must be able to reach each other and the DB. Use a self-referencing SG rule and correct subnet routing, plus an S3 VPC endpoint.</details>

**Q21.** A Glue job attached to a VPC connection can't reach S3. Fix?
A) Public IP on Glue · B) **Add an S3 gateway VPC endpoint (or NAT)** · C) Disable the connection · D) Bucket policy allowing *
<details><summary>Answer</summary>B. Private subnets need an endpoint or NAT to reach S3.</details>

**Q22.** Account A must let account B's analysts query selected catalog tables with column restrictions. Approach?
A) Copy the data to B · B) **Lake Formation cross-account grants (via AWS RAM) + resource links in B** ⚠️ · C) Bucket policy for B · D) Share IAM users
<details><summary>Answer</summary>B. Lake Formation shares catalog resources with fine-grained permissions. C gives no column control.</details>

**Q23.** Compliance requires customer-managed keys and an audit of every decryption. Choose:
A) SSE-S3 · B) **SSE-KMS with a customer-managed key + CloudTrail** · C) Client-side with no logging · D) S3 Object Lock
<details><summary>Answer</summary>B. KMS API calls (Decrypt) are logged in CloudTrail, and the key policy controls usage.</details>

**Q24.** A team has 200 existing Airflow DAGs and wants them managed on AWS. Choose:
A) Rewrite them in Step Functions · B) **Amazon MWAA** · C) Glue workflows · D) EventBridge Scheduler
<details><summary>Answer</summary>B. Managed Airflow runs the existing DAGs with minimal change.</details>

**Q25.** You need to load DynamoDB orders to the lake daily without full-copy duplicates. Best option?
A) Full export daily + append · B) **Incremental export (or full export + MERGE on `order_id`)** · C) Scan the table with Lambda · D) Crawl DynamoDB
<details><summary>Answer</summary>B. Incremental exports carry only changes, and MERGE makes repeats harmless. A is the Challenge G bug. C burns RCUs.</details>

**Q26.** Before publishing a curated table, a job must fail if `order_id` isn't unique or the row count is out of range. Choose:
A) Athena view · B) **Glue Data Quality rules (DQDL) in the job** · C) CloudWatch alarm · D) Lake Formation
<details><summary>Answer</summary>B. e.g. `Uniqueness "order_id" = 1.0` and `RowCount between 45000 and 55000`. Fail the job on violation.</details>

**Q27.** A data scientist gets "Insufficient Lake Formation permission(s): Required SELECT", but their IAM policy allows `athena:*` and `glue:Get*`. What's missing?
A) S3 bucket policy · B) **A Lake Formation grant matching the table (named or tag-based)** · C) KMS · D) Athena workgroup
<details><summary>Answer</summary>B. IAM allows the API call, but Lake Formation denies the data. Fix the grant or the table's tags (Challenge C).</details>

**Q28.** A data lake admin can't change a table's `zone` LF-Tag. Why?
A) Not in the IAM admin group · B) **Missing ASSOCIATE permission on the tag/values** · C) Table is Iceberg · D) Hybrid access mode
<details><summary>Answer</summary>B. Assigning tags needs ASSOCIATE on that tag key/value, even for admins (Challenge C).</details>

**Q29.** A CDC pipeline updates 5% of rows every 10 minutes, and MERGE rewrites huge files each time. Choose:
A) Bigger files · B) **Merge-on-read write mode + scheduled compaction** · C) Copy-on-write · D) More partitions
<details><summary>Answer</summary>B. MOR writes small delete files instead of rewriting data files, and compaction folds them back in later (Challenge B).</details>

**Q30.** A crawler keeps inferring a mix of string and int for a column across files, breaking queries. Best practice?
A) Run the crawler more often · B) **Define the schema explicitly (DDL) or use a schema-on-write table format** · C) Use CSV · D) Disable the catalog
<details><summary>Answer</summary>B. Crawlers infer from samples. For governed tables, define the schema (Iceberg DDL) and control evolution deliberately.</details>

**Q31.** A Glue job must run daily at 02:00, starting anytime within 15 minutes, with retries. Simplest?
A) Lambda + sleep · B) **EventBridge Scheduler (flexible window) → Step Functions/Glue** · C) Crawler schedule · D) EC2 cron
<details><summary>Answer</summary>B. Scheduler supports cron, flexible time windows and retry policies. Glue triggers are also valid for Glue-only flows.</details>

**Q32.** An SQS-triggered Lambda fails on one bad message, and the whole batch keeps retrying. Fix?
A) Batch size 1 · B) **Partial batch response (`ReportBatchItemFailures`)** · C) Increase the timeout · D) FIFO queue
<details><summary>Answer</summary>B. Return only the failed message IDs so the good ones are deleted. A works but kills throughput.</details>

**Q33.** You need to process 50,000 IoT events per second, each in a short (< 1 s) multi-step workflow. Choose:
A) Step Functions Standard · B) **Step Functions Express** · C) MWAA · D) Glue workflow
<details><summary>Answer</summary>B. Express is built for high-volume, short-duration workflows and is priced by duration and requests.</details>

**Q34.** After setting `vacuum_max_snapshot_age_seconds = 60` and running VACUUM, an engineer can't time travel to yesterday. Why?
A) Athena bug · B) **VACUUM expired older snapshots and removed their files** · C) Missing Lake Formation grant · D) Partition evolution
<details><summary>Answer</summary>B. Retention decides your recovery window. Keep it longer than your "time to notice a bad load".</details>

**Q35.** EventBridge should start a pipeline only for `.csv` files under `raw/vendors/` in one bucket. Which pattern fragment is correct?
A) `"key": ["raw/vendors/*.csv"]` · B) **`"key": [{"wildcard": "raw/vendors/*.csv"}]`** · C) `"key": {"prefix": "raw/vendors/"}` · D) `"key": [{"suffix": "csv"}]`
<details><summary>Answer</summary>B. A plain string is an exact match, so `*` is literal. C isn't wrapped in an array and ignores the extension. D misses the prefix and the dot.</details>

---

## 📚 References

- AWS Certified Data Engineer – Associate: https://aws.amazon.com/certification/certified-data-engineer-associate/ (exam guide, domain weights)
- AWS Skill Builder: https://skillbuilder.aws/ (official practice question sets ⚠️ check availability)
- AWS Workshops catalog: https://catalog.workshops.aws/ (search: "Lake Formation", "Glue", "Athena", "Iceberg")
- Each service file's 📚 References section
