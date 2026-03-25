#!/usr/bin/env python3
"""
Sanskrit-USR-Paragraph-NLG (Sanskrit Universal Semantic Representation Paragraph Natural Language Generation)
"""

import os
import sys
import re
import argparse
import time
from collections import deque
from typing import List, Dict, Any

try:
    from google import genai
except ImportError:
    genai = None
    print("Warning: google-genai not available. Install with: pip install google-genai")

API_KEY = "AIzaSyDTcKd7hjRPEcPxf03AZDzfX49havIUwxs"
BATCH_CHAR_LIMIT = 30000

LANGUAGE_PROMPTS = {
    "english": (
        "You are an English paragraph generator from Sanskrit USR semantic data. "
        "The USR contains semantic information about Sanskrit sentences. "
        "You need to generate natural, flowing English sentences from this Sanskrit semantic data. "
        "CRITICAL RULES - WORK FROM SANSKRIT USR SEMANTIC STRUCTURE: "
        "- Read Sanskrit USR semantic data and generate natural English sentences "
        "- The Sanskrit USR contains semantic tokens with Sanskrit roots, suffixes, and grammatical relations "
        "- Extract meaning from these Sanskrit semantic tokens and their relations (like k1, k7, r6, etc.) "
        "- Understand Sanskrit grammatical concepts like vibhakti, dhatu, pratyaya "
        "- Combine words, verbs, adjectives correctly based on Sanskrit USR semantic structure "
        "- Follow English grammar rules in output "
        "- Join all sentences in order to form a coherent paragraph "
        "- Use appropriate connectors and maintain natural flow "
        "- Do not output USR notation, only natural English sentences "
        "- Replace #[masked] with actual English sentences you generate from Sanskrit USR data "
        "- Make the text sound natural and conversational, not formal or instructional "
        "- CRITICAL: Do NOT translate '$addressee' literally - ignore it or make the sentence natural "
        "- Avoid repetitive addressing like 'Respected addressee' - make it flow naturally "
        "- Generate natural sentences as if explaining to a general audience "
        "- STRICTLY preserve the EXACT meaning from the Sanskrit USR data - NO ADDITIONS OR REMOVALS "
        "- DO NOT add any information not present in the Sanskrit USR data "
        "- DO NOT remove any information present in the Sanskrit USR data "
        "- DO NOT create new concepts, objects, or ideas not in the Sanskrit USR "
        "- DO NOT add examples, analogies, or explanations not in the Sanskrit USR "
        "- DO NOT add any new content, facts, or information "
        "- DO NOT create scenarios, situations, or contexts not in the Sanskrit USR "
        "- DO NOT add descriptive details not present in the Sanskrit USR "
        "- Only add a few words here and there for fluency, nothing more "
        "- If Sanskrit USR data is unclear, stick to what is clearly present "
        "- Generate ONLY what the Sanskrit USR data explicitly contains "
        "- NO HALLUCINATION - ONLY SANSKRIT USR CONTENT "
        "- Understand Sanskrit semantic roles and translate them appropriately to English "
        "Example: Generate natural English sentences from Sanskrit USR semantic structure."
    ),
    "hindi": (
        "आप एक संस्कृत USR से हिंदी वाक्य जनरेटर हैं। आपको संस्कृत USR सेमेंटिक डेटा से प्राकृतिक हिंदी वाक्य बनाने हैं। "
        "संस्कृत USR डेटा में संस्कृत वाक्यों की सेमेंटिक जानकारी है। "
        "आपको इस संस्कृत सेमेंटिक जानकारी से प्राकृतिक हिंदी वाक्य बनाने हैं। "
        "महत्वपूर्ण नियम - केवल संस्कृत USR सामग्री से चिपके रहें: "
        "- संस्कृत USR सेमेंटिक डेटा को पढ़कर प्राकृतिक हिंदी वाक्य बनाएं "
        "- संस्कृत USR में संस्कृत धातु, प्रत्यय, विभक्ति के साथ सेमेंटिक टोकन हैं "
        "- इन संस्कृत सेमेंटिक टोकन और उनके संबंधों (k1, k7, r6, आदि) से अर्थ निकालें "
        "- संस्कृत व्याकरण की अवधारणाओं को समझें जैसे विभक्ति, धातु, प्रत्यय "
        "- संस्कृत USR सेमेंटिक संरचना के आधार पर शब्दों, क्रियाओं, विशेषणों को सही तरीके से जोड़ें "
        "- हिंदी व्याकरण के नियमों का पालन करें "
        "- सभी वाक्यों को क्रमानुसार जोड़कर सुसंगत पैराग्राफ बनाएं "
        "- उचित संयोजक और प्राकृतिक प्रवाह बनाए रखें "
        "- USR नोटेशन न दें, सिर्फ प्राकृतिक हिंदी वाक्य दें "
        "- पाठ को प्राकृतिक और बातचीत जैसा बनाएं, औपचारिक या निर्देशात्मक नहीं "
        "- महत्वपूर्ण: '$addressee' का शाब्दिक अनुवाद न करें - इसे अनदेखा करें या वाक्य को प्राकृतिक बनाएं "
        "- दोहराव वाले संबोधन से बचें - प्राकृतिक प्रवाह बनाएं "
        "- सामान्य दर्शकों को समझाते हुए प्राकृतिक वाक्य बनाएं "
        "- कड़ाई से संस्कृत USR डेटा से सटीक अर्थ बनाए रखें - कोई जोड़ या घटाव नहीं "
        "- संस्कृत USR डेटा में नहीं है वैसी कोई जानकारी न जोड़ें "
        "- संस्कृत USR डेटा में है वैसी कोई जानकारी न हटाएं "
        "- नए विचार, वस्तु या अवधारणाएं न बनाएं जो संस्कृत USR में नहीं हैं "
        "- उदाहरण, सादृश्य या स्पष्टीकरण न जोड़ें जो संस्कृत USR में नहीं हैं "
        "- कोई नई सामग्री, तथ्य या जानकारी न जोड़ें "
        "- परिदृश्य, स्थितियां या संदर्भ न बनाएं जो संस्कृत USR में नहीं हैं "
        "- वर्णनात्मक विवरण न जोड़ें जो संस्कृत USR में नहीं हैं "
        "- केवल प्रवाह के लिए यहां-वहां कुछ शब्द जोड़ें, कुछ नहीं "
        "- यदि संस्कृत USR डेटा अस्पष्ट है, तो स्पष्ट रूप से मौजूद चीज़ों से चिपके रहें "
        "- केवल वही उत्पन्न करें जो संस्कृत USR डेटा में स्पष्ट रूप से मौजूद है "
        "- कोई कल्पना नहीं - केवल संस्कृत USR सामग्री "
        "- संस्कृत सेमेंटिक भूमिकाओं को समझें और उन्हें हिंदी में उचित रूप से अनुवाद करें "
        "उदाहरण: संस्कृत USR सेमेंटिक संरचना से प्राकृतिक हिंदी वाक्य बनाएं।"
    )
}

request_times = deque()
MAX_REQUESTS_PER_MIN = 15

def wait_for_rate_limit():
    while len(request_times) >= MAX_REQUESTS_PER_MIN:
        time_since_oldest = time.time() - request_times[0]
        if time_since_oldest < 60:
            sleep_time = (60 - time_since_oldest) + 2
            time.sleep(sleep_time)
        request_times.popleft()

def call_gemini_api_batch(api_input_text, language="hindi", model_name="gemini-2.5-flash", max_retries=3):
    if genai is None:
        raise RuntimeError("google-genai not available")
        
    # NEW SDK Initialization
    client = genai.Client(api_key=API_KEY)

    for attempt in range(max_retries):
        wait_for_rate_limit()
        request_times.append(time.time())
        
        try:
            # NEW SDK Generation Call
            response = client.models.generate_content(
                model=model_name,
                contents=api_input_text
            )
            return response.text.strip()
            
        except Exception as e:
            if "quota" in str(e).lower() or "429" in str(e):
                if attempt < max_retries - 1:
                    time.sleep(4)
                    continue
                return ""
            else:
                if attempt < max_retries - 1:
                    time.sleep(4)
                    continue
                return ""
    return ""

def parse_usr_string(content: str) -> List[Dict[str, Any]]:
    sent_blocks = re.split(r'(?=<sent_id=|segment_id=)', content.strip())
    sent_blocks = [block.strip() for block in sent_blocks if block.strip() and not block.startswith('</')]
    
    items = []
    for block in sent_blocks:
        sent_id_match = re.search(r'(sent_id|segment_id)=([^>]+)>', block)
        if not sent_id_match: continue
        
        sent_id = sent_id_match.group(2)
        lines = block.split('\n')
        original_sentence = ""
        masked_block = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                original_sentence = line.replace('#', '').strip()
                masked_block.append('#[masked]')
            else:
                masked_block.append(line)
        
        if original_sentence:
            items.append({
                'id': sent_id,
                'original': original_sentence,
                'usr_block': '\n'.join(masked_block)
            })
    items.sort(key=lambda x: x['id'])
    return items

def create_paragraph_prompt(language: str, items: List[Dict[str, Any]], few_shot_examples: List[Dict[str, Any]] = None) -> str:
    prompt = LANGUAGE_PROMPTS.get(language, LANGUAGE_PROMPTS["english"]) + "\n\n"
    
    if few_shot_examples:
        prompt += "Examples:\n"
        for i, example in enumerate(few_shot_examples, 1):
            prompt += f"Example {i}:\n"
            for item in example['items']:
                prompt += f"{item['usr_block']}\n"
            prompt += f"Generated Paragraph: [masked]\n\n"
        prompt += "--- GENERATE ---\n\n"
    
    prompt += f"CRITICAL: Generate a complete paragraph from the following {len(items)} Sanskrit USR segments. "
    prompt += "You MUST translate the EXACT content from each Sanskrit USR segment in the given order. "
    prompt += "Do NOT add any information that is not present in the Sanskrit USR segments.\n\n"
    
    for i, item in enumerate(items, 1):
        prompt += f"Segment {i} (ID: {item['id']}):\n{item['usr_block']}\n\n"
    
    prompt += f"CRITICAL INSTRUCTIONS:\n"
    prompt += f"- Study the Sanskrit USR semantic data in each segment above\n"
    prompt += f"- Extract the meaning from the Sanskrit semantic information (words, verbs, adjectives, relations)\n"
    prompt += f"- Generate proper {language} sentences from the Sanskrit semantic data\n"
    prompt += f"- Follow the EXACT order of segments (1, 2, 3, ...)\n"
    prompt += f"- Combine all {len(items)} segments into one coherent paragraph\n"
    prompt += f"- Do NOT add any information not present in the Sanskrit USR segments\n"
    prompt += f"- Do NOT skip any segments\n"
    prompt += f"- Use appropriate connectors to make the paragraph flow naturally\n"
    prompt += f"- IMPORTANT: Replace #[masked] with the actual {language} sentence you generate from Sanskrit USR data\n"
    prompt += f"- Do NOT output #[masked] or any USR notation in your response\n"
    prompt += f"- Generate ONLY the final {language} paragraph\n"
    prompt += f"- WORK DIRECTLY FROM THE SANSKRIT USR SEMANTIC STRUCTURE\n"
    prompt += f"- The Sanskrit USR contains Sanskrit semantic tokens with roots, suffixes, and grammatical relations\n"
    prompt += f"- Extract meaning from these Sanskrit semantic tokens and their relations (k1, k7, r6, rblsk, etc.)\n"
    prompt += f"- If Sanskrit USR has %interrogative, generate a question\n"
    prompt += f"- If Sanskrit USR has %affirmative, generate a statement\n"
    prompt += f"- Pay attention to the main verb (marked with 0:main) and its arguments\n"
    prompt += f"- Follow the semantic relations to understand the sentence structure\n"
    prompt += f"- For questions: $kim means 'what' in Sanskrit, look for the object being asked about\n"
    prompt += f"- The semantic relations (k1, k7, r6, etc.) show how Sanskrit words connect\n"
    prompt += f"- CRITICAL: ONLY use semantic tokens that are EXPLICITLY present in the Sanskrit USR\n"
    prompt += f"- DO NOT add ANY words, concepts, or ideas that are not in the Sanskrit USR semantic tokens\n"
    prompt += f"- If a semantic token is not in the Sanskrit USR, DO NOT mention it in the output\n"
    prompt += f"- Do not add your own interpretations or explanations\n"
    prompt += f"- Do not add extra words, phrases, or information not in the Sanskrit USR\n"
    prompt += f"- Do not change questions into statements or vice versa\n"
    prompt += f"- Do not change time references\n"
    prompt += f"- Do not change action descriptions\n"
    prompt += f"- Do not omit any semantic information from the Sanskrit USR\n"
    prompt += f"- Generate from Sanskrit USR semantic structure, then make it fluent\n"
    prompt += f"- Preserve ALL semantic information from the Sanskrit USR\n\n"
    prompt += f"Generate the paragraph:"
    return prompt

def wrap_text(text: str, width: int = 80) -> str:
    import textwrap
    return textwrap.fill(text, width=width, break_long_words=False, break_on_hyphens=False)

def process_text(input_text: str, language: str, model_name: str) -> str:
    items = parse_usr_string(input_text)
    if not items:
        return "No valid items found in input."
    
    prompt = create_paragraph_prompt(language, items)
    response_text = call_gemini_api_batch(prompt, language=language, model_name=model_name)

    if not response_text:
        return "[NO RESPONSE]"
        
    return response_text.strip()


def parse_usr_file(file_path: str) -> List[Dict[str, Any]]:
    with open(file_path, 'r', encoding='utf-8') as f:
        return parse_usr_string(f.read())

def process_file(input_file: str, output_file: str, language: str, model_name: str) -> None:
    print(f"Processing {input_file} for paragraph generation...")
    items = parse_usr_file(input_file)
    if not items:
        return
    
    prompt = create_paragraph_prompt(language, items)
    response_text = call_gemini_api_batch(prompt, language=language, model_name=model_name)

    if not response_text:
        generated_paragraph = "[NO RESPONSE]"
    else:
        generated_paragraph = response_text.strip()
    
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        wrapped_paragraph = wrap_text(generated_paragraph, width=80)
        f.write(wrapped_paragraph + "\n")
    
    print(f"  - Generated paragraph in {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Sanskrit-USR-Paragraph-NLG Inference Script (Batch Mode)")
    parser.add_argument("usr_folder", help="Folder containing Sanskrit USR input files (e.g., ./InputDataSanskrit/usr)")
    parser.add_argument("-o", "--output_folder", default="output_usr",
                       help="Folder to save generated paragraph outputs (default: ./output_usr)")
    parser.add_argument("-l", "--language", default="english",
                       choices=["english", "hindi"],
                       help="Target language for paragraph generation (default: english)")
    parser.add_argument("-m", "--model", default="gemini-2.5-flash",
                       choices=["gemini-2.5-pro", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
                       help="Gemini model to use (default: gemini-2.5-flash)")

    args = parser.parse_args()

    usr_folder = args.usr_folder
    output_folder = args.output_folder
    prefix_filter = "27_jan_26_bg_10_chap_shloka_1-11"

    if not os.path.exists(usr_folder):
        print(f"❌ Input folder '{usr_folder}' not found.")
        sys.exit(1)

    os.makedirs(output_folder, exist_ok=True)

    usr_files = [f for f in os.listdir(usr_folder) if f.startswith(prefix_filter) and (f.endswith(".usr") or f.endswith(".txt"))]

    if not usr_files:
        print(f"⚠️ No matching files found in '{usr_folder}' starting with '{prefix_filter}'.")
        return

    print(f"📂 Found {len(usr_files)} Sanskrit USR files matching prefix '{prefix_filter}'.")

    if not API_KEY or API_KEY == "YOUR_API_KEY_HERE":
        print("Error: API key not set. Please add it to the script or environment variable.")
        sys.exit(1)

    for filename in sorted(usr_files):
        input_path = os.path.join(usr_folder, filename)
        base_name = os.path.splitext(filename)[0]
        output_path = os.path.join(output_folder, f"{base_name}_gemini_english_usr.txt")

        try:
            process_file(input_path, output_path, args.language, args.model)
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}\n")

if __name__ == "__main__":
    main()