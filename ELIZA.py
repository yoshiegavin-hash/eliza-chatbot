import re
import random
import string
from datetime import datetime

# 实现一个简易的聊天机器人

# ========== 上下文记忆功能 ==========
memory = {
    "name": None,
    "age": None,
    "job": None,
    "major": None,
    "hobby": None,
    "last_topic": None,
}

memory_patterns = [
    (r'(?:my name is|i am called|i\'?m)\s+(\w+)', "name", "name"),
    (r'(?:i am|i\'?m)\s+(\d{1,3})\s*(?:years?\s*old)?', "age", "age"),
    (r'(?:i (?:work|am employed))\s*(?:as\s*)?(.*)', "job", "job"),
    (r'(?:i (?:study|major)\s*(?:in\s*)?)\s*(.*)', "major", "major"),
    (r'(?:my (?:hobby|favorite|hobbies)\s*(?:is|are)?)\s*(.*)', "hobby", "hobby"),
    (r'(?:i (?:like|love|enjoy))\s+(.*)', "hobby", "hobby"),
]

family_words = {"mother", "father", "mom", "dad", "parent", "sister", "brother",
                "wife", "husband", "friend", "family"}

def is_valid_hobby(value):
    """排除家庭成员等非hobby内容"""
    words = {w.strip(string.punctuation) for w in value.lower().split()}
    return not bool(words & family_words)

def try_extract_memory(user_input):
    """尝试从用户输入中提取关键信息并存储到记忆中"""
    for pattern, field, mem_key in memory_patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            value = match.group(1).strip().strip(string.punctuation)
            if value:
                # hobby 类型需要额外过滤(排除家庭成员等)
                if mem_key == "hobby" and not is_valid_hobby(value):
                    continue
                memory[mem_key] = value
                memory["last_topic"] = field

def recall_memory(user_input):
    """在对话中引用已存储的记忆信息"""
    keywords = ["who am i", "what do you know", "remember", "about me", "do you know me", "my name"]
    is_explicit_recall = any(kw in user_input.lower() for kw in keywords)

    if is_explicit_recall:
        facts = []
        if memory["name"]:
            facts.append(f"your name is {memory['name']}")
        if memory["age"]:
            facts.append(f"you are {memory['age']} years old")
        if memory["job"]:
            facts.append(f"you work as {memory['job']}")
        if memory["major"]:
            facts.append(f"you study {memory['major']}")
        if memory["hobby"]:
            facts.append(f"you enjoy {memory['hobby']}")
        if facts:
            return "Let me see... I remember that " + ", and ".join(facts) + ".", None
        return "You haven't told me much about yourself yet. What's your name?", None

    # 随机引用记忆进行引导（非主动询问时）
    if random.random() < 0.15:
        if memory["name"] and "my name" not in user_input.lower():
            return None, f"By the way, {memory['name']}, how does that make you feel?"
        if memory["hobby"] and "mother" not in str(memory["hobby"]).lower():
            return None, f"Have you had time for {memory['hobby']} lately?"
    return None, None

# ========== 规则库 ==========
rules = {
    r'I need(.*)':[
        "Why do you need {0}?",
        "Would it really help you to get {0}?",
        "Are you sure you need {0}?"
    ],
    r'Why don\'t you (.*)\?':[
        "Do you really think I don't {0}?",
        "Perhaps eventually I will {0}.",
        "Do you really want me to {0}?"
    ],
    r'Why can\'t I (.*)\?': [
        "Do you think you should be able to {0}?",
        "If you could {0}, what would you do?",
        "I don't know -- why can't you {0}?"
    ],
    r'I am (.*)': [
        "Did you come to me because you are {0}?",
        "How long have you been {0}?",
        "How do you feel about being {0}?"
    ],
     r'.* mother .*': [
        "Tell me more about your mother.",
        "What was your relationship with your mother like?",
        "How do you feel about your mother?"
    ],
    r'.* father .*': [
        "Tell me more about your father.",
        "How did your father make you feel?",
        "What has your father taught you?"
    ],
    r'.*(?:work|job|career|boss|colleague|office).*': [
        "How do you feel about your work?",
        "What does your daily work look like?",
        "Do you enjoy your job?"
    ],
    r'.*(?:study|school|class|exam|grade|course|major|university).*': [
        "What are you studying?",
        "How do you find your classes?",
        "What do you enjoy most about school?"
    ],
    r'.*(?:hobby|sport|game|music|read|movie|paint|draw|cook).*': [
        "That sounds interesting -- tell me more about it.",
        "How did you get into that?",
        "What do you enjoy most about that?"
    ],
    r'.*(?:stress|anxious|tired|burnout|overwhelm|pressure).*': [
        "It sounds like you're going through a lot. Want to talk about it?",
        "How do you usually cope with that feeling?",
        "Have you talked to anyone about how you feel?"
    ],
     r'.*': [
        "Please tell me more.",
        "Let's change focus a bit... Tell me about your family.",
        "Can you elaborate on that?"
    ]
}

# 定义代词转换规则
prounoun_swap = {
    "i": "you", "you": "i", "me":"you", "my":"your",
    "am": "are", "are":"am", "was":"were", "i'd": "you would",
    "i've": "you have", "i'll": "you will", "yours": "mine",
    "mine": "yours"
}

def swap_pronouns(phrase):
    """
    对输入短语中的代词进行第一/第二人称转换
    """
    words = phrase.lower().split()
    swapped_words = [prounoun_swap.get(word, word) for word in words]
    return " ".join(swapped_words)

def respond(user_input):
    """
    根据规则库生成响应
    """
    # 尝试提取记忆
    try_extract_memory(user_input)

    # 尝试引用记忆
    mem_recall, mem_response = recall_memory(user_input)
    if mem_recall:
        return mem_recall
    if mem_response:
        return mem_response

    for pattern, responses in rules.items():
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            # 捕获匹配到的部分
            captured_group = match.group(1) if match.groups() else ''
            # 进行代词转化
            swapped_group = swap_pronouns(captured_group)
            # 从模板中随机选择一个并格式化
            response = random.choice(responses).format(swapped_group)
            return response

    # 如果没有匹配仍和特定规则，使用最后的通配符规则
    return random.choice(rules[r'.*'])

# 主聊天循环
if __name__ == '__main__':
    print("Therapist: Hello! I'm Eliza. Tell me about yourself -- you can tell me your name, age, job, or hobbies.")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit", "bye"]:
            print("Therapist: Goodbye. It was nice talking to you.")
            break
        response = respond(user_input)
        print(f"Therapist: {response}")