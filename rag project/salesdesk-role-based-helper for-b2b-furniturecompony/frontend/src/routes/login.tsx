import { FormEvent, useMemo, useState } from "react";
import { useNavigate } from "@tanstack/react-router";
import { ArrowRight, Eye, EyeOff, LockKeyhole, Mail, ShieldCheck } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { loginRequest } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/store/auth-store";

type FormErrors = {
  email?: string;
  password?: string;
};

export function LoginPage() {
  const navigate = useNavigate();
  const setSession = useAuthStore((state) => state.setSession);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});
  const [serverError, setServerError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const canSubmit = useMemo(
    () => email.trim().length > 0 && password.length > 0 && !isSubmitting,
    [email, password, isSubmitting],
  );

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setServerError("");

    const nextErrors = validateLogin(email, password);
    setErrors(nextErrors);

    if (Object.keys(nextErrors).length > 0) {
      return;
    }

    setIsSubmitting(true);

    try {
      const data = await loginRequest(email.trim(), password);
      setSession({
        accessToken: data.access_token,
        tokenType: data.token_type,
        user: data.user,
      });
      await navigate({ to: "/home" });
    } catch (error) {
      setServerError(error instanceof Error ? error.message : "Unable to sign in.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top_left,hsl(174_72%_25%/.16),transparent_32%),linear-gradient(135deg,hsl(39_43%_97%),hsl(207_44%_94%))]">
      <div className="mx-auto grid min-h-screen w-full max-w-6xl items-center gap-10 px-5 py-8 md:grid-cols-[1.05fr_0.95fr] md:px-8">
        <section className="hidden md:block">
          <div className="max-w-xl">
            <div className="mb-7 inline-flex items-center gap-2 rounded-full border bg-white/70 px-3 py-1 text-sm font-medium text-primary shadow-sm backdrop-blur">
              <ShieldCheck className="h-4 w-4" />
              Role-based B2B furniture intelligence
            </div>
            <h1 className="text-5xl font-semibold leading-tight tracking-normal text-foreground">
              SalesDesk
            </h1>
            <p className="mt-5 max-w-lg text-lg leading-8 text-muted-foreground">
              Give sales teams one secure workspace for product knowledge, customer context,
              and faster answers.
            </p>
            <div className="mt-10 grid max-w-lg grid-cols-2 gap-4">
              {["Secure tokens", "Role-aware access", "Fast RAG support", "Clean workflows"].map(
                (item) => (
                  <div
                    className="rounded-lg border bg-white/68 px-4 py-3 text-sm font-medium shadow-sm backdrop-blur"
                    key={item}
                  >
                    {item}
                  </div>
                ),
              )}
            </div>
          </div>
        </section>

        <Card className="mx-auto w-full max-w-md border-white/70 bg-white/86 shadow-2xl shadow-slate-900/10 backdrop-blur">
          <CardHeader className="space-y-2">
            <div className="mb-2 flex h-12 w-12 items-center justify-center rounded-lg bg-primary text-primary-foreground shadow">
              <LockKeyhole className="h-6 w-6" />
            </div>
            <CardTitle>Welcome back</CardTitle>
            <CardDescription>Sign in to continue to your SalesDesk workspace.</CardDescription>
          </CardHeader>
          <CardContent>
            <form className="space-y-5" onSubmit={handleSubmit} noValidate>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <div className="relative">
                  <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    placeholder="you@company.com"
                    autoComplete="email"
                    className={cn("pl-9", errors.email && "border-destructive")}
                    aria-invalid={Boolean(errors.email)}
                  />
                </div>
                {errors.email ? (
                  <p className="text-sm font-medium text-destructive">{errors.email}</p>
                ) : null}
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <LockKeyhole className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    placeholder="Minimum 6 characters"
                    autoComplete="current-password"
                    className={cn("px-9", errors.password && "border-destructive")}
                    aria-invalid={Boolean(errors.password)}
                  />
                  <button
                    type="button"
                    className="absolute right-2 top-1/2 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                    onClick={() => setShowPassword((value) => !value)}
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                {errors.password ? (
                  <p className="text-sm font-medium text-destructive">{errors.password}</p>
                ) : null}
              </div>

              {serverError ? (
                <div className="rounded-md border border-destructive/25 bg-destructive/10 px-3 py-2 text-sm font-medium text-destructive">
                  {serverError}
                </div>
              ) : null}

              <Button className="h-11 w-full gap-2" type="submit" disabled={!canSubmit}>
                {isSubmitting ? "Signing in..." : "Sign in"}
                <ArrowRight className="h-4 w-4" />
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}

function validateLogin(email: string, password: string) {
  const nextErrors: FormErrors = {};
  const normalizedEmail = email.trim();

  if (!normalizedEmail) {
    nextErrors.email = "Email is required.";
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(normalizedEmail)) {
    nextErrors.email = "Enter a valid email address.";
  }

  if (!password) {
    nextErrors.password = "Password is required.";
  } else if (password.length < 6) {
    nextErrors.password = "Password must be at least 6 characters.";
  }

  return nextErrors;
}
