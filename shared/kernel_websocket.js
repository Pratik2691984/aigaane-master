// C:\aigaane-master\shared\kernel_websocket.js
// WebSocket client for real-time API communication with Golden Build broadcast

class KernelAPIClient {
  constructor(apiUrl = 'http://localhost:8000') {
    this.apiUrl = apiUrl;
    this.ws = null;
    this.listeners = [];
    this.goldenBuildState = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 3000;
    this.isConnecting = false;
  }

  // ============ Core API Methods ============

  async getCurrent() {
    try {
      const response = await fetch(`${this.apiUrl}/kernel/v3/current`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('[KernelAPI] Failed to get current state:', error);
      return null;
    }
  }

  async updateState(state) {
    try {
      const response = await fetch(`${this.apiUrl}/kernel/v3/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(state)
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('[KernelAPI] Failed to update state:', error);
      return null;
    }
  }

  async getHistory(limit = 50) {
    try {
      const response = await fetch(`${this.apiUrl}/kernel/v3/history?limit=${limit}`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('[KernelAPI] Failed to get history:', error);
      return [];
    }
  }

  async compareStates(indexA = -2, indexB = -1) {
    try {
      const response = await fetch(`${this.apiUrl}/kernel/v3/compare?index_a=${indexA}&index_b=${indexB}`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('[KernelAPI] Failed to compare states:', error);
      return null;
    }
  }

  // ============ Golden Build Methods ============

  async broadcastGoldenBuild(goldenBuildData) {
    try {
      const response = await fetch(`${this.apiUrl}/kernel/v3/golden/build`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...goldenBuildData,
          timestamp: new Date().toISOString(),
          broadcast_id: crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36)
        })
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const result = await response.json();
      console.log('[KernelAPI] Golden Build broadcasted:', result);
      return result;
    } catch (error) {
      console.error('[KernelAPI] Failed to broadcast Golden Build:', error);
      return null;
    }
  }

  async getGoldenBuild() {
    try {
      const response = await fetch(`${this.apiUrl}/kernel/v3/golden/current`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('[KernelAPI] Failed to get Golden Build:', error);
      return null;
    }
  }

  async listGoldenBuilds() {
    try {
      const response = await fetch(`${this.apiUrl}/kernel/v3/golden/list`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('[KernelAPI] Failed to list Golden Builds:', error);
      return [];
    }
  }

  async deleteGoldenBuild(buildId) {
    try {
      const response = await fetch(`${this.apiUrl}/kernel/v3/golden/${buildId}`, {
        method: 'DELETE'
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('[KernelAPI] Failed to delete Golden Build:', error);
      return null;
    }
  }

  // ============ WebSocket Methods ============

  connectWebSocket(onMessage, onOpen, onClose, onError) {
    if (this.isConnecting) {
      console.log('[KernelAPI] Connection already in progress');
      return null;
    }
    
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      console.log('[KernelAPI] WebSocket already connected or connecting');
      return this.ws;
    }
    
    this.isConnecting = true;
    
    try {
      this.ws = new WebSocket(`ws://${this.apiUrl.split('//')[1]}/ws`);
      
      this.ws.onopen = () => {
        console.log('[KernelAPI] WebSocket connected');
        this.reconnectAttempts = 0;
        this.isConnecting = false;
        
        // Subscribe to channels
        this.subscribeToChannel('golden_build');
        this.subscribeToChannel('kernel_state');
        this.subscribeToChannel('anomaly_alerts');
        
        if (onOpen) onOpen();
      };
      
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // Handle different message types
          switch (data.type) {
            case 'golden_build_update':
              this.goldenBuildState = data.payload;
              console.log('[KernelAPI] Golden Build update received:', {
                build: data.payload.metadata?.build_name,
                angle: data.payload.metadata?.cosmic_angle,
                timestamp: data.timestamp
              });
              break;
            case 'kernel_state_update':
              console.log('[KernelAPI] Kernel state update:', data.payload);
              break;
            case 'anomaly_alert':
              console.warn('[KernelAPI] Anomaly alert:', data.payload);
              break;
            case 'subscription_confirmed':
              console.log('[KernelAPI] Subscribed to:', data.channel);
              break;
            default:
              break;
          }
          
          if (onMessage) onMessage(data);
          this.notify(data);
          
        } catch (error) {
          console.error('[KernelAPI] Failed to parse WebSocket message:', error);
        }
      };
      
      this.ws.onerror = (error) => {
        console.error('[KernelAPI] WebSocket error:', error);
        this.isConnecting = false;
        if (onError) onError(error);
      };
      
      this.ws.onclose = (event) => {
        console.log(`[KernelAPI] WebSocket closed: ${event.code} - ${event.reason}`);
        this.isConnecting = false;
        if (onClose) onClose(event);
        
        // Auto-reconnect
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          console.log(`[KernelAPI] Reconnecting in ${this.reconnectDelay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
          setTimeout(() => {
            this.connectWebSocket(onMessage, onOpen, onClose, onError);
          }, this.reconnectDelay);
        }
      };
      
      return this.ws;
      
    } catch (error) {
      console.error('[KernelAPI] Failed to create WebSocket:', error);
      this.isConnecting = false;
      return null;
    }
  }

  subscribeToChannel(channel) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'subscribe',
        channel: channel
      }));
    } else {
      console.log(`[KernelAPI] Cannot subscribe to ${channel}: WebSocket not open`);
    }
  }

  unsubscribeFromChannel(channel) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'unsubscribe',
        channel: channel
      }));
    }
  }

  sendMessage(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
      return true;
    }
    console.error('[KernelAPI] Cannot send message: WebSocket not open');
    return false;
  }

  disconnectWebSocket() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
      console.log('[KernelAPI] WebSocket disconnected');
    }
  }

  // ============ Golden Build Specific Methods ============

  async fetchAndBroadcastGoldenBuild() {
    try {
      // Fetch the Golden Build JSON from root
      const response = await fetch('/golden_build_chitra_53.json');
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      const goldenBuild = await response.json();
      
      // Broadcast via WebSocket
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.sendMessage({
          type: 'golden_build_import',
          payload: goldenBuild,
          timestamp: new Date().toISOString()
        });
      }
      
      // Also broadcast via HTTP
      await this.broadcastGoldenBuild(goldenBuild);
      
      console.log('[KernelAPI] Golden Build fetched and broadcasted');
      return goldenBuild;
      
    } catch (error) {
      console.error('[KernelAPI] Failed to fetch and broadcast Golden Build:', error);
      return null;
    }
  }

  async syncGoldenBuildToAllClients(goldenBuildData) {
    const clients = await this.getConnectedClients();
    for (const client of clients) {
      await this.sendToClient(client.id, {
        type: 'force_golden_sync',
        payload: goldenBuildData
      });
    }
  }

  async getConnectedClients() {
    try {
      const response = await fetch(`${this.apiUrl}/kernel/v3/clients`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('[KernelAPI] Failed to get connected clients:', error);
      return [];
    }
  }

  async sendToClient(clientId, message) {
    try {
      const response = await fetch(`${this.apiUrl}/kernel/v3/send/${clientId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(message)
      });
      return await response.json();
    } catch (error) {
      console.error(`[KernelAPI] Failed to send to client ${clientId}:`, error);
      return null;
    }
  }

  // ============ Event System ============

  subscribe(callback) {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter(cb => cb !== callback);
    };
  }

  notify(data) {
    this.listeners.forEach(cb => {
      try {
        cb(data);
      } catch (error) {
        console.error('[KernelAPI] Listener error:', error);
      }
    });
  }

  // ============ Status Methods ============

  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN;
  }

  getConnectionState() {
    if (!this.ws) return 'DISCONNECTED';
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING: return 'CONNECTING';
      case WebSocket.OPEN: return 'OPEN';
      case WebSocket.CLOSING: return 'CLOSING';
      case WebSocket.CLOSED: return 'CLOSED';
      default: return 'UNKNOWN';
    }
  }

  getGoldenBuildState() {
    return this.goldenBuildState;
  }

  // ============ Utility Methods ============

  async healthCheck() {
    try {
      const response = await fetch(`${this.apiUrl}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }

  async getServerInfo() {
    try {
      const response = await fetch(`${this.apiUrl}/info`);
      return await response.json();
    } catch (error) {
      console.error('[KernelAPI] Failed to get server info:', error);
      return null;
    }
  }
}

// Singleton instance for global use
export const kernelAPI = new KernelAPIClient();

// Export class for custom instances
export { KernelAPIClient };