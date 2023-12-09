async function access(url, method, data) 
{
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

        if (method != 'GET') return;

        let responseText = await response.text();
        document.write(responseText);
        document.close();
        history.pushState(null, null, url);
    }
    catch (error) {
        console.error('Error accessing authenticated route:', error.message);
    }
}