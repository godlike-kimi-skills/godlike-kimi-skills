"""
OpenAI API Skill - 使用示例
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import OpenAISkill


def example_1_basic_chat():
    """示例1: 基本对话"""
    print("=" * 60)
    print("示例1: 基本对话")
    print("=" * 60)
    
    try:
        skill = OpenAISkill()
        
        messages = [
            {"role": "system", "content": "你是一个 helpful assistant."},
            {"role": "user", "content": "你好！请用一句话介绍自己。"}
        ]
        
        response = skill.chat(messages, max_tokens=100)
        
        print(f"助手回复: {response['content']}")
        print(f"使用模型: {response['model']}")
        print(f"Token使用: {response['usage']}")
        
    except Exception as e:
        print(f"示例执行失败: {e}")


def example_2_simple_chat():
    """示例2: 简单对话"""
    print("\n" + "=" * 60)
    print("示例2: 简单对话")
    print("=" * 60)
    
    try:
        skill = OpenAISkill()
        
        response = skill.simple_chat(
            message="Python有什么优点？",
            system_prompt="你是一个Python专家，简洁明了地回答问题。",
            max_tokens=150
        )
        
        print(f"回复: {response}")
        
    except Exception as e:
        print(f"示例执行失败: {e}")


def example_3_conversation():
    """示例3: 多轮对话"""
    print("\n" + "=" * 60)
    print("示例3: 多轮对话")
    print("=" * 60)
    
    try:
        skill = OpenAISkill()
        
        # 对话历史
        messages = [
            {"role": "system", "content": "你是一个知识渊博的助手。"},
        ]
        
        # 第一轮
        messages.append({"role": "user", "content": "什么是机器学习？"})
        response1 = skill.chat(messages, max_tokens=100)
        print(f"用户: 什么是机器学习？")
        print(f"助手: {response1['content']}\n")
        
        # 第二轮（包含上下文）
        messages.append({"role": "assistant", "content": response1['content']})
        messages.append({"role": "user", "content": "它和深度学习有什么关系？"})
        response2 = skill.chat(messages, max_tokens=100)
        print(f"用户: 它和深度学习有什么关系？")
        print(f"助手: {response2['content']}")
        
    except Exception as e:
        print(f"示例执行失败: {e}")


def example_4_text_completion():
    """示例4: 文本补全"""
    print("\n" + "=" * 60)
    print("示例4: 文本补全")
    print("=" * 60)
    
    try:
        skill = OpenAISkill()
        
        prompt = """以下是三个机器学习的优点：
1. 自动化处理大量数据
2. 
"""
        
        response = skill.complete(prompt, max_tokens=100)
        
        print(f"提示: {prompt}")
        print(f"补全结果: {response['text']}")
        print(f"Token使用: {response['usage']}")
        
    except Exception as e:
        print(f"示例执行失败: {e}")


def example_5_embedding():
    """示例5: 文本嵌入"""
    print("\n" + "=" * 60)
    print("示例5: 文本嵌入")
    print("=" * 60)
    
    try:
        skill = OpenAISkill()
        
        # 单文本嵌入
        text = "人工智能正在改变世界"
        result = skill.create_embedding(text)
        
        print(f"文本: {text}")
        print(f"嵌入维度: {len(result['embeddings'])}")
        print(f"前5个值: {result['embeddings'][:5]}")
        print(f"Token使用: {result['usage']}")
        
        # 批量嵌入
        print("\n批量嵌入示例:")
        texts = ["机器学习", "深度学习", "自然语言处理"]
        result_batch = skill.create_embedding(texts)
        
        print(f"文本数量: {len(texts)}")
        print(f"嵌入维度: {len(result_batch['embeddings'][0])}")
        
    except Exception as e:
        print(f"示例执行失败: {e}")


def example_6_semantic_search():
    """示例6: 语义搜索"""
    print("\n" + "=" * 60)
    print("示例6: 语义搜索")
    print("=" * 60)
    
    try:
        skill = OpenAISkill()
        
        # 文档库
        documents = [
            "Python是一种高级编程语言",
            "JavaScript用于网页开发",
            "机器学习是人工智能的一个分支",
            "深度学习使用神经网络",
            "HTML是网页的标记语言"
        ]
        
        # 生成文档嵌入
        doc_embeddings = skill.create_embedding(documents)
        
        # 查询
        query = "什么是神经网络？"
        query_embedding = skill.create_embedding(query)
        
        # 计算相似度
        import numpy as np
        
        query_vec = np.array(query_embedding['embeddings'])
        similarities = []
        
        for doc_emb in doc_embeddings['embeddings']:
            doc_vec = np.array(doc_emb)
            # 余弦相似度
            similarity = np.dot(query_vec, doc_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(doc_vec))
            similarities.append(similarity)
        
        # 排序结果
        ranked = sorted(zip(documents, similarities), key=lambda x: x[1], reverse=True)
        
        print(f"查询: {query}\n")
        print("相关文档:")
        for i, (doc, score) in enumerate(ranked[:3], 1):
            print(f"{i}. [{score:.4f}] {doc}")
        
    except Exception as e:
        print(f"示例执行失败: {e}")


def example_7_image_generation():
    """示例7: 图像生成"""
    print("\n" + "=" * 60)
    print("示例7: 图像生成")
    print("=" * 60)
    
    try:
        skill = OpenAISkill()
        
        prompt = "A cute cat wearing a space suit, digital art"
        
        print(f"生成图像: {prompt}")
        print("(这需要真实的API密钥)")
        
        # 注意：这需要真实的API密钥
        # result = skill.generate_image(prompt, size="1024x1024")
        # print(f"图像URL: {result['images']['url']}")
        
        print("示例完成（未实际调用API）")
        
    except Exception as e:
        print(f"示例执行失败: {e}")


def example_8_audio_transcription():
    """示例8: 语音转文字"""
    print("\n" + "=" * 60)
    print("示例8: 语音转文字 (Whisper)")
    print("=" * 60)
    
    try:
        skill = OpenAISkill()
        
        print("语音转文字功能需要音频文件")
        print("支持的格式: mp3, mp4, mpeg, mpga, m4a, wav, webm")
        
        # 注意：这需要真实的API密钥和音频文件
        # result = skill.transcribe_audio("audio.mp3", language="zh")
        # print(f"转录结果: {result['text']}")
        
        print("示例完成（未实际调用API）")
        
    except Exception as e:
        print(f"示例执行失败: {e}")


def example_9_text_to_speech():
    """示例9: 文本转语音"""
    print("\n" + "=" * 60)
    print("示例9: 文本转语音 (TTS)")
    print("=" * 60)
    
    try:
        skill = OpenAISkill()
        
        text = "你好，这是人工智能的语音。"
        
        print(f"生成语音: {text}")
        
        # 注意：这需要真实的API密钥
        # audio_data = skill.create_speech(text, voice="alloy")
        # with open("output.mp3", "wb") as f:
        #     f.write(audio_data)
        
        voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        print(f"可用声音: {', '.join(voices)}")
        print("示例完成（未实际调用API）")
        
    except Exception as e:
        print(f"示例执行失败: {e}")


def example_10_token_counting():
    """示例10: Token计数和成本估算"""
    print("\n" + "=" * 60)
    print("示例10: Token计数和成本估算")
    print("=" * 60)
    
    try:
        skill = OpenAISkill()
        
        # 测试文本
        texts = [
            "Hello",
            "Hello world",
            "This is a longer text with more words to count tokens.",
            "这是一个中文文本，用于测试token计数功能。"
        ]
        
        print("Token计数结果:")
        for text in texts:
            tokens = skill.count_tokens(text)
            print(f"  '{text[:30]}...' -> {tokens} tokens")
        
        # 成本估算
        print("\n成本估算 (gpt-3.5-turbo):")
        scenarios = [
            (1000, 500, "小型请求"),
            (10000, 5000, "中型请求"),
            (100000, 50000, "大型请求")
        ]
        
        for prompt_tokens, completion_tokens, desc in scenarios:
            cost = skill.estimate_cost(prompt_tokens, completion_tokens, "gpt-3.5-turbo")
            print(f"  {desc}: {prompt_tokens} prompt + {completion_tokens} completion = ${cost:.6f}")
        
    except Exception as e:
        print(f"示例执行失败: {e}")


def example_11_different_models():
    """示例11: 不同模型对比"""
    print("\n" + "=" * 60)
    print("示例11: 不同模型对比")
    print("=" * 60)
    
    try:
        skill = OpenAISkill()
        
        prompt = "解释什么是递归"
        
        models = [
            ("gpt-3.5-turbo", "GPT-3.5"),
            ("gpt-4", "GPT-4"),
        ]
        
        print(f"提示: {prompt}\n")
        
        for model_id, model_name in models:
            print(f"{model_name}:")
            
            # 计算成本
            prompt_tokens = skill.count_tokens(prompt)
            # 估算回复约150 tokens
            cost = skill.estimate_cost(prompt_tokens, 150, model_id)
            
            print(f"  估算成本: ${cost:.6f}")
            print()
        
        print("注意: 实际调用需要有效的API密钥和相应权限")
        
    except Exception as e:
        print(f"示例执行失败: {e}")


def example_12_batch_processing():
    """示例12: 批量处理"""
    print("\n" + "=" * 60)
    print("示例12: 批量处理")
    print("=" * 60)
    
    try:
        skill = OpenAISkill()
        
        # 批量文本
        texts = [
            "解释什么是Python",
            "解释什么是JavaScript",
            "解释什么是Go语言",
            "解释什么是Rust"
        ]
        
        print("批量处理示例:")
        for text in texts:
            tokens = skill.count_tokens(text)
            print(f"  '{text}' -> {tokens} tokens")
        
        # 批量嵌入更经济
        print("\n批量嵌入可以更高效地利用API")
        
    except Exception as e:
        print(f"示例执行失败: {e}")


def main():
    """运行所有示例"""
    examples = [
        example_1_basic_chat,
        example_2_simple_chat,
        example_3_conversation,
        example_4_text_completion,
        example_5_embedding,
        example_6_semantic_search,
        example_7_image_generation,
        example_8_audio_transcription,
        example_9_text_to_speech,
        example_10_token_counting,
        example_11_different_models,
        example_12_batch_processing,
    ]
    
    print("\n" + "=" * 60)
    print("OpenAI API Skill 示例")
    print("=" * 60)
    print("\n注意: 大多数示例需要有效的 OPENAI_API_KEY 环境变量")
    print("=" * 60 + "\n")
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\n[!] {example.__name__} 执行失败: {e}")
    
    print("\n" + "=" * 60)
    print("所有示例执行完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
