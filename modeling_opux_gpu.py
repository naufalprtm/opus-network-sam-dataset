from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import random
import json
import numpy as np
from datetime import datetime, timedelta
import logging
import textstat
from concurrent.futures import ThreadPoolExecutor, as_completed
import torch
import sys
import unicodedata

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Check if GPU is available
device = 0 if torch.cuda.is_available() else -1  # Use GPU if available, otherwise fallback to CPU
model_name = "gpt2"  # Model lebih ringan
tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir="./cache")
model = AutoModelForCausalLM.from_pretrained(model_name, cache_dir="./cache")
access_token = "hf_XXXXXXXXXXXXXXXXXXXXXX"  # Replace with your actual Hugging Face user access token

qa_pipeline = None
try:
    # Load the tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=access_token, clean_up_tokenization_spaces=False)  # Set clean_up_tokenization_spaces
    model = AutoModelForCausalLM.from_pretrained(model_name, use_auth_token=access_token)
    # Initialize the pipeline
    qa_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer, device=device, pad_token_id=tokenizer.eos_token_id)
except Exception as e:
    logging.error(f"Error initializing model or tokenizer: {e}")

# List of keywords, topics, and job titles for generating questions
keywords = [
    'AI', 'blockchain', 'big data', 'machine learning', 'data science', 'cloud computing',
    'cybersecurity', 'IoT', '5G', 'quantum computing', 'virtual reality', 'augmented reality',
    'automated systems', 'natural language processing', 'robotics', 'smart devices', 'digital marketing',
    'e-commerce', 'fintech', 'health tech', 'edtech', 'supply chain management', 'logistics',
    'artificial intelligence', 'deep learning', 'predictive analytics', 'edge computing', 'bioinformatics',
    'digital transformation', 'enterprise software', 'internet security', 'regtech', 'telemedicine',
    'privacy', 'machine vision', 'deepfake detection', 'generative models', 'AI ethics', 'blockchain scalability',
    'smart contracts', 'cryptocurrency', 'financial modeling', 'investment analytics', 'telecommunications',
    'user experience design', 'personalization', 'data mining', 'software architecture', 'agile methodologies',
    'strategy', 'innovation', 'customer experience', 'market trends', 'product development', 'operational efficiency',
    'risk management', 'data privacy', 'technology adoption', 'strategic planning', 'team collaboration',
    'financial performance', 'competitive analysis', 'user engagement', 'sustainability', 'scalability', 'cost reduction',
    'productivity improvement', 'regulatory compliance', 'digital strategy', 'user interface design',
    'supply chain optimization', 'digital payment systems', 'global market expansion', 'business intelligence',
    'real-time data analysis', 'ethical AI practices', 'cyber threat detection', 'customer retention strategies',
    'innovation management', 'cloud migration', 'data governance', 'industry regulations', 'remote work efficiency',
    'web3', 'distributed ledger technology', 'decentralized finance', 'protocol development', 'network security',
    'tokenomics', 'DAO governance', 'protocol scaling', 'data interoperability', 'blockchain forensics',
    'privacy-preserving computation', 'next-generation cryptography', 'digital asset management', 'NFTs'
]

job_titles = [
    'Data Scientist', 'Blockchain Developer', 'AI Researcher', 'Cybersecurity Analyst', 'Cloud Engineer',
    'Product Manager', 'Business Analyst', 'Software Engineer', 'UX/UI Designer', 'Systems Architect',
    'Digital Marketer', 'Project Manager', 'Operations Manager', 'Financial Analyst', 'Tech Lead',
    'Consultant', 'Strategy Advisor', 'Innovation Specialist', 'Research Scientist', 'Technical Writer',
    'DevOps Engineer', 'Systems Administrator', 'Product Designer', 'Technical Project Manager',
    'Data Engineer', 'Growth Hacker', 'Customer Success Manager', 'Compliance Officer', 'Ethical Hacker',
    'Sales Engineer', 'Artificial Intelligence Engineer', 'Machine Learning Engineer', 'Big Data Engineer',
    'Data Privacy Officer', 'Risk Analyst', 'Business Development Manager', 'Marketing Strategist',
    'CRM Specialist', 'Healthcare IT Specialist', 'E-commerce Specialist', 'Web3 Developer',
    'Decentralized Finance Expert', 'Protocol Developer', 'Tokenomics Specialist', 'DAO Governance Expert',
    'Blockchain Forensics Analyst', 'Privacy-Preserving Computation Specialist', 'Cryptography Expert',
    'Digital Asset Manager', 'NFT Specialist'
]


# List of topics for generating questions
topic = [
    'digital transformation', 'data privacy', 'technology adoption', 'innovation management',
    'cloud computing', 'cybersecurity', 'AI ethics', 'blockchain scalability', 'financial modeling',
    'user experience', 'product development', 'strategic planning', 'supply chain optimization',
    'regulatory compliance', 'market trends', 'customer engagement', 'business intelligence',
    'remote work efficiency', 'ethics in AI', 'web3 technology', 'decentralized finance',
    'protocol development', 'network security', 'tokenomics', 'DAO governance', 'blockchain forensics',
    'privacy-preserving computation', 'cryptographic advancements', 'digital asset management',
    'NFTs', 'distributed ledger technology', 'data interoperability'
]


# Function to generate dynamic topics based on keywords
def generate_dynamic_topics():
    return random.sample(keywords, k=5)  # Sample 5 random topics from keywords


def normalize_text(text):
    return unicodedata.normalize('NFKD', text)

def generate_qa_batch(prompts_batch):
    try:
        # Generate responses for the entire batch in one pass
        responses = qa_pipeline(prompts_batch, max_length=300, num_return_sequences=1, temperature=0.9, top_k=100, top_p=0.9, truncation=True)
        qa_pairs = []
        
        for i, prompt in enumerate(prompts_batch):
            question = f"What is {prompt.strip()}?"
            answer = responses[i][0]['generated_text'].strip().replace("\n", " ")  # Adjusted access

            # Normalize the text to remove any unwanted Unicode escapes
            answer = normalize_text(answer)

            # Optional: limit answer length
            if len(answer) > 1000:
                answer = answer[:1000] + "..."

            if not answer.endswith("."):
                answer += "."
            answer += " Thank you for your interest in this topic."

            # Validate answer quality
            if validate_answer(answer, prompt):
                qa_pairs.append({
                    "question": question,
                    "answer": answer
                })
            else:
                qa_pairs.append({
                    "question": question,
                    "answer": "Answer quality is insufficient."
                })
        
        return qa_pairs
    except Exception as e:
        logging.error(f"Error generating QA for batch: {str(e)}")
        return []

        
# Function to validate answer quality
def validate_answer(answer, prompt):
    if len(answer) < 10:
        return False
    prompt_keywords = set(prompt.lower().split())
    answer_keywords = set(answer.lower().split())
    if not prompt_keywords.intersection(answer_keywords):
        return False
    readability_score = textstat.flesch_kincaid_grade(answer)
    return readability_score <= 12

# Function to generate a random timestamp with random time component (hours, minutes, seconds)
def generate_random_timestamp(start_date, end_date):
    time_between_dates = end_date - start_date
    random_number_of_days = np.random.randint(time_between_dates.days)
    random_number_of_seconds = np.random.randint(86400)  # 86400 seconds in a day
    random_timestamp = start_date + timedelta(days=random_number_of_days, seconds=random_number_of_seconds)
    return random_timestamp.strftime("%Y-%m-%d %H:%M:%S")


# Generate the dataset with batch processing
def generate_dataset(prompts, batch_size=10):
    dataset = []
    with open('Dataset-SAM-by-.json', 'w') as f:
        with ThreadPoolExecutor(max_workers=20) as executor:
            for i in range(0, len(prompts), batch_size):
                prompt_batch = prompts[i:i + batch_size]
                future = executor.submit(generate_qa_batch, prompt_batch)
                
                # Wait for batch processing to complete
                qa_pairs = future.result()
                for qa_pair in qa_pairs:
                    # Skip entries where the answer is insufficient
                    if qa_pair['answer'] == "Answer quality is insufficient.":
                        continue  # Skip to the next entry
                    
                    entry = {
                        "content": f"Question: {qa_pair['question']} Answer: {qa_pair['answer']}",
                        "meta": {
                            "time": generate_random_timestamp(datetime(2021, 1, 1), datetime(2023, 12, 31))
                        }
                    }
                    dataset.append(entry)

                    # Save incrementally to file
                    json.dump(entry, f, indent=4)
                    f.write('\n')
                    f.flush()  # Ensure the data is written to disk
    return dataset


# Function to generate questions based on keywords and job titles
# Function to generate questions based on random selections from keywords, job titles, and topics
def generate_prompts(num_prompts=100):
    prompts = []
    for _ in range(num_prompts):
        keyword1 = random.choice(keywords)
        keyword2 = random.choice(keywords)
        job_title = random.choice(job_titles)
        topic_choice = random.choice(topic)  # Renamed to avoid conflict with global variable
        
        prompts.extend([
            # Keywords and Job Titles Integration
            f"How does Sam integrate {keyword1} and {keyword2} to drive innovation in {topic_choice} as a {job_title}?",
            f"In what ways does Sam leverage {keyword1} and {keyword2} to improve {topic_choice} in his role as a {job_title}?",
            f"Discuss how Sam uses {keyword1} and {keyword2} to achieve success in {topic_choice} as a {job_title}.",
            f"How does Sam apply {keyword1} and {keyword2} to overcome challenges in {topic_choice} as a {job_title}?",
            f"What impact does Sam's use of {keyword1} and {keyword2} have on {topic_choice} in his position as a {job_title}?",
            f"How does Sam utilize {keyword1} and {keyword2} to address issues in {topic_choice} as a {job_title}?",
            f"What innovative approaches does Sam take with {keyword1} and {keyword2} to advance {topic_choice} as a {job_title}?",
            f"How do {keyword1} and {keyword2} enhance Sam's strategies for {topic_choice} in his role as a {job_title}?",

            # Role and Expertise
            f"How does Sam's role as a {job_title} influence his approach to {topic_choice} using {keyword1} and {keyword2}?",
            f"In what ways does Sam's expertise in {keyword1} and {keyword2} shape his contributions to {topic_choice}?",
            f"What are the key strategies Sam employs with {keyword1} and {keyword2} to address challenges in {topic_choice}?",
            f"How does Sam’s background in {keyword1} and {keyword2} affect his work on {topic_choice} as a {job_title}?",
            f"How does Sam utilize his skills in {keyword1} and {keyword2} to influence {topic_choice} in his professional role?",
            f"Discuss the significance of Sam’s knowledge in {keyword1} and {keyword2} for his work on {topic_choice} as a {job_title}.",
            
            # Industry Impact and Trends
            f"What are the broader implications of Sam's work with {keyword1} and {keyword2} on {topic_choice}?",
            f"How does Sam’s use of {keyword1} and {keyword2} impact industry trends in {topic_choice}?",
            f"In what ways does Sam’s approach with {keyword1} and {keyword2} set new standards in {topic_choice}?",
            f"How does Sam foresee {keyword1} and {keyword2} evolving in relation to {topic_choice} over the next few years?",
            f"Discuss how Sam’s innovations in {keyword1} and {keyword2} influence future developments in {topic_choice}.",
            f"What role does Sam's expertise in {keyword1} and {keyword2} play in shaping future trends in {topic_choice}?",
            
            # Challenges and Solutions
            f"What are the main challenges Sam encounters when integrating {keyword1} and {keyword2} into {topic_choice}?",
            f"How does Sam address the difficulties of working with {keyword1} and {keyword2} in {topic_choice}?",
            f"In what ways does Sam overcome obstacles related to {keyword1} and {keyword2} in {topic_choice}?",
            f"Discuss the solutions Sam implements for the challenges associated with {keyword1} and {keyword2} in {topic_choice}.",
            f"How does Sam’s approach to {keyword1} and {keyword2} help resolve issues in {topic_choice}?",
            f"How does Sam adapt his strategies with {keyword1} and {keyword2} to handle challenges in {topic_choice}?"
        ])
    return prompts

# Generate prompts and dataset
prompts = generate_prompts()
dataset = generate_dataset(prompts, batch_size=10)

logging.info(f"Dataset generation complete. {len(dataset)} entries saved.")