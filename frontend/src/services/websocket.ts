// src/services/websocket.ts
export class WebSocketService {
    private ws: WebSocket | null = null;
    private reconnectAttempts = 0;
    private maxReconnectAttempts = 5;
  
    connect(url: string, onMessage: (data: any) => void) {
      this.ws = new WebSocket(url);
  
      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        onMessage(data);
      };
  
      this.ws.onclose = () => {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          setTimeout(() => {
            this.reconnectAttempts++;
            this.connect(url, onMessage);
          }, 1000 * Math.pow(2, this.reconnectAttempts));
        }
      };
    }
  
    disconnect() {
      if (this.ws) {
        this.ws.close();
        this.ws = null;
      }
    }
  
    send(data: any) {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify(data));
      }
    }
  }