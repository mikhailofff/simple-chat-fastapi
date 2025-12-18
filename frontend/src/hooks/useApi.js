import { useAuth } from "../components/Auth/AuthProvider"
import { API_BASE_URL } from "../config/api"

export const useApi = () => {
    const { token, refreshToken } = useAuth()

    const makeRequest = async (endpoint, options = {}) => {
        const getHeaders = (currentToken) => ({
            "Content-Type": "application/json",
            ...(currentToken ? { "Authorization": `Bearer ${currentToken}` } : {}),
            ...options.headers,
        })

        let response = await fetch(API_BASE_URL + endpoint, {
            ...options,
            headers: getHeaders(token),
        })

        if (response.status === 401) {
            const newToken = await refreshToken() 
            
            if (newToken) {
                response = await fetch(API_BASE_URL + endpoint, {
                    ...options,
                    headers: getHeaders(newToken),
                })
            }
        }

        if (!response.ok) {
            const errorData = await response.json().catch(() => null)
            if (response.status === 429) throw new Error("Rate limit exceeded")
            throw new Error(errorData?.detail || "Request failed")
        }

        return response.json()
    }

    return { makeRequest }
}
