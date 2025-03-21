import boto3
import textwrap
from botocore.exceptions import NoCredentialsError, ClientError
from groq import Groq
from aixplain.factories import ModelFactory

def generate_flowcharts(transcription, s3_key_prefix, api_key, aws_access_key, aws_secret_key, 
                        bucket_name, region_name, num_concepts=5):
    """
    Generates flowcharts from a transcription and uploads them to S3.
    
    Parameters:
    - transcription (str): The text to process and generate flowcharts from.
    - s3_key_prefix (str): Prefix for the S3 keys where flowcharts will be stored.
    - api_key (str): API key for Groq.
    - aws_access_key (str): AWS access key for S3 access.
    - aws_secret_key (str): AWS secret key for S3 access.
    - bucket_name (str): Name of the S3 bucket to store flowcharts.
    - region_name (str): AWS region for the S3 bucket.
    - num_concepts (int, optional): Number of concepts to extract. Defaults to 5.
    
    Returns:
    - dict: A dictionary containing URLs of generated flowcharts.
    """
    try:
        # Initialize services
        groq_client = Groq(api_key=api_key)
        s3_client = boto3.client('s3', 
                             aws_access_key_id=aws_access_key, 
                             aws_secret_access_key=aws_secret_key, 
                             region_name=region_name)
        
        # Define colors for the flowchart
        colors = {
            'main': {'fill': '#e3f2fd', 'stroke': '#1565c0'},
            'primary': [
                {'fill': '#e8f5e9', 'stroke': '#2e7d32'},
                {'fill': '#fff3e0', 'stroke': '#ef6c00'}
            ],
            'secondary': [
                {'fill': '#f1f8e9', 'stroke': '#558b2f'},
                {'fill': '#fff8e1', 'stroke': '#ff8f00'},
                {'fill': '#f3e5f5', 'stroke': '#6a1b9a'},
                {'fill': '#e1f5fe', 'stroke': '#0288d1'}
            ]
        }
        
        # Process transcription into chunks
        chunks = textwrap.wrap(transcription, width=300)
        num_chunks = min(num_concepts, len(chunks))
        urls = []
        
        for i in range(num_chunks):
            print(f"Processing concept {i + 1}...")
            
            # Extract hierarchy from chunk
            concepts = extract_hierarchy(groq_client, chunks[i])
            if not concepts:
                print(f"Skipping concept {i + 1} due to extraction error.")
                continue
            
            # Generate SVG flowchart
            svg_content = generate_svg(concepts, colors)
            if svg_content:
                s3_key = f"{s3_key_prefix}_concept_{i + 1}.svg"
                
                # Upload to S3
                svg_url = upload_to_s3(s3_client, svg_content.encode('utf-8'), 
                                       s3_key, bucket_name, region_name, 
                                       "image/svg+xml")
                if svg_url:
                    urls.append(svg_url)
        
        return {"urls": urls}
    
    except Exception as e:
        print(f"Error in flowchart generation: {e}")
        return {"urls": [], "error": str(e)}

def truncate_text(text, max_length=30):
    """Truncate text if it exceeds max_length."""
    return text[:max_length] + '...' if len(text) > max_length else text

def wrap_text(text, x, y, max_width=180):
    """Generate SVG text with wrapping and centering."""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        current_line.append(word)
        if len(' '.join(current_line)) > max_width / 10:
            if len(current_line) > 1:
                lines.append(' '.join(current_line[:-1]))
                current_line = [word]
            else:
                lines.append(word)
                current_line = []

    if current_line:
        lines.append(' '.join(current_line))

    lines = lines[:2]
    if len(lines) > 1:
        lines[1] = truncate_text(lines[1], 25)

    svg_text = f'<text x="{x}" y="{y}" text-anchor="middle" font-family="Arial" font-size="14">'
    for i, line in enumerate(lines):
        dy = -10 if len(lines) > 1 else 0
        svg_text += f'<tspan x="{x}" dy="{dy + i * 20}">{line}</tspan>'
    svg_text += '</text>'
    return svg_text

def extract_hierarchy(client, text):
    """Extract hierarchy using Groq API."""
    prompt = """
    Create a concise hierarchical outline with:
    - One main topic (3-4 words max)
    - Two primary subtopics (2-3 words each)
    - Two secondary points per primary topic (2-3 words each)
    
    Format as:
    MAIN: [topic]
    P1: [primary1]
    P2: [primary2]
    S1: [secondary1]
    S2: [secondary2]
    S3: [secondary3]
    S4: [secondary4]
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": f"{prompt}\n\nText: {text}"}],
            model="llama3-8b-8192",
        )
        response = chat_completion.choices[0].message.content

        lines = response.strip().split('\n')
        concepts = {'main': '', 'primary': [], 'secondary': []}

        for line in lines:
            if line.startswith('MAIN:'):
                concepts['main'] = truncate_text(line.replace('MAIN:', '').strip(), 40)
            elif line.startswith('P'):
                concepts['primary'].append(truncate_text(line.split(':', 1)[1].strip(), 30))
            elif line.startswith('S'):
                concepts['secondary'].append(truncate_text(line.split(':', 1)[1].strip(), 25))

        if len(concepts['primary']) < 2:
            concepts['primary'].append("Additional Topic")
        if len(concepts['secondary']) < 4:
            concepts['secondary'].extend(["Additional Detail"] * (4 - len(concepts['secondary'])))

        return concepts

    except Exception as e:
        print(f"Error in extraction: {e}")
        return None

def generate_svg(concepts, colors):
    """Generate SVG for the flowchart."""
    try:
        svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 600">
    <style>
        rect {{ rx: 10; stroke-width: 2; }}
        text {{ font-family: Arial; font-size: 14px; text-anchor: middle; }}
    </style>
    <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#666"/>
        </marker>
    </defs>
    
    <!-- Main Topic -->
    <rect x="400" y="50" width="200" height="60" fill="{colors['main']['fill']}" stroke="{colors['main']['stroke']}"/>
    {wrap_text(concepts['main'], 500, 85)}

    <!-- Primary Topics -->
    <rect x="150" y="200" width="200" height="60" fill="{colors['primary'][0]['fill']}" stroke="{colors['primary'][0]['stroke']}"/>
    {wrap_text(concepts['primary'][0], 250, 235)}

    <rect x="650" y="200" width="200" height="60" fill="{colors['primary'][1]['fill']}" stroke="{colors['primary'][1]['stroke']}"/>
    {wrap_text(concepts['primary'][1], 750, 235)}

    <!-- Secondary Topics -->
    <rect x="50" y="350" width="180" height="60" fill="{colors['secondary'][0]['fill']}" stroke="{colors['secondary'][0]['stroke']}"/>
    {wrap_text(concepts['secondary'][0], 140, 385)}

    <rect x="270" y="350" width="180" height="60" fill="{colors['secondary'][1]['fill']}" stroke="{colors['secondary'][1]['stroke']}"/>
    {wrap_text(concepts['secondary'][1], 360, 385)}

    <rect x="550" y="350" width="180" height="60" fill="{colors['secondary'][2]['fill']}" stroke="{colors['secondary'][2]['stroke']}"/>
    {wrap_text(concepts['secondary'][2], 640, 385)}

    <rect x="770" y="350" width="180" height="60" fill="{colors['secondary'][3]['fill']}" stroke="{colors['secondary'][3]['stroke']}"/>
    {wrap_text(concepts['secondary'][3], 860, 385)}

    <!-- Connections -->
    <line x1="500" y1="110" x2="250" y2="200" stroke="#666" stroke-width="2" marker-end="url(#arrowhead)"/>
    <line x1="500" y1="110" x2="750" y2="200" stroke="#666" stroke-width="2" marker-end="url(#arrowhead)"/>
    <line x1="250" y1="260" x2="140" y2="350" stroke="#666" stroke-width="2" marker-end="url(#arrowhead)"/>
    <line x1="250" y1="260" x2="360" y2="350" stroke="#666" stroke-width="2" marker-end="url(#arrowhead)"/>
    <line x1="750" y1="260" x2="640" y2="350" stroke="#666" stroke-width="2" marker-end="url(#arrowhead)"/>
    <line x1="750" y1="260" x2="860" y2="350" stroke="#666" stroke-width="2" marker-end="url(#arrowhead)"/>
</svg>"""
        return svg_content
    except Exception as e:
        print(f"Error generating SVG: {e}")
        return None

def upload_to_s3(s3_client, file_content, s3_key, bucket_name, region_name, content_type):
    """Upload a file to S3 and return the public URL"""
    try:
        s3_client.put_object(
            Bucket=bucket_name, 
            Key=s3_key, 
            Body=file_content, 
            ContentType=content_type, 
            ACL='public-read'
        )
        return f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{s3_key}"
    except NoCredentialsError:
        print("Credentials not available")
        return None
    except ClientError as e:
        print(f"Unexpected error: {e}")
        return None

# Example usage
"""
transcription = "Your transcription text here..."
api_key = "your_groq_api_key"
aws_access_key = "your_aws_access_key"
aws_secret_key = "your_aws_secret_key"
bucket_name = "your_s3_bucket"
region_name = "your_aws_region"
s3_key_prefix = "flowcharts/example"

result = generate_flowcharts(
    transcription=transcription,
    s3_key_prefix=s3_key_prefix,
    api_key=api_key,
    aws_access_key=aws_access_key,
    aws_secret_key=aws_secret_key,
    bucket_name=bucket_name,
    region_name=region_name
)
print(result)
"""