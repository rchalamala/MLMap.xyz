export default async function getPaper(paperId) {
  try {
    // make a request using the provided paperId
    const response = await fetch(
      `https://rchalamala--ai-landscape-visualizer-api.modal.run/api/get_paper/${paperId}`,
    );

    // check if the response is successful
    if (response.ok) {
      // if successful, parse the response and return it
      const data = await response.json();
      return data;
    } else if (response.status === 404) {
      // if the paper is not found, log an error and return null
      console.error("Paper not found");
      return null;
    } else {
      // if there's an error with the request, log an error and return null
      console.error("Error fetching paper:", response.statusText);
      return null;
    }
  } catch (error) {
    // if there's an error in the try block, log an error and return null
    console.error("Error fetching paper:", error);
    return null;
  }
}
