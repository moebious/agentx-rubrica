import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Rubrica SRE Agent',
  description: 'Autonomous SRE Incident Intake & Triage',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
