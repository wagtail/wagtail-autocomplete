import Cookies from "js-cookie";

const XSRF_COOKIE_NAME = "csrftoken";
const XSRF_HEADER_NAME = "X-CSRFToken";

function httpRequest(url, { body, ...customConfig } = {}) {
	const headers = {};
	if (body) {
		if (Cookies.get(XSRF_COOKIE_NAME)) {
			headers[XSRF_HEADER_NAME] = Cookies.get(XSRF_COOKIE_NAME);
		} else {
			const csrfTokenInput = document.querySelectorAll(
				"input[name='csrfmiddlewaretoken']",
			);
			if (csrfTokenInput.length > 0) {
				headers[XSRF_HEADER_NAME] = csrfTokenInput[0].value;
			}
		}
	}

	const config = {
		method: body ? "POST" : "GET",
		...customConfig,
		headers: {
			...headers,
			...customConfig.headers,
		},
	};

	if (body) {
		config.body = body;
	}

	return window.fetch(url, config).then((response) => {
		if (response.ok) {
			return response.json();
		}
		return Promise.reject();
	});
}

/**
 * Join primary keys for the objects view's pks and the search view's exclude.
 * Each pk is encoded so commas and percent signs in string pks survive; the
 * views split on commas and decode each pk.
 */
export const joinPks = (pks) =>
	pks.map((pk) => encodeURIComponent(pk)).join(",");

const get = (url, params) =>
	httpRequest(`${url}?${new URLSearchParams(params).toString()}`);

const post = (url, data) => httpRequest(url, { body: data });

export const getSuggestions = ({ apiBase, query, type, exclude }) => {
	const data = new FormData();
	data.set("query", query);
	data.set("type", type);
	data.set("exclude", exclude);
	const url = apiBase + "search/";

	return post(url, data).then((res) => {
		if (!Array.isArray(res.items)) {
			return Promise.reject();
		}

		return res.items;
	});
};

export const getObjects = ({ apiBase, ids, type }) => {
	const params = {
		ids,
		type,
	};
	const url = apiBase + "objects/";

	return get(url, params).then((res) => {
		if (!Array.isArray(res.items)) {
			return Promise.reject();
		}

		return res.items;
	});
};

export const createObject = ({ apiBase, type, value }) => {
	const data = new FormData();
	data.set("type", type);
	data.set("value", value);
	const url = apiBase + "create/";

	return post(url, data).then((res) => res);
};
