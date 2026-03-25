#!/usr/bin/env python3
"""
Sanskrit-JSON-Paragraph-NLG (Sanskrit JSON Graph Paragraph Natural Language Generation)
"""

import os
import sys
import re
import json
import argparse
import time
from collections import deque
from typing import List, Dict, Any

try:
    from google import genai
except ImportError:
    genai = None
    print("Warning: google-genai not available. Install with: pip install google-genai")

# Configuration
API_KEY = "AIzaSyCtIxpR2JW4sfXkWqEhXdveYbqB0vdlZOY" \

MODEL_NAME = "gemini-2.5-flash"
BATCH_CHAR_LIMIT = 30000
NUM_FEW_SHOT_EXAMPLES = 2

LANGUAGE_PROMPTS = {
    "english": (
        "Generate a complete, coherent English paragraph from Sanskrit JSON graph data. "
        "The JSON contains semantic information about multiple Sanskrit sentences that form a paragraph. "
        "CRITICAL RULES - WORK FROM SANSKRIT JSON SEMANTIC STRUCTURE: "
        "- Generate a single, coherent paragraph (not separate sentences) "
         "If a JSON structure is marked as TITLE ENTRY, treat it as a title"
        "- The Sanskrit JSON contains semantic tokens with Sanskrit roots, suffixes and their relations (k1, k7, r6, etc.)\n"
        "- Extract meaning from these Sanskrit semantic tokens and their relations\n"
        "- Understand Sanskrit grammatical concepts like vibhakti, dhatu, pratyaya "
        "- Maintain proper discourse flow and pronoun resolution "
        "- Use natural English expressions and transitions "
        "- STRICTLY preserve all semantic information from the Sanskrit JSON "
        "- Ensure CONTINUITY: Each sentence should flow naturally into the next "
        "- Ensure FLUIDITY: Use appropriate connectors, transitions, and cohesive devices "
        "- Maintain logical progression and avoid abrupt jumps between ideas "
        "- No JSON notation or technical terms "
        "- Create a paragraph that reads naturally and smoothly "
        "- DO NOT add any information not present in the Sanskrit JSON data "
        "- DO NOT remove any information present in the Sanskrit JSON data "
        "- DO NOT create new concepts, objects, or ideas not in the Sanskrit JSON "
        "- DO NOT add examples, analogies, or explanations not in the Sanskrit JSON "
        "- Generate ONLY what the Sanskrit JSON data explicitly contains "
        "- If Sanskrit JSON data is unclear, stick to what is clearly present "
        "- CRITICAL: ONLY use semantic tokens that are EXPLICITLY present in the Sanskrit JSON\n"
        "- DO NOT add ANY words, concepts, or ideas that are not in the Sanskrit JSON semantic tokens\n"
        "- Understand Sanskrit semantic roles and translate them appropriately to English "
        "Example: Combine multiple Sanskrit JSON graph structures into one flowing paragraph in the exact order provided with seamless transitions."
    ),
    "hindi": (
        "आप एक संस्कृत JSON से हिंदी वाक्य जनरेटर हैं। आपको संस्कृत JSON सेमेंटिक डेटा से हिंदी वाक्य बनाने हैं। "
        "संस्कृत JSON डेटा में संस्कृत वाक्यों की सेमेंटिक जानकारी है जैसे शब्द, क्रिया, विशेषण, संबंध आदि। "
        "आपको इस संस्कृत सेमेंटिक जानकारी से हिंदी वाक्य बनाने हैं। "
        "मह महत्वपूर्ण नियम - केवल संस्कृत JSON सामग्री से चिपके रहें: "
        " यदि कोई JSON स्ट्रक्चर 'TITLE ENTRY' के रूप में चिन्हित हो, तो उसे शीर्षक मानें।"
        "- संस्कृत JSON सेमेंटिक डेटा को पढ़कर हिंदी वाक्य बनाएं "
        "- संस्कृत JSON में संस्कृत धातु, प्रत्यय, विभक्ति के साथ सेमेंटिक टोकन और उनके संबंध (k1, k7, r6, आदि) हैं\n"
        "- इन संस्कृत सेमेंटिक टोकन और उनके संबंधों से अर्थ निकालें\n"
        "- संस्कृत व्याकरण की अवधारणाओं को समझें जैसे विभक्ति, धातु, प्रत्यय "
        "- शब्दों, क्रियाओं, विशेषणों को सही तरीके से जोड़ें "
        "- व्याकरण के नियमों का पालन करें "
        "- सभी वाक्यों को क्रमानुसार जोड़कर पैराग्राफ बनाएं "
        "- उचित संयोजक और प्रवाह बनाए रखें "
        "- JSON नोटेशन न दें, सिर्फ हिंदी वाक्य दें "
        "- कड़ाई से संस्कृत JSON डेटा से सटीक अर्थ बनाए रखें - कोई जोड़ या घटाव नहीं "
        "- संस्कृत JSON डेटा में नहीं है वैसी कोई जानकारी न जोड़ें "
        "- संस्कृत JSON डेटा में है वैसी कोई जानकारी न हटाएं "
        "- नए विचार, वस्तु या अवधारणाएं न बनाएं जो संस्कृत JSON में नहीं हैं "
        "- उदाहरण, सादृश्य या स्पष्टीकरण न जोड़ें जो संस्कृत JSON में नहीं हैं "
        "- केवल वही उत्पन्न करें जो संस्कृत JSON डेटा में स्पष्ट रूप से मौजूद है "
        "- यदि संस्कृत JSON डेटा अस्पष्ट है, तो स्पष्ट रूप से मौजूद चीज़ों से चिपके रहें "
        "- केवल संस्कृत JSON सामग्री - कोई कल्पना नहीं "
        "- संस्कृत सेमेंटिक भूमिकाओं को समझें और उन्हें हिंदी में उचित रूप से अनुवाद करें "
        "उदाहरण: संस्कृत JSON डेटा से 'हमारी बदलती पृथ्वी' जैसा वाक्य बनाएं।"
    )
}

request_times = deque()
MAX_REQUESTS_PER_MIN = 15

def wait_for_rate_limit():
    while len(request_times) >= MAX_REQUESTS_PER_MIN:
        time_since_oldest = time.time() - request_times[0]
        if time_since_oldest < 60:
            sleep_time = (60 - time_since_oldest) + 2
            print(f"  - Rate limit reached. Pausing for {int(sleep_time)} seconds...")
            time.sleep(sleep_time)
        request_times.popleft()

def call_gemini_api_batch(api_input_text, api_key=None, language="hindi", max_retries=3):
    if genai is None:
        raise RuntimeError("google-genai not available")

    # NEW SDK Initialization
    client = genai.Client(api_key=api_key or API_KEY)

    for attempt in range(max_retries):
        wait_for_rate_limit()
        request_times.append(time.time())

        try:
            # NEW SDK Generation Call
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=api_input_text
            )
            return response.text.strip()

        except Exception as e:
            error_str = str(e).lower()
            if "quota" in error_str or "429" in error_str:
                print(f"  - API quota exceeded (attempt {attempt + 1}/{max_retries})")
                match = re.search(r"retry in (\d+(\.\d+)?)s", error_str)
                if match:
                    delay = float(match.group(1)) + 5 
                    print(f"    → Waiting for {int(delay)} seconds before retrying...")
                    time.sleep(delay)
                else:
                    print("    → Waiting 60 seconds (default cooldown)...")
                    time.sleep(60)
                continue
            elif "rate limit" in error_str:
                print("  - Rate limit reached, waiting 60 seconds...")
                time.sleep(60)
                continue
            else:
                print(f"  - API error (attempt {attempt + 1}/{max_retries}): {e}")
                time.sleep(5)
                continue

    print("  - Failed after maximum retries.")
    return ""

def parse_json_string(json_string: str) -> List[Dict[str, Any]]:
    try:
        data = json.loads(json_string)
    except json.JSONDecodeError:
        return []

    if isinstance(data, dict):
        data = [data]
    
    items = []
    for i, structure in enumerate(data):
        if isinstance(structure, dict):
            sent_id = structure.get('usr_id', structure.get('sent_id', f'structure_{i}'))
            original_sentence = structure.get('text', structure.get('original', ''))
            
            masked_structure = structure.copy()
            if "text" in masked_structure: masked_structure["text"] = "[masked]"
            if "original" in masked_structure: masked_structure["original"] = "[masked]"
            
            if original_sentence:
                items.append({
                    'id': sent_id,
                    'original': original_sentence,
                    'api_content': json.dumps(masked_structure, ensure_ascii=False, indent=2)
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
                prompt += f"{item['api_content']}\n"
            prompt += f"Generated Paragraph: [masked]\n\n"
        prompt += "--- GENERATE ---\n\n"
    
    prompt += f"CRITICAL: Generate a complete paragraph from the following {len(items)} Sanskrit JSON structures. "
    prompt += "You MUST translate the EXACT content from each Sanskrit JSON structure in the given order. "
    prompt += "Do NOT add any information that is not present in the Sanskrit JSON structures.\n\n"
    
    for i, item in enumerate(items, 1):
        prompt += f"Structure {i} (ID: {item['id']}):\n{item['api_content']}\n\n"
    
    prompt += f"CRITICAL INSTRUCTIONS:\n"
    prompt += f"- Study the Sanskrit JSON semantic data in each structure above\n"
    prompt += f"- Extract the meaning from the Sanskrit semantic information (words, verbs, adjectives, relations)\n"
    prompt += f"- Generate proper {language} sentences from the Sanskrit semantic data\n"
    prompt += f"- Follow the EXACT order of structures (1, 2, 3, ...)\n"
    prompt += f"- Combine all {len(items)} structures into one coherent paragraph\n"
    prompt += f"- Do NOT add any information not present in the Sanskrit JSON structures\n"
    prompt += f"- Do NOT skip any structures\n"
    prompt += f"- Use appropriate connectors to make the paragraph flow naturally\n"
    prompt += f"- IMPORTANT: Replace [masked] with the actual {language} sentence you generate from Sanskrit JSON data\n"
    prompt += f"- Do NOT output [masked] or any JSON notation in your response\n"
    prompt += f"- Generate ONLY the final {language} paragraph\n"
    prompt += f"- WORK DIRECTLY FROM THE SANSKRIT JSON SEMANTIC STRUCTURE\n"
    prompt += f"- The Sanskrit JSON contains Sanskrit semantic tokens with roots, suffixes, and grammatical relations\n"
    prompt += f"- Extract meaning from these Sanskrit semantic tokens and their relations (k1, k7, r6, rblsk, etc.)\n"
    prompt += f"- If Sanskrit JSON has %interrogative, generate a question\n"
    prompt += f"- If Sanskrit JSON has %affirmative, generate a statement\n"
    prompt += f"- The semantic relations (k1, k7, r6, etc.) show how Sanskrit words connect\n"
    prompt += f"- CRITICAL: ONLY use semantic tokens that are EXPLICITLY present in the Sanskrit JSON\n"
    prompt += f"- DO NOT add ANY words, concepts, or ideas that are not in the Sanskrit JSON semantic tokens\n"
    prompt += f"- If a semantic token is not in the Sanskrit JSON, DO NOT mention it in the output\n\n"
    prompt += f"Generate the paragraph:"
    return prompt

def wrap_text(text: str, width: int = 80) -> str:
    import textwrap
    return textwrap.fill(text, width=width, break_long_words=False, break_on_hyphens=False)

def process_text(input_text: str, language: str, mode: str = "zero_shot", train_data=None) -> str:
    items = parse_json_string(input_text)
    if not items:
        return "No valid JSON items found in input to process."

    current_batch = []
    batch_char_count = 0
    paragraphs = []

    for item in items:
        item_str = json.dumps(item, ensure_ascii=False)
        if batch_char_count + len(item_str) > BATCH_CHAR_LIMIT:
            prompt = create_paragraph_prompt(language, current_batch, None)
            response_text = call_gemini_api_batch(prompt, None, language)
            paragraphs.append(response_text.strip() if response_text else "[NO RESPONSE]")
            
            time.sleep(60) 
            
            current_batch = []
            batch_char_count = 0

        current_batch.append(item)
        batch_char_count += len(item_str)

    if current_batch:
        prompt = create_paragraph_prompt(language, current_batch, None)
        response_text = call_gemini_api_batch(prompt, None, language)
        paragraphs.append(response_text.strip() if response_text else "[NO RESPONSE]")

    final_paragraph = "\n\n".join(paragraphs)
    return final_paragraph

def parse_json_file(file_path: str) -> List[Dict[str, Any]]:
    with open(file_path, 'r', encoding='utf-8') as f:
        return parse_json_string(f.read())

def process_file(input_file: str, output_file: str, language: str, mode: str = "zero_shot", train_file: str = None) -> None:
    print(f"Processing {input_file} for paragraph generation...")
    items = parse_json_file(input_file)
    if not items:
        return

    few_shot = None
    if mode == "few_shot" and train_file and os.path.exists(train_file):
        train_items = parse_json_file(train_file)
        if len(train_items) >= 3:
            import random
            num_example_items = min(random.randint(3, 5), len(train_items))
            example_items = random.sample(train_items, num_example_items)
            example_items.sort(key=lambda x: x['id'])
            few_shot = [{'items': example_items}]
            print(f"  - Using {len(example_items)} few-shot example items")
        else:
            print("  - Not enough train examples; falling back to zero-shot")

    current_batch = []
    batch_char_count = 0
    batch_id = 1
    paragraphs = []

    for item in items:
        item_str = json.dumps(item, ensure_ascii=False)
        if batch_char_count + len(item_str) > BATCH_CHAR_LIMIT:
            print(f"  - Processing batch {batch_id} with {len(current_batch)} structures...")
            prompt = create_paragraph_prompt(language, current_batch, few_shot)
            response_text = call_gemini_api_batch(prompt, None, language)
            paragraphs.append(response_text.strip() if response_text else "[NO RESPONSE]")

            print("  - Waiting 60 seconds before next batch...")
            time.sleep(60)

            current_batch = []
            batch_char_count = 0
            batch_id += 1

        current_batch.append(item)
        batch_char_count += len(item_str)

    if current_batch:
        print(f"  - Processing batch {batch_id} with {len(current_batch)} structures...")
        prompt = create_paragraph_prompt(language, current_batch, few_shot)
        response_text = call_gemini_api_batch(prompt, None, language)
        paragraphs.append(response_text.strip() if response_text else "[NO RESPONSE]")

    final_paragraph = "\n\n".join(paragraphs)

    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        wrapped_paragraph = wrap_text(final_paragraph, width=80)
        f.write(wrapped_paragraph + "\n")

    print(f"  - Combined {len(paragraphs)} batches into final paragraph in {output_file}")


def main():
    import glob
    parser = argparse.ArgumentParser(description="Sanskrit-JSON-Paragraph-NLG Inference Script")
    parser.add_argument("json_folder", help="Folder containing input Sanskrit JSON files (e.g., ./json)")
    parser.add_argument("-o", "--output_folder", default="output",
                       help="Folder where output paragraphs will be saved (default: ./output)")
    parser.add_argument("-l", "--language", default="english",
                       choices=["english", "hindi"],
                       help="Target language (default: english)")
    parser.add_argument("-m", "--mode", default="zero_shot",
                       choices=["zero_shot", "few_shot"],
                       help="Inference mode (default: zero_shot)")

    args = parser.parse_args()
    json_folder = args.json_folder
    output_folder = args.output_folder

    if not os.path.exists(json_folder):
        print(f"❌ Folder not found: {json_folder}")
        return

    os.makedirs(output_folder, exist_ok=True)

    print(f"\n📂 Checking folder: {json_folder}")
    all_files = os.listdir(json_folder)
    print(f"Found {len(all_files)} total files:")
    for f in all_files:
        print("  -", f)

    json_files = [f for f in all_files if f.startswith("test") and f.endswith(".json")]
    print(f"\n🎯 Matched {len(json_files)} files starting with 'test':")
    for f in json_files:
        print("  ✅", f)

    if not json_files:
        print("⚠️ No matching files found! (check filename prefix or folder path)")
        return

    for filename in sorted(json_files):
        input_path = os.path.join(json_folder, filename)
        base_name = os.path.splitext(filename)[0]
        output_path = os.path.join(output_folder, f"{base_name}_gemini_english_json.txt")

        print(f"\n🔹 Processing: {filename}")
        print(f"   → Input: {input_path}")
        print(f"   → Output: {output_path}")

        try:
            process_file(input_path, output_path, args.language, args.mode)
            if os.path.exists(output_path):
                print(f"✅ File created: {output_path}")
            else:
                print(f"⚠️ No output generated for {filename}")
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")

    print("\n✅ Done. Check your output folder.")

if __name__ == "__main__":
    main()