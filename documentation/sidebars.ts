import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  // Electronic book sidebar
  bookSidebar: [
    'intro',
    {
      type: 'category',
      label: '基础概念',
      items: ['chapters/chapter1', 'chapters/chapter2'],
    },
    {
      type: 'category',
      label: '实践应用',
      items: ['chapters/chapter3', 'chapters/chapter4', {
        type: 'category',
        label: '向量与嵌入基础',
        items: ['chapters/vector_concepts/dot_product_angle'],
      }],
    },
    {
      type: 'category',
      label: '高级主题',
      items: ['chapters/chapter5', 'chapters/chapter6'],
    },
    {
      type: 'category',
      label: 'Transformer深度解析',
      items: [
        'advanced_transformer/transformer_architecture',
        'advanced_transformer/attention_mechanism',
        'advanced_transformer/llm_generation',
        'advanced_transformer/ai_engineering_practices'
      ],
    }
  ],
};

export default sidebars;
