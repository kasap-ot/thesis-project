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