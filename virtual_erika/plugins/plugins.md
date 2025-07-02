# Virtual Erika Plugin Migration Guide

This guide explains how to port Python plugins from the real Erika hardware to JavaScript for the virtual Erika.

## Plugin Structure

### Python Plugin (Original)
```python
from plugins.erika_plugin_base import ErikaBasePlugin

class Telegraf(ErikaBasePlugin):
    def __init__(self, erika=None, erika_mqqt=None):
        super().__init__(
            erika=erika, 
            erika_mqqt=erika_mqqt,
            keylogging=True,
            active=False
        )
    
    def on_message(self, topic: str, msg: str):
        return super().on_message(topic, "Telegraf received: "+msg)

    async def on_keystroke(self, key=""):
        data = {"sender": self.erika.uuid, "text": key}
        await self.erika_mqqt.client.publish(
            self.erika_mqqt.channel_print_all, 
            json.dumps(data), 
            qos=0
        )
```

### JavaScript Plugin (Virtual Erika)
```javascript
class Telegraf extends VirtualErikaBasePlugin {
    constructor(virtualErika) {
        super(virtualErika, {
            topic: 'telegraf',
            keylogging: true,
            active: false,
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
        if (this.active && this.keylogging) {
            const data = {
                sender: this.virtualErika.config.DEVICE_UUID,
                text: key
            };
            
            this.sendMessage(
                this.virtualErika.config.TOPICS.PRINT_ALL, 
                JSON.stringify(data)
            );
        }
    }
}
```

## Migration Steps

### 1. Create Plugin File
Create a new file: `plugins/your-plugin-name.js`

### 2. Import Base Class
```javascript
// Your plugin will automatically have access to VirtualErikaBasePlugin
```

### 3. Convert Constructor
**Python:**
```python
def __init__(self, erika=None, erika_mqqt=None):
    super().__init__(
        erika=erika, 
        erika_mqqt=erika_mqqt,
        keylogging=True,
        active=False
    )
```

**JavaScript:**
```javascript
constructor(virtualErika) {
    super(virtualErika, {
        topic: 'your-topic-name',
        keylogging: true,
        active: false,
        info: "Your plugin description"
    });
}
```

### 4. Convert Methods

#### on_message → onMessage
**Python:**
```python
def on_message(self, topic: str, msg: str):
    # Your logic here
```

**JavaScript:**
```javascript
onMessage(topic, msg) {
    if (this.active) {
        // Your logic here
        this.virtualErika.writeToOutput(`Plugin received: ${msg}`, 'system');
    }
}
```

#### on_keystroke → onKeystroke
**Python:**
```python
async def on_keystroke(self, key=""):
    # Your logic here
```

**JavaScript:**
```javascript
onKeystroke(key) {
    if (this.active && this.keylogging) {
        // Your logic here
    }
}
```

### 5. MQTT Publishing
**Python:**
```python
await self.erika_mqqt.client.publish(topic, message, qos=0)
```

**JavaScript:**
```javascript
this.sendMessage(topic, message);
// or
const mqttMessage = new Paho.MQTT.Message(message);
mqttMessage.destinationName = topic;
this.virtualErika.client.send(mqttMessage);
```

### 6. Access to Virtual Erika
**Python:**
```python
self.erika.uuid
self.erika_mqqt.channel_print_all
```

**JavaScript:**
```javascript
this.virtualErika.config.DEVICE_UUID
this.virtualErika.config.TOPICS.PRINT_ALL
```

## Plugin Registration

Plugins are automatically registered when the virtual Erika loads. To activate a plugin:

```javascript
// In the browser console or in your code
const telegrafPlugin = virtualErika.pluginManager.createPlugin('telegraf');
telegrafPlugin.setActive(true);
```

## Available Methods

### VirtualErikaBasePlugin Methods
- `setActive(active)` - Enable/disable plugin
- `sendMessage(topic, msg)` - Send MQTT message
- `onMessage(topic, msg)` - Handle incoming messages
- `onKeystroke(key)` - Handle keystrokes

### Virtual Erika Access
- `this.virtualErika.client` - MQTT client
- `this.virtualErika.config` - Configuration
- `this.virtualErika.writeToOutput(text, type)` - Write to system pane
- `this.virtualErika.writeToIO(text, type)` - Write to I/O pane

## Example: Complete Plugin Migration

See `telegraf.js` for a complete example of a migrated plugin. 