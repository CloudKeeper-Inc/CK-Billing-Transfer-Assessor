

PROFILES=("dev" "qa" "ss" "prod" "valegacy" "orlegacy")
REGIONS=("us-west-2" "us-east-1")


check_s3() {
    local profile=$1
    local region=$2

    echo "Checking S3 bucket policies for profile: $profile, region: $region"

    
    BUCKETS=$(aws s3api list-buckets --query 'Buckets[].Name' --output text --profile "$profile" --region "$region")

    for bucket in $BUCKETS; do
        POLICY=$(aws s3api get-bucket-policy --bucket "$bucket" --query 'Policy' --output text --profile "$profile" --region "$region" 2>/dev/null)
        if [[ $POLICY == *"PrincipalOrgID"* ]]; then
            echo "Found PrincipalOrgID in S3 bucket policy: $bucket $profile $region"
        fi
    done
}


check_sqs() {
    local profile=$1
    local region=$2

    echo "Checking SQS queue policies for profile: $profile, region: $region"

    
    QUEUES=$(aws sqs list-queues --query 'QueueUrls' --output text --profile "$profile" --region "$region")

    for queue_url in $QUEUES; do
        POLICY=$(aws sqs get-queue-attributes --queue-url "$queue_url" --attribute-names Policy --query 'Attributes.Policy' --output text --profile "$profile" --region "$region" 2>/dev/null)
        if [[ $POLICY == *"PrincipalOrgID"* ]]; then
            echo "Found PrincipalOrgID in SQS queue policy: $queue_url $profile $region"
        fi
    done
}


check_sns() {
    local profile=$1
    local region=$2

    echo "Checking SNS topic policies for profile: $profile, region: $region"

    
    TOPICS=$(aws sns list-topics --query 'Topics[].TopicArn' --output text --profile "$profile" --region "$region")

    for topic_arn in $TOPICS; do
        POLICY=$(aws sns get-topic-attributes --topic-arn "$topic_arn" --query 'Attributes.Policy' --output text --profile "$profile" --region "$region" 2>/dev/null)
        if [[ $POLICY == *"PrincipalOrgID"* ]]; then
            echo "Found PrincipalOrgID in SNS topic policy: $topic_arn $profile $region"
        fi
    done
}


for profile in "${PROFILES[@]}"; do
    for region in "${REGIONS[@]}"; do
        check_s3 "$profile" "$region"
        check_sqs "$profile" "$region"
        check_sns "$profile" "$region"
    done
done

echo "Script completed."