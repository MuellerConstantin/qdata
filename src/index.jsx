import React from 'react';
import * as ReactDOM from 'react-dom/client';
import {HashRouter} from 'react-router-dom';
import {Provider} from 'react-redux';
import reportWebVitals from './reportWebVitals';
import {StatusProvider} from './contexts/StatusContext';
import store from './store';
import App from './App';

import './styles/index.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <Provider store={store}>
      <StatusProvider>
        <HashRouter>
          <App />
        </HashRouter>
      </StatusProvider>
    </Provider>
  </React.StrictMode>,
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
