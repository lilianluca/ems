import { cn } from '@/lib/utils';

/** Brand mark — keep in sync with public/favicon.svg. */
export function LogoMark({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" aria-hidden className={cn('size-8 shrink-0', className)}>
      <rect width="32" height="32" rx="7" fill="#006b79" />
      <circle cx="8.5" cy="8.5" r="3.25" fill="#e3ae28" />
      <path
        d="M19.5 4 9 18h6.5L13 28l10.5-14.5H17z"
        fill="#fff"
        stroke="#fff"
        strokeWidth="0.75"
        strokeLinejoin="round"
      />
    </svg>
  );
}
