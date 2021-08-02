'use strict';
//store csrftoken in a constant
const csrftoken = getCookie('csrftoken');

//function to retrieve Django CSRF token for POST requests - adapted from https://engineertodeveloper.com/how-to-use-ajax-with-django/
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
            }
        }
    }
    return cookieValue;
}
//function to post data from frontend to Django
async function postData(url="", data={}) {
    const response = await fetch(url, {
      	method: "POST",
      	headers: {
        	"X-CSRFToken": csrftoken,
      	},
      	body: JSON.stringify(data),
  	});
  	return response.json();
}
