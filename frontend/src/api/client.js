import axios from 'axios';

// The Vite proxy ensures /api requests are routed to FastAPI at port 8000
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for global error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response ? error.response.status : null;
    
    if (status === 503) {
      console.warn("System is initializing or models are not trained yet.");
    } else if (status === 404) {
      console.error("Resource not found:", error.config.url);
    } else {
      console.error("API Error:", error.message);
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
