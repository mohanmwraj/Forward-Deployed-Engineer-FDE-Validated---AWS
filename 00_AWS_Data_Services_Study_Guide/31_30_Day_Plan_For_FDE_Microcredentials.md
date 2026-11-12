# 🗓️ 30-Day Plan: Clearing the AWS Partner FDE Microcredentials for the Voucher

> **Goal:** finish the **required** FDE exam labs inside the 30-day voucher window, required ones first, while building notes that make every later lab faster.
> **Status:** 1 lab passed (*AWS Data Lakehouse Demonstrated*, 11 Nov 2026). ~50 more available.
> **⚠️ To fill in:** voucher rules (how many labs, which ones are required, the deadline date). I don't have the official list yet. Paste the catalog into the chat and I'll tier it and fill in the tracker below.
> **Back to:** [Study guide index](README.md) · [Vault index](../README.md)

---

## 🎯 Step 1: Pin down the rules (do this today)

| Question | Answer |
|---|---|
| Which labs are **required** for the voucher? | _paste the list_ |
| How many labs must be passed? | _N_ |
| Window start → **deadline** | _start date_ → _deadline_ |
| Does *Needs Improvement* on one task still count as a pass? | My lakehouse lab **passed overall** with G = Needs Improvement, so a pass doesn't need 100% ⚠️ confirm the threshold |
| Retake policy inside the window? | My result page said the soonest retake is 9 months after passing, so **treat every attempt as a one-shot** ⚠️ confirm for failed attempts |
| Time limit per lab? | _from the lab page_ |

**Why this comes first:** if you don't know which labs count, you can easily spend a week on labs that don't move you toward the voucher.

---

## 🧮 Step 2: Capacity math

| Item | Estimate |
|---|---|
| Labs required | **N** (assume ~50 until confirmed) |
| Days available | 30, minus **4 buffer days**, so **26 working days** |
| Labs per working day | 50 ÷ 26 ≈ **2 per day** |
| Time per lab | ~15 min pre-brief + **lab time** (mine took a morning) + ~20 min notes |
| Daily load | **~4–6 hours** at 2 labs a day |

**If that's more than you can sustain alongside work:** do the **required** labs only, and keep optional labs for after the voucher. Don't lower the quality bar. A pass with notes beats two rushed fails.

---

## 🧱 Step 3: Prioritise (first principles)

Rank every lab by four factors, in this order:

1. **Required for the voucher?** Required labs go first, always.
2. **Overlap with what you already know.** Labs in the same family as one you've passed are faster. The lakehouse lab covered S3, Glue, Athena, Lake Formation, Iceberg, Firehose, EventBridge, Step Functions and Lambda, so any data, analytics, serverless or integration lab is now cheaper for you.
3. **Unlocks for later labs.** Foundation-heavy labs (IAM, networking/VPC, security) unblock many others. Do them early, even if they're harder.
4. **Length and risk.** Within a day, do the **long** lab first while you're fresh, and leave the short one for later.

### Tiers

| Tier | What | When |
|---|---|---|
| **T1** | Required, in a family you already know | Days 1–8 (build momentum and bank passes) |
| **T2** | Required, new family | Days 6–22 (one new family at a time, with a pre-read) |
| **T3** | Not required, but builds skills for T2 | Only if a T2 lab needs it |
| **T4** | Optional | After the voucher |

---

## 📅 Step 4: The 30-day shape

| Days | Focus | Output |
|---|---|---|
| **1** | Pin down the rules (Step 1) · read [00 Foundations](00_AWS_Foundations_IAM_Regions_CLI_CloudWatch_KMS.md) (IAM especially) · tier the catalog | Filled tracker |
| **2–8** | **T1 labs** (data/analytics/serverless families): 2 per day | ~12 passes, notes per lab |
| **9** | **Buffer / review.** Re-do weak areas (e.g. Iceberg rollback from Challenge G) | Updated notes |
| **10–16** | **T2 family #1** (biggest new family): pre-read the family, then 2 labs per day | ~12 passes |
| **17** | **Buffer / review** | — |
| **18–24** | **T2 family #2 and beyond** | ~12 passes |
| **25** | **Buffer / review** | — |
| **26–29** | Remaining required labs, highest risk first | Close the gap |
| **30** | **Buffer**: final check that every required lab shows Passed; claim badges | Voucher |

**Rule:** if you fall behind by more than 2 labs, use the next buffer day to catch up. Don't push into late nights.

---

## 🔁 Step 5: Daily routine (time-boxed)

```text
┌─ Before the lab (15 min) ─────────────────────────────────────────┐
│ 1. Read the lab's service list.                                     │
│ 2. Read the ⭐ Must-know section for each of those services here.   │
│    (Or paste the service list to Claude for a pre-brief.)           │
│ 3. Open the cheat sheet's "Lab tactics" table.                     │
└────────────────────────────────────────────────────────────────────┘
┌─ During the lab ──────────────────────────────────────────────────┐
│ 1. Read ALL task cards first (5 min). Note the slow steps.          │
│ 2. Start the slow steps first (job runs, stream updates).           │
│ 3. Do quick console tasks while they run.                           │
│ 4. Press Check after each task. Fix and move on.                    │
│ 5. Stuck for more than 15 min? Screenshot it → ask Claude → continue│
│    with another task while you wait.                                │
└────────────────────────────────────────────────────────────────────┘
┌─ After the lab (20 min) ──────────────────────────────────────────┐
│ 1. Screenshot the result page and the performance report.           │
│ 2. Claude creates the lab folder: 0N_<Lab_Name>/ with one md per    │
│    challenge (task card, root cause, fix, mistakes, study notes).   │
│ 3. Add new cross-lab lessons to the vault README.                   │
└────────────────────────────────────────────────────────────────────┘
┌─ Daily spaced repetition (10 min) ────────────────────────────────┐
│ 5 self-test questions from older notes. Re-read any you miss.       │
└────────────────────────────────────────────────────────────────────┘
```

---

## ✅ Step 6: Exam-lab protocol (keep this open during every lab)

- [ ] Correct **region** (top right) and correct **workgroup / account / role**
- [ ] Read every task card. Note the **slow** steps and start them first
- [ ] Look up **exact resource names** (suffixes!), using CloudShell if the console is slow
- [ ] For each script edit: read the `TODO` / `HINT` lines and use the script's own variable names
- [ ] **Make it live:** Lambda **Deploy** · Glue / Step Functions **Save** · Firehose wait for **Active** · EventBridge **Create/Update rule**
- [ ] Verify the success criteria exactly as written (run the saved queries)
- [ ] Press **Check** after each task
- [ ] Don't re-run ingest jobs after a restore or rollback
- [ ] 10 minutes left? Stop starting new work. Make sure every finished task is saved and checked

---

## 🧠 Step 7: Second-order thinking about the plan

| Decision | Immediate effect | Later consequence | Mitigation |
|---|---|---|---|
| Do 4 labs a day to finish early | Fast progress | Fatigue leads to careless misses (deploy/save/region), and with no retakes those are costly | Cap at 2–3 a day; keep buffer days |
| Skip notes to save time | +20 min a day | Later labs in the same family take longer; nothing to revise for exams | Keep notes short but always write them (Claude drafts them from screenshots) |
| Do the easy optional labs first | Feels productive | Required labs pile up near the deadline | Strict T1 → T2 ordering |
| Leave all the new families to the last week | Comfortable early weeks | Steepest learning when time is shortest | Start T2 by day 10 at the latest |
| Treat Needs Improvement as fine | The pass still counts | The same gap shows up in later labs and exams | Each NI task gets a "complete solution" note (as done for G) |
| Learn every service deeply before any lab | Strong foundation | Burns the window | Pre-read only ⭐ Must-know before a lab; go deep afterwards |

---

## 📋 Step 8: Tracker

| # | Lab (microcredential) | Required? | Tier | Main services | Est. time | Date | Result | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | AWS Data Lakehouse Demonstrated | _?_ | T1 | S3, Glue, Athena, Lake Formation, Iceberg, Firehose, EventBridge, Step Functions, Lambda | ~½ day | 11 Nov 2026 | ✅ Passed (G = Needs Improvement) | [01_AWS_Data_Lakehouse_Demonstrated](../01_AWS_Data_Lakehouse_Demonstrated/README.md) |
| 2 | _paste catalog →_ | | | | | | | |
| 3 | | | | | | | | |
| … | | | | | | | | |

_Once you paste the list of ~50 labs (names + the services each covers), I'll fill this table, assign tiers, group by family, and draft the day-by-day schedule with dates._

---

## 🧰 How this vault speeds up later labs

- **Same services, new scenario:** most data/serverless labs reuse the services in this guide. Start with the **⭐ Must-know** section and the **📈 Troubleshooting** table.
- **New services:** I'll add a service file to this guide using the same template whenever a lab needs one (e.g. Redshift, Kinesis Data Streams, DMS, API Gateway, ECS).
- **Practice before the real thing:** the 7 challenges in [Walkthrough 2](21_Walkthrough_2_QuickBite_Food_Delivery_Lakehouse.md) are written in the exam-lab format.
