module.exports = {
    env: {
        browser: true,
        es2021: true,
    },
    extends: [
        'plugin:vue/vue3-essential',
        'eslint:recommended',
        "plugin:vue/vue3-recommended"
    ],
    parserOptions: {
        ecmaVersion: 12,
        sourceType: 'module',
    },
    rules: {
        'vue/multi-word-component-names': 'off', // 禁用多单词组件名的规则
        // 'vue/no-unused-vars': 'warn',
        'no-undef': 'off',  // 禁用 `no-undef` 检查，避免 ESLint 误报
        'vue/script-setup-uses-vars': 'error',  // 确保 Vue 3 的 script setup 能识别变量
    },
};
