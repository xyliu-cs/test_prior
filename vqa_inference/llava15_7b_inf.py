import torch
from transformers import AutoProcessor, LlavaForConditionalGeneration
from PIL import Image
import json
import os


device = "cuda" if torch.cuda.is_available() else "cpu"
processor = AutoProcessor.from_pretrained("/120040051/llava-1.5-7b-hf")
model = LlavaForConditionalGeneration.from_pretrained("/120040051/llava-1.5-7b-hf").to(device)


with open('/120040051/test_resource/input_question/verb_questions_2_29.json', 'r') as f:
    data = json.load(f)

with open("/120040051/test_resource/output_answers/verb_answers_2_29_full.json", 'w') as f:
    json.dump({'a': 10}, f, indent=4) # test availability

verb_answers = []
for question in data:
    local_answer = question.copy()
    q_id = question['id']
    print(f"[Asking Question {q_id}] ...")

    choice_question = question['choice']
    binary_true = question["binary-yes"]
    binary_false = question["binary-no"]
    binary_compare = question["binary-cp"]

    image_1_path = f"/120040051/test_resource/images/verb_2_19/q{q_id}_1.webp"
    image_2_path = f"/120040051/test_resource/images/verb_2_19/q{q_id}_2.webp"

    if os.path.isfile(image_1_path) and os.path.isfile(image_2_path):
        image_list = [image_1_path, image_2_path]
        for img_id in range(2):
            raw_image = Image.open(image_list[img_id])
            choice_prompt = f"USER: <image>\n{choice_question}\nASSISTANT:"
            binary_y_prompt = f"USER: <image>\n{binary_true}\nASSISTANT:"
            binary_n_prompt = f"USER: <image>\n{binary_false}\nASSISTANT:"
            binary_c_prompt = f"USER: <image>\n{binary_compare}\nASSISTANT:"
            # open_prompt = f"USER: <image>\n{choice_question}\nASSISTANT:"

            for iter in range(5): # test over 5 trials over each question
                inputs = processor(choice_prompt, raw_image, return_tensors='pt').to(device)
                output_ids = model.generate(**inputs, max_new_tokens=200, do_sample=True, temperature=0.2)[0]
                output = processor.decode(output_ids, skip_special_tokens=True)
                answer = output.split('ASSISTANT: ')[1]
                local_answer[f"choice_ans_img{img_id+1}_{iter+1}"] = answer

            for iter in range(5): # test over 5 trials over each question
                inputs = processor(binary_y_prompt, raw_image, return_tensors='pt').to(device)
                output_ids = model.generate(**inputs, max_new_tokens=200, do_sample=True, temperature=0.2)[0]
                output = processor.decode(output_ids, skip_special_tokens=True)
                answer = output.split('ASSISTANT: ')[1]
                local_answer[f"binary-yes_ans_img{img_id+1}_{iter+1}"] = answer

            for iter in range(5): # test over 5 trials over each question
                inputs = processor(binary_n_prompt, raw_image, return_tensors='pt').to(device)
                output_ids = model.generate(**inputs, max_new_tokens=200, do_sample=True, temperature=0.2)[0]
                output = processor.decode(output_ids, skip_special_tokens=True)
                answer = output.split('ASSISTANT: ')[1]
                local_answer[f"binary-no_ans_img{img_id+1}_{iter+1}"] = answer

            for iter in range(5): # test over 5 trials over each question
                inputs = processor(binary_c_prompt, raw_image, return_tensors='pt').to(device)
                output_ids = model.generate(**inputs, max_new_tokens=200, do_sample=True, temperature=0.2)[0]
                output = processor.decode(output_ids, skip_special_tokens=True)
                answer = output.split('ASSISTANT: ')[1]
                local_answer[f"binary-cp_ans_img{img_id+1}_{iter+1}"] = answer
        
        verb_answers.append(local_answer)   
    
    else:
        print(f"Image path {image_1_path} or {image_2_path} does not exist!")


with open("/120040051/test_resource/output_answers/verb_answers_2_29_full.json", 'w') as f:
    json.dump(verb_answers, f, indent=4)