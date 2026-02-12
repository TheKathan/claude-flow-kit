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

**Note**: Infrastructure workflows differ from application code - instead of merging to main and deploying, you merge the Terraform code to main, then apply changes to dev/staging/production environments separately.

---

## Workflow Architecture

### Core Principle

**Isolated, Validation-Driven Quality with Automated Gates**

Every infrastructure change:
1. Gets its own **isolated worktree** with separate state
2. Goes through **mandatory quality gates** before being pushed
3. Has **conflicts resolved automatically** before merge
4. Is **merged to main** after approval (application happens separately)

**Quality Gates**:
1. **Validation Gate** (Step 5) - terraform validate + terraform plan must succeed
2. **Security Scan Gate** (Step 5) - tfsec + checkov must pass
3. **Code Review Gate** (Step 6) - Code must be approved by infrastructure reviewer
4. **Terraform Test Gate** (Step 8) - Automated tests must pass
5. **Conflict Resolution Gate** (Step 10) - Merge conflicts must be resolved
6. **Final Validation Gate** (Step 11) - Final terraform plan with {{MAIN_BRANCH}} merged

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
Step 12: worktree-manager                   → Merge to {{MAIN_BRANCH}}, push
Step 13: worktree-manager                   → Cleanup worktree + state
```

**Important**: After Step 12, infrastructure is NOT automatically applied. Use separate deployment process:
- Step 14 (Manual): Apply to dev environment → `terraform apply` in dev workspace
- Step 15 (Manual): Verify dev deployment → Integration tests
- Step 16 (Manual): Apply to staging → `terraform apply` in staging workspace
- Step 17 (Manual): Verify staging → Integration tests
- Step 18 (Manual): Apply to production → `terraform apply` in prod workspace (with approval)

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

**Commands**:
```bash
# Agent runs:
bash scripts/worktree_create.sh infra-feature-name "Infrastructure change description"
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
- Add meaningful descriptions
- Use consistent naming conventions
- Handle secrets securely
- Place scripts in `scripts/` folder

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

  # Calculate subnet CIDRs
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

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-vpc"
    }
  )
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-igw"
    }
  )
}

# Public Subnets
resource "aws_subnet" "public" {
  count                   = length(var.availability_zones)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = local.public_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-public-subnet-${count.index + 1}"
      Type = "public"
    }
  )
}

# Private Subnets
resource "aws_subnet" "private" {
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.main.id
  cidr_block        = local.private_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-private-subnet-${count.index + 1}"
      Type = "private"
    }
  )
}

# NAT Gateways (one per AZ for high availability)
resource "aws_eip" "nat" {
  count  = length(var.availability_zones)
  domain = "vpc"

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-nat-eip-${count.index + 1}"
    }
  )

  depends_on = [aws_internet_gateway.main]
}

resource "aws_nat_gateway" "main" {
  count         = length(var.availability_zones)
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-nat-gw-${count.index + 1}"
    }
  )
}

# Route Tables
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-public-rt"
    }
  )
}

resource "aws_route_table" "private" {
  count  = length(var.availability_zones)
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-private-rt-${count.index + 1}"
    }
  )
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
- Add proper tagging strategy for resource management
- Implement variable validation for inputs
- Add Terraform native tests for validation
- Add security best practices (DNS enabled, proper routing)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
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
- terraform validate succeeds
- terraform plan succeeds (no errors)
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
- ✅ **Best Practices** (module structure, naming, state management)
- ✅ **Cost Optimization** (right-sized resources, reserved instances)
- ✅ **High Availability** (multi-AZ, redundancy, failover)
- ✅ **Compliance** (tagging, logging, monitoring)
- ✅ **Documentation** (variable descriptions, outputs, README)

**Terraform-Specific Checks**:
- All variables have descriptions
- All outputs have descriptions
- Proper use of locals for DRY
- Module versioning specified
- State backend configured securely
- Sensitive outputs marked as sensitive
- Resource names follow conventions
- Tags applied consistently

**Outcomes**:
- ✅ **APPROVED** - Continue to Step 8
- ❌ **CHANGES REQUESTED** - Go to Step 7

---

### Step 7-13: [Continue with same quality gate structure]

---

## Terraform Development Best Practices

### DO

✅ Use modules for reusability
✅ Implement variable validation
✅ Use remote state with locking
✅ Tag all resources consistently
✅ Use workspaces for environments
✅ Document variables and outputs
✅ Use terraform fmt before committing
✅ Run security scans (tfsec, checkov)
✅ Implement least privilege IAM
✅ Encrypt sensitive data

### DON'T

❌ Hardcode secrets or credentials
❌ Skip variable validation
❌ Use local state in production
❌ Ignore security scan warnings
❌ Create resources without tags
❌ Skip documentation
❌ Use default security groups
❌ Forget to version modules
❌ Create single-AZ resources for critical workloads
❌ Skip cost analysis

---

## Resources

- [Terraform Development Guide](../.claude/TERRAFORM_GUIDE.md) - Terraform best practices
- [Terraform Documentation](https://www.terraform.io/docs) - Official Terraform docs
- [tfsec](https://aquasecurity.github.io/tfsec/) - Security scanner
- [Checkov](https://www.checkov.io/) - Policy-as-code scanner

---

**Last Updated**: {{CURRENT_DATE}}
**Status**: Living Document
