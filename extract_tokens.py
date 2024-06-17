from datetime import datetime
from myfunc.prompts import ConversationDatabase
 
current_date = datetime.now()
start_date = current_date.replace(day=1)
end_date = current_date
 
start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
 
with ConversationDatabase() as db:
    all_tokens = db.extract_token_sums_between_dates("2024-01-01", end_date_str)
    embedding_cost = all_tokens["total_embedding_tokens"] / 10**6 * 0.13
    prompt_cost = all_tokens["total_prompt_tokens"] / 10**6 * 5.0
    completion_cost = all_tokens["total_completion_tokens"] / 10**6 * 15.0
    stt_cost = all_tokens["total_stt_tokens"] / 10**6 / 60 * 0.006
    tts_cost = all_tokens["total_tts_tokens"] / 10**6 * 15.0
    
    print(f"""Cost in USD:
            embedding: {embedding_cost}
            prompt: {prompt_cost}
            completion: {completion_cost}
            stt: {stt_cost}
            tts: {tts_cost}
            total: {embedding_cost + prompt_cost + completion_cost + stt_cost + tts_cost}
            """)
    
# Pa Vi sad razmisljajte o npr. decimalama

