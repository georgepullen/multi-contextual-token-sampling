from transformers import AutoModelForCausalLM, AutoTokenizer
import torch.nn.functional as F
import pickle
import torch
import re

from log_system import store_log, retrieve_logs


model = AutoModelForCausalLM.from_pretrained("apple/OpenELM-270M-Instruct", trust_remote_code=True).to("cuda")
tokenizer = AutoTokenizer.from_pretrained("TheBloke/Dolphin-Llama2-7B-GPTQ")

log_amount = 50
chunk_size = 5


async def generate(model, tokenizer, context_ids, unique_token_ids, n=50, temperature=0.1, repetition_penalty=1.1):
    input_ids = context_ids[0].clone()

    for i in range(n):
        all_next_token_logits = []

        for ctx_ids in context_ids:
            logits = model(input_ids=ctx_ids).logits
            next_token_logits = logits[:, -1, :]

            mask = torch.full_like(next_token_logits, -float('inf'))
            mask[:, unique_token_ids] = 0
            next_token_logits += mask

            all_next_token_logits.append(next_token_logits)

        next_token_probs = [F.softmax(logits / temperature, dim=-1) for logits in all_next_token_logits]

        for logits in all_next_token_logits:
            for i in range(input_ids.shape[1]):
                logits[:, input_ids[0, i]] /= repetition_penalty

        next_tokens = [torch.argmax(probs, dim=-1) for probs in next_token_probs]

        max_probs = [probs[0, token] for probs, token in zip(next_token_probs, next_tokens)]
        highest_prob_idx = torch.argmax(torch.tensor(max_probs))
        next_token = next_tokens[highest_prob_idx].unsqueeze(-1)

        input_ids = torch.cat([input_ids, next_token.to(input_ids.device)], dim=-1)

        next_token_id = next_token.squeeze(0).tolist()
        if '"' in tokenizer.decode(next_token_id):
            break

        for idx in range(len(context_ids)):
            context_ids[idx] = torch.cat([context_ids[idx], next_token.to(context_ids[idx].device)], dim=-1)

    generated_text = tokenizer.decode(input_ids[0], skip_special_tokens=True)
    return generated_text


async def create_response(prompt, username, group_users):
    user_logs = await retrieve_logs(log_amount, group_users)

    context_texts = []

    for key, logs in user_logs.items():
        while len(logs) > 0:
            if len(logs) > chunk_size:
                current_logs = logs[:chunk_size]
                logs = logs[chunk_size:]
            else:
                current_logs = logs
                logs = []

            joined_logs = '\n'.join(current_logs)

            joined_logs += prompt

            context_texts.append(joined_logs)

    context_ids = [tokenizer.encode(ctx, return_tensors="pt").to("cuda") for ctx in context_texts]

    concatenated_ids = torch.cat(context_ids, dim=1)
    unique_token_ids = list(set(concatenated_ids.squeeze(0).tolist()))

    try:
        with open("vocab.pickle", 'rb') as file:
            existing_vocab = pickle.load(file)
    except FileNotFoundError:
        print("No Vocabulary File Present - Creating New")
        existing_vocab = []

    updated_vocab = list(set(existing_vocab).union(set(unique_token_ids)))

    with open("vocab.pickle", 'wb') as file:
        pickle.dump(updated_vocab, file)

    print("Vocabulary Known:", len(updated_vocab))

    completion = await generate(model, tokenizer, context_ids, unique_token_ids)
    responses = re.findall(r'agent replied, "([^"]*)"', completion)
    if responses:
        response = responses[-1]
    else:
        response = "Error: Response wasn't in correct format."

    await store_log(prompt, response, username)
    return response