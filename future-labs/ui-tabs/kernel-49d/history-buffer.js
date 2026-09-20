// C:\aigaane-master\ui\tabs\kernel-49d\history-buffer.js
// Historical Tracking (N-State Buffer)

export class HistoryBuffer {
  constructor(maxSize = 108) {
    this.maxSize = maxSize;
    this.buffer = [];
    this.listeners = [];
  }

  // Add new state to buffer
  push(state) {
    const snapshot = {
      timestamp: new Date().toISOString(),
      angle: state.angle,
      nakshatra_id: state.nakshatra_id,
      pada_id: state.pada_id,
      vector: [...state.vector],
      meta: { ...state.meta },
      shruti_ratio: state.shruti_ratio
    };
    
    if (this.buffer.length >= this.maxSize) {
      this.buffer.shift();
    }
    this.buffer.push(snapshot);
    
    // Notify listeners
    this.notifyListeners('push', snapshot);
    
    return snapshot;
  }

  // Get current state (most recent)
  getCurrent() {
    return this.buffer[this.buffer.length - 1] || null;
  }

  // Get previous state (N steps back)
  getPrevious(offset = 1) {
    const index = this.buffer.length - 1 - offset;
    return this.buffer[index] || null;
  }

  // Get state at specific index
  getAt(index) {
    return this.buffer[index] || null;
  }

  // Get all states
  getAll() {
    return [...this.buffer];
  }

  // Get last N states
  getLastN(n = 10) {
    return this.buffer.slice(-n);
  }

  // Calculate rate of change between two states
  calculateDrift(stateA, stateB) {
    if (!stateA || !stateB) return null;
    
    const angleDelta = stateB.angle - stateA.angle;
    const vectorDeltas = stateB.vector.map((v, i) => v - stateA.vector[i]);
    const avgVectorDelta = vectorDeltas.reduce((a, b) => a + Math.abs(b), 0) / 49;
    
    // Calculate velocity (rate of change per degree)
    const velocity = angleDelta !== 0 ? avgVectorDelta / Math.abs(angleDelta) : 0;
    
    return {
      angle_delta: angleDelta,
      avg_vector_delta: avgVectorDelta,
      velocity: velocity,
      direction: angleDelta > 0 ? 'forward' : 'backward',
      magnitude: Math.abs(angleDelta),
      max_delta: Math.max(...vectorDeltas.map(Math.abs)),
      min_delta: Math.min(...vectorDeltas.map(Math.abs))
    };
  }

  // Get velocity trend over last N states
  getTrend(windowSize = 10) {
    if (this.buffer.length < windowSize) return null;
    
    const recent = this.buffer.slice(-windowSize);
    let totalDrift = 0;
    let drifts = [];
    
    for (let i = 1; i < recent.length; i++) {
      const drift = this.calculateDrift(recent[i-1], recent[i]);
      if (drift) {
        totalDrift += drift.avg_vector_delta;
        drifts.push(drift);
      }
    }
    
    const avgDrift = totalDrift / (windowSize - 1);
    const isStable = avgDrift < 0.01;
    
    return {
      average_drift: avgDrift,
      sample_size: windowSize - 1,
      stable: isStable,
      direction: drifts.length > 0 ? drifts[drifts.length - 1]?.direction : 'neutral',
      drifts: drifts
    };
  }

  // Get Nakshatra transition points
  getTransitions() {
    const transitions = [];
    for (let i = 1; i < this.buffer.length; i++) {
      if (this.buffer[i].nakshatra_id !== this.buffer[i-1].nakshatra_id) {
        transitions.push({
          from_nakshatra: this.buffer[i-1].nakshatra_id,
          to_nakshatra: this.buffer[i].nakshatra_id,
          angle: this.buffer[i].angle,
          timestamp: this.buffer[i].timestamp
        });
      }
    }
    return transitions;
  }

  // Clear buffer
  clear() {
    this.buffer = [];
    this.notifyListeners('clear', null);
  }

  // Get buffer size
  size() {
    return this.buffer.length;
  }

  // Subscribe to buffer changes
  subscribe(callback) {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter(cb => cb !== callback);
    };
  }

  notifyListeners(event, data) {
    this.listeners.forEach(cb => cb({ event, data, bufferSize: this.buffer.length }));
  }
}

// Singleton instance
export const historyBuffer = new HistoryBuffer(108);