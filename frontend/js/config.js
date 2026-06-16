function getApiUrl() {
    const host = window.location.hostname;

    if (host === '192.168.10.10' || host === 'ymmo.local') {
        return '/api';
    }

    return 'http://127.0.0.1:8000';
}

const API_URL = getApiUrl();
