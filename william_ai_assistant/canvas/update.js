// William AI Canvas Updater
document.addEventListener('DOMContentLoaded', () => {
    const currentCommandEl = document.querySelector('#current-command p');
    const thoughtProcessEl = document.querySelector('#thought-process pre');
    const webActionsEl = document.querySelector('#web-actions ul');
    const aiResponseEl = document.querySelector('#ai-response p');
    const systemEventsEl = document.querySelector('#system-events ul');

    // Placeholder for where the data will come from (e.g., a local JSON file or WebSocket)
    const DATA_SOURCE_URL = 'william_canvas_data.json'; // Example: polling a JSON file
    const POLLING_INTERVAL = 2000; // Poll every 2 seconds

    async function fetchAndUpdateCanvas() {
        try {
            // In a real scenario, this would fetch from a live data source.
            // For now, we'll simulate or try to fetch a local file if the Python backend creates it.
            const response = await fetch(DATA_SOURCE_URL + '?_=' + new Date().getTime()); // Cache buster
            if (!response.ok) {
                // console.warn(`Could not fetch canvas data (status: ${response.status}). Waiting for backend to create it.`);
                // You might want to display a "waiting for data" message on the canvas
                if (thoughtProcessEl.textContent === '...') { // only if not already populated
                    thoughtProcessEl.textContent = 'Awaiting data from William AI backend...';
                }
                return;
            }
            const data = await response.json();

            if (data.currentCommand) {
                currentCommandEl.textContent = data.currentCommand;
            }
            if (data.thoughtProcess) {
                thoughtProcessEl.textContent = data.thoughtProcess;
            }
            if (data.aiResponse) {
                aiResponseEl.textContent = data.aiResponse;
            }

            if (data.webActions && Array.isArray(data.webActions)) {
                webActionsEl.innerHTML = ''; // Clear old entries
                data.webActions.forEach(action => {
                    const li = document.createElement('li');
                    li.textContent = action;
                    webActionsEl.appendChild(li);
                });
            }

            if (data.systemEvents && Array.isArray(data.systemEvents)) {
                systemEventsEl.innerHTML = ''; // Clear old entries
                data.systemEvents.forEach(event => {
                    const li = document.createElement('li');
                    // Potentially add status badges or icons here based on event type
                    li.textContent = event;
                    systemEventsEl.appendChild(li);
                });
            }

        } catch (error) {
            // console.error('Error updating canvas:', error);
            // Gracefully handle cases where the file might not exist yet or is malformed
            if (thoughtProcessEl.textContent === '...') {
                 thoughtProcessEl.textContent = 'Error fetching data. Is William AI backend running and generating data?';
            }
        }
    }

    // Initial call and then set up polling
    fetchAndUpdateCanvas();
    setInterval(fetchAndUpdateCanvas, POLLING_INTERVAL);

    // Example of how to add a system event dynamically (for testing)
    // setTimeout(() => {
    //     addSystemEvent("Canvas UI Initialized");
    // }, 1000);
});

// Helper function to add a system event (can be called from other parts of JS if needed)
function addSystemEvent(text) {
    const systemEventsEl = document.querySelector('#system-events ul');
    if (systemEventsEl) {
        const li = document.createElement('li');
        li.textContent = `[${new Date().toLocaleTimeString()}] ${text}`;
        // Prepend to show newest first, or append for chronological
        systemEventsEl.prepend(li);
    }
}

// Helper function to update thought process (can be called from other parts of JS if needed)
function updateThoughtProcess(text) {
    const thoughtProcessEl = document.querySelector('#thought-process pre');
    if (thoughtProcessEl) {
        thoughtProcessEl.textContent = text;
    }
}
