# 《LLMs for Backend Engineers》电子书完整目录规划

这是为《LLMs for Backend Engineers》创建的Docusaurus电子书框架。

## 最终目录结构

本书从AI基础知识入手，为后端工程师提供一个系统性的大语言模型学习路径，从理论基础到实际应用，再到工程实践。

### Part I: AI 基础知识 (为理解LLMs做准备)
- `docs/intro.md` - 电子书简介及学习路径
- `docs/chapters/part1/` - AI基础知识章节
  - `chapter1_introduction_to_ai_ml_dl.md` - AI/ML/DL基础概念：理解从人工智能到大模型的层次关系
  - `chapter2_neural_networks_basics.md` - 神经网络基础：从感知机到深度学习
  - `chapter3_ml_fundamentals.md` - 机器学习核心概念：训练、推理和评估流程
  - `chapter4_math_for_llms.md` - LLM数学基础：向量、点积与嵌入概念
    - `vector_concepts/dot_product_angle.md` - 向量点积与夹角关系详解

### Part II: Transformer 架构深度解析
- `docs/chapters/part2/` - Transformer深度学习章节
  - `chapter5_transformer_architecture.md` - Transformer架构详解：注意力机制与QKV
  - `chapter6_neural_network_training.md` - 神经网络训练：5步核心流程、反向传播、梯度下降
  - `chapter7_model_variants_selection.md` - 模型变体与选择：CNN、RNN与Transformer对比，预训练模型与微调方法

### Part III: LLM 工程实践 (针对后端工程师)
- `docs/chapters/part3/` - LLM工程实践章节
  - `chapter8_llm_fundamentals.md` - LLM基础与生态：模型类型、Hugging Face、模型选择
  - `chapter9_prompt_engineering.md` - 提示工程：不同场景下的提示技巧
  - `chapter10_data_processing_rag.md` - 数据处理与RAG：嵌入、向量数据库、知识库管理
  - `chapter11_backend_integration.md` - 后端集成：API设计、缓存、异步处理、安全性
  - `chapter12_performance_monitoring.md` - 性能与监控：优化、监控指标、A/B测试
  - `chapter13_advanced_applications.md` - 高级应用：后端系统的专业用例
  - `chapter14_future_trends.md` - 未来趋势：新兴技术与发展方向

- `docs/advanced_transformer/` - Transformer高级专题
  - `transformer_architecture.md` - 从分布式系统视角理解Transformer架构
  - `attention_mechanism.md` - Attention机制工程解析
  - `llm_generation.md` - LLM生成机制去神秘化分析
  - `ai_engineering_practices.md` - AI系统工程实践指南

## 开发命令

```bash
cd documentation
npm start # 在开发模式下启动网站
npm run build # 构建静态文件
npm run serve # 本地预览构建的文件
```

## 学习路径建议

对于后端工程师，建议按以下顺序学习：
1. Part I: 建立AI基础知识（特别是数学基础章节）
2. Part II: 深入理解Transformer架构（这是LLM的基础）
3. Part III: 实践应用（侧重后端集成和工程实践）

电子书已经在 `http://localhost:3000` 可访问。