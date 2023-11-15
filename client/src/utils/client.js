import axios from 'axios';
import cookies from 'axios/unsafe/helpers/cookies';


axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';

axios.interceptors.request.use(
  config => {
    if (!cookies.read(config.xsrfCookieName)) {
      const csrfTokenInput = document.querySelectorAll("input[name='csrfmiddlewaretoken']");
      if (csrfTokenInput.length > 0) {
        config.headers.common[axios.defaults.xsrfHeaderName] = csrfTokenInput[0].value;;
      }
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

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
  const data = new FormData();
  data.set('query', query);
  data.set('type', type);
  data.set('exclude', exclude);
  const url = apiBase + 'search/';

  return post(url, data)
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
