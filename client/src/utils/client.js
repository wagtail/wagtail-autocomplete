import axios from 'axios';


axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';


const get = (url, params) =>
  axios.get(url, { params })
    .then(res => {
      if (res.status < 200 || res.status >= 300) {
        return Promise.reject();
      }

      return res.data;
    });


const post = (url, data) =>
  axios.post(url, data)
    .then(res => {
      if (res.status < 200 || res.status >= 300) {
        return Promise.reject();
      }

      return res.data;
    });


export const getSuggestions = ({ apiBase, query, type, exclude }) => {
  const params = {
    query,
    type,
    exclude,
  };
  const url = apiBase + 'search/';

  return get(url, params)
    .then(res => {
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
  const url = apiBase + 'objects/';

  return get(url, params)
    .then(res => {
      if (!Array.isArray(res.items)) {
        return Promise.reject();
      }

      return res.items;
    });
};


export const createObject = ({ apiBase, type, value }) => {
  const data = new FormData();
  data.set('type', type);
  data.set('value', value);
  const url = apiBase + 'create/';

  return post(url, data)
    .then(res => res);
};
