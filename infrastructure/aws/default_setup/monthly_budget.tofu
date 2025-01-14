provider "aws" {
  region = "eu-central-1"
}

resource "aws_budgets_budget" "monthly_budget" {
  name              = "Monthly-Budget"
  budget_type       = "COST"
  limit_amount      = "20"          # Set your budget amount here
  limit_unit        = "USD"
  time_unit         = "MONTHLY"

  cost_types {
    include_tax          = true
    include_subscription = true
    use_blended          = false
  }

  notification {
    comparison_operator = "GREATER_THAN"
    threshold           = 80         # Send alert at 80% of the budget
    threshold_type      = "PERCENTAGE"
    notification_type   = "ACTUAL"
    subscriber_email_addresses = ["info@tes4all.com"]
  }
}
