from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import random
import json
import numpy as np
from datetime import datetime, timedelta
import logging
import textstat
from concurrent.futures import ThreadPoolExecutor, as_completed

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize text generation pipeline with a more advanced model
device = -1  # Use CPU
model_name = "gpt2"  # Replace with a valid model identifier
access_token = "hf_XXXXXXXXXXXXXXXXXXXX"  # Replace with your actual Hugging Face user access token

qa_pipeline = None
try:
    # Load the tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=access_token)
    model = AutoModelForCausalLM.from_pretrained(model_name, use_auth_token=access_token)
    # Initialize the pipeline
    qa_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer, device=device, pad_token_id=tokenizer.eos_token_id)
except Exception as e:
    logging.error(f"Error initializing model or tokenizer: {e}")

# Use the pipeline if it is properly initialized
if qa_pipeline:
    question = "What role do e-commerce and big data play in Sam's approach to next-generation cryptography in his capacity as a Healthcare IT Specialist?"
    try:
        answer = qa_pipeline(question)
        print(answer)
    except Exception as e:
        logging.error(f"Error generating answer: {e}")
else:
    logging.error("The QA pipeline was not initialized properly.")

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

# Function to generate answers with a long length and ensure proper closing
def generate_qa(text_prompt):
    try:
        # Optimize output with adjusted parameters
        response = qa_pipeline(text_prompt, max_length=10000, truncation=True, num_return_sequences=1, 
                               temperature=0.8, top_k=100, top_p=0.9)
        generated_text = response[0]["generated_text"]
        
        # Generate a question and answer
        question = f"What is {text_prompt.strip()}?"
        answer = generated_text.strip().replace("\n", " ")  # Clean up the answer
        
        # Optional: Limit length of answer and ensure quality
        max_answer_length = 10000
        if len(answer) > max_answer_length:
            answer = answer[:max_answer_length] + "..."
        
        # Ensure answer has a proper closing statement
        if not answer.endswith("."):
            answer += "."
        answer += " Thank you for your interest in this topic."

        # Validate answer quality
        if not validate_answer(answer, text_prompt):
            answer = "Answer quality is insufficient."
        
        return {
            "question": question,
            "answer": answer
        }
    except Exception as e:
        logging.error(f"Error generating QA for prompt '{text_prompt}': {str(e)}")
        return {
            "question": f"What is {text_prompt.strip()}?",
            "answer": f"Unable to generate answer due to error: {str(e)}"
        }
        
# Placeholder function to validate answer quality
def validate_answer(answer, prompt):
    # Check length
    if len(answer) < 10:
        return False
    
    # Check for presence of keywords from the prompt
    prompt_keywords = set(prompt.lower().split())
    answer_keywords = set(answer.lower().split())
    if not prompt_keywords.intersection(answer_keywords):
        return False
    
    # Check readability score (Flesch-Kincaid Grade Level)
    readability_score = textstat.flesch_kincaid_grade(answer)
    if readability_score > 12:  # Adjust threshold based on the expected audience
        return False
    
    return True

# Function to generate a random timestamp
def generate_random_timestamp(start_date, end_date):
    time_between_dates = end_date - start_date
    random_number_of_days = np.random.randint(time_between_dates.days)
    random_timestamp = start_date + timedelta(days=random_number_of_days)
    return random_timestamp.strftime("%Y-%m-%d %H:%M:%S")

# Function to generate dataset with improved sampling strategy
def generate_dataset(prompts, num_samples=5):
    dataset = []
    sampled_prompts = random.sample(prompts, min(num_samples, len(prompts)))
    
    # Define the maximum number of workers (threads) to use
    max_workers = 4

    # Use ThreadPoolExecutor to limit the number of concurrent tasks
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_prompt = {executor.submit(generate_qa, prompt): prompt for prompt in sampled_prompts}
        
        for future in as_completed(future_to_prompt):
            prompt = future_to_prompt[future]
            try:
                qa_pair = future.result()
                entry = {
                    "content": f"Question: {qa_pair['question']} Answer: {qa_pair['answer']}",
                    "meta": {
                        "time": generate_random_timestamp(datetime(2021, 1, 1), datetime(2021, 12, 31))
                    }
                }
                dataset.append(entry)
            except Exception as e:
                logging.error(f"Error generating dataset entry for prompt '{prompt}': {str(e)}")
    
    return dataset

# Function to generate questions based on keywords and job titles
def generate_prompts():
    prompts = []
    topics = generate_dynamic_topics()
    for keyword1 in keywords:
        for keyword2 in keywords:
            for job_title in job_titles:
                for topic in topics:
                    prompts.extend([
    # Keywords and Job Titles Integration
    f"How does Sam integrate {keyword1} and {keyword2} to drive innovation in {topic} as a {job_title}?",
    f"In what ways does Sam leverage {keyword1} and {keyword2} to improve {topic} in his role as a {job_title}?",
    f"Discuss how Sam uses {keyword1} and {keyword2} to achieve success in {topic} as a {job_title}.",
    f"How does Sam apply {keyword1} and {keyword2} to overcome challenges in {topic} as a {job_title}?",
    f"What impact does Sam's use of {keyword1} and {keyword2} have on {topic} in his position as a {job_title}?",
    f"How does Sam utilize {keyword1} and {keyword2} to address issues in {topic} as a {job_title}?",
    f"What innovative approaches does Sam take with {keyword1} and {keyword2} to advance {topic} as a {job_title}?",
    f"How do {keyword1} and {keyword2} enhance Sam's strategies for {topic} in his role as a {job_title}?",

    # Role and Expertise
    f"How does Sam's role as a {job_title} influence his approach to {topic} using {keyword1} and {keyword2}?",
    f"In what ways does Sam's expertise in {keyword1} and {keyword2} shape his contributions to {topic}?",
    f"What are the key strategies Sam employs with {keyword1} and {keyword2} to address challenges in {topic}?",
    f"How does Sam’s background in {keyword1} and {keyword2} affect his work on {topic} as a {job_title}?",
    f"How does Sam utilize his skills in {keyword1} and {keyword2} to influence {topic} in his professional role?",
    f"Discuss the significance of Sam’s knowledge in {keyword1} and {keyword2} for his work on {topic} as a {job_title}.",
    
    # Industry Impact and Trends
    f"What are the broader implications of Sam's work with {keyword1} and {keyword2} on {topic}?",
    f"How does Sam’s use of {keyword1} and {keyword2} impact industry trends in {topic}?",
    f"In what ways does Sam’s approach with {keyword1} and {keyword2} set new standards in {topic}?",
    f"How does Sam foresee {keyword1} and {keyword2} evolving in relation to {topic} over the next few years?",
    f"Discuss how Sam’s innovations in {keyword1} and {keyword2} influence future developments in {topic}.",
    f"What role does Sam's expertise in {keyword1} and {keyword2} play in shaping future trends in {topic}?",
    
    # Challenges and Solutions
    f"What are the main challenges Sam encounters when integrating {keyword1} and {keyword2} into {topic}?",
    f"How does Sam address the difficulties of working with {keyword1} and {keyword2} in {topic}?",
    f"What solutions does Sam implement to overcome obstacles in {topic} using {keyword1} and {keyword2}?",
    f"How does Sam tackle complex issues related to {keyword1} and {keyword2} in {topic}?",
    f"What innovative solutions has Sam developed to address challenges in {topic} involving {keyword1} and {keyword2}?",
    f"In what ways does Sam's problem-solving approach with {keyword1} and {keyword2} improve outcomes in {topic}?",
    
    # Strategic Vision and Future Directions
    f"How does Sam plan to use {keyword1} and {keyword2} to advance {topic} in the coming years?",
    f"What strategic initiatives does Sam propose for integrating {keyword1} and {keyword2} into {topic}?",
    f"How does Sam envision the future of {keyword1} and {keyword2} in relation to {topic}?",
    f"What are Sam’s long-term goals for leveraging {keyword1} and {keyword2} in {topic}?",
    f"How does Sam plan to address emerging trends in {keyword1} and {keyword2} to influence {topic}?",
    f"What future advancements in {keyword1} and {keyword2} does Sam anticipate will impact {topic}?",
    
    # Cross-Disciplinary Insights
    f"How does Sam’s work with {keyword1} and {keyword2} bridge different domains within {topic}?",
    f"In what ways does Sam’s expertise in {keyword1} and {keyword2} contribute to interdisciplinary solutions for {topic}?",
    f"How does Sam apply {keyword1} and {keyword2} across various disciplines to enhance {topic}?",
    f"Discuss the role of {keyword1} and {keyword2} in Sam’s approach to integrating different fields within {topic}.",
    f"How does Sam’s cross-disciplinary approach with {keyword1} and {keyword2} address complex issues in {topic}?",
    
    # Personal and Professional Impact
    f"How does Sam’s personal vision for {keyword1} and {keyword2} shape his professional work in {topic}?",
    f"What personal insights does Sam bring to his role involving {keyword1} and {keyword2} in {topic}?",
    f"How does Sam’s career trajectory influence his approach to {keyword1} and {keyword2} in {topic}?",
    f"In what ways does Sam’s professional background impact his use of {keyword1} and {keyword2} in {topic}?",
    f"Discuss how Sam’s personal goals align with his professional strategies involving {keyword1} and {keyword2} in {topic}.",
    
    # Impact on Digital Twin Creation
    f"How does Sam’s work with {keyword1} and {keyword2} contribute to creating a comprehensive digital twin for {topic}?",
    f"In what ways does Sam’s expertise in {keyword1} and {keyword2} enhance the digital twin model for {topic}?",
    f"How does Sam’s integration of {keyword1} and {keyword2} support the development of an accurate digital twin for {topic}?",
    f"What role does Sam’s knowledge in {keyword1} and {keyword2} play in refining the digital twin for {topic}?",
    f"How does Sam’s approach to {keyword1} and {keyword2} influence the accuracy and completeness of the digital twin for {topic}?"
                    ])
    return prompts

# Generate prompts
prompts = generate_prompts()

# Generate dataset
dataset = generate_dataset(prompts, num_samples=1000)

# Save the dataset to a JSON file
with open('Dataset-SAM-by-zixine.json', 'w') as f:
    json.dump(dataset, f, indent=4)

logging.info(f"Dataset generation complete. {len(dataset)} entries saved to 'generated_dataset.json'.")
