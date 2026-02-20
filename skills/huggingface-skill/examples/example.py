"""
Hugging Face Skill - 使用示例
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import HuggingFaceSkill


def example_1_basic_usage():
    """示例1: 基本使用"""
    print("=" * 50)
    print("示例1: 基本使用")
    print("=" * 50)
    
    skill = HuggingFaceSkill()
    print(f"使用设备: {skill.device}")
    print(f"缓存目录: {skill.cache_dir}")
    
    # 情感分析
    print("\n1. 情感分析:")
    texts = [
        "这部电影真的太棒了！",
        "这个产品让我非常失望。"
    ]
    
    for text in texts:
        result = skill.pipeline_infer("sentiment-analysis", text)
        print(f"  文本: {text}")
        print(f"  结果: {result}")


def example_2_named_entity_recognition():
    """示例2: 命名实体识别"""
    print("\n" + "=" * 50)
    print("示例2: 命名实体识别 (NER)")
    print("=" * 50)
    
    skill = HuggingFaceSkill()
    
    text = "阿里巴巴的总部在杭州，创始人是马云。"
    result = skill.pipeline_infer("ner", text, model="ckiplab/bert-base-chinese-ner")
    print(f"文本: {text}")
    print(f"NER结果:")
    for entity in result:
        print(f"  - {entity['word']}: {entity['entity']} (置信度: {entity['score']:.4f})")


def example_3_question_answering():
    """示例3: 问答系统"""
    print("\n" + "=" * 50)
    print("示例3: 问答系统")
    print("=" * 50)
    
    skill = HuggingFaceSkill()
    
    context = """
    Python是一种高级编程语言，由Guido van Rossum于1991年创建。
    它以简洁易读的语法著称，支持多种编程范式。
    Python广泛应用于Web开发、数据科学、人工智能等领域。
    """
    
    question = "Python是谁创建的？"
    
    result = skill.pipeline_infer(
        "question-answering",
        {"context": context, "question": question}
    )
    
    print(f"问题: {question}")
    print(f"答案: {result['answer']}")
    print(f"置信度: {result['score']:.4f}")


def example_4_text_generation():
    """示例4: 文本生成"""
    print("\n" + "=" * 50)
    print("示例4: 文本生成")
    print("=" * 50)
    
    skill = HuggingFaceSkill()
    
    prompt = "人工智能的未来发展将会"
    
    result = skill.pipeline_infer(
        "text-generation",
        prompt,
        max_length=50,
        do_sample=True,
        temperature=0.7
    )
    
    print(f"提示: {prompt}")
    print(f"生成结果: {result[0]['generated_text']}")


def example_5_dataset_loading():
    """示例5: 数据集加载"""
    print("\n" + "=" * 50)
    print("示例5: 数据集加载")
    print("=" * 50)
    
    skill = HuggingFaceSkill()
    
    # 加载IMDB情感分析数据集
    try:
        dataset = skill.load_dataset("imdb", split="train[:100]")
        print(f"数据集大小: {len(dataset)} 条")
        print(f"第一条数据:")
        print(f"  文本: {dataset[0]['text'][:100]}...")
        print(f"  标签: {'正面' if dataset[0]['label'] == 1 else '负面'}")
    except Exception as e:
        print(f"加载数据集失败（可能需要认证）: {e}")


def example_6_tokenizer_encoding():
    """示例6: Tokenizer编码"""
    print("\n" + "=" * 50)
    print("示例6: Tokenizer编码与解码")
    print("=" * 50)
    
    skill = HuggingFaceSkill()
    
    text = "Hello, 世界!"
    tokenizer_name = "bert-base-chinese"
    
    # 编码
    encoded = skill.encode_text(tokenizer_name, text)
    print(f"原始文本: {text}")
    print(f"编码结果:")
    print(f"  Input IDs: {encoded['input_ids']}")
    print(f"  Attention Mask: {encoded['attention_mask']}")
    
    # 解码
    decoded = skill.decode_tokens(tokenizer_name, encoded['input_ids'])
    print(f"解码结果: {decoded}")


def example_7_model_search():
    """示例7: 模型搜索"""
    print("\n" + "=" * 50)
    print("示例7: 模型搜索")
    print("=" * 50)
    
    skill = HuggingFaceSkill()
    
    models = skill.search_models("chinese bert", limit=5)
    print(f"找到 {len(models)} 个模型:")
    for model in models:
        print(f"  - {model['modelId']}")
        print(f"    下载量: {model.get('downloads', 'N/A')}")
        print(f"    点赞数: {model.get('likes', 'N/A')}")


def example_8_fill_mask():
    """示例8: 掩码填充"""
    print("\n" + "=" * 50)
    print("示例8: 掩码填充")
    print("=" * 50)
    
    skill = HuggingFaceSkill()
    
    # 使用[MASK]标记需要预测的位置
    text = "北京是中国的[MASK]城市。"
    
    result = skill.pipeline_infer("fill-mask", text)
    print(f"输入: {text}")
    print("预测结果:")
    for pred in result[:3]:
        print(f"  - {pred['token_str']}: {pred['score']:.4f}")


def example_9_translation():
    """示例9: 机器翻译"""
    print("\n" + "=" * 50)
    print("示例9: 机器翻译")
    print("=" * 50)
    
    skill = HuggingFaceSkill()
    
    text = "Hello, how are you today?"
    
    result = skill.pipeline_infer(
        "translation_en_to_zh",
        text
    )
    
    print(f"英文: {text}")
    print(f"中文: {result[0]['translation_text']}")


def example_10_summarization():
    """示例10: 文本摘要"""
    print("\n" + "=" * 50)
    print("示例10: 文本摘要")
    print("=" * 50)
    
    skill = HuggingFaceSkill()
    
    long_text = """
    人工智能（Artificial Intelligence，简称AI）是计算机科学的一个分支，
    它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。
    人工智能领域的研究包括机器人、语言识别、图像识别、自然语言处理和专家系统等。
    人工智能从诞生以来，理论和技术日益成熟，应用领域也不断扩大。
    """
    
    result = skill.pipeline_infer(
        "summarization",
        long_text,
        max_length=50,
        min_length=10
    )
    
    print("原文:")
    print(long_text[:100] + "...")
    print("\n摘要:")
    print(result[0]['summary_text'])


def main():
    """运行所有示例"""
    examples = [
        example_1_basic_usage,
        example_2_named_entity_recognition,
        example_3_question_answering,
        example_4_text_generation,
        example_5_dataset_loading,
        example_6_tokenizer_encoding,
        example_7_model_search,
        example_8_fill_mask,
        example_9_translation,
        example_10_summarization,
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\n[!] {example.__name__} 执行失败: {e}")
    
    print("\n" + "=" * 50)
    print("所有示例执行完成!")
    print("=" * 50)


if __name__ == "__main__":
    main()
