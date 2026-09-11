# Infrastructure (Terraform)

Terraform IaC for the AWS deployment baseline of the Payments MVP.

```
infra/
  bootstrap/       One-time setup: S3 state backend + DynamoDB lock + GitHub OIDC role
  modules/
    network/       VPC, public/private subnets across 2 AZs, IGW, routing
    msk/           Amazon MSK (Kafka) cluster + security group (TLS)
    eventbridge/   Integration event bus, payment-status rule, log target
    cognito/       User pool, resource server (payment scopes), M2M app client
    readmodel/     DynamoDB table for the CQRS payment-status projection
    compute/       ECS Fargate cluster, task execution role, log group
    api-gateway/   HTTP API + Cognito JWT authorizer + stage throttling
  environments/
    dev/           Root config wiring all modules + Secrets Manager secret
```

Region: **us-east-1**. State: **S3 remote backend** (created by `bootstrap/`).

## Scopes

The Cognito resource server exposes the scopes used by the services and contracts:
`payments.initiate`, `payments.read`, `payments.write`, `payments.execute`.

## CI/CD pipeline setup (one-time)

The GitHub Actions workflow (`.github/workflows/terraform.yml`) authenticates to AWS with
**OIDC** — no long-lived access keys. Getting it operational is a one-time, three-part
setup. Parts 1 and 2 require your AWS account and are run from your machine.

### Part 1 — Run the bootstrap (creates the state backend + the OIDC role)

This provisions the S3 state bucket, the DynamoDB lock table, the GitHub OIDC identity
provider, and the IAM role that GitHub Actions will assume. It uses **local** state.

```powershell
cd infra/bootstrap
Copy-Item terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars: set a GLOBALLY UNIQUE state_bucket_name
#   (e.g. payments-tfstate-<your-account-id>)

terraform init
terraform apply    # requires AWS credentials with permissions to create IAM/S3/DynamoDB
```

Capture the outputs — you will need them in Part 2:

```powershell
terraform output github_actions_role_arn   # -> GitHub secret AWS_ROLE_ARN
terraform output state_bucket               # -> GitHub variable TF_STATE_BUCKET
terraform output lock_table                 # -> GitHub variable TF_LOCK_TABLE
```

> If the account already has a GitHub OIDC provider, import it before applying:
> `terraform import aws_iam_openid_connect_provider.github arn:aws:iam::<account-id>:oidc-provider/token.actions.githubusercontent.com`

### Part 2 — Configure GitHub (environments, secret, variables)

Create two deployment environments and register the backend/role values. Using the
GitHub CLI (`gh`):

```powershell
$REPO = "hectorlaris/bian-payments-platform"

# Secret: the IAM role ARN the pipeline assumes via OIDC
gh secret set AWS_ROLE_ARN --repo $REPO --body "<github_actions_role_arn from Part 1>"

# Non-secret variables: the remote-state backend coordinates
gh variable set TF_STATE_BUCKET --repo $REPO --body "<state_bucket from Part 1>"
gh variable set TF_LOCK_TABLE   --repo $REPO --body "<lock_table from Part 1>"

# Environments: 'dev' for plan, 'dev-apply' for approval-gated apply.
# Add a required reviewer to 'dev-apply' in the GitHub UI:
#   Settings > Environments > dev-apply > Required reviewers.
```

Environments are created automatically the first time the workflow references them, but
the **required-reviewer** protection on `dev-apply` must be enabled in the UI (or via the
GitHub API). That approval gate is what makes `apply` a deliberate, human-approved step.

### Part 3 — How the pipeline runs

- **validate** — always runs (fmt + `init -backend=false` + validate). No AWS needed.
- **plan** — runs in the `dev` environment, assumes the role via OIDC, inits the S3
  backend, and produces a plan.
- **apply** — runs only on `main`, in the `dev-apply` environment, and waits for a
  reviewer to approve before applying.

## Local development usage

```powershell
cd infra/environments/dev

# Validate without AWS credentials
terraform init -backend=false
terraform validate
terraform fmt -recursive -check

# Deploy from your machine (uses the same S3 backend as CI)
Copy-Item backend.hcl.example backend.hcl   # fill in bucket + lock table from bootstrap
terraform init -backend-config=backend.hcl
terraform plan
terraform apply
```

Secrets are managed via AWS Secrets Manager (a placeholder secret is created); values are
populated out-of-band and never stored in code.

## Security notes

- Authentication is **OIDC only** — there are no AWS access keys in the repo or in CI.
- The OIDC trust policy restricts role assumption to this repository and the `dev` /
  `dev-apply` environments (plus `pull_request` for plan).
- The bootstrap deploy policy is intentionally broad to manage the whole dev stack;
  tighten it to least-privilege as part of a security review before production use.
