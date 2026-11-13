# 🅲 Challenge C: Provision a workload identity for a self-hosted agent

> **Status:** 🟡 In progress · **Diagram label:** C (**AWS Systems Manager** → *Manage* → **EC2 `compliance-agent-host`** → *Retrieve workload access token* → **Compliance audit agent**)
> **Services:** Amazon Bedrock **AgentCore Identity** (`create-workload-identity`, tags, `GetWorkloadAccessToken`), **Systems Manager** (Parameter Store, Documents, Run Command, Session Manager), EC2, IAM (pre-created `ComplianceAgentRole`)
> **Lab:** [AWS Securing Agent Identities Demonstrated](README.md) · **Vault:** [index](../README.md)

---

## ✅ Status checklist (success criteria)

- [ ] Workload identity **`compliance-audit-agent`** exists with tag **`Team=compliance`**
- [ ] SSM parameter **`/compliance-agent/workload-identity-arn`** holds that identity's **ARN**
- [ ] On **`compliance-agent-host`**: **`RestartComplianceAgent`** succeeds, and **`InvokeComplianceAgent`** returns success (the agent obtained a workload access token)

---

## 🖼️ Task card

![Challenge C task card: Provision a workload identity for a self-hosted agent](assets/challenge_C/01_task_card.png)

<details>
<summary>Text copy of the task</summary>

**Provision a workload identity for a self-hosted agent**

A self-hosted compliance agent runs on Amazon EC2 and authenticates to a third-party regulatory reporting API by using a workload access token. The compliance team deployed the agent without creating its workload identity, so the agent cannot obtain tokens. The agent reads its identity Amazon Resource Name (ARN) from an SSM parameter that does not exist yet. This parameter is stored in Parameter Store, a capability of AWS Systems Manager.

**Prerequisites:**
- Confirm that the EC2 instance named *compliance-agent-host* exists.
- Confirm that the SSM documents named *RestartComplianceAgent* and *InvokeComplianceAgent* exist under the Owned by me tab on the Systems Manager Documents console.
- Confirm access to the workstation EC2 instance by using Session Manager, and then run `sudo su - ec2-user` to use the terminal as ec2-user. The instance's IAM role has permissions only for AgentCore operations.
- Review the agent's reference code on the workstation under `/home/ec2-user/reference-code/compliance-agent/` (agent.py, test_token_fetch.py, and compliance-agent.service). **Note:** These are the same files that the SSM documents run on the *compliance-agent-host* instance, showing how the agent reads its identity ARN and fetches a token.

**Main areas to investigate:**
- The agent code on the workstation shows it reads from the SSM parameter */compliance-agent/workload-identity-arn*, which does not exist yet.
- Listing workload identities with the *aws bedrock-agentcore-control* CLI returns no identity for the compliance agent.
- The *RestartComplianceAgent* and *InvokeComplianceAgent* SSM documents describe how to restart the agent and verify token retrieval.
- The agent role *ComplianceAgentRole* already has *GetWorkloadAccessToken* scoped to the *compliance-audit-agent* identity.

**Your task:** Create a workload identity for the compliance agent by using the bedrock-agentcore-control CLI, store its ARN in the SSM parameter, restart the agent, and verify it can obtain a token.

**Note:** Run Command cannot be executed from the workstation's terminal. Run the SSM documents from the Systems Manager console.

**Success criteria:**
- A workload identity named *compliance-audit-agent* exists with tag *Team=compliance*.
- The SSM parameter */compliance-agent/workload-identity-arn* holds the workload identity ARN.
- Both SSM documents run against the compliance-agent-host EC2 instance: running *RestartComplianceAgent* succeeds, and running *InvokeComplianceAgent* returns a success response confirming that the agent obtained a workload access token.

</details>

---

## 🗺️ Where it sits in the architecture

```text
BEFORE
  compliance-agent-host (EC2, role ComplianceAgentRole)
    agent.py → ssm:GetParameter /compliance-agent/workload-identity-arn   ❌ ParameterNotFound
             → (never reaches) bedrock-agentcore:GetWorkloadAccessToken(compliance-audit-agent)  ❌ identity doesn't exist

AFTER
  workstation CLI ──create-workload-identity──▶ compliance-audit-agent [Team=compliance]
  Parameter Store  /compliance-agent/workload-identity-arn = …/workload-identity/compliance-audit-agent
  SSM Run Command ─RestartComplianceAgent─▶ host: agent restarts and reads the parameter
                  ─InvokeComplianceAgent──▶ host: GetWorkloadAccessToken ✅ token
```

**Key idea:** Runtime and Gateway agents get a workload identity **automatically** (see the list in Challenge B: `client_advisor_runtime_…`, `trading-gateway-…`). A **self-hosted** agent, here on EC2, needs one **created by hand**. It then calls `GetWorkloadAccessToken` itself, using its own IAM role (`ComplianceAgentRole`, already scoped to this identity name).

### Where each step happens

| Step | Where | UI path | CLI alternative |
|---|---|---|---|
| 1 | **Workstation** (AgentCore CLI only) | EC2 → Instances → `workstation-b4183f00` → **Connect ▾** → **Session Manager** | `create-workload-identity`, `tag-resource`, `get-workload-identity` |
| 2 | **Systems Manager → Parameter Store** | Top search **Parameter Store** → **Create parameter** | CloudShell: `aws ssm put-parameter` |
| 3 | **Systems Manager → Documents / Run Command** (console only, *not* the workstation) | Top search **Documents** → **Owned by me** → document → **Run command** → target `compliance-agent-host` → **Run** | CloudShell: `aws ssm send-command` + `get-command-invocation` |

---

## 🔍 Root cause

1. **No identity.** Nobody created the compliance agent's workload identity, so `GetWorkloadAccessToken` has nothing to issue a token for.
2. **No pointer.** The agent finds its identity through the SSM parameter `/compliance-agent/workload-identity-arn`, which didn't exist.
3. **Stale process.** Even after both exist, the running agent needs a **restart** to read the new parameter.

IAM is **not** the problem: `ComplianceAgentRole` already allows `GetWorkloadAccessToken` on `compliance-audit-agent`. That's why the **name must match exactly**.

---

## 🛠️ Solution

### Values

| Thing | Value |
|---|---|
| Identity name | `compliance-audit-agent` (exact, because the role's permission is scoped to it) |
| Identity tag | `Team=compliance` |
| Expected identity ARN | `arn:aws:bedrock-agentcore:us-east-1:987347315034:workload-identity-directory/default/workload-identity/compliance-audit-agent` |
| SSM parameter | `/compliance-agent/workload-identity-arn`, Standard, **String** |
| Target instance | **`compliance-agent-host`** (not `workstation-b4183f00`) |
| SSM documents | `RestartComplianceAgent`, then `InvokeComplianceAgent` (Owned by me) |

### Step 1: Create and tag the identity (workstation)

**UI:** EC2 → **Instances** → `workstation-b4183f00` → **Connect ▾** → **Session Manager** → Connect, or reuse the open tab.

```bash
sudo su - ec2-user
export AWS_DEFAULT_REGION=us-east-1

# 10-second look at how the agent reads the parameter (name, decryption, region)
ls ~/reference-code/compliance-agent/
grep -n -i -E "ssm|get_parameter|WithDecryption|workload" ~/reference-code/compliance-agent/agent.py | head -20

aws bedrock-agentcore-control create-workload-identity --name compliance-audit-agent --tags '{"Team":"compliance"}'
```

If `--tags` isn't accepted by `create-workload-identity`:
```bash
aws bedrock-agentcore-control create-workload-identity --name compliance-audit-agent
aws bedrock-agentcore-control tag-resource \
  --resource-arn arn:aws:bedrock-agentcore:us-east-1:987347315034:workload-identity-directory/default/workload-identity/compliance-audit-agent \
  --tags '{"Team":"compliance"}'
```

Verify:
```bash
export CA_ARN=$(aws bedrock-agentcore-control get-workload-identity --name compliance-audit-agent --query workloadIdentityArn --output text)
echo "$CA_ARN"
aws bedrock-agentcore-control list-tags-for-resource --resource-arn "$CA_ARN"
```

### Step 2: Create the SSM parameter

**UI (Systems Manager):**
1. Top search bar → type **Parameter Store** → click it (a Systems Manager feature). Or go Systems Manager → left nav *Application tools* → **Parameter Store** ⚠️.
2. Click **Create parameter** and fill in:
   - Name: `/compliance-agent/workload-identity-arn`
   - Description: optional
   - Tier: **Standard**
   - Type: **String**
   - Data type: **text**
   - Value: the ARN from step 1
3. Click **Create parameter**.

**CLI (CloudShell, `>_` in the console top bar).** The workstation role can't call SSM.
```bash
aws ssm put-parameter --name /compliance-agent/workload-identity-arn --type String \
  --value arn:aws:bedrock-agentcore:us-east-1:987347315034:workload-identity-directory/default/workload-identity/compliance-audit-agent
aws ssm get-parameter --name /compliance-agent/workload-identity-arn --query Parameter.Value --output text
```

### Step 3: Run the SSM documents on `compliance-agent-host`

**UI (Systems Manager), click by click.** Do the whole flow for **RestartComplianceAgent** first, then repeat it for **InvokeComplianceAgent**.

**A. Open the document**
1. Top search bar → type **Documents** → click **Documents** under *Features* (Systems Manager). Or go Systems Manager → left nav *Shared resources* → **Documents**.
2. Tabs: *Owned by Amazon* · **Owned by me** · *Shared with me* · *All documents*. Click **Owned by me**.
3. Search box: `Compliance`. Both `RestartComplianceAgent` and `InvokeComplianceAgent` are listed.
4. Click the **name** `RestartComplianceAgent` (blue link) to open its details page.
   - Optional: the **Content** tab shows the script.
5. Top right → **Run command** (orange). The *Run a command* page opens with the document preselected.
   - Fallback: in the list, select the document's radio button → **Actions ▾** → **Run command**.

**B. Fill in the "Run a command" page (top to bottom)**

| Section | Setting |
|---|---|
| Command document | Preselected. Don't change it |
| Document version | **Default version at runtime** |
| Command parameters | Defaults (may be none) |
| **Target selection** | **Choose instances manually** → type `compliance` in the filter → tick **compliance-agent-host**. **Not** `workstation-b4183f00` |
| Other parameters | Leave them (timeout 600 s) |
| Rate control | Leave them |
| **Output options** | **Untick "Enable an S3 bucket"** if ticked, because the lab role may not be able to write there. Leave CloudWatch logs off |
| SNS notifications | Disabled |
| AWS command line interface command | Optional: expand it to see the matching `aws ssm send-command` |

→ **Run** (orange, bottom right).

**C. Status and output**
1. Page: **Command ID: … was successfully sent!**
   - **Command status**: *In progress* → **Success**.
   - Click **refresh ↻** every few seconds (it takes 5–30 s).
2. **Targets and outputs** → the `compliance-agent-host` row should show **Success**.
3. Click the **Instance ID** link to open the **Output** page.
   - **Step 1 – Output** is stdout. For Restart, the service restarted or is active.
   - **Step 1 – Error** is stderr. Paste it if anything fails.

**D. Repeat for InvokeComplianceAgent**
1. **Documents** → **Owned by me** → **InvokeComplianceAgent** → **Run command**.
2. **Choose instances manually** → tick **compliance-agent-host** → untick S3 → **Run**.
3. Refresh until **Success** → **Instance ID** → **Step 1 – Output**. It should report that the **workload access token was obtained**.

| What you see | Meaning / fix |
|---|---|
| Host isn't in the manual list | Not an SSM-managed node yet. Clear the filter, wait about 1 min, refresh |
| **Failed** / **Delivery timed out** | Instance ID → **Step 1 – Error** |
| Invoke: `ParameterNotFound` | Parameter name mismatch, or Restart ran before the parameter existed. Fix it, then **Restart** → **Invoke** |
| Invoke: `AccessDenied` / `ResourceNotFound` on `GetWorkloadAccessToken` | The parameter value isn't exactly the `compliance-audit-agent` ARN |

Alternative path: Systems Manager → *Node tools* → **Run Command** → **Run command** → search for the document name ⚠️.

**CLI (CloudShell):**
```bash
IID=$(aws ec2 describe-instances --filters "Name=tag:Name,Values=compliance-agent-host*" "Name=instance-state-name,Values=running" \
  --query "Reservations[].Instances[].InstanceId" --output text); echo $IID

C1=$(aws ssm send-command --document-name RestartComplianceAgent --targets Key=InstanceIds,Values=$IID --query Command.CommandId --output text)
aws ssm get-command-invocation --command-id $C1 --instance-id $IID --query "[Status,StandardOutputContent,StandardErrorContent]" --output text

C2=$(aws ssm send-command --document-name InvokeComplianceAgent --targets Key=InstanceIds,Values=$IID --query Command.CommandId --output text)
aws ssm get-command-invocation --command-id $C2 --instance-id $IID --query "[Status,StandardOutputContent,StandardErrorContent]" --output text
```
`InProgress` means it's still running. Re-run `get-command-invocation` after about 10 seconds.

### Step 4: Check

Press **Check**.

### Order of operations

```text
1 identity (+tag) → 2 parameter = ARN → 3a RestartComplianceAgent → 3b InvokeComplianceAgent → Check
(The restart must come AFTER the parameter exists.)
```

---

## ⚠️ Mistakes & lessons

_Fill in as I go. Screenshots go in `assets/challenge_C/`._

---

## 🧯 Troubleshooting table

| Symptom | Likely cause | Fix |
|---|---|---|
| `create-workload-identity: Unknown options: --tags` | Older CLI or API shape | Create without tags, then `tag-resource` |
| `ConflictException` / already exists | Created earlier | `get-workload-identity --name compliance-audit-agent`, then just tag it |
| `aws ssm …` on the workstation → `AccessDenied` | The workstation role is AgentCore-only | Use the console or CloudShell |
| Invoke output: `ParameterNotFound` | Parameter name typo, or restart ran before the parameter existed | Check the exact name `/compliance-agent/workload-identity-arn`, then **Restart** again, then Invoke |
| Invoke output: `AccessDenied … GetWorkloadAccessToken` | Identity name isn't exactly `compliance-audit-agent` | Re-create it with the exact name and update the parameter |
| Invoke output: `ResourceNotFound` for the identity | Parameter holds a wrong or truncated ARN | `get-parameter` and compare with `get-workload-identity` |
| Run Command target list doesn't show the host | Instance not SSM-managed yet, or the wrong filter | Choose instances manually, clear the filters, refresh |
| Check fails on the documents | Ran on the workstation instead of `compliance-agent-host` | Re-run both documents on the right instance |

---

## 📚 Study notes

### Self-hosted agent identity flow

| Step | Call | Who |
|---|---|---|
| 1. Identity exists | `CreateWorkloadIdentity(name)` | Admin (control plane) |
| 2. Agent finds its identity | `ssm:GetParameter` → ARN, then name | Agent (instance role) |
| 3. Agent gets a token | `GetWorkloadAccessToken(workloadName)` | Agent, authorized by IAM **on the identity ARN** |
| 4. *(next)* Downstream credentials | `GetResourceOauth2Token` / `GetResourceApiKey` with that token | Agent → token vault → third-party API |

**Hosted vs self-hosted:** on AgentCore Runtime, the platform creates the identity and passes the workload access token to the agent (inbound JWT → `GetWorkloadAccessTokenForJWT`). Self-hosted agents do steps 1–3 themselves.

### Systems Manager pieces used

| Piece | Used for |
|---|---|
| **Parameter Store** | Config and pointers (`String` / `StringList` / `SecureString`). Standard tier is free, up to 4 KB |
| **Documents** (SSM documents) | Scripted actions. *Owned by me* = custom docs the lab created |
| **Run Command** | Runs a document on managed instances, **without SSH**, and keeps the output per instance |
| **Session Manager** | Interactive shell (the workstation) |

### 🧪 Self-test
1. Why does the identity name have to be exactly `compliance-audit-agent`?
2. Why must `RestartComplianceAgent` run **after** the parameter is created?
3. How does a self-hosted agent's identity differ from a Runtime agent's?
4. Why can't you `send-command` from the workstation?

---

## 📝 Run log (fill in as I go)

| Step | What I did | Result / output |
|---|---|---|
| 1 | Reference code grep | ✅ `SSM_PARAM_NAME = "/compliance-agent/workload-identity-arn"`. `get_parameter(Name=…)` has **no decryption**, so **String** is fine. `workload_name = identity_arn.split("/")[-1]`, so the ARN must **end in the name** (no trailing space or slash). Then `get_workload_access_token(workloadName=…)` |
| 1 | create-workload-identity `--tags '{"Team":"compliance"}'` | ✅ Accepted. ARN `arn:aws:bedrock-agentcore:us-east-1:987347315034:workload-identity-directory/default/workload-identity/compliance-audit-agent`, `allowedResourceOauth2ReturnUrls: []`. ✅ `get-workload-identity` → same ARN. `list-tags-for-resource` → `{"Team": "compliance"}` (the only tag, since this identity wasn't created by CloudFormation) |
| 2 | Parameter created | _value = ?_ |
| 3a | RestartComplianceAgent | _Success?_ |
| 3b | InvokeComplianceAgent | _token obtained?_ |
| 4 | Check | _result_ |

### Raw output: step 1 (13 Nov 2026)

```text
[ec2-user@ip-10-0-0-12 ~]$ ls ~/reference-code/compliance-agent/
agent.py  compliance-agent.service  test_token_fetch.py

[ec2-user@ip-10-0-0-12 ~]$ grep -n -i -E "ssm|get_parameter|WithDecryption|workload" ~/reference-code/compliance-agent/agent.py | head -20
4:This agent authenticates to AgentCore Identity by fetching a workload access
5:token. It reads the workload identity ARN from an SSM parameter at startup,
8:Without a valid workload identity and scoped IAM permissions, this agent
20:SSM_PARAM_NAME = "/compliance-agent/workload-identity-arn"
41:def get_identity_arn(ssm_client):
42:    """Read workload identity ARN from SSM parameter."""
44:        response = ssm_client.get_parameter(Name=SSM_PARAM_NAME)
46:    except ssm_client.exceptions.ParameterNotFound:
49:        logger.error("Failed to read SSM parameter: %s", e)
54:    """Attempt to get a workload access token."""
55:    # ARN format: arn:aws:bedrock-agentcore:REGION:ACCOUNT:workload-identity-directory/default/workload-identity/NAME
56:    workload_name = identity_arn.split("/")[-1]
57:    response = agentcore_client.get_workload_access_token(
58:        workloadName=workload_name
69:    ssm_client = boto3.client("ssm", region_name=region)
72:    # Wait for SSM parameter to be configured
73:    logger.info("Reading identity ARN from SSM parameter: %s", SSM_PARAM_NAME)
74:    identity_arn = get_identity_arn(ssm_client)
78:            "SSM parameter '%s' not found. "
79:            "Agent cannot authenticate without a workload identity.",

[ec2-user@ip-10-0-0-12 ~]$ aws bedrock-agentcore-control create-workload-identity --name compliance-audit-agent --tags '{"Team":"compliance"}'
{
    "name": "compliance-audit-agent",
    "workloadIdentityArn": "arn:aws:bedrock-agentcore:us-east-1:987347315034:workload-identity-directory/default/workload-identity/compliance-audit-agent",
    "allowedResourceOauth2ReturnUrls": []
}
```

**What the code tells us:**
- The agent reads the parameter **without** `WithDecryption`, so the parameter must be **String**. A SecureString would come back encrypted.
- It takes the **last `/` segment** of the ARN as the `workloadName` for `GetWorkloadAccessToken`. A wrong ARN, or a trailing `/` or space, breaks it even if the parameter exists.
- It reads the parameter **at startup**, which is why `RestartComplianceAgent` must run after the parameter is created.
