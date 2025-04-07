import React from 'react';
import ReactDOM from 'react-dom';
import './index.css'; // We created this
import App from './App';
// Remove the service worker import if you're not using it
// import * as serviceWorker from './serviceWorker';

// Remove the reportWebVitals import
// import reportWebVitals from './reportWebVitals';

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
// serviceWorker.unregister();

// Remove the reportWebVitals function call
// reportWebVitals(); 