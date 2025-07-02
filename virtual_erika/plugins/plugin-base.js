// Base class for Virtual Erika Plugins
class VirtualErikaBasePlugin {
    constructor(virtualErika, options = {}) {
        this.virtualErika = virtualErika;
        this.pluginName = this.constructor.name.toLowerCase();
        this.topic = options.topic || this.pluginName;
        this.keylogging = options.keylogging || false;
        this.active = options.active || false;
        this.info = options.info || "Base plugin - override this description";
        
        this.registerPlugin();
    }

    registerPlugin() {
        // Add plugin to virtual Erika's plugin list
        if (!this.virtualErika.plugins) {
            this.virtualErika.plugins = [];
        }
        
        if (this.active) {
            this.virtualErika.plugins.push(this);
        }
        
        console.log(`Plugin '${this.pluginName}' registered`);
    }

    setActive(active) {
        console.log(`Setting plugin '${this.pluginName}' active: ${active}`);
        this.active = active;
        
        if (active) {
            console.log(`Plugin '${this.pluginName}' is ON`);
            if (!this.virtualErika.plugins.includes(this)) {
                this.virtualErika.plugins.push(this);
                console.log(`Added plugin '${this.pluginName}' to virtualErika.plugins`);
            }
            
            // Subscribe to topic if MQTT is connected
            if (this.virtualErika.client && this.virtualErika.client.isConnected()) {
                const topic = `erika/${this.topic}/${this.virtualErika.config.DEVICE_UUID}`;
                this.virtualErika.client.subscribe(topic);
                this.virtualErika.writeToOutput(`Plugin '${this.pluginName}' subscribed to: ${topic}`, 'system');
            }
        } else {
            console.log(`Plugin '${this.pluginName}' is OFF`);
            const index = this.virtualErika.plugins.indexOf(this);
            if (index > -1) {
                this.virtualErika.plugins.splice(index, 1);
                console.log(`Removed plugin '${this.pluginName}' from virtualErika.plugins`);
            }
        }
    }

    onMessage(topic, msg) {
        if (this.active) {
            console.log(`Plugin '${this.pluginName}' received: ${topic} - ${msg}`);
        }
    }

    onKeystroke(key) {
        if (this.active && this.keylogging) {
            console.log(`Plugin '${this.pluginName}' keystroke: ${key}`);
        }
    }

    sendMessage(topic, msg) {
        console.log(`Plugin '${this.pluginName}' sendMessage called with topic: ${topic}, msg:`, msg);
        console.log(`Plugin active: ${this.active}, client:`, this.virtualErika.client);
        console.log(`Client connected: ${this.virtualErika.client && this.virtualErika.client.isConnected()}`);
        
        if (this.active && this.virtualErika.client && this.virtualErika.client.isConnected()) {
            const payload = JSON.stringify(msg);
            console.log(`Sending plugin message to topic ${topic}:`, payload);
            
            // Use Paho MQTT API: create message object and send
            const message = new Paho.MQTT.Message(payload);
            message.destinationName = topic;
            this.virtualErika.client.send(message);
            
            this.virtualErika.writeToOutput(`Plugin '${this.pluginName}' sent: ${payload} to ${topic}`, 'system');
            console.log(`Message sent successfully`);
        } else {
            console.log(`Cannot send message: plugin not active or client not connected`);
            console.log(`Active: ${this.active}, Client exists: ${!!this.virtualErika.client}, Client connected: ${this.virtualErika.client && this.virtualErika.client.isConnected()}`);
        }
    }
} 