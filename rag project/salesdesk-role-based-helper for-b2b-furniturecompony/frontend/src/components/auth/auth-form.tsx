import { type InputHTMLAttributes, type ReactNode, useState } from "react";
import { Eye, EyeOff, LockKeyhole, ShieldCheck, type LucideIcon } from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";

type AuthPageLayoutProps = {
  children: ReactNode;
  description: string;
  footer?: ReactNode;
  icon: ReactNode;
  title: string;
};

export function AuthPageLayout({
  children,
  description,
  footer,
  icon,
  title,
}: AuthPageLayoutProps) {
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
              {icon}
            </div>
            <CardTitle>{title}</CardTitle>
            <CardDescription>{description}</CardDescription>
          </CardHeader>
          <CardContent>
            {children}
            {footer ? (
              <div className="mt-6 border-t pt-5 text-center text-sm text-muted-foreground">
                {footer}
              </div>
            ) : null}
          </CardContent>
        </Card>
      </div>
    </main>
  );
}

type AuthInputFieldProps = InputHTMLAttributes<HTMLInputElement> & {
  error?: string;
  icon: LucideIcon;
  label: string;
};

export function AuthInputField({
  className,
  error,
  icon: Icon,
  id,
  label,
  ...inputProps
}: AuthInputFieldProps) {
  return (
    <div className="space-y-2">
      <Label htmlFor={id}>{label}</Label>
      <div className="relative">
        <Icon className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          id={id}
          className={cn("pl-9", error && "border-destructive", className)}
          aria-invalid={Boolean(error)}
          {...inputProps}
        />
      </div>
      {error ? <p className="text-sm font-medium text-destructive">{error}</p> : null}
    </div>
  );
}

type PasswordFieldProps = Omit<AuthInputFieldProps, "icon" | "type">;

export function PasswordField({
  autoComplete,
  error,
  id,
  label,
  ...inputProps
}: PasswordFieldProps) {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <div className="space-y-2">
      <Label htmlFor={id}>{label}</Label>
      <div className="relative">
        <LockKeyhole className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          id={id}
          type={showPassword ? "text" : "password"}
          autoComplete={autoComplete}
          className={cn("px-9", error && "border-destructive")}
          aria-invalid={Boolean(error)}
          {...inputProps}
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
      {error ? <p className="text-sm font-medium text-destructive">{error}</p> : null}
    </div>
  );
}

export function AuthFormError({ message }: { message: string }) {
  if (!message) {
    return null;
  }

  return (
    <div className="rounded-md border border-destructive/25 bg-destructive/10 px-3 py-2 text-sm font-medium text-destructive">
      {message}
    </div>
  );
}
