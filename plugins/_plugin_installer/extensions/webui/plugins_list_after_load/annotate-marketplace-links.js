import { store as pluginInstallStore } from "../../../webui/pluginInstallStore.js";

function getPluginName(plugin) {
  return typeof plugin?.name === "string" ? plugin.name.trim() : "";
}

function getMarketplaceMatch(plugin, marketplacePlugins) {
  const pluginName = getPluginName(plugin);
  if (!pluginName || !marketplacePlugins?.[pluginName]) {
    return null;
  }

  return {
    key: pluginName,
    title: marketplacePlugins[pluginName]?.title || pluginName,
  };
}

export default async function annotateMarketplaceLinks(context) {
  const plugins = Array.isArray(context?.plugins) ? context.plugins : null;
  const store = context?.store;
  if (!plugins?.length) return;

  const loaded = await pluginInstallStore.ensureIndexLoaded({ background: true });
  if (!loaded) return;

  const marketplacePlugins = pluginInstallStore.index?.plugins;
  if (!marketplacePlugins || typeof marketplacePlugins !== "object") return;

  let changed = false;
  for (const plugin of plugins) {
    if (!plugin || typeof plugin !== "object") continue;

    const nextMarketplace = getMarketplaceMatch(plugin, marketplacePlugins);
    const currentKey = plugin?.marketplace?.key || "";
    const nextKey = nextMarketplace?.key || "";
    if (currentKey === nextKey) continue;

    plugin.marketplace = nextMarketplace;
    changed = true;
  }

  if (changed && store?.plugins === plugins) {
    store.plugins = [...plugins];
  }
}
