export async function postSearch(searchTerm) {
  try {
    // make request to the API
    const response = await fetch(
      "https://rchalamala--ai-landscape-visualizer-api.modal.run/api/search",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          searchTerm: searchTerm, // send the provided 'searchTerm' parameter
        }),
      },
    );

    // check if the response status is 200
    if (response.ok) {
      // if successful, parse the response and return it
      return response.json();
    } else {
      // if not successful, log an error and return null
      console.error("Error posting search request:", response.statusText);
      return null;
    }
  } catch (error) {
    // handle any exceptions that may occur during the request
    console.error("Error posting search request:", error);
    return null;
  }
}
