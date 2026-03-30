import { createStore } from "/js/AlpineStore.js";

export const cosmeticStore = createStore("cosmeticStore", {
    currentCss: "",

    init() {
        this.fetchCss();

        // Listen for socket events from backend
        // 'message' event is emitted by the websocket manager for custom events
        window.addEventListener('a0-ws-message', (e) => {
            const data = e.detail;
            if (data && data.type === 'cosmetic_css_update' && data.data && typeof data.data.css === 'string') {
                this.currentCss = data.data.css;
            }
        });

        // Alternatively hook directly into the socketio instance if present
        if (window.socket) {
            window.socket.on("cosmetic_css_update", (data) => {
                if (data && typeof data.css === 'string') {
                    this.currentCss = data.css;
                }
            });
        }
    },

    async fetchCss() {
        try {
            const response = await fetch('/api/plugins/cosmetic_committee/get_css', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            });
            const data = await response.json();
            if (data && data.css) {
                this.currentCss = data.css;
            }
        } catch (err) {
            console.error("Failed to load cosmetic CSS", err);
        }
    }
});
