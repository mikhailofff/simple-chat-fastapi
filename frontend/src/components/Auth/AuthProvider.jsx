import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react"
import { API_BASE_URL } from "../../config/api"

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
    const [token, setToken] = useState(() => {
        const stored = localStorage.getItem("jwt_token")
        if (stored) {
            try {
                const payload = JSON.parse(atob(stored.split('.')[1]))
                const now = Math.floor(Date.now() / 1000)
                if (payload.exp && payload.exp > now) {
                    return stored
                }
            } catch (e) {
                localStorage.removeItem("jwt_token")
            }
        }
        return ""
    })

    const signOut = useCallback(() => {
        setToken("")
        setUser(null)
    }, [])

    const refreshToken = useCallback(async () => {
        try {
            const response = await fetch(API_BASE_URL + "refresh", {
                method: "POST",
                credentials: "include", 
            });

            if (response.ok) {
                const data = await response.json();
                setToken(data.access_token); 
                return data.access_token;
            }
        } catch (error) {
            console.error("Refresh failed", error);
        }
        
        signOut();
        return null;
    }, [signOut]);

    const apiFetch = useCallback(async (endpoint, options = {}) => {
        const headers = {
            ...options.headers,
            Authorization: `Bearer ${token}`,
        };

        let response = await fetch(API_BASE_URL + endpoint, { ...options, headers });

        if (response.status === 401) {
            const newToken = await refreshToken();
            if (newToken) {
                headers.Authorization = `Bearer ${newToken}`;
                response = await fetch(API_BASE_URL + endpoint, { ...options, headers });
            }
        }

        return response;
    }, [token, refreshToken]);
    
    const [user, setUser] = useState(() => {
        const stored = localStorage.getItem("auth_user")
        return stored ? JSON.parse(stored) : null
    })

    useEffect(() => {
        if (token) {
            localStorage.setItem("jwt_token", token)
        } else {
            localStorage.removeItem("jwt_token")
        }
    }, [token])

    useEffect(() => {
        if (user) {
            localStorage.setItem("auth_user", JSON.stringify(user))
        } else {
            localStorage.removeItem("auth_user")
        }
    }, [user])

    const signIn = useCallback(async ({ username, password }) => {
        const form = new URLSearchParams()
        form.set("username", username)
        form.set("password", password)

        const response = await fetch(API_BASE_URL + "token", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: form.toString(),
            credentials: "include",
        })

        if (!response.ok) {
            const errorData = await response.json().catch(() => null)
            throw new Error(errorData?.detail || "Authentication failed")
        }

        const data = await response.json()
        setToken(data.access_token)
        setUser({ username })
        return true
    }, [])

    const signUp = useCallback(async ({ username, password }) => {
        const response = await fetch(API_BASE_URL + "sign-up", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password }),
        })

        if (!response.ok) {
            const errorData = await response.json().catch(() => null)
            throw new Error(errorData?.detail || "Registration failed")
        }

        await signIn({ username, password })
        return true
    }, [signIn])

    const value = useMemo(() => ({ 
        token, 
        setToken,
        user, 
        isAuthenticated: Boolean(token), 
        signIn, 
        signUp, 
        signOut,
        refreshToken
    }), [token, user, signIn, signUp, signOut, refreshToken])

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
    const ctx = useContext(AuthContext)
    if (!ctx) throw new Error("useAuth must be used within AuthProvider")
    return ctx
}


