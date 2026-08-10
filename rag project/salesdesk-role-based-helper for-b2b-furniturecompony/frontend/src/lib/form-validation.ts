export function validateEmail(email: string) {
  const normalizedEmail = email.trim();

  if (!normalizedEmail) {
    return "Email is required.";
  }

  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(normalizedEmail)) {
    return "Enter a valid email address.";
  }

  return undefined;
}

export function validatePassword(password: string) {
  if (!password) {
    return "Password is required.";
  }

  if (password.length < 6) {
    return "Password must be at least 6 characters.";
  }

  if (new TextEncoder().encode(password).length > 72) {
    return "Password cannot be longer than 72 bytes.";
  }

  return undefined;
}
