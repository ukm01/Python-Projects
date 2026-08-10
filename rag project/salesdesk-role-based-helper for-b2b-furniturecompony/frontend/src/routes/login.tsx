import { type FormEvent, useMemo, useState } from "react";
import { Link, useNavigate } from "@tanstack/react-router";
import { ArrowRight, LockKeyhole, Mail } from "lucide-react";

import {
  AuthFormError,
  AuthInputField,
  AuthPageLayout,
  PasswordField,
} from "@/components/auth/auth-form";
import { Button } from "@/components/ui/button";
import { useLogin } from "@/hooks/api";
import { validateEmail, validatePassword } from "@/lib/form-validation";
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
  const [errors, setErrors] = useState<FormErrors>({});
  const {
    execute: login,
    isLoading: isSubmitting,
    error: serverError,
  } = useLogin();

  const canSubmit = useMemo(
    () => email.trim().length > 0 && password.length > 0 && !isSubmitting,
    [email, password, isSubmitting],
  );

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const nextErrors = validateLogin(email, password);
    setErrors(nextErrors);

    if (Object.values(nextErrors).some(Boolean)) {
      return;
    }

    const data = await login(email.trim(), password);

    if (!data) return;

    setSession({
      accessToken: data.access_token,
      tokenType: data.token_type,
      user: data.user,
    });
    await navigate({ to: "/home" });
  }

  return (
    <AuthPageLayout
      title="Welcome back"
      description="Sign in to continue to your SalesDesk workspace."
      icon={<LockKeyhole className="h-6 w-6" />}
      footer={
        <Link className="font-semibold text-primary hover:underline" to="/forgot-password">
          Forgot password?
        </Link>
      }
    >
      <form className="space-y-5" onSubmit={handleSubmit} noValidate>
        <AuthInputField
          id="email"
          label="Email"
          icon={Mail}
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="you@company.com"
          autoComplete="email"
          error={errors.email}
        />

        <PasswordField
          id="password"
          label="Password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="Minimum 6 characters"
          autoComplete="current-password"
          error={errors.password}
        />

        <AuthFormError message={serverError} />

        <Button className="h-11 w-full gap-2" type="submit" disabled={!canSubmit}>
          {isSubmitting ? "Signing in..." : "Sign in"}
          <ArrowRight className="h-4 w-4" />
        </Button>
      </form>
    </AuthPageLayout>
  );
}

function validateLogin(email: string, password: string) {
  return {
    email: validateEmail(email),
    password: validatePassword(password),
  };
}
