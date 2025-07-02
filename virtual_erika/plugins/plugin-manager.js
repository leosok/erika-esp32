// Plugin Manager for Virtual Erika
class PluginManager {
    constructor(virtualErika) {
        this.virtualErika = virtualErika;
        this.plugins = [];
        this.pluginRegistry = {};
    }

    // Register a plugin class
    registerPlugin(pluginClass) {
        const pluginName = pluginClass.name.toLowerCase();
        this.pluginRegistry[pluginName] = pluginClass;
        console.log(`Plugin class '${pluginName}' registered`);
    }

    // Create and activate a plugin
    createPlugin(pluginName, options = {}) {
        console.log(`Creating plugin: ${pluginName}`);
        console.log('Available plugins in registry:', Object.keys(this.pluginRegistry));
        
        const PluginClass = this.pluginRegistry[pluginName];
        if (!PluginClass) {
            console.error(`Plugin '${pluginName}' not found in registry`);
            return null;
        }

        const plugin = new PluginClass(this.virtualErika, options);
        this.plugins.push(plugin);
        
        console.log(`Plugin '${pluginName}' created, total plugins:`, this.plugins.length);
        console.log('Plugin details:', {
            name: plugin.pluginName,
            active: plugin.active,
            keylogging: plugin.keylogging,
            topic: plugin.topic
        });
        console.log('VirtualErika client available:', !!this.virtualErika.client);
        return plugin;
    }

    // Get all available plugins
    getAvailablePlugins() {
        return Object.keys(this.pluginRegistry);
    }

    // Get all active plugins
    getActivePlugins() {
        return this.plugins.filter(plugin => plugin.active);
    }

    // Handle incoming messages for all plugins
    handleMessage(topic, msg) {
        this.plugins.forEach(plugin => {
            if (plugin.active) {
                plugin.onMessage(topic, msg);
            }
        });
    }

    // Handle keystrokes for all plugins
    handleKeystroke(key) {
        console.log(`PluginManager handleKeystroke called with key: ${key}, active plugins:`, this.plugins.filter(p => p.active).map(p => p.pluginName));
        
        this.plugins.forEach(plugin => {
            if (plugin.active && plugin.keylogging) {
                console.log(`Calling onKeystroke for plugin: ${plugin.pluginName}`);
                plugin.onKeystroke(key);
            } else {
                console.log(`Plugin ${plugin.pluginName} not active or not keylogging`);
            }
        });
    }

    // Update client reference for all plugins
    updateClient(client) {
        this.virtualErika.client = client;
        console.log('PluginManager: Updated client reference');
        
        // Update client reference for all plugins
        this.plugins.forEach(plugin => {
            plugin.virtualErika.client = client;
            console.log(`Plugin '${plugin.pluginName}': Updated client reference`);
        });
    }

    // Subscribe all active plugins to their topics
    subscribeActivePlugins() {
        this.plugins.forEach(plugin => {
            if (plugin.active && this.virtualErika.client && this.virtualErika.client.isConnected()) {
                const topic = `erika/${plugin.topic}/${this.virtualErika.config.DEVICE_UUID}`;
                this.virtualErika.client.subscribe(topic);
                this.virtualErika.writeToOutput(`Plugin '${plugin.pluginName}' subscribed to: ${topic}`, 'system');
            }
        });
    }
} 