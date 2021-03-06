#!/bin/bash

INSTANCE_NAME=$1
EC2_PUBLIC_IP=$(aws ec2 describe-instances --filters "Name=tag:Name,Values=$INSTANCE_NAME" --query 'Reservations[*].Instances[*].PublicIpAddress' --output text)
if [ -n $2 ]
  then
  ssh -i $2 ec2-user@$EC2_PUBLIC_IP
fi
ssh ec2-user@$EC2_PUBLIC_IP
