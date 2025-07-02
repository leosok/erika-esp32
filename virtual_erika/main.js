// Virtual Erika Terminal Interface
let client = null;
let isConnected = false;
let manualDisconnect = false;
let pluginManager = null;
let commandMode = false;
let tabCount = 0;
let lastTabTime = 0;
let keystrokeAudio = null;

// DOM elements
const statusEl = document.getElementById('status');
const outputEl = document.getElementById('output');
const ioOutputEl = document.getElementById('io-output');
const inputEl = document.getElementById('input');
const connectBtn = document.getElementById('connectBtn');
const disconnectBtn = document.getElementById('disconnectBtn');

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Check if Paho MQTT library is loaded
    if (typeof Paho === 'undefined') {
        writeToOutput('ERROR: Paho MQTT library not loaded. Please check your internet connection.', 'system');
        setStatus('Library Error', '#ff6b6b');
        return;
    }
    
    setupAudio();
    setupInputHandling();
    setupButtonHandlers();
    setupPluginSystem();
    
    // Auto-connect on startup (standard behavior)
    setTimeout(connect, 100); // Small delay to ensure everything is ready
});

function setStatus(text, color = '#ff6b6b') {
    statusEl.textContent = text;
    statusEl.style.color = color;
}

function writeToOutput(text, type = 'normal') {
    const timestamp = new Date().toLocaleTimeString();
    let prefix = '';
    
    switch(type) {
        case 'system':
            prefix = `[${timestamp}] SYSTEM: `;
            break;
        case 'received':
            prefix = `[${timestamp}] RECEIVED: `;
            break;
        case 'sent':
            prefix = `[${timestamp}] SENT: `;
            break;
        default:
            prefix = `[${timestamp}] `;
    }
    
    outputEl.textContent += prefix + text + '\n';
    outputEl.scrollTop = outputEl.scrollHeight;
}

function writeToIO(text, type = 'normal') {
    const timestamp = new Date().toLocaleTimeString();
    let prefix = '';
    
    switch(type) {
        case 'input':
            prefix = `[${timestamp}] > `;
            break;
        case 'output':
            prefix = `[${timestamp}] < `;
            break;
        default:
            prefix = `[${timestamp}] `;
    }
    
    ioOutputEl.textContent += prefix + text + '\n';
    ioOutputEl.scrollTop = ioOutputEl.scrollHeight;
}

function connect() {
    try {
        // Check if Paho is available
        if (typeof Paho === 'undefined' || typeof Paho.MQTT === 'undefined') {
            writeToOutput('ERROR: Paho MQTT library not available', 'system');
            setStatus('Library Error', '#ff6b6b');
            return;
        }
        
        // The Paho MQTT client constructor takes (host, port, path, clientId)
        // For WebSocket URLs, we need to parse them differently
        const url = new URL(config.MQTT_SERVER);
        const host = url.hostname;
        const port = parseInt(url.port) || (url.protocol === 'wss:' ? 443 : 80);
        const path = url.pathname || '/mqtt';
        
        client = new Paho.MQTT.Client(host, port, path, config.DEVICE_UUID);
        
        console.log('MQTT Client created with:', { host, port, path, clientId: config.DEVICE_UUID });
        
        client.onConnectionLost = onConnectionLost;
        client.onMessageArrived = onMessageArrived;
        
        const connectOptions = {
            onSuccess: onConnect,
            onFailure: onConnectFailure,
            useSSL: true
        };
        
        // Add credentials if provided
        if (config.MQTT_USERNAME) {
            connectOptions.userName = config.MQTT_USERNAME;
        }
        if (config.MQTT_PASSWORD && config.MQTT_PASSWORD.trim() !== '') {
            connectOptions.password = config.MQTT_PASSWORD;
        }
        
        client.connect(connectOptions);
        writeToOutput('Connecting to MQTT broker...', 'system');
        
    } catch (error) {
        writeToOutput('Failed to create MQTT client: ' + error.message, 'system');
        setStatus('Error', '#ff6b6b');
    }
}

function onConnect() {
    isConnected = true;
    setStatus('Connected', '#00ff00');
    writeToOutput('Connected to MQTT broker', 'system');
    writeToOutput(`Device UUID: ${config.DEVICE_UUID}`, 'system');
    writeToOutput(`Subscribing to: ${config.TOPICS.PRINT}`, 'system');
    writeToOutput(`Subscribing to: ${config.TOPICS.PRINT_ALL}`, 'system');
    
    // Subscribe to print commands (both specific and global)
    client.subscribe(config.TOPICS.PRINT);
    client.subscribe(config.TOPICS.PRINT_ALL);
    
    // Update plugin manager with connected client and subscribe active plugins
    if (pluginManager) {
        pluginManager.updateClient(client);
        pluginManager.subscribeActivePlugins();
    }
    
    // Publish initial status
    publishStatus(config.STATUS.READY);
    
    // Update button states
    connectBtn.disabled = true;
    disconnectBtn.disabled = false;
    
    // Focus input
    inputEl.focus();
}

function disconnect() {
    if (client && isConnected) {
        manualDisconnect = true;
        publishStatus(config.STATUS.OFFLINE);
        client.disconnect();
        writeToOutput('Manually disconnected', 'system');
        
        // Update button states
        connectBtn.disabled = false;
        disconnectBtn.disabled = true;
    }
}

function setupButtonHandlers() {
    connectBtn.addEventListener('click', function() {
        manualDisconnect = false;
        connect();
    });
    
    disconnectBtn.addEventListener('click', function() {
        disconnect();
    });
}

function onConnectFailure(error) {
    setStatus('Connection Failed', '#ff6b6b');
    writeToOutput('Connection failed: ' + error.errorMessage, 'system');
    isConnected = false;
    
    // Update button states
    connectBtn.disabled = false;
    disconnectBtn.disabled = true;
}

function onConnectionLost(responseObject) {
    isConnected = false;
    setStatus('Disconnected', '#ff6b6b');
    writeToOutput('Connection lost', 'system');
    
    if (responseObject.errorCode !== 0) {
        writeToOutput('Error: ' + responseObject.errorMessage, 'system');
    }
    
    // Update button states
    connectBtn.disabled = false;
    disconnectBtn.disabled = true;
    
    // Don't auto-reconnect when manually disconnected
    if (!manualDisconnect) {
        // Try to reconnect after 5 seconds
        setTimeout(connect, 5000);
    }
}

function onMessageArrived(message) {
    const topic = message.destinationName;
    const payload = message.payloadString;
    
    // Debug logging for all received messages
    console.log(`Received message on topic ${topic}:`, payload);
    writeToOutput(`DEBUG: Received on ${topic}: ${payload}`, 'system');
    
    if (topic === config.TOPICS.KEYSTROKES) {
        // Handle incoming keystrokes - just type them
        handleIncomingKeystroke(payload);
    } else if (topic === config.TOPICS.PRINT) {
        writeToOutput(`Print command (specific): ${payload}`, 'received');
        // Display the received text directly (no sending back to MQTT)
        displayReceivedText(payload);
    } else if (topic === config.TOPICS.PRINT_ALL) {
        // MONITORING: Log all print_all messages to console
        console.log('=== PRINT_ALL MESSAGE RECEIVED ===');
        console.log('Topic:', topic);
        console.log('Payload:', payload);
        console.log('Payload type:', typeof payload);
        console.log('Payload length:', payload.length);
        console.log('=====================================');
        
        // Check if this is a Telegraf keystroke message or a real print command
        try {
            const parsed = JSON.parse(payload);
            console.log('Parsed JSON:', parsed);
            console.log('Has sender:', !!parsed.sender);
            console.log('Has text:', parsed.text !== undefined);
            console.log('Sender:', parsed.sender);
            console.log('Text:', parsed.text);
            
            if (parsed.sender && parsed.text !== undefined) {
                // This is a Telegraf keystroke message
                writeToOutput(`Telegraf keystroke from ${parsed.sender}: ${parsed.text}`, 'received');
                
                // Don't process our own keystrokes (prevent echo)
                if (parsed.sender === config.DEVICE_UUID) {
                    writeToOutput(`Ignoring own Telegraf keystroke: ${parsed.text}`, 'system');
                    console.log('Ignoring own Telegraf keystroke');
                    return;
                }
                
                // Handle as keystroke for other devices
                console.log('Processing Telegraf keystroke from other device');
                handleIncomingKeystroke(payload);
            } else {
                // This is a real print command
                writeToOutput(`Print command (global): ${payload}`, 'received');
                displayReceivedText(payload);
            }
        } catch (e) {
            console.log('JSON parse error:', e);
            // Not JSON, treat as regular print command
            writeToOutput(`Print command (global): ${payload}`, 'received');
            displayReceivedText(payload);
        }
    } else {
        // Handle plugin-specific topics
        if (pluginManager) {
            pluginManager.handleMessage(topic, payload);
        }
    }
}

function handleIncomingKeystroke(keystrokeData) {
    let key;
    let sender;
    
    // Parse JSON if it's a string, or use object directly
    if (typeof keystrokeData === 'string') {
        try {
            const parsed = JSON.parse(keystrokeData);
            key = parsed.text;
            sender = parsed.sender;
        } catch (e) {
            // Fallback to treating it as plain text
            key = keystrokeData;
            sender = 'unknown';
        }
    } else {
        key = keystrokeData.text;
        sender = keystrokeData.sender;
    }
    
    // Only process keystrokes from other devices (not our own)
    if (sender === config.DEVICE_UUID) {
        return;
    }
    
    // Play keystroke sound for any character (except DEL)
    if (key !== 'DEL') {
        playKeystrokeSound();
    }
    
    if (key === 'DEL') {
        // Handle backspace - remove last character from I/O output
        const currentText = ioOutputEl.textContent;
        if (currentText.endsWith('\n')) {
            // Remove the last line break and the character before it
            ioOutputEl.textContent = currentText.slice(0, -2);
        } else {
            // Remove the last character
            ioOutputEl.textContent = currentText.slice(0, -1);
        }
    } else if (key === '\n' || key === '\r') {
        // Handle line breaks
        ioOutputEl.textContent += '\n';
    } else {
        // Handle regular characters - append to current line without timestamps
        ioOutputEl.textContent += key;
    }
    
    // Scroll to bottom
    ioOutputEl.scrollTop = ioOutputEl.scrollHeight;
}

function publishStatus(status) {
    if (client && isConnected) {
        const message = new Paho.MQTT.Message(status);
        message.destinationName = config.TOPICS.STATUS;
        client.send(message);
    }
}

function publishKeystroke(key) {
    if (client && isConnected) {
        const keystrokeData = {
            sender: config.DEVICE_UUID,
            text: key
        };
        
        const payload = JSON.stringify(keystrokeData);
        
        // Log the payload being sent
        console.log('Sending keystroke payload:', payload);
        writeToOutput(`Sending keystroke: ${payload}`, 'system');
        
        const message = new Paho.MQTT.Message(payload);
        message.destinationName = config.TOPICS.KEYSTROKES;
        client.send(message);
    }
}

function displayReceivedText(text) {
    if (!text) return;
    
    writeToOutput(`Displaying received text: ${text}`, 'system');
    
    // Display the text directly in the I/O output pane with typing effect
    let index = 0;
    const typeInterval = setInterval(() => {
        if (index < text.length) {
            const char = text[index];
            
            // Display the character in the I/O output pane
            if (char === '\n' || char === '\r') {
                // Handle line breaks
                ioOutputEl.textContent += '\n';
            } else {
                // Handle regular characters - append to current line without timestamps
                ioOutputEl.textContent += char;
            }
            
            // Scroll to bottom
            ioOutputEl.scrollTop = ioOutputEl.scrollHeight;
            
            // Play sound for each character
            playKeystrokeSound();
            index++;
        } else {
            clearInterval(typeInterval);
            writeToOutput('Finished displaying received text', 'system');
        }
    }, 100); // 100ms delay between characters
}

function simulateTyping(text) {
    if (!text) return;
    
    writeToOutput(`Typing: ${text}`, 'system');
    publishStatus(config.STATUS.PRINTING);
    
    // Simulate typing delay - only send keystrokes to MQTT, don't display locally
    let index = 0;
    const typeInterval = setInterval(() => {
        if (index < text.length) {
            const char = text[index];
            publishKeystroke(char);
            // Play sound for each character
            playKeystrokeSound();
            index++;
        } else {
            clearInterval(typeInterval);
            publishStatus(config.STATUS.READY);
            writeToOutput('Finished typing', 'system');
        }
    }, 100); // 100ms delay between characters
}

function setupAudio() {
    writeToOutput('Audio system initialized', 'system');
}

function playKeystrokeSound() {
    try {
        // Create a new audio instance for each keystroke to avoid conflicts
        const audio = new Audio('stroke_effect.wav');
        audio.volume = 0.3;
        audio.play().catch(e => {
            // Ignore audio play errors silently
        });
    } catch (error) {
        // Ignore audio errors silently
    }
}

function setupPluginSystem() {
    // Create plugin manager with the virtual Erika instance
    pluginManager = new PluginManager({
        client: client,
        config: config,
        writeToOutput: writeToOutput,
        writeToIO: writeToIO,
        // Add all the methods and properties that plugins need
        publishKeystroke: publishKeystroke,
        publishStatus: publishStatus,
        playKeystrokeSound: playKeystrokeSound
    });
    
    // Register available plugins
    pluginManager.registerPlugin(Telegraf);
    
    writeToOutput('Plugin system initialized', 'system');
    writeToOutput('Available plugins: telegraf', 'system');
}

function setupInputHandling() {
    inputEl.addEventListener('keydown', function(event) {
        if (!isConnected) return;
        
        // Handle TAB TAB TAB for command mode
        if (event.key === 'Tab') {
            event.preventDefault();
            handleTabCommand();
            return;
        }
        
        // Handle command mode
        if (commandMode) {
            handleCommandMode(event);
            return;
        }
        
        // Send keystrokes immediately as you type
        let keystrokeToSend = event.key;
        let keystrokeForPlugin = event.key;
        
        if (event.key === 'Enter') {
            keystrokeToSend = '\n';
            keystrokeForPlugin = '\n';
            inputEl.value = '';
        } else if (event.key === 'Backspace') {
            keystrokeToSend = 'DEL';
            keystrokeForPlugin = 'DEL';
        } else if (event.key.length === 1) {
            // Single character keys - send immediately
            keystrokeToSend = event.key;
            keystrokeForPlugin = event.key;
        }
        
        // Send the keystroke
        publishKeystroke(keystrokeToSend);
        
        // Handle keystrokes for plugins
        if (pluginManager) {
            console.log('Calling pluginManager.handleKeystroke with key:', keystrokeForPlugin);
            pluginManager.handleKeystroke(keystrokeForPlugin);
        } else {
            console.log('PluginManager is null!');
        }
    });
    
    // Keep focus on input
    document.addEventListener('click', function() {
        inputEl.focus();
    });
}

function handleTabCommand() {
    const now = Date.now();
    
    // Reset tab count if too much time has passed
    if (now - lastTabTime > 1000) {
        tabCount = 0;
    }
    
    tabCount++;
    lastTabTime = now;
    
    if (tabCount === 3) {
        // Enter command mode
        commandMode = true;
        tabCount = 0;
        inputEl.value = '';
        inputEl.placeholder = 'COMMAND MODE - Type: help, plugins, status, exit';
        writeToOutput('Entered command mode', 'system');
        writeToIO('=== COMMAND MODE ===', 'system');
    }
}

function handleCommandMode(event) {
    if (event.key === 'Enter') {
        const command = inputEl.value.trim().toLowerCase();
        executeCommand(command);
        inputEl.value = '';
        // Exit command mode after executing a command
        exitCommandMode();
    } else if (event.key === 'Escape') {
        exitCommandMode();
    }
}

function executeCommand(command) {
    writeToIO(`> ${command}`, 'input');
    
    switch(command) {
        case 'help':
            showHelp();
            break;
        case 'plugins':
            showPlugins();
            break;
        case 'status':
            showStatus();
            break;
        case 'exit':
            exitCommandMode();
            break;
        default:
            // Check if it's a plugin toggle command
            if (pluginManager && pluginManager.getAvailablePlugins().includes(command)) {
                togglePlugin(command);
            } else {
                writeToIO(`Unknown command: ${command}`, 'output');
                writeToIO('Type "help" for available commands', 'output');
            }
    }
}

function showHelp() {
    writeToIO('Available commands:', 'output');
    writeToIO('  help          - Show this help', 'output');
    writeToIO('  plugins       - Show available plugins', 'output');
    writeToIO('  status        - Show connection status', 'output');
    writeToIO('  exit          - Exit command mode', 'output');
    writeToIO('', 'output');
    writeToIO('Plugin commands (toggle on/off):', 'output');
    if (pluginManager) {
        pluginManager.getAvailablePlugins().forEach(plugin => {
            writeToIO(`  ${plugin}`, 'output');
        });
    }
}

function showPlugins() {
    if (!pluginManager) {
        writeToIO('Plugin system not available', 'output');
        return;
    }
    
    const available = pluginManager.getAvailablePlugins();
    const active = pluginManager.getActivePlugins();
    
    writeToIO('Available plugins:', 'output');
    available.forEach(plugin => {
        const status = active.includes(plugin) ? 'ACTIVE' : 'inactive';
        writeToIO(`  ${plugin}: ${status}`, 'output');
    });
}

function showStatus() {
    writeToIO(`Connection: ${isConnected ? 'Connected' : 'Disconnected'}`, 'output');
    writeToIO(`Device UUID: ${config.DEVICE_UUID}`, 'output');
    writeToIO(`MQTT Server: ${config.MQTT_SERVER}`, 'output');
}

function togglePlugin(pluginName) {
    if (!pluginManager) {
        writeToIO('Plugin system not available', 'output');
        return;
    }
    
    const activePlugins = pluginManager.getActivePlugins();
    const plugin = activePlugins.find(p => p.pluginName === pluginName);
    
    if (plugin && plugin.active) {
        // Plugin is active, turn it off
        plugin.setActive(false);
        writeToIO(`${pluginName} plugin toggled OFF`, 'output');
    } else {
        // Plugin is not active, turn it on
        const newPlugin = pluginManager.createPlugin(pluginName);
        if (newPlugin) {
            newPlugin.setActive(true);
            writeToIO(`${pluginName} plugin toggled ON`, 'output');
        } else {
            writeToIO(`Failed to activate ${pluginName} plugin`, 'output');
        }
    }
}

function exitCommandMode() {
    commandMode = false;
    inputEl.placeholder = 'Type here...';
    writeToOutput('Exited command mode', 'system');
    writeToIO('=== NORMAL MODE ===', 'system');
}

// Handle page visibility changes
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        publishStatus(config.STATUS.OFFLINE);
    } else {
        publishStatus(config.STATUS.READY);
    }
});

// Handle page unload
window.addEventListener('beforeunload', function() {
    if (client && isConnected) {
        publishStatus(config.STATUS.OFFLINE);
        client.disconnect();
    }
}); 