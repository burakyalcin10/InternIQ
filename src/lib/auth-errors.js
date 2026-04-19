export function formatAuthErrorMessage(error) {
  const rawMessage = error?.message || 'Beklenmeyen bir kimlik doğrulama hatası oluştu.'
  const message = rawMessage.toLowerCase()

  if (message.includes('email rate limit exceeded')) {
    return 'Çok kısa sürede fazla kayıt denemesi yapıldı. Supabase doğrulama e-postasını geçici olarak sınırladı. Birkaç dakika bekleyip tekrar deneyin veya gelen doğrulama e-postasını kontrol edin.'
  }

  if (message.includes('user already registered')) {
    return 'Bu e-posta ile daha önce kayıt olunmuş görünüyor. Doğrudan giriş yapmayı deneyin.'
  }

  if (message.includes('invalid login credentials')) {
    return 'E-posta veya şifre hatalı görünüyor.'
  }

  if (message.includes('email not confirmed')) {
    return 'E-posta adresinizi henüz doğrulamadınız. Gelen kutunuzu ve spam klasörünü kontrol edin.'
  }

  if (message.includes('password should be at least')) {
    return 'Şifre en az 6 karakter olmalıdır.'
  }

  if (message.includes('invalid email')) {
    return 'Geçerli bir e-posta adresi girin.'
  }

  return rawMessage
}
