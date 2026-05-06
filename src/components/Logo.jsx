/**
 * InternIQ logomark — 5-square matrix pattern.
 *
 * Evokes IQ-test pattern recognition: four corner squares + one center square.
 * Works at any size. Use `standalone` when the background is not already colored.
 */
export default function Logo({ size = 28, standalone = false, className = '' }) {
  if (standalone) {
    return (
      <svg
        width={size}
        height={size}
        viewBox="0 0 28 28"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className={className}
        aria-label="InternIQ logo"
      >
        <rect width="28" height="28" rx="4" fill="#f59e0b" />
        {/* top-left */}
        <rect x="3" y="3" width="5" height="5" fill="#0a0a0a" />
        {/* top-right */}
        <rect x="20" y="3" width="5" height="5" fill="#0a0a0a" />
        {/* center */}
        <rect x="11" y="11" width="6" height="6" fill="#0a0a0a" />
        {/* bottom-left */}
        <rect x="3" y="20" width="5" height="5" fill="#0a0a0a" />
        {/* bottom-right */}
        <rect x="20" y="20" width="5" height="5" fill="#0a0a0a" />
      </svg>
    )
  }

  // Mark-only variant — fills are currentColor so the parent controls the color.
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 28 28"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-label="InternIQ logo"
    >
      <rect x="3" y="3" width="5" height="5" fill="currentColor" />
      <rect x="20" y="3" width="5" height="5" fill="currentColor" />
      <rect x="11" y="11" width="6" height="6" fill="currentColor" />
      <rect x="3" y="20" width="5" height="5" fill="currentColor" />
      <rect x="20" y="20" width="5" height="5" fill="currentColor" />
    </svg>
  )
}
