import os
from transformers import AutoTokenizer, AutoConfig

base_dir = r"D:\AGenticVul\3s_back\user_sys\DetectionModels\BaseModel"
models_to_download = {
    "GraphCodeBERT-base": "microsoft/graphcodebert-base",
    "CodeBERT-base": "microsoft/codebert-base",
    "CodeT5-base": "Salesforce/codet5-base"
}

os.makedirs(base_dir, exist_ok=True)

for local_name, hf_id in models_to_download.items():
    save_path = os.path.join(base_dir, local_name)
    print(f"Downloading {hf_id} to {save_path} ...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(hf_id)
        config = AutoConfig.from_pretrained(hf_id)
        
        tokenizer.save_pretrained(save_path)
        config.save_pretrained(save_path)
        print(f"Successfully downloaded {hf_id}")
    except Exception as e:
        print(f"Error downloading {hf_id}: {e}")

