from boto.sns import connect_to_region, SNSConnection

def publish_msg_to_sns_topic(region, aws_access_key, aws_secret_key, topic, message, subject):
    
    connect_to_region(region)
    
    conn = SNSConnection(aws_access_key, aws_secret_key)
    
    conn.publish(topic, message, subject)

