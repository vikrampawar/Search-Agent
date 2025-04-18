
```
aws ec2 create-security-group --group-name "launch-wizard-1" --description "launch-wizard-1 created 2025-04-17T07:44:33.751Z" --vpc-id "vpc-04aa0237d9453e5e0" 
aws ec2 authorize-security-group-ingress --group-id "sg-preview-1" --ip-permissions '{"IpProtocol":"tcp","FromPort":22,"ToPort":22,"IpRanges":[{"CidrIp":"0.0.0.0/0"}]}' 
aws ec2 run-instances --image-id "ami-05238ab1443fdf48f" --instance-type "t2.micro" --network-interfaces '{"AssociatePublicIpAddress":true,"DeviceIndex":0,"Groups":["sg-preview-1"]}' --credit-specification '{"CpuCredits":"standard"}' --metadata-options '{"HttpEndpoint":"enabled","HttpPutResponseHopLimit":2,"HttpTokens":"required"}' --private-dns-name-options '{"HostnameType":"ip-name","EnableResourceNameDnsARecord":true,"EnableResourceNameDnsAAAARecord":false}' --count "1" 
