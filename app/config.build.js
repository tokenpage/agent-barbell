import { MetaTag } from '@kibalabs/build/scripts/react-app-vite/injectSeoPlugin.js';

const title = 'Agent Barbell';
const description = 'A risk-budget barbell agent for Robinhood Chain.';

const seoTags = [
  new MetaTag('description', description),
];

export default (config) => {
  const newConfig = config;
  newConfig.seoTags = seoTags;
  newConfig.title = title;
  newConfig.analyzeBundle = false;
  newConfig.viteConfigModifier = (viteConfig) => {
    const newViteConfig = viteConfig;
    newViteConfig.server.host = '0.0.0.0';
    newViteConfig.server.port = 3100;
    newViteConfig.server.allowedHosts = true;
    newViteConfig.resolve = newViteConfig.resolve || {};
    newViteConfig.resolve.dedupe = ['react', 'react-dom'];
    return newViteConfig;
  };
  return newConfig;
};
