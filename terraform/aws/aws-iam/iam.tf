provider "aws" {
  region = "us-east-1"
}

# Required to be able to set instance_profile on EC2 instance
resource "aws_iam_policy" "passInstanceProfile" {
  name        = "AllowPassingInstanceProfileToEC2"
  path        = "/"
  description = "Allow to assing EC2 to InstanceProfile"

  policy = <<-EOF
  {
      "Version": "2012-10-17",
      "Statement": [
          {
              "Effect": "Allow",
              "Action": [
                  "iam:PassRole",
                  "iam:ListInstanceProfiles"
              ],
              "Resource": "*"
          }
      ]
  }
  EOF
}


# Required to run
# aws sts decode-authorization-message --encoded-message (encoded error message) --query DecodedMessage --output text | jq '.'
# to decode encoded authorization error messages
resource "aws_iam_policy" "decodeAuthorizedMessages" {
  name        = "AllowDecodeAuthorizationMessages"
  path        = "/"
  description = "Allow to execute aws sts decode-authorization-message "

  policy = <<-EOF
  {
      "Version": "2012-10-17",
      "Statement": [
          {
              "Effect": "Allow",
              "Action": "sts:DecodeAuthorizationMessage",
              "Resource": "*"
          }
      ]
  }
  EOF
}

# Required to create AutoScalingGroup and ALB
resource "aws_iam_policy" "createASGAndALB" {
  name        = "AllowCreateAutoScalingGroupAndApplicationLoadBalancer"
  path        = "/"
  description = "Allow to create linked role for ASG and ALB"

  policy = <<-EOF
  {
      "Version": "2012-10-17",
      "Statement": [
          {
              "Effect": "Allow",
              "Action": "iam:CreateServiceLinkedRole",
              "Resource": "arn:aws:iam::*:role/aws-service-role/autoscaling.amazonaws.com/AWSServiceRoleForAutoScaling*",
              "Condition": {"StringLike": {"iam:AWSServiceName": "autoscaling.amazonaws.com"}}
          },
          {
              "Effect": "Allow",
              "Action": "iam:CreateServiceLinkedRole",
              "Resource": "arn:aws:iam::*:role/aws-service-role/elasticloadbalancing.amazonaws.com/AWSServiceRoleForElasticLoadBalancing*",
              "Condition": {"StringLike": {"iam:AWSServiceName": "elasticloadbalancing.amazonaws.com"}}
          },
          {
              "Effect": "Allow",
              "Action": [
                  "iam:AttachRolePolicy",
                  "iam:PutRolePolicy"
              ],
              "Resource": "arn:aws:iam::*:role/aws-service-role/autoscaling.amazonaws.com/AWSServiceRoleForAutoScaling*"
          },
          {
              "Effect": "Allow",
              "Action": [
                  "iam:AttachRolePolicy",
                  "iam:PutRolePolicy"
              ],
              "Resource": "arn:aws:iam::*:role/aws-service-role/elasticloadbalancing.amazonaws.com/AWSServiceRoleForElasticLoadBalancing*"
          }
      ]
  }
  EOF
}



# Admin group will limited admin privilidges
resource "aws_iam_group" "limitedAdmin" {
  name = "LimitedAdmin"
  path = "/"
}

resource "aws_iam_group_policy_attachment" "createASGAndALB" {
  group      = aws_iam_group.limitedAdmin.name
  policy_arn = aws_iam_policy.createASGAndALB.arn
}

resource "aws_iam_group_policy_attachment" "decodeAuthorizedMessagesToAdminGroup" {
  group      = aws_iam_group.limitedAdmin.name
  policy_arn = aws_iam_policy.decodeAuthorizedMessages.arn
}

resource "aws_iam_group_policy_attachment" "passInstanceProfileToAdminGroup" {
  group      = aws_iam_group.limitedAdmin.name
  policy_arn = aws_iam_policy.passInstanceProfile.arn
}

resource "aws_iam_group_policy_attachment" "thisUserChangePasswordAttachment" {
  group      = aws_iam_group.limitedAdmin.name
  policy_arn = "arn:aws:iam::aws:policy/IAMUserChangePassword"
}

resource "aws_iam_group_policy_attachment" "viewOnlyAccessToAdminGroup" {
  group      = aws_iam_group.limitedAdmin.name
  policy_arn = "arn:aws:iam::aws:policy/job-function/ViewOnlyAccess"
}

resource "aws_iam_group_policy_attachment" "billingToAdminGroup" {
  group      = aws_iam_group.limitedAdmin.name
  policy_arn = "arn:aws:iam::aws:policy/job-function/Billing"
}

resource "aws_iam_group_policy_attachment" "systemAdminPolicyToAdminGroup" {
  group      = aws_iam_group.limitedAdmin.name
  policy_arn = "arn:aws:iam::aws:policy/job-function/SystemAdministrator"
}

resource "aws_iam_group_policy_attachment" "networkAdminPolicyToAdminGroup" {
  group      = aws_iam_group.limitedAdmin.name
  policy_arn = "arn:aws:iam::aws:policy/job-function/NetworkAdministrator"
}


# IAM Admin group allow to define priviledges
resource "aws_iam_group" "iamAdmin" {
  name = "IamAdmin"
  path = "/"
}


resource "aws_iam_group_policy_attachment" "iamFullAccessToIamAdminGroup" {
  group      = aws_iam_group.iamAdmin.name
  policy_arn = "arn:aws:iam::aws:policy/IAMFullAccess"
}


resource "aws_iam_role" "jenkins-master" {
  name               = "jenkins-master"
  description        = "Should be applied to EC2 with Jenkins Master - so that Jenkins can spawn Jenkins Agent being EC2s"
  assume_role_policy = <<-EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": "ec2.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  }
  EOF
}

# Only roles exposed as instance_profile can be assigned to EC2
# EC2 instance can obtain the credentials via:
# curl http://169.254.169.254/latest/meta-data/iam/security-credentials/s3all
# AWS CLI inherits them automatically
resource "aws_iam_instance_profile" "jenkins-master" {
  name = "jenkins-master"
  role = aws_iam_role.jenkins-master.name
}

resource "aws_iam_role_policy_attachment" "jenkins-master-s3-attach" {
  role       = aws_iam_role.jenkins-master.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "jenkins-master-ec2-attach" {
  role       = aws_iam_role.jenkins-master.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2FullAccess"
}


resource "aws_iam_role" "s3all" {
  name = "s3all"

  assume_role_policy = <<-EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": "ec2.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  }
  EOF
}

resource "aws_iam_role_policy_attachment" "s3all-attach" {
  role       = aws_iam_role.s3all.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_instance_profile" "s3all" {
  name = "s3all"
  role = aws_iam_role.s3all.name
}

resource "aws_iam_role" "s3reader" {
  name = "s3reader"

  assume_role_policy = <<-EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": "ec2.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  }
  EOF
}

resource "aws_iam_role_policy_attachment" "s3reader-attach" {
  role       = aws_iam_role.s3reader.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}

resource "aws_iam_instance_profile" "s3reader" {
  name = "s3reader"
  role = aws_iam_role.s3reader.name
}
