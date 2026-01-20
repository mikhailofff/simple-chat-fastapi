import React, { useEffect } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import { SignInForm, SignUpForm } from "./AuthForms"
import { useAuth } from "./AuthProvider"

export function AuthenticationPage() {
    const location = useLocation()
    const navigate = useNavigate()
    const { isAuthenticated } = useAuth()
    const isSignIn = location.pathname.includes("sign-in")

    useEffect(() => {
        if (isAuthenticated) {
            navigate("/", { replace: true })
        }
    }, [isAuthenticated, navigate])

    return (
        <div className="auth-container">
            {isSignIn ? <SignInForm /> : <SignUpForm />}
        </div>
    )
}
