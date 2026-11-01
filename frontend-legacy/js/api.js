const API_BASE_URL = "http://127.0.0.1:8000/api";


async function apiRequest(
    endpoint,
    method = "GET",
    body = null
) {

    const options = {
        method: method,
        headers: {
            "Content-Type": "application/json"
        }
    };


    if (body) {

        options.body = JSON.stringify(
            body
        );
    }


    const response = await fetch(
        API_BASE_URL + endpoint,
        options
    );


    const data = await response.json();


    if (!response.ok) {

        throw new Error(
            data.detail || "API request failed"
        );
    }


    return data;
}