import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn('Supabase ortam değişkenleri eksik. VITE_SUPABASE_URL ve VITE_SUPABASE_ANON_KEY tanımlanmalı.')
}

export const supabase = createClient(
  supabaseUrl || 'https://example.supabase.co',
  supabaseAnonKey || 'public-anon-key',
  {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
      detectSessionInUrl: true,
    },
  },
)

export function clearSupabaseAuthStorage() {
  if (typeof window === 'undefined') {
    return
  }

  const clearStorage = (storage) => {
    const keys = []

    for (let index = 0; index < storage.length; index += 1) {
      const key = storage.key(index)
      if (key?.startsWith('sb-') || key?.includes('supabase.auth')) {
        keys.push(key)
      }
    }

    keys.forEach((key) => storage.removeItem(key))
  }

  clearStorage(window.localStorage)
  clearStorage(window.sessionStorage)
}
