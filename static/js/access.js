async function access(url, method, data, isFormData = false) 
/**
 * After the user has successfully logged in and 
 * saved his JWT in the session storage, the user
 * will should use this function to access any API
 * endpoints that require authorization.
 * 
 * Simply passes the JWT into the Authorization header 
 */
{
    console.log("accessing: ", url, method, data)

    const token = sessionStorage.getItem('token');

    if (!token) {
        console.error('JWT token not found. Please log in first.');
        return;
    }

    try {
        const headers = {'Authorization': `Bearer ${token}`}

        let body = data
        
        if (!isFormData) {
            headers['Content-Type'] = 'application/json'
            body = JSON.stringify(data)
        }

        const response = await fetch(
            url,
            {
                method: method,
                headers: headers,
                body: body,
            }
        );

        if (method == 'GET') {
            let responseText = await response.text();
            document.write(responseText);
            document.close();
            history.pushState(null, null, url);
        }
    }
    catch (error) {
        console.error('Error accessing authenticated route:', error.message);
    }
}