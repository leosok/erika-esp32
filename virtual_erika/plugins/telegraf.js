// Telegraf Plugin for Virtual Erika
// Mirrors the Python telegraf.py plugin functionality

class Telegraf extends VirtualErikaBasePlugin {
    constructor(virtualErika) {
        super(virtualErika, {
            topic: 'telegraf',
            keylogging: true,
            active: false, // Start inactive
            info: "Ein Telegraf, der an alle Erikas sendet, die gerade an sind. ON/OFF"
        });
    }

    onMessage(topic, msg) {
        if (this.active) {
            this.virtualErika.writeToOutput(`Telegraf received: ${msg}`, 'system');
            this.virtualErika.writeToIO(`Telegraf: ${msg}`, 'output');
        }
    }

    onKeystroke(key) {
        console.log(`Telegraf plugin onKeystroke called with key: ${key}, active: ${this.active}, keylogging: ${this.keylogging}`);
        
        if (this.active && this.keylogging) {
            // Send keystroke to all Erikas via print_all channel (like real Telegraf)
            const data = {
                sender: this.virtualErika.config.DEVICE_UUID,
                text: key
            };
            
            this.sendMessage(this.virtualErika.config.TOPICS.PRINT_ALL, data);
            this.virtualErika.writeToOutput(`Telegraf broadcast: ${key}`, 'system');
        } else {
            console.log(`Telegraf plugin not active or not keylogging`);
        }
    }
} 