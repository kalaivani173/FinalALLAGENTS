import { useEffect, useMemo, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Lock, ShieldCheck, User } from 'lucide-react'
import changeIqBg from '@/assets/changeiq-login-bg.png'
import upiBanner from '@/assets/upi-banner.png'
import fastLogoMark from '@/assets/fast-logo-mark.png'

const ROLES = ['Product', 'Developer', 'Admin']
const DEFAULT_PASSWORD = 'password'

export default function Login({ onLogin }) {
  const [role, setRole] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [headlineWordsShown, setHeadlineWordsShown] = useState(0)

  const heroBanner = useMemo(
    () => ({
      headline: 'Real-time UPI change orchestration',
      subLabel: 'Live readiness tracking',
      icon: ShieldCheck,
    }),
    [],
  )
  const headlineWords = useMemo(() => heroBanner.headline.split(' '), [heroBanner.headline])

  useEffect(() => {
    // Slightly slower word-by-word reveal loop
    let tickTimer = null
    let restartTimer = null

    const start = () => {
      setHeadlineWordsShown(0)
      tickTimer = window.setInterval(() => {
        setHeadlineWordsShown((c) => Math.min(c + 1, headlineWords.length))
      }, 560)
    }

    start()

    restartTimer = window.setInterval(() => {
      setHeadlineWordsShown((c) => {
        if (c >= headlineWords.length) {
          if (tickTimer) window.clearInterval(tickTimer)
          window.setTimeout(() => start(), 2300)
        }
        return c
      })
    }, 900)

    return () => {
      if (tickTimer) window.clearInterval(tickTimer)
      if (restartTimer) window.clearInterval(restartTimer)
    }
  }, [headlineWords.length])

  const handleSubmit = (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    // Simulate API call delay
    setTimeout(() => {
      if (!role) {
        setError('Please select a role')
        setLoading(false)
        return
      }

      if (password !== DEFAULT_PASSWORD) {
        setError('Invalid password. Use "password" for all roles.')
        setLoading(false)
        return
      }

      // Successful login
      setLoading(false)
      onLogin(role)
    }, 500)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-950 to-slate-900 flex items-stretch">
      {/* Left brand panel (70%) */}
      <div className="hidden lg:flex lg:w-[70%] relative overflow-hidden border-r">
        {/* Single background image */}
        <div className="absolute inset-0 bg-cover bg-center" style={{ backgroundImage: `url(${changeIqBg})` }} />
        {/* Readability overlays */}
        <div className="absolute inset-0 bg-gradient-to-br from-slate-950/70 via-slate-950/45 to-[#2F888A]/35" />
        <div className="absolute inset-0 opacity-[0.16] [background-image:linear-gradient(to_right,rgba(255,255,255,0.14)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.12)_1px,transparent_1px)] [background-size:52px_52px]" />
        <div className="absolute -top-24 -left-24 h-72 w-72 rounded-full bg-white/10 blur-3xl" />
        <div className="absolute bottom-[-120px] right-[-120px] h-80 w-80 rounded-full bg-[#2F888A]/20 blur-3xl" />

        <div className="relative z-10 p-12 2xl:p-14 flex flex-col justify-between w-full">
          <div className="space-y-8">
            <div className="flex items-center justify-between gap-6">
              <div className="inline-flex items-center gap-3">
                <div className="flex items-center gap-4">
                  <img
                    src={fastLogoMark}
                    alt="ChangeIQ logo"
                    className="h-20 w-20 object-contain drop-shadow-[0_18px_40px_rgba(2,6,23,0.55)]"
                    loading="lazy"
                  />
                  <div className="leading-tight">
                    <div className="text-[11px] text-white/70 uppercase tracking-[0.24em]">NPCI • UPI</div>
                    <div className="mt-1 text-[44px] font-semibold leading-none brand-3d">
                      ChangeIQ
                    </div>
                  </div>
                </div>
              </div>

            </div>

            {/* Hero banner (fixed headline) */}
            <div className="glass-panel p-8 w-full text-white min-h-[290px] flex items-stretch">
              {(() => {
                const b = heroBanner
                const Icon = b.icon
                return (
                  <div className="w-full">
                    <div className="grid gap-6 xl:grid-cols-[1.55fr_1fr] xl:items-stretch">
                      <div className="flex items-start gap-4">
                        <div className="h-11 w-11 rounded-2xl bg-white/10 border border-white/20 flex items-center justify-center shrink-0 shadow-sm">
                          <Icon className="h-5 w-5 text-white" />
                        </div>
                        <div className="min-w-0">
                          <div
                            className="headline-motion text-[30px] 2xl:text-[36px] font-semibold tracking-tight leading-[1.14] flex flex-wrap gap-x-2 gap-y-1"
                            aria-label={b.headline}
                          >
                            {headlineWords.map((w, idx) => (
                              <span
                                key={`${w}-${idx}`}
                                className={idx < headlineWordsShown ? 'word-in' : 'word-ghost'}
                                style={{ animationDelay: `${idx * 55}ms` }}
                              >
                                {w}
                              </span>
                            ))}
                          </div>
                          <div className="mt-3 text-sm text-white/80">
                            <div>{b.subLabel}</div>
                          </div>
                        </div>
                      </div>

                      <div className="hidden xl:block">
                        <div className="relative h-full min-h-[220px] overflow-hidden rounded-2xl border border-white/15 bg-slate-950/10">
                          {/* Soft fill so the frame never looks empty */}
                          <div
                            className="absolute inset-0 opacity-[0.55] blur-xl scale-[1.08]"
                            style={{ backgroundImage: `url(${upiBanner})`, backgroundSize: 'cover', backgroundPosition: 'center' }}
                            aria-hidden="true"
                          />
                          <div className="absolute inset-0 bg-gradient-to-l from-transparent via-slate-950/10 to-slate-950/35" aria-hidden="true" />

                          {/* Sharp foreground that preserves the full logo */}
                          <img
                            src={upiBanner}
                            alt="UPI"
                            className="relative z-10 h-full w-full object-contain p-2 opacity-[0.98] [filter:saturate(1.05)_contrast(1.05)]"
                            loading="lazy"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                )
              })()}
            </div>
          </div>

          <div className="text-xs text-white/70" />
        </div>
      </div>

      {/* Right sign-in panel (30%) */}
      <div className="flex-1 lg:w-[30%] relative flex items-center justify-center p-6 sm:p-10 bg-gradient-to-br from-slate-50 via-sky-50/80 to-[#2F888A]/10">
        <div className="absolute inset-0 opacity-[0.55] [background-image:radial-gradient(circle_at_15%_20%,rgba(56,189,248,0.35),transparent_42%),radial-gradient(circle_at_85%_25%,rgba(99,102,241,0.22),transparent_45%),radial-gradient(circle_at_30%_85%,rgba(14,165,233,0.18),transparent_42%)]" />
        <div className="absolute inset-0 opacity-[0.10] [background-image:linear-gradient(to_right,rgba(2,6,23,0.10)_1px,transparent_1px),linear-gradient(to_bottom,rgba(2,6,23,0.08)_1px,transparent_1px)] [background-size:56px_56px]" />

        <Card className="relative w-full max-w-md border-slate-200/50 bg-white/18 backdrop-blur-2xl shadow-md shadow-slate-900/10">
          <CardHeader className="space-y-2">
            <div className="flex justify-center">
              <div className="bg-white/18 p-3 rounded-2xl border border-slate-200/50">
                <Lock className="h-7 w-7 text-primary" />
              </div>
            </div>
            <CardTitle className="text-2xl text-center text-slate-900">Sign in to ChangeIQ</CardTitle>
            <CardDescription className="text-center text-slate-600">
              Choose a role to continue
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="role" className="text-slate-700">Role</Label>
                <Select value={role} onValueChange={setRole} required>
                  <SelectTrigger id="role">
                    <SelectValue placeholder="Select your role" />
                  </SelectTrigger>
                  <SelectContent>
                    {ROLES.map((r) => (
                      <SelectItem key={r} value={r}>
                        {r}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="password" className="text-slate-700">Password</Label>
                <div className="relative">
                  <User className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                  <Input
                    id="password"
                    type="password"
                    placeholder="Enter password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="pl-10"
                    required
                  />
                </div>
                <p className="text-xs text-slate-500">
                  Default password: <span className="font-mono">password</span>
                </p>
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md text-sm">
                  {error}
                </div>
              )}

              <Button type="submit" disabled={loading} className="w-full">
                {loading ? 'Signing in...' : 'Sign In'}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
