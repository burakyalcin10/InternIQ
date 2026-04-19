import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

export default function ScrollToTop() {
  const { pathname, hash, search } = useLocation()
  useEffect(() => {
    const params = new URLSearchParams(search)
    const shouldSkipTopScroll = hash || params.get('autorun') === '1'

    if (shouldSkipTopScroll) {
      return
    }
    window.scrollTo(0, 0)
  }, [pathname, hash, search])
  return null
}
