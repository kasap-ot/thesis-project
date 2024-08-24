async function login(url, username, password)
/**
 * Used when the user logs into the application.
 * 
 * Takes in the parameters for authentication and
 * send them to the API endpoint for logging in.
 * 
 * Awaits the JWT token and saves it to session storage.
 * 
 * This token will then be used for all later API
 * requests by the user.
 */
{
    const loginUrl = url;
    const credentials = new URLSearchParams();
    credentials.append('username', username);
    credentials.append('password', password);

    try {
      const response = await fetch(loginUrl, {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded',},
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