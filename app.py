import boto3
import botocore
import json
import datetime


def blog_generation(blog_topic):
    prompt = f"""
    <s>[INST] Human: Write a 200 words blog on the topic {blog_topic}.
    Assistant: </INST></s>"""

    body = {
        "prompt": prompt,
        "max_gen_len": 512,
        "temperature": 0.6,
        "top_p": 0.9
    }

    try: 
        bedrock = boto3.client("bedrock", region_name="us-east-1",
                                config=botocore.config.Config(read_timeout=300, retries={"max_attempts": 3}))
        response = bedrock.invoke_model(body=json.dumps(body), modelId="meta.llama2-13b-chat-v1")
        print("response ", response)
        response_content = response.get('body').read()
        response_data = json.loads(response_content)
        print("response_data ", response_data)
        blog_details = response_data['generation']
        print("blog_details ", blog_details)
        return blog_details
    except Exception as e:
        print(e)
        return ""


def save_blog_details(s3_key, s3_bucket, generate_blog):
    s3 = boto3.client('s3')
    try:
        s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=generate_blog)
        print("Code saved to s3 bucket")
    except Exception as e:
        print(e)
        return ""

def lambda_handler(event, context):
    event = json.loads(event['body'])
    blog_topic = event['blog_topic']

    generate_blog = blog_generation(blog_topic)

    if generate_blog:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        s3_key = f"blog_output/{current_time}_{blog_topic}.txt"
        s3_bucket = 'aws_bedrock_demo'
        save_blog_details(s3_key, s3_bucket, generate_blog)
    else:
        print("Blog generation failed")

    return {
        "statusCode": 200,
        "body": json.dumps("Blog generated successfully")
    }
        


