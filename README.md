# Crypto.com takehome

## Q1 Rate-limiting

Run `python3 Q1.py`

Input files are in `./test_logs`

## Q2.​ AWS​ API​ programming

Run `./Q2.sh <name_of_your_instance>`

## Q3. System design and Implementation

### Implementation

see `Q3` folder

### Design

Since we are allowed to base our infrasture on AWS, it seems ideal to use the following AWS services for our system:

#### Compute: AWS Lambda

Our main functionality of creating an new url and redirecting an existing url can be implemented with one Lambda function that can easily suffice our requirements.

##### Availablility

AWS Lambda is a regional service and has uptime of at least [99.95%](https://aws.amazon.com/lambda/sla/)

In the event of a disater or service of the entire region is down,
we need a copy of the function in a differnt region which should be deployed whenever we do deployment

##### Scalability

If we need to scale from 0 to more than 1000+ rps in short period of time, we need to deploy our function in these regions: US West (Oregon), US East (N. Virginia), Europe (Ireland) to have 3000 burst concurrency limit. We should also request for high concurrency limit beforehand if needed which by default is 1000.

If we have a higher requirement of latency for each request, we should use Application Auto Scaling API to adjust Provision concurrency so that when requests come in, the instances are already ready to serve

![auto-scaling](https://docs.aws.amazon.com/lambda/latest/dg/images/features-scaling-provisioned-auto.png)

#### Storage: Dynamodb

We will use DynamoDB for storing original urls and its shortened urls. It gives us minimum operation and maintainance required to keep it highly available and scalable which are not as easy to acheive with other alternatives like RDS and Aurora. Plus we don't need a relational database for our simple data.

##### Availablility

[DynamoDB has up time of at least 99.999% if the Global Tables SLA applies, or (b) at least 99.99% if the Standard SLA applies.](https://aws.amazon.com/dynamodb/sla/).

In the event of a disater or service of the entire region is down, we need a copy of our data in a different region which can be achieve with point-in-time recovery as documented [here](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/PointInTimeRecovery.html)

As a alternative, we can also use DynamoDB global tables for maximum availablity even in the event of disater. However the cost would be higher.

##### Scalability

By default we have 40,000 read request units and 40,000 write request units as throughput quotas. With occational burst of traffic it should use burst capacity which retains up to 5 minutes (300 seconds) of unused read and write capacity per-partition. We might want to do auto scaling to optimize our cost.

![auto-scaling](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/images/auto-scaling.png)

#### Rest API: API Gateway

[API Gateway has up time of at least 99.95% for each AWS region.](https://aws.amazon.com/api-gateway/sla/)

In the event of a disater or service of the entire region is down, to prevent any downtime, we can do a active-active deployment for API Gateway. We can configure AWS Route 53 with latency-based routing and health checks to achieve an active-active setup that can fail over between regions in case of an issue.

##### Scalability

[API Gateway allows 10000 rps as a default quota](<https://aws.amazon.com/about-aws/whats-new/2017/06/amazon-api-gateway-increases-account-level-throttle-limits-to-10000-requests-per-second-rps/#:~:text=What's%20New-,Amazon%20API%20Gateway%20Increases%20Account%20Level%20Throttle,10%2C000%20Requests%20per%20Second%20(RPS)&text=Amazon%20API%20Gateway%20has%20raised,(RPS)%20from%201%2C000%20RPS>)
