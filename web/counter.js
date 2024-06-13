async function updateVisitorCounter() {
    const functionUrl = 'https://counterfunctionapi.azurewebsites.net/api/VisitorCounterFunction?';

    try {
        // Fetch the current visitor count from the Azure Function
        const count = await fetchCurrentVisitorCount(functionUrl);
        
        // Update the visitor count on the webpage
        const updatedCount = count + 1;
        document.getElementById('visitorCount').innerText = updatedCount;
        
        // Send the updated count to the Azure Function to store it
        await postUpdatedVisitorCount(functionUrl, updatedCount);8

        console.log('Visitor count updated successfully in the database.');
    } catch (error) {
        console.error('Error updating visitor count:', error);
    }
}

async function fetchCurrentVisitorCount(url) {
    try {
        const response = await fetch(`${url}?getCount=true`);
        if (!response.ok) {
            throw new Error(`GET request failed: ${response.statusText}`);
        }
        const data = await response.json();
        console.log('Current visitor count fetched:', data.count);
        return data.count || 0;
    } catch (error) {
        console.error('Error fetching visitor count:', error);
        throw error; // Re-throw error to be handled by the caller
    }
}

async function postUpdatedVisitorCount(url, count) {
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ count: count }) // JSON stringified
        });
        if (!response.ok) {
            throw new Error(`POST request failed: ${response.statusText}`);
        }
        console.log('Updatdd visitor count posted successfully:', count);
    } catch (error) {
        console.error('Errors sposting updated visitor count:', error);
        throw error; // Re-throw error to be handled by the caller
    }
}

// Call the function to update the visitor counter when the page loads
updateVisitorCounter();
