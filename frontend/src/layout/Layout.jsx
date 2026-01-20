import React, { useEffect, useRef, useState } from "react"
import { Outlet, Link, Navigate, useNavigate } from "react-router-dom"
import { useAuth } from "../components/Auth/AuthProvider"
import { useApi } from "../hooks/useApi"

export function Layout() {
    const { isAuthenticated, signOut, user } = useAuth()
    const navigate = useNavigate()
    const [isMenuOpen, setIsMenuOpen] = useState(false)
    const [oldPassword, setOldPassword] = useState("")
    const [newPassword, setNewPassword] = useState("")
    const [isChangePwdOpen, setIsChangePwdOpen] = useState(false)
    const dropdownRef = useRef(null)
    const { makeRequest } = useApi()

    const handleSignOut = () => {
        signOut()
        navigate("/sign-in")
    }

    const username = user?.username || "Profile"

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsMenuOpen(false)
            }
        }
        document.addEventListener('mousedown', handleClickOutside)
        return () => document.removeEventListener('mousedown', handleClickOutside)
    }, [])

    const handleChangePassword = async (e) => {
        e.preventDefault()
        if (!oldPassword || !newPassword) {
            alert('Please fill both fields')
            return
        }
        if (newPassword.length < 8) {
            alert('New password must be at least 8 characters long')
            return
        }
        try {
            const resp = await makeRequest("change-password", {
                method: "PATCH",
                body: JSON.stringify({
                    username: username,
                    old_password: oldPassword,
                    new_password: newPassword
                })
            })
            if (!resp || resp.success === false) {
                const message = resp?.detail || 'Old password is incorrect'
                alert(message)
                return
            }
            alert('Password changed successfully')
            setOldPassword("")
            setNewPassword("")
            setIsChangePwdOpen(false)
        } catch (err) {
            alert(err.message || 'Failed to change password')
        }
    }

    return (
        <div className="app-layout">
            <header className="app-header">
                <div className="header-content">
                    <h1>Simple chat</h1>
                    <nav>
                        {isAuthenticated ? (
                            <>
                                <div style={{ position: 'relative', display: 'inline-block' }} ref={dropdownRef}>
                                    <button onClick={() => setIsMenuOpen((v) => !v)}>
                                        {username}
                                    </button>
                                    {isMenuOpen && (
                                        <div
                                            style={{
                                                position: 'absolute',
                                                right: 0,
                                                marginTop: '8px',
                                                background: 'white',
                                                border: '1px solid #e5e7eb',
                                                borderRadius: '8px',
                                                boxShadow: '0 8px 16px rgba(0,0,0,0.08)',
                                                minWidth: '220px',
                                                zIndex: 50,
                                                padding: '8px'
                                            }}
                                        >
                                            <button
                                                onClick={() => { setIsMenuOpen(false); setIsChangePwdOpen(true) }}
                                                style={{ display: 'block', width: '100%', padding: '8px 12px', textAlign: 'left', background: 'transparent', border: 'none', cursor: 'pointer', color: '#19439e' }}
                                            >
                                                Change password
                                            </button>
                                            <hr style={{ margin: '8px 0', borderColor: '#f3f4f6' }} />
                                            <button
                                                onClick={() => { setIsMenuOpen(false); handleSignOut() }}
                                                style={{ display: 'block', width: '100%', padding: '8px 12px', textAlign: 'left', background: 'transparent', border: 'none', cursor: 'pointer', color: '#ef4444' }}
                                            >
                                                Sign Out
                                            </button>
                                        </div>
                                    )}
                                </div>
                            </>
                        ) : (
                            <>
                                <button onClick={() => navigate("/sign-in")}>Sign In</button>
                                <button onClick={() => navigate("/sign-up")}>Sign Up</button>
                            </>
                        )}
                    </nav>
                </div>
            </header>

            <main className="app-main">
                {!isAuthenticated && <Navigate to="/sign-up" replace />}
                {isAuthenticated && <Outlet />}
            </main>

            {isAuthenticated && isChangePwdOpen && (
                <div
                    onClick={() => setIsChangePwdOpen(false)}
                    style={{
                        position: 'fixed',
                        inset: 0,
                        background: 'rgba(0,0,0,0.35)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        zIndex: 100,
                    }}
                >
                    <div
                        onClick={(e) => e.stopPropagation()}
                        style={{
                            width: 'min(92vw, 420px)',
                            background: 'white',
                            borderRadius: '12px',
                            boxShadow: '0 10px 24px rgba(0,0,0,0.2)',
                            padding: '20px',
                        }}
                    >
                        <h3 style={{ marginTop: 0, marginBottom: '12px' }}>Change password</h3>
                        <form onSubmit={handleChangePassword} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                            <label style={{ fontSize: '12px', color: '#6b7280' }}>Old password</label>
                            <input type="password" value={oldPassword} onChange={(e) => setOldPassword(e.target.value)} style={{ padding: '10px', border: '1px solid #d1d5db', borderRadius: '8px' }} />
                            <label style={{ fontSize: '12px', color: '#6b7280' }}>New password</label>
                            <input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} style={{ padding: '10px', border: '1px solid #d1d5db', borderRadius: '8px' }} />
                            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px', marginTop: '8px' }}>
                                <button type="button" onClick={() => setIsChangePwdOpen(false)} style={{ padding: '8px 12px' }}>Cancel</button>
                                <button type="submit" style={{ padding: '8px 12px' }}>Submit</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    )
}
