# Infrastructure (Terraform)

Terraform IaC for the AWS deployment baseline of the Payments MVP.

```
infra/
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

## Scopes

The Cognito resource server exposes the scopes used by the services and contracts:
`payments.initiate`, `payments.read`, `payments.write`, `payments.execute`.

## Usage

```powershell
cd infra/environments/dev

# Validate without AWS credentials
terraform init -backend=false
terraform validate
terraform fmt -recursive -check

# Deploy (requires AWS credentials and a configured backend)
terraform init
terraform plan
terraform apply
```

Secrets are managed via AWS Secrets Manager (a placeholder secret is created); values
are populated out-of-band and never stored in code. The S3 remote-state backend is
declared but commented in `providers.tf`; configure it per environment.
