export const VITE_API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000/api';

/**
 * kiboFetch implements exponential backoff and throws on non-2xx HTTP responses.
 */
export async function kiboFetch(url: string, options: RequestInit = {}, maxRetries = 3): Promise<Response> {
  const fullUrl = url.startsWith('http') ? url : `${VITE_API_BASE}${url}`;
  
  let attempt = 0;
  
  while (attempt <= maxRetries) {
    try {
      const response = await fetch(fullUrl, options);
      
      if (!response.ok) {
        throw new Error(`HTTP Error: ${response.status} ${response.statusText}`);
      }
      
      return response;
    } catch (error) {
      if (attempt === maxRetries) {
        throw error;
      }
      
      // Exponential backoff: 500ms, 1000ms, 2000ms
      const delay = Math.pow(2, attempt) * 500;
      await new Promise(resolve => setTimeout(resolve, delay));
      attempt++;
    }
  }
  
  throw new Error('kiboFetch failed');
}
