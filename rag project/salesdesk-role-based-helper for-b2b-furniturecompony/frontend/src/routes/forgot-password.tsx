import { type FormEvent, useMemo, useState } from "react";
import { Link } from "@tanstack/react-router";
import { ArrowRight, CheckCircle2, KeyRound, Mail } from "lucide-react";

import {
  AuthFormError,
  AuthInputField,
  AuthPageLayout,
  PasswordField,
} from "@/components/auth/auth-form";
import { Button } from "@/components/ui/button";
import {
  usePasswordResetConfirmation,
  usePasswordResetRequest,
  usePasswordResetVerification,
} from "@/hooks/api";
import { validateEmail, validatePassword } from "@/lib/form-validation";

type ResetStep = "email" | "otp" | "password" | "complete";

export function ForgotPasswordPage() {
  const [step, setStep] = useState<ResetStep>("email");
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [resetToken, setResetToken] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [fieldError, setFieldError] = useState("");
  const requestAction = usePasswordResetRequest();
  const verificationAction = usePasswordResetVerification();
  const confirmationAction = usePasswordResetConfirmation();
  const isSubmitting =
    requestAction.isLoading ||
    verificationAction.isLoading ||
    confirmationAction.isLoading;
  const serverError =
    requestAction.error || verificationAction.error || confirmationAction.error;

  const canSubmit = useMemo(() => {
    if (isSubmitting) return false;
    if (step === "email") return email.trim().length > 0;
    if (step === "otp") return otp.length === 6;
    if (step === "password") return password.length > 0 && confirmPassword.length > 0;
    return false;
  }, [confirmPassword, email, isSubmitting, otp, password, step]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFieldError("");

    if (step === "email") {
      const error = validateEmail(email);
      if (error) {
        setFieldError(error);
        return;
      }
    }

    if (step === "otp" && !/^\d{6}$/.test(otp)) {
      setFieldError("Enter the six-digit code from your email.");
      return;
    }

    if (step === "password") {
      const error = validatePassword(password);
      if (error) {
        setFieldError(error);
        return;
      }
      if (password !== confirmPassword) {
        setFieldError("Passwords do not match.");
        return;
      }
    }

    if (step === "email") {
      const response = await requestAction.execute(email.trim());
      if (response) {
        setStep("otp");
      }
    } else if (step === "otp") {
      const response = await verificationAction.execute(email.trim(), otp);
      if (response) {
        setResetToken(response.reset_token);
        setStep("password");
      }
    } else if (step === "password") {
      const response = await confirmationAction.execute(
        resetToken,
        password,
        confirmPassword,
      );
      if (response) {
        setStep("complete");
      }
    }
  }

  return (
    <AuthPageLayout
      title={getStepTitle(step)}
      description={getStepDescription(step, email)}
      icon={
        step === "complete" ? (
          <CheckCircle2 className="h-6 w-6" />
        ) : (
          <KeyRound className="h-6 w-6" />
        )
      }
      footer={
        <Link className="font-semibold text-primary hover:underline" to="/">
          Back to sign in
        </Link>
      }
    >
      {step === "complete" ? (
        <div className="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-4 text-sm text-emerald-800">
          Your password has been updated. You can now sign in with the new password.
        </div>
      ) : (
        <form className="space-y-5" onSubmit={handleSubmit} noValidate>
          {step === "email" ? (
            <AuthInputField
              id="reset-email"
              label="Email"
              icon={Mail}
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@company.com"
              autoComplete="email"
              error={fieldError}
            />
          ) : null}

          {step === "otp" ? (
            <AuthInputField
              id="reset-otp"
              label="Verification code"
              icon={KeyRound}
              value={otp}
              onChange={(event) =>
                setOtp(event.target.value.replace(/\D/g, "").slice(0, 6))
              }
              placeholder="000000"
              inputMode="numeric"
              autoComplete="one-time-code"
              maxLength={6}
              error={fieldError}
            />
          ) : null}

          {step === "password" ? (
            <>
              <PasswordField
                id="new-password"
                label="New password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="Minimum 6 characters"
                autoComplete="new-password"
                error={fieldError || undefined}
              />
              <PasswordField
                id="confirm-new-password"
                label="Confirm new password"
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
                placeholder="Enter the password again"
                autoComplete="new-password"
              />
            </>
          ) : null}

          <AuthFormError message={serverError} />

          <Button className="h-11 w-full gap-2" type="submit" disabled={!canSubmit}>
            {getSubmitLabel(step, isSubmitting)}
            <ArrowRight className="h-4 w-4" />
          </Button>
        </form>
      )}
    </AuthPageLayout>
  );
}

function getStepTitle(step: ResetStep) {
  if (step === "email") return "Forgot password?";
  if (step === "otp") return "Check your email";
  if (step === "password") return "Create a new password";
  return "Password updated";
}

function getStepDescription(step: ResetStep, email: string) {
  if (step === "email") return "Enter your account email to receive a verification code.";
  if (step === "otp") return `Enter the six-digit code sent to ${email}.`;
  if (step === "password") return "Choose a new password for your SalesDesk account.";
  return "Your account is ready to use again.";
}

function getSubmitLabel(step: ResetStep, isSubmitting: boolean) {
  if (isSubmitting) return "Please wait...";
  if (step === "email") return "Send verification code";
  if (step === "otp") return "Verify code";
  return "Update password";
}
