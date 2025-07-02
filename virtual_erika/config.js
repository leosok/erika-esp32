// Virtual Erika Configuration
// This file loads sensitive config from config.local.js if available

// Default configuration (fallback)
const defaultConfig = {
    // MQTT Broker Settings
    MQTT_SERVER: "wss://test.mosquitto.org:8081/mqtt", // Default public broker
    MQTT_USERNAME: "", // Add if needed
    MQTT_PASSWORD: "", // Add if needed
    
    // Device Settings
    DEVICE_UUID: "virtual_erika_" + Math.random().toString(16).substr(2, 8),
};

// Load local config if available, otherwise use defaults
const config = typeof localConfig !== 'undefined' ? localConfig : defaultConfig;

// Topic Structure (matches real Erika)
config.TOPICS = {
    KEYSTROKES: "erika/keystrokes/",
    STATUS: "erika/status/",
    PRINT: "erika/print/",
    PRINT_ALL: "erika/print/all"
};

// Status Values (matches real Erika)
config.STATUS = {
    OFFLINE: "0",
    READY: "1", 
    PRINTING: "2"
};

// Generate full topic names
config.TOPICS.KEYSTROKES += config.DEVICE_UUID;
config.TOPICS.STATUS += config.DEVICE_UUID;
config.TOPICS.PRINT += config.DEVICE_UUID;
// PRINT_ALL stays as is - it's a global topic 