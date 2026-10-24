// C:\aigaane-master\shared\kernel_websocket.js
// HTTP API client for Vercel deployment (WebSockets disabled)

class KernelAPIClient {
  constructor() {
    // Use relative URLs – works on any origin (Vercel, localhost, custom domain)
    this.baseUrl = '';  // empty = same origin
    this.listeners = [];
    this.goldenBuildState = null;
  }

  // Helper to build full URL
  _url(path) {
    return `${this.baseUrl}${path}`;
  }

  // ============ Core API Methods ============

  async getCurrent() {
    try {
      const response = await fetch(this._url('/api/kernel/v3/current'));
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('[KernelAPI] Failed to get current state:', error);
      return null;
    }
  }

  async updateState(state) {
    try {
      const response = await fetch(this._url('/api/kernel/v3/update'), {
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
      const response = await fetch(this._url(`/api/kernel/v3/history?limit=${limit}`));
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('[KernelAPI] Failed to get history:', error);
      return [];
    }
  }

  async compareStates(indexA = -2, indexB = -1) {
    try {
      const response = await fetch(this._url(`/api/kernel/v3/compare?index_a=${indexA}&index_b=${indexB}`));
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
      const response = await fetch(this._url('/api/kernel/v3/golden/build'), {
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
      const response = await fetch(this._url('/api/kernel/v3/golden/current'));
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('[KernelAPI] Failed to get Golden Build:', error);
      return null;
    }
  }

  async listGoldenBuilds() {
    try {
      const response = await fetch(this._url('/api/kernel/v3/golden/list'));
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('[KernelAPI] Failed to list Golden Builds:', error);
      return [];
    }
  }

  async deleteGoldenBuild(buildId) {
    try {
      const response = await fetch(this._url(`/api/kernel/v3/golden/${buildId}`), {
        method: 'DELETE'
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('[KernelAPI] Failed to delete Golden Build:', error);
      return null;
    }
  }

  // ============ WebSocket methods removed (not supported on Vercel) ============
  // All real-time features are now HTTP‑only. If you need live updates,
  // consider polling or a separate WebSocket service.

  // Dummy methods to avoid breaking existing imports
  connectWebSocket() {
    console.warn('[KernelAPI] WebSockets disabled on Vercel');
    return null;
  }

  disconnectWebSocket() {}

  subscribeToChannel() {}

  unsubscribeFromChannel() {}

  sendMessage() { return false; }

  isConnected() { return false; }

  getConnectionState() { return 'DISABLED'; }

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

  // ============ Removed Methods (WebSocket dependent) ============
  async fetchAndBroadcastGoldenBuild() {
    console.warn('[KernelAPI] fetchAndBroadcastGoldenBuild not implemented without WebSocket');
    return null;
  }

  async syncGoldenBuildToAllClients() {
    console.warn('[KernelAPI] syncGoldenBuildToAllClients not implemented without WebSocket');
  }

  async getConnectedClients() {
    return [];
  }

  async sendToClient() {
    return null;
  }

  getGoldenBuildState() {
    return this.goldenBuildState;
  }

  // ============ Utility Methods ============

  async healthCheck() {
    try {
      const response = await fetch(this._url('/api/health'));
      return response.ok;
    } catch {
      return false;
    }
  }

  async getServerInfo() {
    try {
      const response = await fetch(this._url('/api/info'));
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