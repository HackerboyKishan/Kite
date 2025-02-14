import json
import random

keywords = [
    "Kite AI", "blockchain", "AI", "Proof of AI", "decentralized", "transparency",
    "collaboration", "scalability", "data subnets", "model subnets", "agent subnets",
    "intelligent applications", "democratize AI", "open collaboration", "infrastructure",
    "smart contracts", "NFT", "DeFi", "crypto mining", "machine learning",
    "AI governance", "Web3", "DAO", "metaverse", "hashing", "public ledger",
    "crypto wallet", "Ethereum", "Bitcoin", "staking", "consensus mechanism",
    "privacy coins", "oracles", "layer 2 scaling", "quantum computing in blockchain",
    "AI-powered trading", "automated decision-making", "neural networks",
    "AI-driven security", "tokenomics", "game theory in crypto", "zero-knowledge proofs",
    "crypto regulation", "AI-generated content", "self-sovereign identity",
    "AI ethics", "cryptographic security", "AI and decentralized finance"
]

extra_phrases = [
    "in the future", "impact on economy", "challenges faced", "advantages and disadvantages",
    "real-world applications", "security concerns", "scalability issues",
    "role in financial markets", "integration with IoT", "comparison with traditional systems",
    "future predictions", "ethical concerns", "adoption by enterprises",
    "potential for mass adoption", "innovation opportunities", "current trends"
]

starters = [
    "What is", "How does", "Why is", "Can you explain", "What are the benefits of",
    "How can", "What makes", "What are the features of", "How does", "What is the purpose of",
    "Why should we use", "What are the risks of", "What are the future prospects of"
]

def generate_random_question():
    random_starter = random.choice(starters)
    random_keyword = random.choice(keywords)
    random_extra = random.choice(extra_phrases)
    return f"{random_starter} {random_keyword} {random_extra}?"

def generate_questions(count):
    return [generate_random_question() for _ in range(count)]

question_count = 10000
random_questions = generate_questions(question_count)

with open('random_questions.json', 'w') as f:
    json.dump(random_questions, f, indent=2)

print(f"{question_count} random questions have been saved in random_questions.json")
