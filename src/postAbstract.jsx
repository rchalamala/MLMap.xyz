export async function postAbstract(abstract) {
  try {
    // make request
    const response = await fetch(
      "https://rchalamala--ai-landscape-visualizer-api.modal.run/api/abstract",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          abstract: abstract, // send the provided 'abstract' parameter
        }),
      },
    );

    // check if the response status is 200
    if (response.status === 200) {
      // if successful, parse response and return it
      return response.json();
    } else {
      // if not successful, log an error and return null
      console.error(
        "Error posting abstract for analysis:",
        response.statusText,
      );
      return null;
    }
  } catch (error) {
    // handle any exceptions that may occur during the request
    console.error("Error posting abstract for analysis:", error);
    return null;
  }
}
