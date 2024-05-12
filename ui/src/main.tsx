import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import '@gravity-ui/uikit/styles/fonts.css';
import '@gravity-ui/uikit/styles/styles.css';
import {ThemeProvider} from '@gravity-ui/uikit';

ReactDOM.createRoot(document.getElementById('root')!).render(
    <ThemeProvider theme="light">
        <App />
    </ThemeProvider>,
);
