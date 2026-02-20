# Infrastructure Terraform Workflow - {{PROJECT_NAME}}

**Date**: {{CURRENT_DATE}}
**Status**: ✅ ACTIVE
**Version**: 2.0 - Terraform Infrastructure Worktree-Based Workflow

---

## Overview

This guide covers the 13-step worktree-based workflow for **Terraform infrastructure-as-code development**. This workflow integrates:
- **Worktree isolation** (each infrastructure change gets its own worktree)
- **Architectural planning** (optional for complex infrastructure)
- **Automated validation and testing** (mandatory with terraform validate/plan/test)
- **Quality gates** (validation + security scans + code review + terraform plan)
- **Merge conflict resolution** (automated before merge)
- **Automatic merge & cleanup** (after all gates pass)

**Note**: Infrastructure workflows differ from application code — you merge the Terraform code to the base branch, then apply changes to dev/staging/production environments separately.

---

## Workflow Architecture

### Core Principle

**Isolated, Validation-Driven Quality with Automated Gates**

Every infrastructure change:
1. Gets its own **isolated worktree** with separate state
2. Goes through **mandatory quality gates** before being pushed
3. Has **conflicts resolved automatically** before merge
4. Is **merged to the base branch** after approval (application happens separately)

**Quality Gates**:
1. **Validation Gate** (Step 5) - `terraform validate` + `terraform plan` must succeed
2. **Security Scan Gate** (Step 5) - tfsec + checkov must pass
3. **Code Review Gate** (Step 6) - Code must be approved by infrastructure reviewer
4. **Terraform Test Gate** (Step 8) - Automated tests must pass
5. **Conflict Resolution Gate** (Step 10) - Merge conflicts must be resolved
6. **Final Validation Gate** (Step 11) - Final terraform plan with base branch merged

---

## Agent System

**Specialized Agents for Terraform Infrastructure**:

| Agent | Type | Scope | Role | Model |
|-------|------|-------|------|-------|
| software-architect | Architect | All | Design infrastructure (optional) | opus |
| **worktree-manager** | **Manager** | **All** | **Create worktrees, merge, cleanup** | sonnet |
| **terraform-developer** | **Developer** | **Infrastructure** | **Write Terraform configurations** | sonnet |
| **terraform-test-specialist** | **Tester** | **Infrastructure** | **Write Terratest/compliance tests** | sonnet |
| **infrastructure-code-reviewer** | **Reviewer** | **Infrastructure** | **Review Terraform code** | sonnet/opus |
| integration-tester | Tester | All | Execute validation and tests | haiku |
| **merge-conflict-resolver** | **Resolver** | **All** | **Detect and resolve merge conflicts** | opus |

---

## 13-Step Terraform Infrastructure Workflow

```
Step 0:  [OPTIONAL] software-architect      → Design infrastructure architecture
Step 1:  worktree-manager                   → Create worktree + isolated state
Step 2:  terraform-developer                → Write Terraform configuration
Step 3:  terraform-test-specialist          → Write validation/compliance tests
Step 4:  terraform-developer                → Commit infrastructure code + tests
Step 5:  integration-tester                 → Run terraform validate + plan + security [GATE]
Step 6:  infrastructure-code-reviewer       → Review Terraform code [GATE]
Step 7:  terraform-developer                → Fix if needed (loop to 5-6)
Step 8:  integration-tester                 → Run terraform test + Terratest [GATE]
Step 9:  terraform-developer                → Push to feature branch
Step 10: merge-conflict-resolver            → Resolve conflicts [GATE]
Step 11: integration-tester                 → Final terraform plan [GATE]
Step 12: worktree-manager                   → Merge to base branch, push
Step 13: worktree-manager                   → Cleanup worktree + state
```

**Important**: After Step 12, infrastructure is NOT automatically applied. Use a separate deployment process:
- Step 14 (Manual): Apply to dev environment — `terraform apply` in dev workspace
- Step 15 (Manual): Verify dev deployment — integration tests
- Step 16 (Manual): Apply to staging — `terraform apply` in staging workspace
- Step 17 (Manual): Verify staging — integration tests
- Step 18 (Manual): Apply to production — `terraform apply` in prod workspace (with approval)

---

## Step-by-Step Guide

### Step 0: Infrastructure Architecture Planning (Optional)

**When to Use**:
- ✅ New cloud services or infrastructure components
- ✅ Network architecture changes
- ✅ Multi-region deployments
- ✅ Major refactoring

**When to Skip**:
- ❌ Minor configuration tweaks
- ❌ Simple resource additions
- ❌ Documentation updates

**Agent**: software-architect (opus model)

**Output**: Infrastructure architecture document with:
- Context and requirements
- Proposed Terraform module structure
- Resource naming conventions
- State management strategy
- Security considerations
- Cost estimates
- Implementation plan

---

### Step 1: Create Worktree

**Agent**: worktree-manager

**Action**: Create isolated worktree with separate Terraform state

> **Note**: The worktree branches from whichever branch is currently checked out. At Step 12, the feature branch will be merged back to that same base branch.

**Commands**:
```bash
# Agent runs:
python scripts/worktree_create.py infra-feature-name
```

**Output**:
- Worktree created at `.worktrees/infra-feature-name`
- Branch created: `infra/feature-name`
- Separate Terraform workspace created (if using workspaces)
- Isolated state backend configuration

---

### Step 2: Write Terraform Configuration

**Agent**: terraform-developer

**Responsibilities**:
- Write clean, modular Terraform code
- Follow Terraform best practices
- Use modules for reusability
- Implement proper variable validation
- Add meaningful descriptions to all variables and outputs
- Use consistent naming conventions
- Handle secrets securely
- Place scripts in `scripts/` folder (never `/tmp/`)

**Terraform-Specific Patterns**:
```hcl
# modules/vpc/main.tf
# VPC module following Terraform best practices

terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Input variables with validation
variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "VPC CIDR must be a valid IPv4 CIDR block."
  }
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "availability_zones" {
  description = "List of availability zones to use"
  type        = list(string)

  validation {
    condition     = length(var.availability_zones) >= 2
    error_message = "At least 2 availability zones must be specified for high availability."
  }
}

variable "tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}

# Local values for computed configurations
locals {
  common_tags = merge(
    var.tags,
    {
      Environment = var.environment
      ManagedBy   = "Terraform"
      Module      = "vpc"
    }
  )

  public_subnet_cidrs = [
    for idx in range(length(var.availability_zones)) :
    cidrsubnet(var.vpc_cidr, 4, idx)
  ]

  private_subnet_cidrs = [
    for idx in range(length(var.availability_zones)) :
    cidrsubnet(var.vpc_cidr, 4, idx + length(var.availability_zones))
  ]
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(local.common_tags, { Name = "${var.environment}-vpc" })
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(local.common_tags, { Name = "${var.environment}-igw" })
}

# Public Subnets
resource "aws_subnet" "public" {
  count                   = length(var.availability_zones)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = local.public_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = merge(local.common_tags, {
    Name = "${var.environment}-public-subnet-${count.index + 1}"
    Type = "public"
  })
}

# Private Subnets
resource "aws_subnet" "private" {
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.main.id
  cidr_block        = local.private_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = merge(local.common_tags, {
    Name = "${var.environment}-private-subnet-${count.index + 1}"
    Type = "private"
  })
}

# NAT Gateways (one per AZ for high availability)
resource "aws_eip" "nat" {
  count  = length(var.availability_zones)
  domain = "vpc"

  tags = merge(local.common_tags, { Name = "${var.environment}-nat-eip-${count.index + 1}" })

  depends_on = [aws_internet_gateway.main]
}

resource "aws_nat_gateway" "main" {
  count         = length(var.availability_zones)
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = merge(local.common_tags, { Name = "${var.environment}-nat-gw-${count.index + 1}" })
}

# Route Tables
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = merge(local.common_tags, { Name = "${var.environment}-public-rt" })
}

resource "aws_route_table" "private" {
  count  = length(var.availability_zones)
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }

  tags = merge(local.common_tags, { Name = "${var.environment}-private-rt-${count.index + 1}" })
}

# Route Table Associations
resource "aws_route_table_association" "public" {
  count          = length(var.availability_zones)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private" {
  count          = length(var.availability_zones)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

# Outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = aws_subnet.private[*].id
}

output "nat_gateway_ips" {
  description = "Elastic IPs of the NAT Gateways"
  value       = aws_eip.nat[*].public_ip
}
```

**DO NOT commit yet** - tests need to be written first

---

### Step 3: Write Validation and Compliance Tests

**Agent**: terraform-test-specialist

**Responsibilities**:
- Analyze Terraform configuration
- Design validation tests
- Implement Terratest integration tests (optional)
- Write compliance policy tests (OPA/Sentinel)
- Verify security configurations
- Document test scenarios

**Terraform Test Structure** (Terraform 1.6+ native testing):
```hcl
# tests/vpc_test.tftest.hcl
# Terraform native tests for VPC module

variables {
  vpc_cidr           = "10.0.0.0/16"
  environment        = "dev"
  availability_zones = ["us-east-1a", "us-east-1b"]
  tags = {
    Project = "test-project"
  }
}

run "validate_vpc_cidr" {
  command = plan

  assert {
    condition     = aws_vpc.main.cidr_block == "10.0.0.0/16"
    error_message = "VPC CIDR does not match expected value"
  }
}

run "validate_subnet_count" {
  command = plan

  assert {
    condition     = length(aws_subnet.public) == 2
    error_message = "Expected 2 public subnets"
  }

  assert {
    condition     = length(aws_subnet.private) == 2
    error_message = "Expected 2 private subnets"
  }
}

run "validate_nat_gateway_count" {
  command = plan

  assert {
    condition     = length(aws_nat_gateway.main) == 2
    error_message = "Expected one NAT gateway per AZ for high availability"
  }
}

run "validate_tags" {
  command = plan

  assert {
    condition     = aws_vpc.main.tags["Environment"] == "dev"
    error_message = "VPC missing expected environment tag"
  }

  assert {
    condition     = aws_vpc.main.tags["ManagedBy"] == "Terraform"
    error_message = "VPC missing ManagedBy tag"
  }
}

run "validate_dns_enabled" {
  command = plan

  assert {
    condition     = aws_vpc.main.enable_dns_hostnames == true
    error_message = "DNS hostnames should be enabled"
  }

  assert {
    condition     = aws_vpc.main.enable_dns_support == true
    error_message = "DNS support should be enabled"
  }
}

run "validate_public_subnets_routable" {
  command = plan

  assert {
    condition     = length(aws_route_table_association.public) == 2
    error_message = "All public subnets should be associated with public route table"
  }
}

run "validate_private_subnets_routable" {
  command = plan

  assert {
    condition     = length(aws_route_table_association.private) == 2
    error_message = "All private subnets should be associated with private route tables"
  }
}
```

---

### Step 4: Commit Infrastructure Code + Tests

**Agent**: terraform-developer

**Commands**:
```bash
# Format Terraform code
terraform fmt -recursive

# Validate configuration
terraform validate

# Commit
git add .
git commit -m "feat: add VPC module with high availability

- Implement VPC module with public/private subnets across 2 AZs
- Add NAT gateways for private subnet internet access
- Add tagging strategy for resource management
- Implement variable validation for inputs
- Add Terraform native tests for validation
- Apply security best practices (DNS enabled, proper routing)"
```

---

### Step 5: Run Validation + Security Scans ⚠️ GATE

**Agent**: integration-tester (haiku model)

**Commands**:
```bash
# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Generate plan
terraform plan -out=tfplan

# Security scan with tfsec
tfsec .

# Security scan with checkov
checkov -d .

# Compliance checks (if using OPA)
opa test policies/
```

**Pass Criteria**:
- `terraform validate` succeeds
- `terraform plan` succeeds with no errors
- tfsec passes (no HIGH/CRITICAL issues)
- checkov passes (no HIGH/CRITICAL issues)
- Compliance tests pass

**On Fail**:
- Workflow BLOCKED
- Orchestrator invokes terraform-developer to fix
- Returns to Step 5 after fix

---

### Step 6: Code Review ⚠️ GATE

**Agent**: infrastructure-code-reviewer (sonnet, opus for critical)

**Review Criteria**:
- ✅ **Security** (IAM least privilege, encryption, secret management)
- ✅ **Best Practices** (module structure, naming conventions, state management)
- ✅ **Cost Optimization** (right-sized resources, lifecycle policies)
- ✅ **High Availability** (multi-AZ, redundancy, failover)
- ✅ **Compliance** (tagging, logging, monitoring)
- ✅ **Documentation** (variable descriptions, output descriptions, README)

**Terraform-Specific Checks**:
- All variables have descriptions
- All outputs have descriptions
- Proper use of locals for DRY code
- Module versioning specified
- State backend configured securely
- Sensitive outputs marked as `sensitive = true`
- Resource names follow conventions
- Tags applied consistently

**Outcomes**:
- ✅ **APPROVED** - Continue to Step 8
- ❌ **CHANGES REQUESTED** - Go to Step 7

---

### Step 7: Fix Review Issues

**Agent**: terraform-developer

**Action**: Address all code review feedback

**Process**:
1. Read review comments carefully
2. Fix each identified issue
3. Run `terraform validate` and `terraform fmt -recursive`
4. Re-run security scans to confirm issues are resolved
5. Commit fixes

**Commands**:
```bash
# Format after fixes
terraform fmt -recursive

# Validate
terraform validate

# Re-run security scans
tfsec .
checkov -d .

# Commit fixes
git add .
git commit -m "fix: address infrastructure code review feedback

- Add missing descriptions to all variables and outputs
- Mark sensitive outputs with sensitive = true
- Add encryption configuration to S3 bucket
- Fix IAM policy to apply least privilege"
```

**Then**: Return to Step 5 to re-run quality gates

---

### Step 8: Run Terraform Tests ⚠️ GATE

**Agent**: integration-tester (haiku model)

**Commands**:
```bash
# Run Terraform native tests (Terraform 1.6+)
terraform test

# Run Terratest (if configured)
cd tests/
go test -v -timeout 30m ./...

# Run OPA policy tests (if configured)
opa test policies/ -v

# Run compliance framework tests (if configured)
checkov -d . --framework terraform --check CKV_AWS_*
```

**Pass Criteria**:
- All `terraform test` assertions pass
- Terratest integration tests pass (if configured)
- OPA policy tests pass
- No new security findings introduced

**On Fail**:
- Workflow BLOCKED
- Orchestrator invokes terraform-developer to fix failures
- Returns to Step 8 after fix

---

### Step 9: Push to Feature Branch

**Agent**: terraform-developer

**Commands**:
```bash
# Push feature branch to remote
git push origin infra/feature-name

# Verify push succeeded
git log origin/infra/feature-name --oneline -5
```

---

### Step 10: Resolve Merge Conflicts ⚠️ GATE

**Agent**: merge-conflict-resolver (opus model)

**Actions**:
1. Pull latest base branch
2. Merge base branch into feature branch
3. Detect conflicts (pay special attention to `.tf` and `.tfvars` files)
4. Resolve automatically (or request manual review for state-impacting conflicts)
5. Commit resolution
6. Push resolved feature branch to remote

**Commands**:
```bash
# Pull latest and merge base branch
git fetch origin
git merge origin/<base-branch>

# After conflict resolution - re-validate to confirm integrity:
terraform fmt -recursive
terraform validate
terraform plan -out=tfplan

# Push after conflict resolution:
git push origin HEAD --force-with-lease
```

**Terraform Conflict Notes**:
- Conflicts in `.tf` files are usually safe to resolve by keeping both resource blocks
- Conflicts in `terraform.lock.hcl` should keep the more recent provider versions
- Never attempt auto-resolution of `.tfstate` files — these require manual review
- After resolution, always run `terraform validate` and `terraform plan` to confirm no unintended changes

**On Fail**:
- Complex conflicts or `.tfstate` conflicts require manual resolution
- Orchestrator alerts developer to resolve manually
- Returns to Step 10 after manual resolution

---

### Step 11: Final Validation ⚠️ GATE

**Agent**: integration-tester (haiku model)

**Commands**:
```bash
# Final validation after base branch merged
terraform validate

# Final plan — review carefully for unexpected changes
terraform plan -out=tfplan-final

# Re-run security scans with merged state
tfsec .
checkov -d .
```

**Pass Criteria**:
- `terraform validate` succeeds
- `terraform plan` shows only the expected changes (no unintended resource drift)
- Security scans pass
- No unexpected resource destructions or replacements in the plan

**On Fail**:
- terraform-developer investigates unexpected plan changes
- Fix any regressions introduced by the base branch merge
- Returns to Step 11 after fix

---

### Step 12: Merge to Base Branch ⚠️ FINAL

**Agent**: worktree-manager

**Action**: Merge feature branch into base branch and push

**Commands**:
```bash
# Agent runs:
python scripts/worktree_merge.py <worktree-id>
```

**Output**:
- Feature merged to base branch
- Base branch pushed to remote
- Ready for cleanup

**After merge**: Infrastructure code is now in the base branch but NOT yet applied. Follow the manual deployment process (Steps 14-18) to apply changes to each environment.

---

### Step 13: Cleanup Worktree + State

**Agent**: worktree-manager

**Commands**:
```bash
# Agent runs:
python scripts/worktree_cleanup.py <worktree-id>

# Clean up Terraform workspace (if using workspaces)
terraform workspace select default
terraform workspace delete infra-feature-name

# Remove temporary plan files
rm -f tfplan tfplan-final
```

**Output**:
- Worktree removed from `.worktrees/`
- Feature branch deleted locally (remote branch kept for PR history)
- Temporary Terraform workspace cleaned up

---

## Workflow Variants

### Standard Workflow (11 steps)
**Steps**: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 9 → 10 → 12 → 13
**Use For**: Regular infrastructure changes (80% of work)
**Note**: Skips Terratest (Step 8) — use when native `terraform test` coverage is sufficient

### Full Workflow (13 steps)
**Steps**: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13
**Use For**: New modules, network changes, multi-region deployments, major refactors
**Note**: Includes all quality gates including Terratest

### Hotfix Workflow (9 steps)
**Steps**: 1 → 2 → 4 → 5 → 6 → 7 → 9 → 10 → 12 → 13
**Use For**: Critical infrastructure fixes, urgent security patches
**Note**: Skips test writing (assumes tests exist), skips Terratest; includes fix loop (Step 7)

### Test-Only Workflow (7 steps)
**Steps**: 1 → 3 → 4 → 5 → 9 → 12 → 13
**Use For**: Adding tests to existing Terraform modules, improving validation coverage

### Docs-Only Workflow (5 steps)
**Steps**: 1 → 2 → 9 → 12 → 13
**Use For**: Documentation updates, README changes, variable description improvements

---

## Terraform Development Best Practices

### DO

✅ Use modules for reusability
✅ Implement variable validation
✅ Use remote state with locking
✅ Tag all resources consistently
✅ Use workspaces for environment isolation
✅ Document all variables and outputs with descriptions
✅ Run `terraform fmt` before committing
✅ Run security scans (tfsec, checkov) before every review
✅ Implement least privilege IAM policies
✅ Encrypt sensitive data at rest and in transit

### DON'T

❌ Hardcode secrets or credentials in `.tf` files
❌ Skip variable validation for critical inputs
❌ Use local state in shared or production environments
❌ Ignore security scan warnings
❌ Create resources without consistent tags
❌ Skip documentation on variables and outputs
❌ Use default security groups
❌ Forget to version external modules
❌ Create single-AZ resources for critical workloads
❌ Skip cost analysis for new resource types

---

## Resources

- [Terraform Development Guide](../.claude/TERRAFORM_GUIDE.md) - Terraform best practices
- [Testing Guide](TESTING_GUIDE.md) - Terratest and native testing practices
- [Terraform Documentation](https://www.terraform.io/docs) - Official Terraform docs
- [tfsec](https://aquasecurity.github.io/tfsec/) - Security scanner for Terraform
- [Checkov](https://www.checkov.io/) - Policy-as-code scanner

---

**Last Updated**: {{CURRENT_DATE}}
**Status**: Living Document
