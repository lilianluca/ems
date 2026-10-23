import { definePlugin, defineRule } from 'vite-plus/lint/plugins';

const LOCAL_DATE_GETTERS = new Set([
  'getHours',
  'getMinutes',
  'getDate',
  'getMonth',
  'getDay',
  'getFullYear',
]);

// Timezone safety: local Date getters silently use the machine timezone
const noLocalDateGetters = defineRule({
  meta: {
    messages: {
      localGetter:
        'Local Date getters ignore the timezone. Use TZDate or Intl.DateTimeFormat with Europe/Prague.',
    },
  },
  create(context) {
    return {
      CallExpression(node) {
        const { callee } = node;
        if (
          callee.type === 'MemberExpression' &&
          callee.property.type === 'Identifier' &&
          LOCAL_DATE_GETTERS.has(callee.property.name)
        ) {
          context.report({ node, messageId: 'localGetter' });
        }
      },
    };
  },
});

export default definePlugin({
  meta: { name: 'ems' },
  rules: { 'no-local-date-getters': noLocalDateGetters },
});
