import { useEffect, useState } from 'react'
import { AuthContext } from './auth-context'
import { getCurrentUser, getProfile, uploadProfileCv } from '../services/api'
import { formatAuthErrorMessage } from '../lib/auth-errors'
import { supabase } from '../lib/supabase'

export function AuthProvider({ children }) {
  const [session, setSession] = useState(null)
  const [user, setUser] = useState(null)
  const [profile, setProfile] = useState(null)
  const [authLoading, setAuthLoading] = useState(true)

  useEffect(() => {
    let active = true

    const syncFromSession = async (nextSession) => {
      if (!active) return

      setSession(nextSession)
      if (!nextSession?.access_token) {
        setUser(null)
        setProfile(null)
        setAuthLoading(false)
        return
      }

      try {
        const data = await getCurrentUser()
        if (!active) return
        setUser(data.user)
        setProfile(data.profile)
      } catch (error) {
        console.error('Auth sync failed:', error)
        setUser(null)
        setProfile(null)
      } finally {
        if (active) {
          setAuthLoading(false)
        }
      }
    }

    const bootstrap = async () => {
      try {
        const { data } = await supabase.auth.getSession()
        await syncFromSession(data.session)
      } catch (error) {
        console.warn('Supabase session unavailable; continuing as guest.', error)
        await syncFromSession(null)
      }
    }

    bootstrap()

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      syncFromSession(nextSession)
    })

    return () => {
      active = false
      subscription.unsubscribe()
    }
  }, [])

  const register = async ({ name, email, password }) => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name: name,
        },
      },
    })

    if (error) {
      error.message = formatAuthErrorMessage(error)
      throw error
    }

    if (!data.session) {
      return {
        message: 'Kayıt oluşturuldu. E-posta doğrulama bağlantısını kontrol edin.',
        requiresEmailConfirmation: true,
      }
    }

    const me = await getCurrentUser()
    setSession(data.session)
    setUser(me.user)
    setProfile(me.profile)
    return {
      message: 'Hesabınız oluşturuldu.',
      requiresEmailConfirmation: false,
    }
  }

  const login = async ({ email, password }) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })

    if (error) {
      error.message = formatAuthErrorMessage(error)
      throw error
    }

    const me = await getCurrentUser()
    setSession(data.session)
    setUser(me.user)
    setProfile(me.profile)
    return {
      message: 'Giriş başarılı.',
    }
  }

  const logout = async () => {
    const { error } = await supabase.auth.signOut()
    if (error) {
      throw error
    }
    setSession(null)
    setUser(null)
    setProfile(null)
  }

  const refreshProfile = async () => {
    const nextProfile = await getProfile()
    setProfile(nextProfile)
    return nextProfile
  }

  const saveProfileCv = async ({ cvFile, cvText }) => {
    const data = await uploadProfileCv(cvFile, cvText)
    setUser(data.user)
    setProfile(data.profile)
    return data
  }

  const value = {
    session,
    user,
    profile,
    authLoading,
    isAuthenticated: Boolean(session?.access_token && user),
    register,
    login,
    logout,
    refreshProfile,
    saveProfileCv,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
