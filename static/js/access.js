async function access(url, method, data) {
    /**
     * Sends the given data object to the specified URL
     * along with the token stored in session-storage.
     * Receives an HTML response and writes it on the
     * document. Adds the url to history, for a better
     * user experience.
     */
    const token = sessionStorage.getItem('token');

    if (!token) {
        console.error('JWT token not found. Please log in first.');
        return;
    }

    console.log(url)
    console.log(method)
    console.log(data)

    try {
        const response = await fetch(
            url,
            {
                method: method,
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            }
        );

        console.log('here is the test');

        let responseText = await response.text();
        document.write(responseText);
        document.close();
        history.pushState(null, null, url);
    }
    catch (error) {
        console.error('Error accessing authenticated route:', error.message);
    }
}