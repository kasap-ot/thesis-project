async function login(url, username, password) {
    /**
     * Accesses the given URL with the given credential.
     * If successful, saves the returned JWT token to session-storage.
     * Otherwise, raises errors.
     */
    const loginUrl = url;
    const credentials = new URLSearchParams();
    credentials.append('username', username);
    credentials.append('password', password);

    try {
      const response = await fetch(loginUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: credentials,
      });

      if (!response.ok) {
        console.log(await response.text())
        return false;
      }

      const data = await response.json();
      const token = data.access_token;

      sessionStorage.setItem('token', token);

      console.log(data);
      console.log('session storage: ', sessionStorage.getItem('token'));

      return true;
    }
    catch (error) {
      console.error('Error during login:', error.message);
      return false;
    }
  }


async function access(url, method, data) {
    /**
     * Sends the given data object to the specified URL
     * along with the token stored in session-storage
     */
    const token = sessionStorage.getItem('token');

    if (!token) {
        console.error('JWT token not found. Please log in first.');
        return;
    }

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

        let responseText = await response.text();
        document.write(responseText);
        history.pushState(null, null, url);
        console.log('Response: ', responseText);
    }
    catch (error) {
        console.error('Error accessing authenticated route:', error.message);
    }
}