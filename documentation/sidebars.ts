import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  bookSidebar: [
    'intro',
    // ========== 第一层：数学与机器学习基础 ==========
    {
      type: 'category',
      label: '第一层：数学与机器学习基础',
      items: [
        'math_foundations/ai-math-essentials',
        'chapters/vector_concepts/dot_product_angle',
        'math_foundations/softmax',
        'math_foundations/activation-functions',
        'math_foundations/perceptron-learning',
        'math_foundations/cross-entropy',
        'math_foundations/backpropagation',
        'math_foundations/vanishing-exploding-gradients',
        'math_foundations/layer-norm',
        'embeddings/from-onehot-to-embedding',
      ],
    },
    // ========== 第二层：LLM 内部机制 ==========
    {
      type: 'category',
      label: '第二层：LLM 内部机制',
      items: [
        'embeddings/embedding-evolution',
        'advanced_transformer/transformer_architecture',
        'advanced_transformer/attention_mechanism',
        'advanced_transformer/llm_generation',
        'advanced_transformer/fine-tuning-and-distillation',
        'advanced_transformer/optimizer-selection',
        'advanced_transformer/ai_engineering_practices',
      ],
    },
    // ========== 第三层：LLM 与外部系统的连接 ==========
    {
      type: 'category',
      label: '第三层：LLM 与外部系统的连接',
      items: [
        'chapters/chapter4',
        {
          type: 'link',
          label: '外部工具调用（待补充）',
          href: '#',
        },
      ],
    },
  ],
};

export default sidebars;
